# JB Glossary — Pharma Corpus Hyperlink Quality Audit

**Corpus:** Pharma (759 entries) · **Linker model:** exact case-insensitive term-name substring match across `plain` / `snappy` / `detail`, longest-match-first · **Audit method:** automated flagging → multi-agent classification → exact-edit proposal → adversarial mechanical re-verification of the auto-apply-safe set · **Owner decision:** apply verified-safe edits on a branch; route everything else to a human review queue.

---

## 1. Executive summary

The audit swept all 759 Pharma entries and surfaced **1,158 findings** across the three text fields. Classification disposition:

| Verdict | Count | Share of findings |
|---|---:|---:|
| `leave` (correct/acceptable as-is) | 996 | 86.0% |
| `needs-human` | 101 | 8.7% |
| `fix` | 33 | 2.8% |
| `create-entry` | 28 | 2.4% |
| **Total** | **1,158** | 100% |

The vast majority of flags (86%) were noise the linker handled acceptably; the audit's value is concentrated in the ~14% that classified as actionable.

**Finding categories** (a single finding can carry one primary category):

| Category | Count |
|---|---:|
| dangling (phrase matches no entry) | 550 |
| high-density (many links in one field) | 213 |
| inflected (plural/possessive/verb form of a term) | 149 |
| wrong-sense-generic (links to wrong-concept short term) | 118 |
| repeated-dangling | 55 |
| canonical-drift (short/variant form of a real entry) | 38 |
| self-link | 24 |
| zero-link (entry with no live links) | 11 |

**What gets applied vs. reviewed:**

- **14 edits auto-apply on the branch** — the verified-safe set (6 canonical-drift fixes, 8 wrong-sense link-breaks). Every one passed adversarial re-verification for: `old` found verbatim and unique, meaning preserved, and the link effect mechanically correct.
- **4 candidates were killed by the verifier** before reaching the branch (see §5) — the safety net worked.
- **148 items route to the human review queue**: 92 inflected, 31 dangling (create-entry candidates), 11 zero-link cross-reference proposals, 8 residual wrong-sense, 3 canonical-drift judgement calls, 3 repeated-dangling.

**Highest-leverage themes** (ranked by structural leverage, not raw count):

1. **Systematic inflection gap (149 flags).** The linker only matches exact term names, so it misses every plural (`Antibodies`→`Antibody`, `Immunotherapies`→`Immunotherapy`, `comorbidities`→`Comorbidity`), possessive (`FDA's`, `Gilead's`, `Cell's`, `Eliquis's`), and verb/participle (`graded`→`Grade`) form of an existing term. These are genuine same-concept misses that **cannot be fixed in prose** without mangling grammar. This is the single biggest case for a one-time linker change (§4).

2. **Acronym/long-form self-aliasing.** A recurring `dangling` sub-pattern is an entry's *own acronym* failing to link from its own and sibling entries: `AMR`→Antimicrobial Resistance, `BCC`→Basal Cell Carcinoma, `BBB`→Blood-Brain Barrier. Forcing the long form into prose reads unnaturally *and* would create self-links. Also a linker-side fix (§4).

