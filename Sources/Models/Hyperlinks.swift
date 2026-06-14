import Foundation
import SwiftUI

/// One compiled link target: the matched surface form, its precompiled word-bounded
/// regex, and the term it resolves to. Compiled ONCE per industry (see
/// `GlossaryStore.linkUnitsCache`) and reused across every term/field, instead of
/// recompiling ~2,700 regexes on every linkification.
typealias LinkUnit = (text: String, regex: NSRegularExpression, term: Term)

extension GlossaryStore {
    /// Builds an AttributedString for a term's detail body, with every reference to
    /// another known term wrapped as a tappable `<brand-scheme>://term/<name>` link
    /// styled in the brand accent color with a thin underline. Cached per
    /// (term, field) — see `attributedCache` on `GlossaryStore`.
    func attributedDetail(for term: Term) -> AttributedString {
        attributedText(term.detail, for: term, field: "detail")
    }

    /// Same hyperlink treatment, applied to the "plain English" tier (the
    /// novice-friendly line above snappy). Empty when the term has no `plain`.
    func attributedPlain(for term: Term) -> AttributedString {
        attributedText(term.plain, for: term, field: "plain")
    }

    /// Same hyperlink treatment, applied to the intermediate `snappy` tier.
    func attributedSnappy(for term: Term) -> AttributedString {
        attributedText(term.snappy, for: term, field: "snappy")
    }

    private func attributedText(_ body: String, for term: Term, field: String) -> AttributedString {
        let key = "\(term.id)::\(field)"
        if let cached = attributedCache[key] { return cached }
        // Reuse the industry's precompiled link units instead of rebuilding ~2,700
        // regexes on every call — the dominant cost of opening a term detail.
        let built = Self.applyUnits(to: body, units: cachedUnits(), currentTermId: term.id, urlScheme: Brand.current.urlScheme)
        attributedCache[key] = built
        return built
    }

    /// The industry's link units, compiled once and cached. Built eagerly off the
    /// main thread by `prewarmLinkUnits()`; this is the lazy fallback for the rare
    /// case a term is opened before that finishes.
    func cachedUnits() -> [LinkUnit] {
        if let u = linkUnitsCache { return u }
        let u = Self.buildUnits(allTerms)
        linkUnitsCache = u
        return u
    }

    /// Generic linker. Used for all three tiers (`plain`, `snappy`, `detail`)
    /// because the rules — longest-first, acronym case-sensitivity, hyphen-aware
    /// word boundaries — are identical for any prose that references other terms.
    nonisolated static func computeAttributedText(_ body: String, currentTermId: String, allTerms: [Term], urlScheme: String) -> AttributedString {
        applyUnits(to: body, units: buildUnits(allTerms), currentTermId: currentTermId, urlScheme: urlScheme)
    }

    /// Compile the link units for a term set: every term's canonical name AND each of
    /// its aliases (≥2 chars), each with a precompiled word-bounded regex resolving to
    /// that term. Sorted longest-first (by the matched string) so "ACE Inhibitor" wins
    /// over the alias "ACE", and "monoclonal antibody" wins over "antibody".
    ///
    /// Acronym strings (no lowercase, e.g. "ALL", "AMR", "BCL-2") compile case-sensitively
    /// so common words ("all", "ace") don't get linked; mixed/lowercase strings compile
    /// case-insensitively so a sentence-start "Antibody" still resolves.
    nonisolated static func buildUnits(_ allTerms: [Term]) -> [LinkUnit] {
        var units: [LinkUnit] = []
        units.reserveCapacity(allTerms.count * 2)
        for term in allTerms {
            for text in CollectionOfOne(term.term) + term.aliases where text.count >= 2 {
                let hasLowercase = text.contains { $0.isLowercase }
                let options: NSRegularExpression.Options = hasLowercase ? [.caseInsensitive] : []
                guard let regex = try? NSRegularExpression(pattern: linkPattern(for: text), options: options) else { continue }
                units.append((text: text, regex: regex, term: term))
            }
        }
        units.sort { $0.text.count > $1.text.count }
        return units
    }

