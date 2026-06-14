import Foundation

struct Term: Codable, Identifiable, Hashable {
    let letter: String
    let term: String
    let full: String
    /// Total-novice tier — one jargon-free sentence written for someone who has
    /// never heard of the term. Empty for terms that haven't been backfilled yet.
    /// See `docs/clarity-policy.md` for authoring rules.
    let plain: String
    let snappy: String
    let detail: String
    let indications: [String]
    let category: String
    let sources: [String]
    /// Extra surface forms that should also link to this entry — short/long forms,
    /// acronyms, and hyphen variants the linker can't derive from the canonical name
    /// (e.g. "ACE" → "ACE Inhibitor", "AMR" → "Antimicrobial Resistance", "BCL-2" →
    /// "BCL2"). Optional in JSON; defaults to []. Curate conservatively — an alias that
    /// collides with a common word or another entry's name creates wrong-sense links.
    let aliases: [String]

    var id: String { "\(letter)::\(term)" }

    var hasFull: Bool { !full.isEmpty }
    var hasPlain: Bool { !plain.isEmpty }
    var hasSnappy: Bool { !snappy.isEmpty }
    var hasCategory: Bool { !category.isEmpty }
    var hasSources: Bool { !sources.isEmpty }

    var shareText: String {
        var s = term
        if hasFull { s += " (\(full))" }
        if hasPlain { s += "\n\n\(plain)" }
        if hasSnappy { s += "\n\n\(snappy)" }
        s += "\n\n\(detail)"
        return s
    }

    // Custom decoder so existing glossary JSONs (which predate the `plain` field)
    // decode successfully — missing `plain` defaults to "". Swift still
    // synthesises encode(to:) from the CodingKeys enum below.
    enum CodingKeys: String, CodingKey {
        case letter, term, full, plain, snappy, detail, indications, category, sources, aliases
    }

    init(from decoder: Decoder) throws {
        let c = try decoder.container(keyedBy: CodingKeys.self)
        letter = try c.decode(String.self, forKey: .letter)
        term = try c.decode(String.self, forKey: .term)
        full = try c.decodeIfPresent(String.self, forKey: .full) ?? ""
        plain = try c.decodeIfPresent(String.self, forKey: .plain) ?? ""
        snappy = try c.decodeIfPresent(String.self, forKey: .snappy) ?? ""
        detail = try c.decode(String.self, forKey: .detail)
        indications = try c.decodeIfPresent([String].self, forKey: .indications) ?? []
        category = try c.decodeIfPresent(String.self, forKey: .category) ?? ""
        sources = try c.decodeIfPresent([String].self, forKey: .sources) ?? []
        aliases = try c.decodeIfPresent([String].self, forKey: .aliases) ?? []
    }

    /// "Source: [FDA](https://www.fda.gov), [NIH](https://www.nih.gov)".
    /// Each source name becomes a markdown link if `Brand.sourceURLs` has
    /// a matching key; otherwise it renders as plain text.
    var sourcesMarkdown: String {
        let urls = Brand.current.sourceURLs
        let parts = sources.map { name -> String in
            if let url = urls[name] {
                return "[\(name)](\(url.absoluteString))"
            }
            return name
        }
        return "Source: " + parts.joined(separator: ", ")
    }
}

struct FilterState: Equatable {
    var indications: Set<String> = []
    var categories: Set<String> = []

    var isActive: Bool { !indications.isEmpty || !categories.isEmpty }

    var summary: String {
        let parts = indications.sorted() + categories.sorted()
        return parts.joined(separator: " · ")
    }
}

/// One row of the precomputed search index: a term plus its lowercased searchable
/// fields, built once in `load()` so per-keystroke ranking never re-lowercases the
/// corpus. `blob` concatenates the three definition tiers for body matches.
struct SearchRow {
    let term: Term
    let name: String       // lowercased canonical name
    let full: String       // lowercased acronym expansion
    let aliases: [String]  // lowercased aliases
    let blob: String       // lowercased plain + snappy + detail
}