3. **The "Alzheimer's-Disease" canonical-drift cluster.** Multi-word disease entries (`Alzheimer's Disease`, `Parkinson's Disease`, `Crohn's Disease`) are repeatedly referenced by their colloquial short/possessive forms (`Alzheimer's`, `Parkinson's`, `Crohn's`). Where the short form sits standalone at a sentence/list boundary, the long form inserts cleanly — **6 such sites are in the safe set**. Where it's a possessive followed by a noun (`Alzheimer's antibody`, 16 hits on Alzheimer's Disease alone), it can't be reworded and joins the structural possessive class.

4. **Wrong-sense generic links from one-word entries.** Short generic entries — `Base` (acid/base chemistry), `Stage` (cancer TNM), `Label` (regulatory document), `Resistance` (cancer), `pH`, `Protocol`, `Acid` — auto-link from contexts where the word means something else entirely (DNA `base`, disease `stage`, "umbrella `label`", `Ph+` for Philadelphia). **8 clean link-breaks are in the safe set**; the un-breakable ones (e.g. `Base` inside "base pair"/"base editing") are flagged structural.

5. **Brand-drug and policy-term create-entry candidates (28).** Recurring named drugs with no entry (`Xarelto`, `Xolair`, `Abilify`, `Vraylar`, `Alecensa`, `Kisunla`) and regulatory/clinical concepts (`Complete Response Letter`, `Factor VIII`, `PTSD`, `POLE`, `PASTEUR Act`) are referenced from 2+ entries each. These are content-authoring decisions, not mechanical fixes.

---

## 2. Safe auto-apply manifest (14 edits)

All 14 below are committed to the branch. Each passed: `old` is verbatim + unique in the named field, the reword preserves meaning and grammar, and the link effect is mechanically correct (longest-match-first verified; no accidental new term introduced).

### 2a. `fix_drift` — short/variant form → canonical entry (6 edits, all create a link)

| Host term | Field | old → new (changed span) | Link created |
|---|---|---|---|
| Digital Biomarker | detail | `…typing speed in Parkinson's,` → `…in Parkinson's Disease,` | → Parkinson's Disease |
| GLP-1 Agonist | detail | `…and possibly Alzheimer's.` → `…and possibly Alzheimer's Disease.` | → Alzheimer's Disease |
| LOE | detail | `…the door to a Generic or Biosimilar` → `…a Generic Drug or Biosimilar` | → Generic Drug (Biosimilar still links) |
| Stem Cell | detail | `…in development for Parkinson's, diabetes` → `…for Parkinson's Disease, diabetes` | → Parkinson's Disease |
| TNF Inhibitor | detail | `…rheumatoid arthritis, Crohn's, ulcerative colitis` → `…Crohn's Disease, ulcerative colitis` | → Crohn's Disease |
| Ulcerative Colitis | plain | `…close cousin to Crohn's.` → `…close cousin to Crohn's Disease.` | → Crohn's Disease |
| Ulcerative Colitis | snappy | `…discussed alongside Crohn's.` → `…alongside Crohn's Disease.` | → Crohn's Disease |

*(7 rows; the Ulcerative Colitis entry contributes two — plain and snappy.)*

### 2b. `break_link` — remove wrong-sense generic link (8 edits)

| Host term | Field | old → new (changed span) | Link broken | Link created |
|---|---|---|---|---|
| Antibiotic | snappy | `…bacteria evolve resistance.` → `…evolve antimicrobial resistance.` | Resistance (cancer) | Antimicrobial Resistance |
| Golgi Apparatus | plain | `…wraps and labels proteins…` → `…wraps and tags proteins…` | Label (regulatory) | — |
| Inhibitor | detail | `…used to label drug classes across every pharma pipeline` → `…used to name drug classes…` | Label | — |
| Inhibitor | detail | `…used to label drug classes` → `…used to name drug classes` | Label | — |
| Non-Hodgkin Lymphoma | plain | `An umbrella label for dozens of…` → `An umbrella term for…` | Label | — |
| Monomer | detail | `…impurities at the monomer stage can cause` → `…at the monomer step can cause` | Stage (cancer) | — |
| Outbreak | plain | `…most local stage before it can grow into an epidemic.` → `…most local phase before…` | Stage (cancer) | — |

*(8 rows; the Inhibitor entry contributes two near-identical detail spans.)*

Note: the Antibiotic edit relies on longest-match-first — `antimicrobial resistance` outranks the bare `resistance` substring, redirecting from the wrong-sense `Resistance` (oncology) entry to the correct `Antimicrobial Resistance` entry. Both targets exist in the corpus.

---

## 3. Human review queue (148 items)

### 3a. Inflected — 92 items · **decision: fix in the linker, not in prose**

Every example is a genuine same-concept inflection of an existing term that the exact-match linker cannot catch and that prose edits would damage. There is essentially **nothing to decide per-item** — the recommendation is to accept the structural fix in §4 and clear this queue wholesale. Sub-patterns:

- **Possessives (largest):** `FDA's` (recurs across Aduhelm, AUC, BLA, Black Box Warning, Boxed Warning, EMA…), `Gilead's`, `AstraZeneca's`, `Vertex's`, `Humira's`, `Eliquis's`, `HIV's`, `Cell's` (Apoptosis, BRAF, CDK4/6, Cytoplasm, Degrader…), `Oncology's` (ALK, CML), `Epidemic's`.
- **Plurals:** `Antibodies`→Antibody (Alzheimer's Disease, B-cell, Biologic, Cytoplasm, Epitope…), `Immunotherapies`→Immunotherapy (Antigen, BioNTech, Chemotherapy, Cytotoxic…), `comorbidities`→Comorbidity.
- **Verb/participle:** `graded`→Grade (Astrocytoma, Dysplasia, Ependymoma — tumor-grading sense, medium confidence).

Representative examples (all `verdict: needs-human`, all `edit: null`):

| Host | Field | Flagged form | Target | Note |
|---|---|---|---|---|
| Alzheimer's Disease | detail | `Alzheimer's` + noun ×16 | Alzheimer's Disease | possessive; reword reads poorly ("anti-amyloid Alzheimer's Disease antibody") |
| Alzheimer's Disease | detail | `Antibodies` | Antibody | plural; can't singularize in-place |
| Antigen | detail | `Immunotherapies` | Immunotherapy | -ies plural |
| Astrocytoma | detail | `graded` I–IV | Grade | verb form, medium conf. |
| Aduhelm | plain | `FDA's` | FDA | possessive |
| Apoptosis | plain | `Cell's` | Cell | possessive |