    /// Apply precompiled `units` to `body`, wrapping each non-overlapping match in a
    /// tappable brand-accent link. Skips the current term (no self-links). Longest-first
    /// ordering of `units` ensures a shorter match never overlaps a longer one.
    nonisolated static func applyUnits(to body: String, units: [LinkUnit], currentTermId: String, urlScheme: String) -> AttributedString {
        var attributed = AttributedString(body)
        guard !body.isEmpty else { return attributed }

        let fullRange = NSRange(location: 0, length: (body as NSString).length)
        var linked: [NSRange] = []

        for unit in units {
            if unit.term.id == currentTermId { continue }
            let matches = unit.regex.matches(in: body, options: [], range: fullRange)
            for match in matches {
                let r = match.range
                if linked.contains(where: { NSIntersectionRange($0, r).length > 0 }) { continue }

                guard
                    let stringRange = Range(r, in: body),
                    let attrRange = Range(stringRange, in: attributed),
                    let url = Self.termURL(for: unit.term, urlScheme: urlScheme)
                else { continue }

                attributed[attrRange].link = url
                attributed[attrRange].foregroundColor = PGColors.accent
                attributed[attrRange].underlineStyle = .single

                linked.append(r)
            }
        }

        return attributed
    }

    /// Builds the word-bounded regex used to find a term name in prose.
    ///
    /// - The lookarounds reject a `\w` or hyphen on either side, so a substring of a
    ///   hyphenated medical compound ("cell" in "B-cell") never wins; standalone
    ///   occurrences ("cell." / "the cell ") still match.
    /// - `(?:e?s)?` consumes a regular plural suffix so "Bond" links from "Bonds" and
    ///   "Vanilla Option" from "vanilla options".
    /// - For a term ending in consonant + "y", an extra alternation matches the
    ///   "y → ies" plural so "Antibody" also links from "Antibodies" and "Cell Therapy"
    ///   from "Cell Therapies". Vowel + "y" terms ("Assay" → "Assays") already work via
    ///   `e?s` and are deliberately left untouched.
    ///
    /// The suffix is included in the match (the underline covers the whole word), but
    /// the tappable URL is always built from the canonical term name, so taps land on
    /// the right entry regardless of inflection.
    nonisolated static func linkPattern(for name: String) -> String {
        let escaped = NSRegularExpression.escapedPattern(for: name)
        let core: String
        if name.count > 3, let last = name.last, last == "y" || last == "Y",
           let penult = name.dropLast().last, !"aeiouAEIOU".contains(penult) {
            let stem = NSRegularExpression.escapedPattern(for: String(name.dropLast()))
            core = "(?:\(escaped)(?:e?s)?|\(stem)ies)"
        } else {
            core = "\(escaped)(?:e?s)?"
        }
        return "(?<![\\w-])\(core)(?![\\w-])"
    }

    /// Resolve a `<brand-scheme>://term/<encoded-name>` URL back to a Term in the store.
    func term(matchingURL url: URL) -> Term? {
        guard url.scheme == Brand.current.urlScheme, url.host == "term" else { return nil }
        let raw = url.path.hasPrefix("/") ? String(url.path.dropFirst()) : url.path
        guard let decoded = raw.removingPercentEncoding else { return nil }
        return allTerms.first { $0.term.compare(decoded, options: .caseInsensitive) == .orderedSame }
    }

    nonisolated static func termURL(for term: Term, urlScheme: String) -> URL? {
        let allowed = CharacterSet.urlPathAllowed
        let encoded = term.term.addingPercentEncoding(withAllowedCharacters: allowed) ?? term.term
        return URL(string: "\(urlScheme)://term/\(encoded)")
    }
}
