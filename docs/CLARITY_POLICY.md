# JB Glossary — Clarity Policy

**Status:** v1.0, 2026-05-19. Complements [CONTENT_STYLE_GUIDE.md](CONTENT_STYLE_GUIDE.md). Defines the rules for the **`plain` tier** (added 2026-05-19) and formalises how `snappy` and `detail` work alongside it.

## The three tiers

| Tier | Audience | Length | Voice |
|---|---|---|---|
| `plain` | Total novice — never heard of the term | ≤25 words, 1 sentence | Everyday metaphor, conversational |
| `snappy` | Informed generalist — knows basic vocabulary of the field | ~12 words, 1 sentence | Precise, italic accent |
| `detail` | Curious reader who wants depth | 40–80 words | Full prose, "where you'd hear it" beat |

All three tiers receive automatic hyperlinking — any reference to another entry becomes a tappable link. **Authors don't add link markup**; the regex linker in [Hyperlinks.swift](../Sources/Models/Hyperlinks.swift) handles it.

## `plain` rules

1. **One sentence. ≤25 words.** If you're over, you're explaining too much — that's what `detail` is for.
2. **Written for a reader who has never heard of the term.** Imagine a curious teenager or a relative at a holiday dinner. Don't assume domain vocabulary.
3. **Prefer everyday metaphors over precise technical phrasing.** "A bet that only pays off if…" beats "an option that activates if…". Save precision for `snappy`.
4. **At most 2 domain terms.** And each domain term used MUST itself have an entry in the glossary, so the chain terminates with another `plain` line. If a term doesn't deserve its own entry (proper nouns like "S&P 500", "Federal Reserve"), inline-define it instead. See **The "any-tier" linking rule** below — this constraint applies to `snappy` and `detail` too, just less aggressively (more domain terms allowed).
5. **No new abbreviations.** Don't introduce acronyms in `plain`. If unavoidable, expand inline ("a government-sponsored enterprise (GSE)") AND ensure the abbreviation has its own entry.
6. **Don't start with the term's own name.** ❌ "Barrier Option is…" ✅ "A bet you can buy that only pays off if…"
7. **No clinical/financial advice.** Same prohibition as elsewhere — no "you should buy", no dosing, no comparative claims.

## `snappy` rules (formalised from existing practice)

Unchanged from [CONTENT_STYLE_GUIDE.md](CONTENT_STYLE_GUIDE.md): 18–30 words, italic, plain English voice, no banned jargon list. The audience for `snappy` is the informed generalist who already knows what an "option" or "bond" or "antibody" is.

## `detail` rules (formalised from existing practice)

Unchanged: 40–80 words, full prose, anchor with examples, include a "where you'd hear it" beat, no bullet lists, no links (links are auto-applied).

## Examples — Finance

### ✅ Good `plain` lines

**Barrier Option** — "A bet on a Stock or other Underlying that only pays off — or stops working — if the price hits a chosen Strike Price." *(uses 3 domain terms, all existing entries → 3 hyperlinks; no acronyms; starts with concept not term name; 23 words)*

**Agency MBS** — "A Bond made of US home loans where a US government-owned company effectively insures investors against homeowner defaults." *(2 domain terms, 1 with entry; "government-owned company" inline-defines GSE without using the abbreviation; 18 words)*

**MBS** — "An investment where thousands of home loans are bundled, and investors earn the monthly mortgage payments homeowners make." *(0 domain terms, 18 words — terminates the chain in plain English)*

### ❌ Bad `plain` lines

**Barrier Option** — "An option contract with a knock-in or knock-out feature based on the underlying's path." *(unexplained jargon: option, knock-in, knock-out, underlying; novice still lost)*

**Agency MBS** — "MBS issued by GSEs like FNMA, FHLMC, and GNMA — credit-risk-free, prepay-exposed." *(four undefined acronyms; one sentence requires four entries to decode)*