### 3b. Dangling create-entry candidates — 31 items · **decision: which deserve their own authored entry**

These phrases recur in 2+ entries and have no link target. They split into two clean groups; both need authored content, so none is auto-safe.

- **Brand-drug entries** (corpus already has siblings like Eliquis, Xalkori, Tagrisso): `Xarelto` (rivaroxaban, DOAC), `Xolair` (omalizumab, anti-IgE), `Abilify` (aripiprazole), `Vraylar` (cariprazine), `Alecensa` (alectinib, ALK inhibitor), `Kisunla` (donanemab, anti-amyloid). Each cited in ~2 entries. Strong, consistent create case.
- **Disease / molecular-marker / policy concepts:** `POLE` (canonical endometrial-cancer molecular subtype; appears in Endometrial Cancer + Ultramutation), `PTSD` (cited in Anxiety Disorder; natural glossary term), `PASTEUR Act` (proposed US antibiotic-incentive legislation; niche policy call), `ATTR` (transthyretin amyloidosis — note: conceptually already covered by the Amyloidosis entry; its `closest` match `Onpattro` is a *drug*, wrong concept, so no drift edit is valid — editorial call only).

### 3c. Repeated-dangling create-entry — 3 items · **decision: author one shared entry**

| Phrase | Hosts | Note |
|---|---|---|
| Complete Response Letter (CRL) | CMC, FDA | Significant FDA regulatory action, no entry. Caveat: the flagged tokens are plural/`FDA`-prefixed (`FDA Complete Response Letters`), so even after authoring, the **verbatim singular** "Complete Response Letter" must appear in host prose to link. |
| Factor VIII | Hemophilia A (snappy + detail) | Central hematology concept (deficient protein in Hemophilia A; Factor IX for Hemophilia B). Would cross-link Hemophilia A/B. Low confidence — authoring call. |

### 3d. Zero-link cross-reference proposals — 11 items · **decision: approve concrete content additions**

These are the **only review items that ship a concrete proposed edit** (`intent: add_crossref`, all high confidence). Each entry currently has zero live links; the proposed reword weaves in an existing term verbatim. They are not in the auto-apply set because they add content (editorial), not because they are mechanically risky.

| Host | Field | Changed span → | Link created |
|---|---|---|---|
| Epilepsy | detail | `…for drug-resistant cases.` → `…for refractory (drug-resistant) cases.` | Refractory |
| First-in-Human | snappy | `…a high-stakes Phase 1 study…` → `…Phase 1 Trial…` | Phase 1 Trial |
| First-in-Human | detail | `…carefully escalating amounts,` → `…escalating amounts (Dose Escalation),` | Dose Escalation |
| Oligometastatic | detail | `…stereotactic radiosurgery or targeted surgery…` → `…radiosurgery, a form of focused Radiation Therapy, or…` | Radiation Therapy |
| Oligometastatic | detail | `…1-5 metastases…` → `…1-5 sites of Metastasis…` | Metastasis |
| Oncology | detail | `…largest share of new drug approvals.` → `…approvals; its drug arsenal spans Chemotherapy, Targeted Therapy, and Immunotherapy.` | Chemotherapy, Targeted Therapy, Immunotherapy |
| Phase 2 Trial | snappy | `…doses chosen in Phase 1.` → `…in a Phase 1 Trial.` | Phase 1 Trial |
| Phase 2 Trial | detail | `…Phase 3 investment is hard to justify.` → `…Phase 3 Trial investment…` | Phase 3 Trial |
| Prior Authorization | detail | `…utilization-management tool…failed alternatives…` → `…Utilization Management tool…failed alternatives (Step Therapy)…` | Utilization Management, Step Therapy |
| Therapeutic Index | detail | `Most chemo drugs have narrow TIs` → `Most cytotoxic chemo drugs…` | Cytotoxic |
| Therapeutic Index | snappy | `…requires careful monitoring.` → `…monitoring of the drug's Therapeutic Window.` | Therapeutic Window |

