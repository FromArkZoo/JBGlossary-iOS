"""Mechanical auto-fix pass on a glossary JSON per CLARITY_POLICY.md hygiene rules.

Applies high-confidence fixes only:

1. Lowercase common-noun glossary term names that appear capitalised mid-
   sentence (Bond, Stock, Option, Inflation, Volatility, Yield, Interest Rate,
   Share, and their plurals). The auto-linker matches case-insensitively for
   mixed-case terms, so the hyperlink still resolves; lowercase reads more
   naturally.

2. Replace non-canonical short forms with canonical equivalents so the auto-
   linker can wire up the hyperlink (Sortino → Sortino Ratio,
   vol-of-vol → vol of vol, Treasuries → Treasury securities, etc.).

3. A small curated set of hyphen-block rephrasings where the wording change is
   clearly improved by removing the hyphen (post-LIBOR → after LIBOR was
   retired).

Does NOT auto-fix — these are surfaced by audit_clarity.py for human review:
- General hyphen-block compounds (broker-dealer, bid-ask, Treasury-like).
- Wrong-context-candidate occurrences (put / call / beta / rho).
- Plain English subjective rewrites (over-length, vague metaphors).

Usage:
    python3 scripts/apply_style_fixes.py finance
    python3 scripts/apply_style_fixes.py finance --dry-run
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent

INDUSTRY_PATHS = {
    "finance": ROOT / "Targets/Finance/Resources/glossary_finance.json",
    "pharma":  ROOT / "Targets/Pharma/Resources/glossary_pharma.json",
    "ai":      ROOT / "Targets/AI/Resources/glossary_ai.json",
    "law":     ROOT / "Targets/Law/Resources/glossary_law.json",
}

BODY_FIELDS = ("plain", "snappy", "detail")

# Whitelisted mid-sentence lowercasing. Each cap-form maps to its lowercase
# form. The linker still resolves the hyperlink for mixed-case terms.
CAPITALISATION_LOWERCASE = {
    "Bond": "bond", "Bonds": "bonds",
    "Stock": "stock", "Stocks": "stocks",
    "Share": "share", "Shares": "shares",
    "Option": "option", "Options": "options",
    "Yield": "yield", "Yields": "yields",
    "Inflation": "inflation",
    "Volatility": "volatility",
    "Interest Rate": "interest rate",
    "Interest Rates": "interest rates",
}

# Compiled (find, replace) pairs. Word-boundary aware via the linker's
# (?<![\w-]) / (?![\w-]) lookarounds.
NON_CANONICAL_REPLACEMENTS = [
    (re.compile(r"(?<![\w-])Sortino(?!\s+Ratio)(?![\w-])"), "Sortino Ratio"),
    (re.compile(r"(?<![\w-])Sharpe(?!\s+Ratio)(?![\w-])"), "Sharpe Ratio"),
    (re.compile(r"(?<![\w-])vol-of-vol(?![\w-])", re.IGNORECASE), "vol of vol"),
    (re.compile(r"(?<![\w-])Treasuries(?![\w-])"), "Treasury securities"),
    (re.compile(r"(?<![\w-])special-purpose vehicle(?![\w-])", re.IGNORECASE), "SPV"),
]

# Curated hyphen-block rephrasings — wording change but clear benefit.
HYPHEN_BLOCK_REPLACEMENTS = [
    (re.compile(r"(?<![\w-])post-LIBOR(?![\w-])"), "after LIBOR was retired"),
]


def _is_sentence_start(body: str, pos: int) -> bool:
    if pos == 0:
        return True
    i = pos - 1
    while i >= 0 and body[i].isspace():
        i -= 1
    if i < 0:
        return True
    return body[i] in ".!?\n"


def apply_capitalisation_fix(body: str, name_lookup: set[str]) -> tuple[str, int]:
    """Lowercase mid-sentence capitalised whitelist words.

    Skips sentence-start positions and positions where a longer multi-word
    glossary term starts (so 'Inflation Target' is not affected just because
    'Inflation' is whitelisted).
    """
    if not body:
        return body, 0

    longer = {}
    for w in CAPITALISATION_LOWERCASE:
        longer[w] = sorted(
            (n for n in name_lookup if n != w and n.lower().startswith(w.lower() + " ")),
            key=len, reverse=True,
        )

    # Process longest whitelist entries first so "Interest Rates" wins over "Interest Rate".
    ordered = sorted(CAPITALISATION_LOWERCASE.items(), key=lambda kv: -len(kv[0]))

    edits = []
    for cap_form, lower_form in ordered:
        pattern = re.compile(re.escape(cap_form) + r"(?![A-Za-z])")
        for m in pattern.finditer(body):
            pos = m.start()
            if _is_sentence_start(body, pos):
                continue
            rest = body[pos:]
            if any(
                rest.lower().startswith(ext.lower())
                and (len(rest) == len(ext) or not rest[len(ext):len(ext) + 1].isalpha())
                for ext in longer[cap_form]
            ):
                continue
            edits.append((pos, m.end(), lower_form))

    if not edits:
        return body, 0

    # Apply edits right-to-left so positions don't shift; drop overlaps.
    edits.sort(key=lambda e: -e[0])
    new_body = body
    seen_ranges: list[tuple[int, int]] = []
    n_applied = 0
    for start, end, replacement in edits:
        if any(s < end and start < e for s, e in seen_ranges):
            continue
        new_body = new_body[:start] + replacement + new_body[end:]
        seen_ranges.append((start, end))
        n_applied += 1
    return new_body, n_applied


def apply_pattern_replacements(body: str, patterns) -> tuple[str, int]:
    n_edits = 0
    for pat, repl in patterns:
        new_body, count = pat.subn(repl, body)
        if count:
            body = new_body
            n_edits += count
    return body, n_edits


def process_industry(industry: str, dry_run: bool = False):
    path = INDUSTRY_PATHS[industry]
    data = json.loads(path.read_text())
    name_lookup = {t["term"] for t in data}

    stats = {"capitalisation": 0, "non-canonical": 0, "hyphen-block": 0}
    touched_terms = set()
    sample_edits = []  # (term, field, before_snippet, after_snippet)

    for entry in data:
        for field in BODY_FIELDS:
            body = entry.get(field, "") or ""
            if not body:
                continue

            new_body, n_cap = apply_capitalisation_fix(body, name_lookup)
            new_body, n_nc = apply_pattern_replacements(new_body, NON_CANONICAL_REPLACEMENTS)
            new_body, n_hb = apply_pattern_replacements(new_body, HYPHEN_BLOCK_REPLACEMENTS)

            total = n_cap + n_nc + n_hb
            if total:
                if len(sample_edits) < 8:
                    sample_edits.append((entry["term"], field, body[:120], new_body[:120]))
                entry[field] = new_body
                touched_terms.add(entry["term"])
                stats["capitalisation"] += n_cap
                stats["non-canonical"] += n_nc
                stats["hyphen-block"] += n_hb

    if not dry_run:
        path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n")

    return stats, touched_terms, sample_edits


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("industry", choices=sorted(INDUSTRY_PATHS))
    p.add_argument("--dry-run", action="store_true",
                   help="Don't write the JSON; just print stats and sample edits.")
    args = p.parse_args()

    stats, touched, samples = process_industry(args.industry, dry_run=args.dry_run)

    mode = "DRY-RUN — not written" if args.dry_run else "Applied"
    print(f"=== {mode} ({args.industry}) ===")
    for kind, n in stats.items():
        print(f"  {kind}: {n} edits")
    print(f"Total terms touched: {len(touched)}")
    print()
    print("Sample edits (first 8):")
    for term, field, before, after in samples:
        print(f"  [{term}.{field}]")
        print(f"    - {before}…")
        print(f"    + {after}…")


if __name__ == "__main__":
    main()
