import Foundation
import SwiftUI

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
        let built = Self.computeAttributedText(body, currentTermId: term.id, allTerms: allTerms, urlScheme: Brand.current.urlScheme)
        attributedCache[key] = built
        return built
    }

    /// Generic linker. Used for all three tiers (`plain`, `snappy`, `detail`)
    /// because the rules — longest-first, acronym case-sensitivity, hyphen-aware
    /// word boundaries — are identical for any prose that references other terms.
    nonisolated static func computeAttributedText(_ body: String, currentTermId: String, allTerms: [Term], urlScheme: String) -> AttributedString {
        var attributed = AttributedString(body)
        guard !body.isEmpty else { return attributed }

        // Build the set of strings to match: every other term's canonical name AND each
        // of its aliases, every one resolving to that term's canonical URL. Sort longest-
        // first (by the matched string) so "ACE Inhibitor" wins over the alias "ACE", and
        // "monoclonal antibody" wins over "antibody". Skip self-references and single-char
        // tokens that risk false positives (e.g. "I", "K").
        var units: [(text: String, term: Term)] = []
        for term in allTerms where term.id != currentTermId {
            if term.term.count >= 2 { units.append((term.term, term)) }
            for alias in term.aliases where alias.count >= 2 { units.append((alias, term)) }
        }
        units.sort { $0.text.count > $1.text.count }

        let fullRange = NSRange(location: 0, length: (body as NSString).length)

        // Track NSRanges already linked so shorter matches don't overlap longer ones.
        var linked: [NSRange] = []

        for unit in units {
            // Acronym strings (no lowercase letters, e.g. "ALL", "AMR", "BCL-2") match case-
            // sensitively so common English words like "all" or "ace" don't get linked.
            // Mixed/lowercase strings ("Antibody", "Cmax") match case-insensitively so a
            // sentence-start "Antibody" still resolves to its lowercase canonical entry.
            let hasLowercase = unit.text.contains { $0.isLowercase }
            let options: NSRegularExpression.Options = hasLowercase ? [.caseInsensitive] : []
            guard let regex = try? NSRegularExpression(pattern: Self.linkPattern(for: unit.text), options: options) else { continue }

            let matches = regex.matches(in: body, options: [], range: fullRange)
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