These are high-value: they take 7 entries from zero to multiple live links. Recommend approving as a batch — the medical substitutions are faithful (FIH studies *are* Phase 1; SRS *is* focused radiation therapy; chemo drugs *are* cytotoxic).

### 3e. Residual wrong-sense — 8 items · **decision: accept reword, or send to structural linker fix**

Of the 8 here, **5 carry a concrete proposed edit** (medium–high confidence) and 3 are flagged structural (`edit: null`):

Concrete-edit candidates (judgement calls — verify no new mis-link):
- **Base Pair / detail** — `(base editing)` → `(so-called nucleotide editing)`: breaks wrong `Base` (chemistry) link, adds `Nucleotide`. ⚠️ *This exact edit was also a verifier rejection in another pass — see §5; "base editing" is an established term of art.*
- **Nucleotide / detail** — `four bases (A,T,G,C…)` → `four letters — A,T,G,C…`: intends to break `Base`. ⚠️ *See §5: "bases" is plural and does not actually link to `Base`, so there may be no link to break.*
- **Philadelphia Chromosome / detail** — `Ph+ … Ph-negative` → `Philadelphia-positive … Philadelphia-negative`: intends to break wrong `pH` link. ⚠️ *See §5: "Philadelphia" still contains the `ph` substring and re-creates the link.*
- **Leqembi / plain** — `in its early stages` → `while it is still early`: intends to break cancer-`Stage`. ⚠️ *See §5: "stages" is plural, may not link to `Stage`.*
- **Molecule / detail** — `nucleic acids` → `RNA and DNA`: breaks wrong `Acid` link, adds RNA + DNA links. Medium confidence — flagged for review because it *introduces* new links.
- **Li-Fraumeni Syndrome / detail** — `(Toronto protocol)` → `(the Toronto surveillance regimen)`: breaks wrong clinical-trial `Protocol` link. Medium confidence — "Toronto protocol" is a recognized proper noun; reword is a judgement call.

Structural (`edit: null`, route to §4):
- **Amino Acid / detail** — self-link suppression on "Amino Acid" exposes the shorter `Acid` substring inside the host's own name, mis-linking 3× to stomach `Acid`. Best fixed by a linker rule (do not let a shorter term match a fragment of the host term's own name), not by rewording an entry whose subject *is* amino acids.
- **Base Pair / detail** — bare `base` fires 4× to chemistry `Base`; "base pair"/"base editing" are verbatim domain terms that must not be reworded. Linker-side suppression of generic `Base` inside "base pair"/"base editing" is the right fix.

### 3f. Canonical-drift judgement calls — 3 items

| Host | Field | Issue | Note |
|---|---|---|---|
| BCL2 | detail | `BCL-2` (hyphenated) ×10 won't match entry `BCL2` (no hyphen) | Structural hyphen-variant class — fix in linker or alias the entry; the entry's own body uses `BCL-2` so don't mangle prose. |
| Hereditary Cancer Syndromes | detail | `Li-Fraumeni` won't link to `Li-Fraumeni Syndrome` | Sits in a parallel list where "syndrome" is dropped for rhythm; inserting only here breaks the list. Human call. |
| Stage | detail | `TNM` → `TNM Staging` (has a proposed edit) | `using systems like TNM` → `…like TNM Staging` is mildly redundant with surrounding staging language. Plausible but not cleanly mechanical. |

---

## 4. Structural recommendation — fix the linker, not 100+ text sites

The data makes a strong quantitative case that the two largest actionable classes are **linker-engineering problems, not content problems**. Per-site prose edits here are both higher-effort and lower-quality (they mangle grammar or typography), and they don't prevent the same misses recurring as the corpus grows.

**Class A — inflection stemming (≈149 flags, 92 in the review queue).**
The linker matches only exact term names. Three deterministic morphology rules would clear almost the entire inflected category at once:

1. **Possessive stripping** — match `Term's` / `Term'` as `Term` (covers `FDA's`, `Gilead's`, `Cell's`, `Eliquis's`, `Oncology's`, `Epidemic's`, `Vertex's`, `Humira's`, `AstraZeneca's`, `HIV's` — by far the largest sub-bucket).
2. **Plural folding** — match `Term`+`s` and `-y`→`-ies` (`Antibodies`→Antibody, `Immunotherapies`→Immunotherapy, `comorbidities`→Comorbidity).
3. **(Optional, medium-confidence) verb/participle for grade-type terms** — `graded`→Grade. Lower priority; "grade/graded" verges on generic, so gate carefully.

Proposal: add a normalization step that, on a failed exact match, strips a trailing `'s`/`'` and tries `-s`/`-ies`→`-y` singularization before giving up — applied to multi-character term names only (skip 1–2 char names to avoid noise). This single change is worth ~149 flags and is grammatically lossless (no prose touched).