@MainActor
final class GlossaryStore: ObservableObject {
    @Published private(set) var allTerms: [Term] = []
    @Published private(set) var byLetter: [String: [Term]] = [:]
    @Published private(set) var letters: [String] = []
    @Published private(set) var favorites: Set<String> = []

    /// Cache of hyperlinked AttributedStrings, keyed by "<term.id>::<field>" where
    /// field ∈ {plain, snappy, detail}. Built lazily on first view and cached.
    var attributedCache: [String: AttributedString] = [:]

    /// The industry's link units (term names + aliases → precompiled regex), compiled
    /// ONCE and reused for every linkification. Filled off-main by `prewarmLinkUnits()`.
    var linkUnitsCache: [LinkUnit]?

    /// Precomputed lowercased search fields, built once in `load()`.
    private(set) var searchIndex: [SearchRow] = []

    let industryID: IndustryID

    private var favoritesKey: String {
        "pg.favorites.\(industryID.rawValue).v1"
    }

    var alphabetLetters: [String] {
        letters.filter { $0.range(of: "^[A-Z]$", options: .regularExpression) != nil }
    }

    func terms(forLens lens: LensConfig) -> [Term] {
        let matched: [Term]
        switch lens.kind {
        case .allowlist(let allow):
            matched = allTerms.filter { allow.contains($0.term) }
        case .categoryFilter(let categories, let excludedTerms):
            matched = allTerms.filter {
                categories.contains($0.category) && !excludedTerms.contains($0.term)
            }
        }
        return matched.sorted {
            $0.term.localizedCaseInsensitiveCompare($1.term) == .orderedAscending
        }
    }

    init(industryID: IndustryID) {
        self.industryID = industryID
        IndustryConfig.activate(industryID)
        load()
        loadFavorites()
    }

    // MARK: - Favorites

    private func loadFavorites() {
        // One-time migration: legacy Pharma installs stored favorites under
        // "pg.favorites.v1". Move them to the per-industry key so they survive
        // the JB Pharma → JB Glossary rebrand.
        if industryID == .pharma {
            let legacyKey = "pg.favorites.v1"
            if UserDefaults.standard.stringArray(forKey: favoritesKey) == nil,
               let legacy = UserDefaults.standard.stringArray(forKey: legacyKey) {
                UserDefaults.standard.set(legacy, forKey: favoritesKey)
            }
        }
        let stored = UserDefaults.standard.stringArray(forKey: favoritesKey) ?? []
        favorites = Set(stored)
    }

    private func persistFavorites() {
        UserDefaults.standard.set(Array(favorites).sorted(), forKey: favoritesKey)
    }

    func toggleFavorite(_ term: Term) {
        if favorites.contains(term.term) {
            favorites.remove(term.term)
        } else {
            favorites.insert(term.term)
        }
        persistFavorites()
    }

    func isFavorited(_ term: Term) -> Bool {
        favorites.contains(term.term)
    }

    var favoriteTerms: [Term] {
        allTerms
            .filter { favorites.contains($0.term) }
            .sorted { $0.term.localizedCaseInsensitiveCompare($1.term) == .orderedAscending }
    }

    private func load() {
        guard let url = Bundle.main.url(forResource: Brand.current.dataResource, withExtension: "json") else {
            assertionFailure("\(Brand.current.dataResource).json missing from bundle")
            return
        }
        do {
            let data = try Data(contentsOf: url)
            let terms = try JSONDecoder().decode([Term].self, from: data)
            self.allTerms = terms
            self.byLetter = Dictionary(grouping: terms, by: { $0.letter })
            self.letters = byLetter.keys.sorted()
            self.searchIndex = terms.map { t in
                SearchRow(
                    term: t,
                    name: t.term.lowercased(),
                    full: t.full.lowercased(),
                    aliases: t.aliases.map { $0.lowercased() },
                    blob: "\(t.plain) \(t.snappy) \(t.detail)".lowercased()
                )
            }
            prewarmLinkUnits()
        } catch {
            assertionFailure("Failed to decode \(Brand.current.dataResource).json: \(error)")
        }
    }

