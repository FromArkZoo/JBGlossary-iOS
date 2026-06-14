import XCTest
@testable import JBGlossary

/// Tests for the ranked search scorer (`GlossaryStore.searchScore`). The scorer
/// ranks term-NAME prefix matches above word-prefix, above substring, above
/// alias/acronym, above definition-body matches — so typing "ga" surfaces
/// Gain / Gait / Gain scheduling before terms that merely mention "ga" in prose.
final class SearchTests: XCTestCase {

    private func score(_ name: String, q: String, full: String = "", aliases: [String] = [], blob: String = "") -> Int {
        // All inputs are pre-lowercased by the index; tests pass lowercase.
        GlossaryStore.searchScore(name: name, full: full, aliases: aliases, blob: blob, query: q)
    }

    func testExactNameWinsHighest() {
        XCTAssertEqual(score("gain", q: "gain"), 1000)
    }

    func testNamePrefixMatches() {
        XCTAssertEqual(score("gain", q: "ga"), 900)
        XCTAssertEqual(score("gait", q: "ga"), 900)
        XCTAssertEqual(score("gain scheduling", q: "ga"), 900)
        XCTAssertEqual(score("gain tuning", q: "ga"), 900)
    }

    func testWordPrefixInMultiWordName() {
        // "ga" is the prefix of the SECOND word -> word-prefix tier, below whole-name prefix.
        XCTAssertEqual(score("adaptive gain control", q: "ga"), 800)
        XCTAssertEqual(score("scheduling gain", q: "ga"), 800)
    }

    func testNameSubstringBelowPrefix() {
        // "navigation" contains "ga" mid-word -> substring tier.
        let s = score("navigation", q: "ga")
        XCTAssertEqual(s, 600)
        XCTAssertLessThan(s, score("gain", q: "ga"))      // prefix beats substring
        XCTAssertLessThan(score("adaptive gain", q: "ga"), score("gain", q: "ga"))
    }

    func testAliasPrefix() {
        // canonical name doesn't match, but an alias prefix does.
        XCTAssertEqual(score("global navigation satellite system", q: "gn", aliases: ["gnss"]), 820)
    }

    func testAcronymFullMatch() {
        XCTAssertEqual(score("simultaneous localization and mapping", q: "slam", full: "slam"), 400)
    }

    func testDefinitionBodyMatchIsLowest() {
        let s = score("torque ripple", q: "ga", blob: "reduced by careful gain selection")
        XCTAssertEqual(s, 100)
        XCTAssertLessThan(s, score("navigation", q: "ga"))   // body below name-substring
    }

    func testSingleCharDoesNotMatchBody() {
        // 1-char queries must not scan definition bodies (too noisy).
        XCTAssertEqual(score("torque ripple", q: "g", blob: "uses gain"), 0)
        // but a 1-char name prefix still matches
        XCTAssertEqual(score("gain", q: "g"), 900)
    }

    func testNoMatchScoresZero() {
        XCTAssertEqual(score("reinforcement learning", q: "xyzzy", full: "rl", blob: "trains a policy"), 0)
    }

    func testRankingOrderIsMonotonic() {
        let q = "ga"
        let exact = score("ga", q: q)
        let prefix = score("gain", q: q)
        let wordPrefix = score("adaptive gain", q: q)
        let substring = score("navigation", q: q)
        let body = score("torque", q: q, blob: "gain term")
        XCTAssertGreaterThan(exact, prefix)
        XCTAssertGreaterThan(prefix, wordPrefix)
        XCTAssertGreaterThan(wordPrefix, substring)
        XCTAssertGreaterThan(substring, body)
        XCTAssertGreaterThan(body, 0)
    }
}
