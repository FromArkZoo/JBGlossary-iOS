"""Audit the clarity / linkability of glossary entries against CLARITY_POLICY.md.

Originally focused on the `plain` tier; extended to enforce hyperlinking-hygiene
rules across all three tiers (plain, snappy, detail). See docs/CLARITY_POLICY.md.

Usage:
    python3 scripts/audit_clarity.py finance
    python3 scripts/audit_clarity.py pharma --top 50
    python3 scripts/audit_clarity.py finance --letter B
    python3 scripts/audit_clarity.py finance --csv > worklist.csv
    python3 scripts/audit_clarity.py --all                  # all 4 industries

Severity ordering (highest impact first):
    1. missing                 — plain is empty/unset
    2. chain-break             — plain references a term whose own plain is empty
    3. over-length             — plain > 25 words
    4. unexpanded-ack          — plain contains an unexpanded all-caps acronym
    5. capitalisation          — common-noun term capitalised mid-sentence
    6. hyphen-block            — hyphenated phrase blocks an existing term's auto-link
    7. non-canonical           — non-canonical short form used where a canonical name would link
    8. wrong-context-candidate — homonym term in body; surface for human review
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).parent.parent

INDUSTRY_PATHS = {
    "finance": ROOT / "Targets/Finance/Resources/glossary_finance.json",
    "pharma":  ROOT / "Targets/Pharma/Resources/glossary_pharma.json",
    "ai":      ROOT / "Targets/AI/Resources/glossary_ai.json",
    "law":     ROOT / "Targets/Law/Resources/glossary_law.json",
}

MAX_PLAIN_WORDS = 25
ACRONYM_RE = re.compile(r"\b[A-Z]{2,}\b")
# Word counter — matches actual word tokens (letters/digits/internal hyphens/
# apostrophes), so standalone punctuation like "—" or commas don't inflate the count.
WORD_RE = re.compile(r"[A-Za-z0-9][\w'\-]*")

# Body fields the new hygiene checks scan (plain + snappy + detail).
BODY_FIELDS = ("plain", "snappy", "detail")

# Common-noun terms that should be lowercase mid-sentence. Each is a real
# glossary entry whose canonical form starts with a capital, but the underlying
# concept is a generic noun the writer rarely intends to highlight. The linker
# matches case-insensitively for mixed-case terms, so lowercasing preserves
# the hyperlink. See CLARITY_POLICY.md §"Hyperlinking hygiene" rule 1.
COMMON_NOUN_LOWERCASE_WHITELIST = {
    "Bond", "Bonds", "Stock", "Stocks", "Share", "Shares",
    "Option", "Options", "Yield", "Yields",
    "Inflation", "Volatility", "Interest Rate", "Interest Rates",
}

# (regex_pattern, suggested_canonical) tuples — non-canonical short forms
# that don't auto-link because they don't match an existing term name exactly.
# Patterns are case-sensitive and assume the leading word in the canonical
# entry is itself capitalised. See CLARITY_POLICY.md §"Hyperlinking hygiene"
# rule 2 for examples.
NON_CANONICAL_PATTERNS = [
    (re.compile(r"(?<![\w-])Sortino(?!\s+Ratio)(?![\w-])"), "Sortino Ratio"),
    (re.compile(r"(?<![\w-])Sharpe(?!\s+Ratio)(?![\w-])"), "Sharpe Ratio"),
    (re.compile(r"(?<![\w-])vol-of-vol(?![\w-])", re.IGNORECASE), "vol of vol"),
    (re.compile(r"(?<![\w-])Treasuries(?![\w-])"), "Treasury bonds and notes"),
    (re.compile(r"(?<![\w-])special-purpose vehicle(?![\w-])", re.IGNORECASE), "SPV"),
]

# Homonyms — standalone glossary term names that also function as common
# English verbs, adjectives, or Greek-letter parameter names. Each entry
# here must exist as a bare term in some industry's glossary (lowercase
# form intersected with name_lookup at runtime); otherwise the lowercase
# use can't actually auto-link, so it's not a false-positive risk.
# Occurrences are surfaced for human review; the audit never auto-fixes
# them. See CLARITY_POLICY.md rule 4.
#
# The set is the union across all industries — runtime filtering narrows
# per-industry. Finance bares: put, call, beta, rho. AI bares: agent,
# attention, batch, bias, layer, model, prompt, reasoning, reward, token,
# weight.
HOMONYM_TERMS = {
    # Finance
    "put", "call", "beta", "rho",
    # AI
    "agent", "attention", "batch", "bias", "layer",
    "model", "prompt", "reasoning", "reward", "token", "weight",
    # Pharma
    "assay", "cell", "protein", "receptor",
}

# Tokens that look like jargon but shouldn't trigger a chain-break warning.
# Proper nouns / brand names that we'd never want their own entry.
LINKER_DENYLIST = {
    "US", "USD", "EUR", "GBP", "JPY", "UK", "EU", "EU's", "US's",
    "S&P", "Dow", "Fed", "Treasury", "Treasuries",  # brand names / instruments-as-proper-nouns
    "Bloomberg", "Reuters", "Wall", "Street",  # publishers / locations
    "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December",
    # Company / brand-name acronyms that appear inside index entries — we'd never
    # add these as glossary entries.
    "SAP", "HSBC", "LVMH", "QQQ", "IT", "PM", "AM",
    # Roman numerals attached to proper nouns (e.g. "MiFID II")
    "II", "III", "IV", "VI",
    # Exchange short-names that already have entries under different forms
    "CME", "NYSE", "CBOT", "ICE", "NASDAQ", "LSE", "CBOE",
    # Common everyday three-letter words people might write in all caps
    "IOU",
    # Pervasive informal abbreviations used across plain text without
    # warranting their own entries (the long-form is the entry, e.g.,
    # "Artificial intelligence" for AI).
    "AI", "DNA", "USB", "JSON", "KV", "SSD", "VS", "BMW",
    "TV", "COVID",
}


def load_terms(industry):
    path = INDUSTRY_PATHS.get(industry)
    if path is None:
        sys.exit(f"Unknown industry '{industry}'. Choices: {sorted(INDUSTRY_PATHS)}")
    if not path.exists():
        sys.exit(f"Glossary not found: {path}")
    with path.open() as f:
        return json.load(f)


def word_count(s):
    return len(WORD_RE.findall(s)) if s else 0


def compute_reference_frequency(terms):
    """Count how often each term name appears inside other terms' detail fields.
    Plain-text scan, case-insensitive for mixed-case terms, case-sensitive for
    all-caps acronyms — same rules as the in-app linker."""
    name_lookup = {}
    for t in terms:
        name = t["term"]
        if len(name) < 2:
            continue
        is_acronym = not any(c.islower() for c in name)
        name_lookup[name] = is_acronym
    counts = Counter()
    for t in terms:
        body = t.get("detail", "") or ""
        for name, is_acronym in name_lookup.items():
            if name == t["term"]:
                continue
            # Same hyphen-aware word boundary as the Swift linker.
            pattern = r"(?<![\w-])" + re.escape(name) + r"(?![\w-])"
            flags = 0 if is_acronym else re.IGNORECASE
            matches = re.findall(pattern, body, flags=flags)
            counts[name] += len(matches)
    return counts


def find_referenced_terms_in_plain(plain, term_name_set, acronym_set):
    """Return (linked_names, suspect_tokens). linked_names = entry names this
    plain references (and would auto-link to). suspect_tokens = capitalised
    multi-word phrases that LOOK like jargon but have no matching entry."""
    linked = set()
    if not plain:
        return linked, set()
    for name in term_name_set:
        if len(name) < 2:
            continue
        pattern = r"(?<![\w-])" + re.escape(name) + r"(?![\w-])"
        flags = 0 if name in acronym_set else re.IGNORECASE
        if re.search(pattern, plain, flags=flags):
            linked.add(name)
    return linked, set()


def _is_sentence_start(body, pos):
    """A position is sentence-start if it's the first char of the field or
    preceded by sentence-terminating punctuation followed by whitespace."""
    if pos == 0:
        return True
    # Walk back over whitespace
    i = pos - 1
    while i >= 0 and body[i].isspace():
        i -= 1
    if i < 0:
        return True
    return body[i] in ".!?\n"


def detect_capitalisation(entry, name_lookup):
    """Flag mid-sentence occurrences of common-noun glossary terms in
    capitalised form. Skips sentence-start positions and positions where a
    longer multi-word term name starts (so `Inflation Target` is not flagged
    just because `Inflation` is whitelisted)."""
    violations = []
    seen = set()  # (term, field) — one report per pair

    # Precompute longer-term extensions per whitelist entry.
    longer = {}
    for w in COMMON_NOUN_LOWERCASE_WHITELIST:
        longer[w] = [n for n in name_lookup
                     if n != w and n.lower().startswith(w.lower() + " ")]

    for field in BODY_FIELDS:
        body = entry.get(field, "") or ""
        if not body:
            continue
        for w in COMMON_NOUN_LOWERCASE_WHITELIST:
            pattern = re.escape(w) + r"(?![A-Za-z])"
            for m in re.finditer(pattern, body):
                pos = m.start()
                if _is_sentence_start(body, pos):
                    continue
                # Skip if a longer term name starts here (e.g., Inflation Target).
                rest = body[pos:]
                if any(rest.lower().startswith(ext.lower())
                       and (len(rest) == len(ext) or not rest[len(ext):len(ext)+1].isalpha())
                       for ext in longer[w]):
                    continue
                key = (w, field)
                if key not in seen:
                    seen.add(key)
                    violations.append({
                        "kind": "capitalisation",
                        "msg": f"'{w}' capitalised mid-sentence in {field}",
                    })
                break  # one report per (term, field)
    return violations


def detect_hyphen_block(entry, name_lookup, acronym_set):
    """Flag hyphenated phrases that would have auto-linked if the hyphen
    weren't on the boundary. Uses linker-exact strict pattern vs hyphen-
    permissive relaxed pattern; the set difference is hyphen-blocked."""
    violations = []
    seen = set()  # (term, field)

    for field in BODY_FIELDS:
        body = entry.get(field, "") or ""
        if not body:
            continue
        for name in name_lookup:
            if len(name) < 2 or name == entry["term"]:
                continue
            escaped = re.escape(name)
            strict = re.compile(r"(?<![\w-])" + escaped + r"(?:e?s)?(?![\w-])",
                                flags=0 if name in acronym_set else re.IGNORECASE)
            relaxed = re.compile(r"(?<![\w])" + escaped + r"(?:e?s)?(?![\w])",
                                 flags=0 if name in acronym_set else re.IGNORECASE)
            strict_spans = {(m.start(), m.end()) for m in strict.finditer(body)}
            relaxed_spans = {(m.start(), m.end()) for m in relaxed.finditer(body)}
            blocked = relaxed_spans - strict_spans
            if blocked and (name, field) not in seen:
                seen.add((name, field))
                violations.append({
                    "kind": "hyphen-block",
                    "msg": f"'{name}' blocked by adjacent hyphen in {field}",
                })
    return violations


def detect_non_canonical(entry):
    """Flag uses of non-canonical short forms where a fuller canonical term
    name would auto-link."""
    violations = []
    seen = set()
    for field in BODY_FIELDS:
        body = entry.get(field, "") or ""
        if not body:
            continue
        for pattern, canonical in NON_CANONICAL_PATTERNS:
            if pattern.search(body):
                key = (pattern.pattern, field)
                if key not in seen:
                    seen.add(key)
                    violations.append({
                        "kind": "non-canonical",
                        "msg": f"non-canonical form in {field}; suggest '{canonical}'",
                    })
    return violations


def detect_wrong_context(entry, name_lookup):
    """Surface occurrences of homonym terms in body fields, with context.
    Only flags homonyms that exist as bare standalone terms in this industry
    (otherwise the lowercase form can't auto-link, so there's no risk).
    Skips positions where a longer term name match is in play (e.g., 'Call'
    inside 'Call Option') and skips self-references."""
    name_lookup_lower = {n.lower(): n for n in name_lookup}
    active = {h for h in HOMONYM_TERMS if h in name_lookup_lower}
    if not active:
        return []

    # Longer-term extensions per active homonym, so 'Call Option' suppresses 'Call'.
    longer = {}
    for h in active:
        canonical = name_lookup_lower[h]
        longer[h] = [n for n in name_lookup
                     if n != canonical and n.lower().startswith(h + " ")]

    violations = []
    for field in BODY_FIELDS:
        body = entry.get(field, "") or ""
        if not body:
            continue
        for h in active:
            canonical = name_lookup_lower[h]
            if canonical == entry["term"]:
                continue  # self-reference, linker skips anyway
            pattern = re.compile(
                r"(?<![\w-])" + re.escape(h) + r"(?:e?s)?(?![\w-])",
                flags=re.IGNORECASE,
            )
            for m in pattern.finditer(body):
                pos = m.start()
                rest = body[pos:]
                if any(rest.lower().startswith(ext.lower())
                       and (len(rest) == len(ext)
                            or not rest[len(ext):len(ext)+1].isalpha())
                       for ext in longer[h]):
                    continue
                start = max(0, m.start() - 25)
                end = min(len(body), m.end() + 25)
                ctx = body[start:end].replace("\n", " ").strip()
                violations.append({
                    "kind": "wrong-context-candidate",
                    "msg": f"'{h}' in {field}: …{ctx}…",
                })
    return violations


RANK_FOR = {
    "missing": 1,
    "chain-break": 2,
    "over-length": 3,
    "unexpanded-ack": 4,
    "capitalisation": 5,
    "hyphen-block": 6,
    "non-canonical": 7,
    "wrong-context-candidate": 8,
}


def audit_entry(entry, all_terms, name_lookup, acronym_set, plain_set):
    """Returns (severity_rank, list_of_violation_dicts) for one entry.
    Severity 1–4 covers plain-only baseline checks; 5–8 covers hygiene
    checks across plain+snappy+detail; 99 = clean.
    """
    violations = []
    plain = entry.get("plain", "") or ""

    if not plain:
        violations.append({"kind": "missing", "msg": "plain is empty"})
    else:
        wc = word_count(plain)
        if wc > MAX_PLAIN_WORDS:
            violations.append({"kind": "over-length", "msg": f"{wc} words (max {MAX_PLAIN_WORDS})"})

        for ack in ACRONYM_RE.findall(plain):
            if ack in LINKER_DENYLIST:
                continue
            if ack in name_lookup:
                continue
            violations.append({"kind": "unexpanded-ack", "msg": f"acronym '{ack}' has no entry and no inline expansion"})

        linked, _ = find_referenced_terms_in_plain(plain, set(name_lookup), acronym_set)
        for ref in sorted(linked):
            if ref not in plain_set:
                violations.append({"kind": "chain-break", "msg": f"references '{ref}' which has no plain"})

    # Hygiene checks — run regardless of plain state, scan plain+snappy+detail.
    violations.extend(detect_capitalisation(entry, name_lookup))
    violations.extend(detect_hyphen_block(entry, name_lookup, acronym_set))
    violations.extend(detect_non_canonical(entry))
    violations.extend(detect_wrong_context(entry, name_lookup))

    if not violations:
        return 99, []
    worst = min(RANK_FOR[v["kind"]] for v in violations)
    return worst, violations


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("industry", nargs="?", choices=sorted(INDUSTRY_PATHS),
                   help="Industry to audit. Omit when using --all.")
    p.add_argument("--all", action="store_true",
                   help="Audit all 4 industries in sequence.")
    p.add_argument("--top", type=int, default=None,
                   help="Show only the top N entries by reference frequency.")
    p.add_argument("--letter", type=str, default=None,
                   help="Filter to a single letter (e.g. 'B').")
    p.add_argument("--csv", action="store_true",
                   help="Emit CSV instead of human-readable text.")
    p.add_argument("--include-clean", action="store_true",
                   help="Also list entries with no violations.")
    args = p.parse_args()

    if args.all and args.industry:
        sys.exit("Pass either an industry name OR --all, not both.")
    if not args.all and not args.industry:
        sys.exit("Specify an industry (e.g. 'finance') or pass --all.")

    if args.all:
        for industry in sorted(INDUSTRY_PATHS):
            args.industry = industry
            _run_one(args)
        return
    _run_one(args)


def _run_one(args):
    terms = load_terms(args.industry)
    name_lookup = {t["term"]: t for t in terms}
    acronym_set = {n for n in name_lookup if not any(c.islower() for c in n)}
    plain_set = {t["term"] for t in terms if (t.get("plain") or "").strip()}
    ref_freq = compute_reference_frequency(terms)

    # Build report rows
    rows = []
    for t in terms:
        if args.letter and t["letter"] != args.letter.upper():
            continue
        severity, violations = audit_entry(t, terms, name_lookup, acronym_set, plain_set)
        if severity == 99 and not args.include_clean:
            continue
        rows.append({
            "term": t["term"],
            "letter": t["letter"],
            "severity": severity,
            "violations": violations,
            "ref_freq": ref_freq.get(t["term"], 0),
            "category": t.get("category", ""),
        })

    # Sort: severity asc, then ref_freq desc, then term asc.
    rows.sort(key=lambda r: (r["severity"], -r["ref_freq"], r["term"]))

    if args.top:
        rows = rows[: args.top]

    # Coverage stat
    total = len(terms)
    covered = len(plain_set)
    pct = 100.0 * covered / total if total else 0

    if args.csv:
        print("severity,letter,term,ref_freq,category,violation")
        for r in rows:
            for v in r["violations"] or [{"msg": "ok"}]:
                print(f"{r['severity']},{r['letter']},\"{r['term']}\",{r['ref_freq']},\"{r['category']}\",\"{v['msg']}\"")
        return

    sev_label = {
        1: "MISSING", 2: "CHAIN-BREAK", 3: "OVER-LENGTH", 4: "UNEXPANDED-ACK",
        5: "CAPITALISATION", 6: "HYPHEN-BLOCK", 7: "NON-CANONICAL",
        8: "WRONG-CONTEXT", 99: "OK",
    }
    print(f"\n=== Clarity audit — {args.industry.upper()} ===")
    print(f"Coverage: {covered} / {total} terms have plain ({pct:.1f}%)")
    print(f"Showing: {len(rows)} entries needing work\n")
    current_sev = None
    for r in rows:
        if r["severity"] != current_sev:
            current_sev = r["severity"]
            print(f"\n--- {sev_label[current_sev]} ---")
        freq_tag = f" [×{r['ref_freq']}]" if r["ref_freq"] else ""
        print(f"  [{r['letter']}] {r['term']}{freq_tag}")
        for v in r["violations"]:
            print(f"        • {v['msg']}")


if __name__ == "__main__":
    main()
