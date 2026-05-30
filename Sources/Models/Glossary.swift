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

@MainActor
final class GlossaryStore: ObservableObject {
    @Published private(set) var allTerms: [Term] = []
    @Published private(set) var byLetter: [String: [Term]] = [:]
    @Published private(set) var letters: [String] = []
    @Published private(set) var favorites: Set<String> = []

    /// Cache of hyperlinked AttributedStrings, keyed by "<term.id>::<field>" where
    /// field ∈ {plain, snappy, detail}. Prewarmed off the main thread in `load()`.
    var attributedCache: [String: AttributedString] = [:]

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
            prewarmAttributedCache(terms: terms)
        } catch {
            assertionFailure("Failed to decode \(Brand.current.dataResource).json: \(error)")
        }
    }

    /// Build the hyperlinked AttributedString for every (term, field) pair off
    /// the main thread, then bulk-merge into the cache. The regex pass is the
    /// dominant cost of pushing a TermDetailView; prewarming makes repeat
    /// navigations effectively free across all three tiers.
    private func prewarmAttributedCache(terms: [Term]) {
        let urlScheme = Brand.current.urlScheme
        Task.detached(priority: .utility) { [weak self] in
            var built: [String: AttributedString] = [:]
            built.reserveCapacity(terms.count * 3)
            for term in terms {
                if term.hasPlain {
                    built["\(term.id)::plain"] = Self.computeAttributedText(term.plain, currentTermId: term.id, allTerms: terms, urlScheme: urlScheme)
                }
                if term.hasSnappy {
                    built["\(term.id)::snappy"] = Self.computeAttributedText(term.snappy, currentTermId: term.id, allTerms: terms, urlScheme: urlScheme)
                }
                built["\(term.id)::detail"] = Self.computeAttributedText(term.detail, currentTermId: term.id, allTerms: terms, urlScheme: urlScheme)
            }
            await MainActor.run {
                guard let self else { return }
                for (key, attr) in built where self.attributedCache[key] == nil {
                    self.attributedCache[key] = attr
                }
            }
        }
    }

    func search(_ query: String) -> [Term] {
        let q = query.trimmingCharacters(in: .whitespacesAndNewlines).lowercased()
        guard !q.isEmpty else { return [] }
        return allTerms.filter {
            $0.term.lowercased().contains(q)
                || $0.full.lowercased().contains(q)
                || $0.snappy.lowercased().contains(q)
                || $0.detail.lowercased().contains(q)
        }
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