**MBS** — "MBS is a bond backed by a pool of mortgages." *(starts with the term's own name; "bond" is fine but "mortgages" should link)*

## Linking expectations

The linker is case-aware in two modes (see [Hyperlinks.swift:42-47](../Sources/Models/Hyperlinks.swift)):

- **Mixed-case terms** ("Antibody", "Strike Price"): match case-insensitively. So `plain` can use "stock" or "Stock" — both will link to the "Stock" entry.
- **All-caps acronyms** ("MBS", "GSE", "FOMC"): match case-sensitively to avoid false positives on common English words ("all", "net"). So acronym references in `plain` must match exact casing.

Multi-word terms ("Barrier Option", "Strike Price") match as a whole — longest-first means "Barrier Option" wins over a standalone "Option" match.

### The "any-tier" linking rule

**Any technical jargon used in ANY tier — plain, snappy, or detail — should have its own entry, so the auto-linker can wire it up.**

The linker doesn't care which tier the text is in; it scans whatever it's given. The constraint on the author is to populate the entry SET, not to add link markup. If `detail` mentions "Monte Carlo" or "vanilla options" without those terms being entries, the reader hits an explanation dead-end.

Concretely, when you write a new `detail`:

1. Scan the prose for any term-of-art a generalist might not know.
2. For each, check: does it have an entry? (`grep '"term": "X"'` in the glossary JSON.)
3. If no — either add an entry for it, OR rewrite the prose to avoid the jargon, OR inline-define it ("Monte Carlo (a simulation technique that…)").

Same applies to `plain` and `snappy`. The audit script currently flags chain-breaks in `plain`; a future enhancement will flag candidate jargon in `detail` too.

### Worked examples — Barrier Option's `detail`

Live `detail`: *"Four flavours: knock-in (activates on touch), knock-out (extinguishes on touch), up-and-in, down-and-out. Cheaper than **vanilla options** because part of the time the holder doesn't own anything. Heavily used in structured products and FX hedging. Pricing handles path-dependence — analytical solutions for some types, **Monte Carlo** for others. Barrier breaches in stressed markets create discontinuous payoff jumps that hedgers fear."*

What should auto-link, but doesn't today, because the entry is missing:
- **Vanilla Option** (or "Vanilla" as a concept) — add an entry so "vanilla options" links.
- **Monte Carlo** (the simulation technique) — add an entry so "Monte Carlo" links.
- **FX** — add as an entry (probably already exists; verify).
- **Knock-in / Knock-out** — these are sub-types of barrier option; could be their own entries OR inline-explained (the entry already does this, so optional).

Whenever you find a `detail` that uses jargon the reader can't unpack, that's a signal the missing entry needs writing.

## Hyperlinking hygiene

The auto-linker is mechanical. To make it work for every reader, the text must be written with the linker's behaviour in mind. Four rules below, with before/after examples from real Finance fixes. The audit script (`scripts/audit_clarity.py`) catches all of them — run it after editing.

### 1. Capitalisation hygiene

Common-noun glossary terms must be lowercase mid-sentence. The linker matches case-insensitively for mixed-case terms, so lowercase still resolves to the right entry — and reads more naturally.

- ✅ *"A bond made of US home loans…"*
- ❌ *"A Bond made of US home loans…"*

Same rule for: stock, share, option, yield, inflation, volatility, interest rate. Sentence-start position is fine — that's normal English. All-caps acronyms (MBS, LIBOR, SEC) keep their casing because the linker matches them case-sensitively to avoid false positives on English words.

### 2. Canonical-form hyperlinks

Use the exact canonical term name as it appears in the glossary, or the link won't resolve.

- ✅ *"Tracked alongside the Sharpe Ratio in modern performance reporting."*
- ❌ *"Tracked alongside Sharpe in modern performance reporting."* — `Sharpe` alone doesn't match the entry `Sharpe Ratio`.

- ✅ *"ν is vol of vol"* — matches `Vol of Vol`.
- ❌ *"ν is vol-of-vol"* — hyphens block the match; see Rule 3.

- ✅ *"US Treasury bonds and notes also settle T+1."*
- ❌ *"US Treasuries settle T+1."* — the linker doesn't handle y→ies plurals; `Treasury` won't match `Treasuries`.

- ✅ *"a bankruptcy-remote SPV (special-purpose vehicle), which issues bonds…"*
- ❌ *"a bankruptcy-remote special-purpose vehicle, which issues bonds…"* — no `Special-Purpose Vehicle` entry; use the acronym + inline expansion.

### 3. Hyphen-blocked matches

The linker rejects matches whose neighbour is a word character or a hyphen. So a hyphenated phrase blocks any term-name match sitting inside it.

| Hyphen form | Blocks | Rephrase |
|---|---|---|
| `post-LIBOR` | LIBOR | *"after LIBOR was retired"* |
| `subprime-related` | Subprime | *"tied to Subprime exposure"* |
| `floating-rate` | Floating Rate | *"Floating Rate"* (space form) |
| `CME-listed` | CME | *"listed on CME"* |

### 4. Wrong-context auto-links

Some glossary terms share their name with common verbs or adjectives. The linker can't tell context apart. Authors must rephrase.

- ❌ *"runoff has put pressure on mortgage spreads"* — `put` (verb) auto-links to `Put` (the option).
  ✅ *"runoff has placed pressure on mortgage spreads"*

- ❌ *"Four parameters (alpha, beta, rho, nu) fit the smile shape"* — `beta` / `rho` (SABR parameter names) auto-link to `Beta` / `Rho` (the option Greeks).
  ✅ *"Four parameters — α, β, ρ, and ν — fit the smile shape"* — Greek letters bypass the linker entirely.

- ❌ *"value-tilted smart beta underperformed"* — inside the `Smart Beta` entry's own body, lone `beta` auto-links to `Beta`.
  ✅ *"value-tilted versions underperformed"*

Other Finance watchwords: `spot`, `long`, `short`, `call`, `strike`, `swap`, `futures`, `dealers`. When in doubt, rephrase.

### 4b. Don't inline-expand acronyms in prose

When an entry's `full` field already shows the acronym's expansion in the UI, do NOT repeat the expansion as bare prose in another entry's body. The linker scans the prose word-by-word and will auto-link any component word that happens to be its own entry — creating semantically wrong links inside what the reader perceives as a single proper noun.

| Bad (auto-link bleeds) | Good |
|---|---|
| *"…must follow USPAP — Uniform Standards of Professional Appraisal Practice — and are independent…"* — "Appraisal" inside the expansion auto-links to the standalone Appraisal entry. | *"…must follow USPAP and are independent…"* — USPAP's own entry shows the expansion in metadata. |
| *"…enforces CC&Rs — Covenants, Conditions, and Restrictions — that bind every owner…"* — "Covenants" auto-links to Covenant entry via +s plural. | *"…enforces the CC&Rs that bind every owner…"* — tap CC&Rs for the expansion. |
| *"…regulates GSEs (Government-Sponsored Enterprises)…"* — if "Enterprise" is its own entry, the expansion bleeds. | *"…regulates GSEs…"* — entry's `full` covers the expansion. |

The reader gets the expansion by tapping the acronym, where the entry's UI shows it. Repeating it inline doubles the prose with no benefit and risks wrong-context links.

### 5. Word-form variants (gerund / past tense / possessive)

The linker's regex catches `+s` and `+es` plurals only. It does NOT catch `-ing`, `-ed`, `-'s`, `-d` (silent-e past tense), or `-ies` (y→ies) variations. Inflected forms of existing entries read like jargon to the novice but produce no hyperlink.

| Variant in prose | Existing entry | Effect |
|---|---|---|
| *"escrowed"* | `Escrow` | won't link — past tense |
| *"refinancing"* | `Refinance` | won't link — gerund |
| *"appraiser's report"* | `Appraiser` | won't link — possessive |
| *"deeded"* | `Deed` | won't link — past tense |
| *"LIBOR's retirement"* | `LIBOR` | won't link — possessive |
| *"Treasuries"* | `Treasury` | won't link — y→ies plural |

**Two acceptable fixes:**

1. **Rephrase to a linkable form**: *"held in Escrow"* (not "escrowed"); *"after the Refinance"* (not "refinancing"); *"the Appraiser report"* (not "appraiser's"); *"with its own Deed"* (not "deeded"); *"retirement of LIBOR"* (not "LIBOR's").
2. **Accept the gap** when the alternative is unnaturally awkward, and ensure the term is hyperlinked at least once nearby in the same definition (so the chain isn't broken — the reader can still drill down).

The audit script (`scripts/audit_hyperlinks.py`) flags inflected forms of existing entries via `--inflections`. Treat severity 3 (canonical-drift) findings here the same as elsewhere.

### 6. Corpus-thoroughness check

A separate, corpus-wide thoroughness rule: if a capitalised proper noun (Fannie Mae, Freddie Mac, HUD, USPAP) or a domain compound (Property Tax, Appraisal Contingency, NOI) appears **3+ times across the corpus** without being its own entry, it is almost always a missing entry. Frequency is the signal.

- A novice hits the same unfamiliar word three times across the glossary and learns nothing about it → that's a corpus gap, not a per-entry gap.
- The audit's `--repeated-dangling N` flag surfaces these. The default threshold is 3.

This rule applies before the others: write the entries first, then write the prose, so cross-references find live targets.

## What gets a `plain` line

Every term, eventually. But prioritise by **reference frequency** — terms most cited in other definitions should get `plain` first, so chains terminate cleanly at the most-traversed nodes. The audit script ranks terms by frequency.

Terms that probably don't need a `plain` (use empty string, the UI skips the tier):
- Trivial proper nouns where the snappy is already plain ("Bloomberg", "JPMorgan").
- Terms whose `snappy` is already under 12 words and jargon-free.

## Process

1. Run `scripts/audit_clarity.py <industry>` to get the worklist.
2. Author `plain` lines for the top batch (high-frequency first).
3. Update the JSON via the Python `entry()` helper (`plain="..."` parameter).
4. Re-run the audit. Iterate.
5. Spot-check on the simulator — open the term, confirm the `plain` line reads cleanly to a friend who doesn't know the field.

## Reference

- Code: [Sources/Models/Glossary.swift](../Sources/Models/Glossary.swift) (`Term.plain` field), [Sources/Models/Hyperlinks.swift](../Sources/Models/Hyperlinks.swift) (linker), [Sources/Views/TermDetailView.swift](../Sources/Views/TermDetailView.swift) (`plainEnglish` section).
- Authoring scripts: [scripts/add_finance_terms.py](../scripts/add_finance_terms.py) and siblings — `entry()` helper accepts `plain=""`.
- Audit: [scripts/audit_clarity.py](../scripts/audit_clarity.py).
