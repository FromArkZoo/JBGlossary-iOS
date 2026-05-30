import XCTest
@testable import JBGlossary

/// Golden-case tests for the in-app hyperlink linker (`GlossaryStore.computeAttributedText`
/// / `linkPattern`). Covers the y→ies plural rule and the `aliases` field, plus regression
/// cases for the existing behavior (regular plurals, acronym case-sensitivity, hyphen
/// boundaries, self-link suppression, longest-first ordering).
final class HyperlinkTests: XCTestCase {

    /// Decode `Term` fixtures from JSON — also exercises the (optional) `aliases` decoder.
    private func decode(_ json: String) -> [Term] {
        try! JSONDecoder().decode([Term].self, from: Data(json.utf8))
    }

    /// Returns the links the linker fires, as (linkedText, targetTermName) pairs.
    private func links(_ body: String, current: String = "", terms: [Term]) -> [(String, String)] {
        let attr = GlossaryStore.computeAttributedText(body, currentTermId: current, allTerms: terms, urlScheme: "jbg")
        var out: [(String, String)] = []
        for (link, range) in attr.runs[\.link] {
            guard let url = link else { continue }
            let text = String(attr[range].characters)
            let raw = url.path.hasPrefix("/") ? String(url.path.dropFirst()) : url.path
            out.append((text, raw.removingPercentEncoding ?? raw))
        }
        return out
    }

    private func entry(_ term: String, letter: String = "A", aliases: [String] = []) -> String {
        let aliasJSON = aliases.map { "\"\($0)\"" }.joined(separator: ",")
        return """
        {"letter":"\(letter)","term":"\(term)","detail":"x","aliases":[\(aliasJSON)]}
        """
    }

    // MARK: - y→ies plurals (Change 1)

    func testYtoIesPluralLinks() {
        let terms = decode("[\(entry("Antibody"))]")
        XCTAssertEqual(links("monoclonal Antibodies bind antigens", terms: terms).map(\.0), ["Antibodies"])
        XCTAssertEqual(links("monoclonal Antibodies bind antigens", terms: terms).first?.1, "Antibody")
    }

    func testYtoIesMultiWord() {
        let terms = decode("[\(entry("Cell Therapy"))]")
        let l = links("emerging Cell Therapies for cancer", terms: terms)
        XCTAssertEqual(l.map(\.0), ["Cell Therapies"])
        XCTAssertEqual(l.first?.1, "Cell Therapy")
    }

    func testRegularPluralStillLinks() {
        let terms = decode("[\(entry("Bond"))]")
        XCTAssertEqual(links("holding two Bonds", terms: terms).map(\.0), ["Bonds"])
    }

    func testVowelYNotOverFolded() {
        // "Assay" ends in vowel+y → plural is "Assays" (handled by e?s), NOT "Assaies".
        let terms = decode("[\(entry("Assay"))]")
        XCTAssertEqual(links("running Assays today", terms: terms).map(\.0), ["Assays"])
        XCTAssertTrue(links("the word Assaies", terms: terms).isEmpty)
    }

    // MARK: - aliases (Change 3)

    func testAliasAcronymLinks() {
        let terms = decode("[\(entry("ACE Inhibitor", aliases: ["ACE"]))]")
        let l = links("an ACE drug for hypertension", terms: terms)
        XCTAssertEqual(l.map(\.0), ["ACE"])
        XCTAssertEqual(l.first?.1, "ACE Inhibitor")
    }

    func testAliasAcronymIsCaseSensitive() {
        // "ACE" has no lowercase → case-sensitive, so prose "ace" must NOT link.
        let terms = decode("[\(entry("ACE Inhibitor", aliases: ["ACE"]))]")
        XCTAssertTrue(links("an ace up the sleeve", terms: terms).isEmpty)
    }

    func testAliasLongestFirst() {
        // Full canonical name wins where it appears; the bare alias links elsewhere.
        let terms = decode("[\(entry("ACE Inhibitor", aliases: ["ACE"]))]")
        let l = links("an ACE Inhibitor is an ACE class", terms: terms)
        XCTAssertEqual(l.map(\.0), ["ACE Inhibitor", "ACE"])
        XCTAssertTrue(l.allSatisfy { $0.1 == "ACE Inhibitor" })
    }

    func testAliasShortToLongForm() {
        let terms = decode("[\(entry("Alzheimer's Disease", aliases: ["Alzheimer's"]))]")
        let l = links("a drug that treats Alzheimer's early", terms: terms)
        XCTAssertEqual(l.map(\.0), ["Alzheimer's"])
        XCTAssertEqual(l.first?.1, "Alzheimer's Disease")
    }

    // MARK: - regression / existing behavior

    func testBackwardCompatNoAliasesField() {
        // Entries predating the field decode with aliases == [].
        let terms = try! JSONDecoder().decode([Term].self, from: Data(#"[{"letter":"A","term":"Antibody","detail":"x"}]"#.utf8))
        XCTAssertEqual(terms.first?.aliases, [])
    }

    func testSelfIsNotLinked() {
        let terms = decode("[\(entry("Antibody"))]")
        XCTAssertTrue(links("Antibody binds its antigen", current: "A::Antibody", terms: terms).isEmpty)
    }

    func testHyphenBoundaryBlocksFragment() {
        // "cell" must not link inside the hyphenated compound "B-cell".
        let terms = decode("[\(entry("Cell"))]")
        XCTAssertTrue(links("a B-cell malignancy", terms: terms).isEmpty)
    }

    func testLongestFirstAcrossTerms() {
        let terms = decode("[\(entry("Cell")),\(entry("Cell Therapy", letter: "C"))]")
        let l = links("a novel Cell Therapy approach", terms: terms)
        XCTAssertEqual(l.map(\.0), ["Cell Therapy"])
        XCTAssertEqual(l.first?.1, "Cell Therapy")
    }
}