    /// Compile the industry's link units ONCE, off the main thread, so the first
    /// term-open doesn't pay ~2,700 regex compilations on the main thread. Replaces
    /// the old eager prewarm of every (term,field) AttributedString — at ~2,400
    /// entries that flooded a CPU core with ~19M regex ops right after launch.
    /// Attributed strings are now built lazily on first view and cached per (term,field).
    private func prewarmLinkUnits() {
        let terms = allTerms
        Task.detached(priority: .utility) { [weak self] in
            let units = GlossaryStore.buildUnits(terms)
            await MainActor.run { self?.linkUnitsCache = units }
        }
    }

    /// Result cap for the search box — top-ranked matches only, so the results List
    /// stays light even when a short query matches hundreds of definition bodies.
    static let searchResultLimit = 60

    /// Ranked, capped search over the precomputed index. Sorts by relevance score
    /// (term-name prefixes first, definition-body matches last), then alphabetically.
    func search(_ query: String) -> [Term] {
        let q = query.trimmingCharacters(in: .whitespacesAndNewlines).lowercased()
        guard !q.isEmpty else { return [] }
        var scored: [(term: Term, score: Int)] = []
        for row in searchIndex {
            let s = Self.searchScore(name: row.name, full: row.full, aliases: row.aliases, blob: row.blob, query: q)
            if s > 0 { scored.append((row.term, s)) }
        }
        scored.sort {
            $0.score != $1.score
                ? $0.score > $1.score
                : $0.term.term.localizedCaseInsensitiveCompare($1.term.term) == .orderedAscending
        }
        return scored.prefix(Self.searchResultLimit).map(\.term)
    }

    /// Rank one term against a lowercased query (all inputs pre-lowercased). Higher =
    /// better. Tiers, high→low: exact name, name prefix, alias prefix, word-prefix in a
    /// multi-word name, name substring, alias substring, acronym/full match, definition
    /// body. Single-char queries skip the body to avoid flooding results. 0 = no match.
    nonisolated static func searchScore(name: String, full: String, aliases: [String], blob: String, query q: String) -> Int {
        if name == q { return 1000 }
        if name.hasPrefix(q) { return 900 }
        if aliases.contains(where: { $0.hasPrefix(q) }) { return 820 }
        if name.split(whereSeparator: { $0 == " " || $0 == "-" }).contains(where: { $0.hasPrefix(q) }) { return 800 }
        if name.contains(q) { return 600 }
        if aliases.contains(where: { $0.contains(q) }) { return 500 }
        if !full.isEmpty && full.contains(q) { return 400 }
        if q.count >= 2 && blob.contains(q) { return 100 }
        return 0
    }

    func filtered(by filter: FilterState) -> [Term] {
        allTerms
            .filter { term in
                let indMatch = filter.indications.isEmpty
                    || !filter.indications.isDisjoint(with: Set(term.indications))
                let catMatch = filter.categories.isEmpty
                    || filter.categories.contains(term.category)
                return indMatch && catMatch
            }
            .sorted { $0.term.localizedCaseInsensitiveCompare($1.term) == .orderedAscending }
    }

    var allIndications: [String] {
        let counts = allTerms.reduce(into: [String: Int]()) { acc, term in
            for ind in term.indications { acc[ind, default: 0] += 1 }
        }
        return counts.keys.sorted { (counts[$0] ?? 0) > (counts[$1] ?? 0) }
    }

    var allCategories: [String] {
        let counts = allTerms.reduce(into: [String: Int]()) { acc, term in
            acc[term.category, default: 0] += 1
        }
        return counts.keys.sorted { (counts[$0] ?? 0) > (counts[$1] ?? 0) }
    }

    func indicationCount(_ name: String) -> Int {
        allTerms.reduce(0) { $0 + ($1.indications.contains(name) ? 1 : 0) }
    }

    func categoryCount(_ name: String) -> Int {
        allTerms.reduce(0) { $0 + ($1.category == name ? 1 : 0) }
    }
}