**Class B — acronym / long-form aliasing (recurring `dangling` self-aliases).**
Multiple entries' own acronyms never link: `AMR`→Antimicrobial Resistance, `BCC`→Basal Cell Carcinoma, `BBB`→Blood-Brain Barrier (each `verdict: needs-human`, each flagged structural). Forcing the long form into prose reads unnaturally *and* creates self-links. Proposal: give each entry an optional `aliases` field (or auto-derive the initialism from multi-word capitalized term names) and let the linker match aliases the same way. This also subsumes the **hyphen-variant** case (`BCL-2`↔`BCL2`) — alias `BCL-2` to the `BCL2` entry rather than rewriting standard typography in 10 places.

**Class C — host-name fragment suppression (small but high-quality).**
When self-link suppression on a multi-word host fires, the linker currently exposes a *shorter* term that is a fragment of the host's own name — producing wrong-sense links: `Acid` inside the **Amino Acid** entry (3×), `Base` inside **Base Pair** (4×). Proposal: a one-line rule — do not let a shorter term match text that lies inside the host entry's own (suppressed) name span. Cheap, removes a whole class of cross-sense noise that cannot be fixed in prose without damaging entries whose subject *is* that term.

**Bottom line:** Classes A+B+C together account for the large majority of the 148-item review queue. A handful of linker rules retire them permanently and keep retiring them as the corpus grows — strictly higher-leverage than ~140 hand edits, several of which (the §5 rejections) prove prose edits are error-prone in exactly these contexts.

---

## 5. Verifier rejections — the safety net fired 4 times

Four candidates reached the adversarial verifier as auto-apply proposals and were **killed before touching the branch**. They are instructive because each failed for a different, real reason — confirming the verifier checks meaning *and* mechanical link effect, not just textual validity.

| # | Host / field | Proposed edit | Why rejected |
|---|---|---|---|
| 1 | Base Pair / detail | `(base editing)` → `(so-called nucleotide editing)` | **Meaning not preserved.** `old` is verbatim/unique and the link effect is valid, but "base editing" is the established name of a specific CRISPR technique; "nucleotide editing" is non-standard and factually misleading. Also only a *partial* break — 3 other `Base` links remain in the field. |
| 2 | Nucleotide / detail | `four bases (A,T,G,C…)` → `four letters…` | **False link-effect premise.** The matched text is `bases` (plural); per linker rules plurals do **not** match the singular term `Base`. There is no live `Base` link to break, so the edit is mechanically unwarranted. |
| 3 | Philadelphia Chromosome / detail | `Ph+ … Ph-negative` → `Philadelphia-positive … Philadelphia-negative` | **Break fails — link re-created.** Goal was to stop `Ph` matching the case-insensitive `pH` term. But "Phila**ph**…" — "Philadelphia" itself contains `ph`, and under longest-match-first the new text re-creates the exact `pH` link it claimed to break. |
| 4 | Leqembi / plain | `in its early stages` → `while it is still early` | **False link-effect premise.** Claims to break a `Stage` link, but the host text is `stages` (plural), which does not match the singular term `Stage`. No link exists to break; edit accomplishes nothing for linking. |

Two of the four rejections (#2, #4) hinge on the same fact the structural recommendation rests on — **the linker does not match plurals** — which is precisely why those "break-link" edits were no-ops. Rejections #1 and #3 caught a domain-meaning error and a substring-recreation trap respectively. All four correctly stayed out of the auto-apply set and now live in the §3e review queue (with these caveats attached) for human disposition.
---

## 6. Realized results (applied 2026-05-30, branch `pharma-hyperlink-audit`)

| Metric | Before | After | Δ |
|---|---:|---:|---:|
| Live links | 5,783 | 5,785 | **+2 net** |
| Zero-link entries | 7 | 7 | 0 |
| High-density (≥10) | 237 | 237 | 0 |
| Total flagged issues (audit lines) | 3,431 | 3,424 | −7 |

**Edits applied: 13 of 14** (1 was a duplicate of the `Inhibitor` "label→name" fix — the first occurrence consumed it, the second correctly found nothing to change). The net +2 understates the quality change: **+8 correct links created** (7 disease-name drift fixes + the Antibiotic → *Antimicrobial Resistance* redirect) and **6 wrong-sense links removed** (Label/Stage/Resistance noise). Diff is exactly 13 changed lines; entry count and JSON validity unchanged; no zero-link or high-density regressions. Nothing from the 148-item review queue was touched.
