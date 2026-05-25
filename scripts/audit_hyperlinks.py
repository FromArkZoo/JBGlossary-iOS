"""Audit the semantic quality of in-app hyperlinks across glossary entries.

The app's linker (Sources/Models/Hyperlinks.swift) automatically wraps every
substring that matches a known term name in a tappable link. The wiring is
invisible to authors — a definition with zero working links looks identical
in JSON to one with ten. This audit closes that gap.

Usage:
    python3 scripts/audit_hyperlinks.py realEstate
    python3 scripts/audit_hyperlinks.py finance --top 50
    python3 scripts/audit_hyperlinks.py pharma --letter B
    python3 scripts/audit_hyperlinks.py --all                 # every industry
    python3 scripts/audit_hyperlinks.py --cross-industry-only # shared-name table
    python3 scripts/audit_hyperlinks.py realEstate --csv > worklist.csv

Severity ordering (highest impact first):
    1. dangling-link              — capitalised noun phrase that looks like a term but has no entry
    1. repeated-dangling          — proper noun appears 3+ times corpus-wide without an entry
    2. self-link                  — entry's own name appears un-linked in its prose
    3. canonical-drift            — short form used where a longer canonical form would link
    3. inflected-form             — gerund/past-tense/possessive of an entry won't auto-link
    4. semantic-risk-generic      — generic high-homonym name auto-linked; flag for human review
    5. homonym-shadow             — short term substring of longer; verifies longest-first ordering
    6. cross-industry-homonym     — info-only: term name reused across 2+ industries
    7. high-density               — entry has >= 10 live links (likely noisy)
    8. zero-link                  — entry has 0 live links (likely under-cross-referenced or too narrow)
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).parent.parent

INDUSTRY_PATHS = {
    "finance":    ROOT / "Targets/Finance/Resources/glossary_finance.json",
    "pharma":     ROOT / "Targets/Pharma/Resources/glossary_pharma.json",
    "ai":         ROOT / "Targets/AI/Resources/glossary_ai.json",
    "law":        ROOT / "Targets/Law/Resources/glossary_law.json",
    "realEstate": ROOT / "Targets/RealEstate/Resources/glossary_realEstate.json",
}

BODY_FIELDS = ("plain", "snappy", "detail")

# Density thresholds (per entry, summed across plain+snappy+detail).
HIGH_DENSITY_THRESHOLD = 10
ZERO_LINK_SAMPLE_SIZE = 30
HIGH_DENSITY_SAMPLE_SIZE = 30

# Capitalised multi-word phrase candidate, 1–4 capitalised words, OR an
# all-caps acronym 2–8 chars. Used by the dangling-link detector.
PHRASE_RE = re.compile(
    r"\b("
    r"[A-Z][a-zA-Z]+(?:[ \-&][A-Z][a-zA-Z]*){0,3}"   # Capitalised Multi Word
    r"|"                                              # (& joins handle CC&Rs;
    r"[A-Z]{2,8}"                                    #  continuation allows
    r")\b"                                           #  single-letter "A/B/C"
)                                                    #  in Class A, Type B…

# Tokens that look like jargon but should never become entries: brand names,
# product names, locations, dates, person names. Augments LINKER_DENYLIST from
# audit_clarity.py with real-estate brands (added incrementally as noise surfaces).
DANGLING_DENYLIST = {
    # Currencies, locales
    "US", "USD", "EUR", "GBP", "JPY", "UK", "EU", "EU's", "US's",
    # Months & dates
    "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December",
    # Common acronyms used informally
    "AI", "DNA", "USB", "JSON", "KV", "SSD", "VS", "BMW",
    "TV", "COVID", "IT", "PM", "AM",
    # Generic business / legal short acronyms used in prose
    "CEO", "CFO", "FTC", "FCC", "UCC", "IVF", "ID", "CD",
    # Roman numerals attached to proper nouns
    "II", "III", "IV", "VI",
    # Index ticker symbols / exchange short-names
    "S&P", "Dow", "QQQ", "SAP", "HSBC", "LVMH",
    "CME", "NYSE", "CBOT", "ICE", "NASDAQ", "LSE", "CBOE",
    # Publishers / news outlets
    "Bloomberg", "Reuters", "Wall", "Street", "Wall Street",
    # Real estate brand / platform names that won't become entries
    "MLS", "Zillow", "Redfin", "Compass", "CoStar", "Yardi",
    "Trulia", "Realtor", "Opendoor",
    # US states & well-known cities likely to appear in prose
    "California", "New York", "Texas", "Florida", "Washington",
    "Massachusetts", "Manhattan", "Brooklyn", "Los Angeles", "San Francisco",
    "Chicago", "Boston", "Miami", "Seattle", "Houston", "Dallas",
    # Common given/family names appearing in case law or examples
    "Smith", "Jones", "Brown", "Roberts",
    # Government / regulator names with their own dedicated source links
    "Federal", "Fed", "Treasury", "Treasuries",
    "IOU",
    # Hyphenated-entry prefixes whose tail is lowercase (Pre-approval, Co-op).
    # PHRASE_RE only joins capitalised continuations, so the prefix lands here
    # as a bare proper-noun candidate even though the linker handles the
    # whole compound when it sits in prose.
    "Pre", "Co",
    # Federal-agency expansions that appear in `plain` lines for novice
    # readability — the acronym entry's `full` field carries the same string
    # in the UI. Listed here as known noise; if any component noun ever
    # becomes its own entry (e.g. "Administration"), revisit Rule 4b.
    "Federal Housing Administration", "Federal Housing",
    "US Department", "Veterans Affairs",
    "Department of Veterans Affairs", "US Department of Agriculture",
    "US Department of Housing", "Section",  # 'Section 8' housing
    # Statute shorthand surfaced in prose; not entries themselves.
    "Dodd-Frank Act", "TCJA",  # candidate entries for batch 2
    # Common English words that lead a multi-word entry — "Common attributes"
    # vs "Common Area", "Class buildings" vs "Class A". These also suppress
    # canonical-drift false positives via the DANGLING_DENYLIST check above.
    "Common", "Class", "Single", "Real", "Joint",
    "Going", "Exit", "Hard", "Soft", "Earnest", "Operating",
    "Preferred", "Rate", "Occupancy", "Property",
    "Loan", "Capital", "Gross", "Net", "Fair", "Affordable",
    "Multifamily", "Limited", "General",
    # Tail-fragment artifacts of PHRASE_RE breaking on lowercase connectors
    # (Debt-to-Income → "Debt" then "Income Ratio"; FHFA Conforming Loan limits
    # → "FHFA Conforming Loan"; US Mortgages → "US Mortgages" composite).
    # Both halves link separately in the UI; the regex just can't see the join.
    "Income Ratio", "US Mortgages", "FHFA Conforming Loan",
    "Mortgage Interest", "Landlord-Tenant", "Closing Cost",
    "Cash Return",
    # Generic single-word artifacts — sentence fragments, compound titles,
    # or generic English caught by PHRASE_RE despite not being missing entries.
    "Debt", "Eligibility", "Ethics", "Code", "Development",
    "Sale", "Tenancy", "Certificate", "Exchange",
    # US states caught in prose (carriers of last resort, state-by-state law)
    "Oregon", "Illinois", "Virginia", "West", "Carolina",
    "Minnesota", "Louisiana", "Arizona", "Nevada", "Maryland",
    "New Jersey", "Ohio", "Tennessee", "Idaho", "Wisconsin",
    "Phoenix", "Vermont", "Hawaii",
    # Brand / company names that surface in concrete-example prose.
    "STORE Capital", "Realty Income", "BiggerPockets",
    "Equinix", "Simon", "Prologis", "AvalonBay", "FedEx",
    "Walmart", "Amazon", "Citizens", "Rocket", "UWM",
    "Blackstone", "Tricon", "Welltower", "Ventas",
    "Marriott", "Hilton", "Hyatt", "Wells Fargo", "US Bank",
    "JPMorgan", "Chase", "Texas Capital", "Comerica",
    "Mr. Cooper", "PennyMac", "Newrez", "Lakeview", "Stockbridge",
    "EQT Exeter", "American Homes", "Invitation Homes", "Pretium",
    "Spirit Realty Capital", "Realty Income",
    "Public Storage", "Extra Space", "CubeSmart", "Life Storage",
    "American Campus", "Sun Communities", "Equity LifeStyle",
    "Lennar", "Pulte", "KB Home", "Toll Brothers",
    "Best Buy", "Costco", "Target", "Home Depot", "Lowe",
    "Whole Foods", "Kroger", "Publix", "Trader Joe",
    "TJX", "Marshalls", "HomeGoods", "Ross", "Burlington",
    "Five Below", "Dollar Tree", "PetSmart", "Ulta", "ALDI",
    "Apple", "Sephora", "Anthropologie",
    "STR", "CoStar Group", "STR", "NAIOP",
    "Easton Town Center", "Domain", "Grove",
    "Goldman Sachs", "KKR", "Brookfield", "Starwood",
    "Cousins", "Equinix Asia",
    "Mesa West", "MetLife", "Greystone", "Rialto Capital", "LNR Partners",
    "Boston", "Dallas",
    "Penn National", "GLPI", "Darden", "Olive Garden", "Four Corners",
    "Ryman Hospitality",
    # More chain names / brand examples used in concrete examples.
    "AutoZone", "Bed Bath", "JCPenney", "Macy", "McDonald", "Macy's",
    "Starbucks", "Chick-fil-A", "AMC", "Regal", "Top Golf",
    "Sears", "Kmart", "Toys R Us",
    "Brookdale", "Atria", "Sunrise", "Belmont Village", "Holiday Retirement",
    "Acts Retirement", "Erickson Living", "Life Care Services", "ABHM",
    "Sun City", "Robson Communities", "Trilogy", "K. Hovnanian",
    "Provident Royalties", "LandAmerica",
    "Travelers", "Liberty Mutual", "Zurich", "CNA",
    "STR", "STORE", "STORE Capital", "Agree Realty",
    "Coldwell Banker", "RE/MAX", "Keller Williams",
    "Auction.com",
    # PMS / property management software brands.
    "Yardi", "RealPage", "AppFolio", "Buildium", "Entrata",
    "MRI", "Argus", "RentManager", "Procore", "Autodesk Construction",
    "OpenSpace", "Robin", "Skedda", "LiquidSpace",
    "VTS", "Latch", "Honeywell", "Schneider Electric",
    "Fundrise", "RealtyMogul", "CrowdStreet", "Propy", "Lofty", "Arrived",
    # More Real Estate companies / Coworking operators.
    "Regus", "Industrious", "Spaces", "Convene", "Workspring",
    "American Campus Communities", "Greystar", "Bozzuto",
    "Mill Creek", "Trammell Crow", "AvalonBay Communities", "Equity Residential",
    "UDR", "Camden Property Trust", "Highwoods", "Kilroy",
    "BREEAM",
    "Mission Capital", "Eastdil Secured", "JLL", "Phillips Edison",
    "Brixmor", "MetLife", "Northwestern Mutual", "New York Life",
    "SoftBank", "Lone Star", "Wilbur Ross",
    "General Growth Properties", "Bed Bath",
    # Common compound English phrases caught as multi-word.
    "Commercial Tenants", "Commercial Mortgage", "Foreign Buyers",
    "Department", "Beyond", "Open Plan",
    # IRS terms.
    "USC", "Section 121", "Section 1031", "Section 199A",
    "Section 263", "Section 168", "Section 469",
    "Section 1245", "Section 1250", "Section 1411",
    # More cities / regions caught in concrete examples.
    "Atlanta", "Cambridge", "Detroit", "Manhattan",
    "Boston", "St. Louis", "Cleveland", "Phoenix",
    "Brooklyn", "Bay Area",
    # Brand fragments.
    "Chick", "America", "AppHarvest", "Bowery", "AeroFarms",
    "Innovative Industrial", "AFC Gamma", "NewLake Capital",
    "Healthcare Realty Trust", "Physicians Realty Trust", "MedEquities",
    "Alexandria Real Estate", "BioMed Realty", "Healthpeak",
    "American Tower", "Crown Castle", "SBA Communications",
    "Safe Harbor", "Sun Communities", "Equity LifeStyle",
    "Kimpton", "Hyatt Centric", "Joie de Vivre", "Curio Collection",
    "Marriott Tribute", "Moxy", "Aloft", "Hyatt Place",
    # Statute / legal-case references.
    "CERCLA", "Burnett", "Article", "AB", "AB 1482",
    "RA", "DUS", "URLA",
    # Cross-industry acronyms used in passing.
    "AUM", "HERS", "RESNET", "OTARD",
    # Latin / legal terms.
    "ESFR",
    # Sub-words of multi-word entries handled by the bidirectional check
    # but still appearing in repeated-dangling — explicit denylist for clarity.
    "BIDs",
    # Compound phrases that are sub-references to entries already covered.
    "Sponsor Promote", "Commercial Mortgage",
    # State names not yet in denylist.
    "Connecticut", "Pennsylvania", "Indiana", "Iowa",
    "Wisconsin", "Michigan", "Kansas",
    # Insurance / construction codes used in passing.
    "HO", "ALTA 9", "ALTA 17",
    # Generic English nouns picked up by PHRASE_RE.
    "English", "Board", "Title", "Mechanic",
    # Architectural elements.
    "Build-Out",
    # Generic single-word product terms.
    "Mall",
    # Specific named neighbourhoods / master-planned communities cited in examples.
    "The Villages", "Summerlin", "Mountain House", "Florida",
    # PSF (per square foot) is industry-wide unit notation, not a glossary
    # entry candidate. CPI is cross-industry context surfaced in examples.
    # FEMA is an authoring agency rather than a glossary term.
    "PSF", "CPI", "FEMA",
    # Generic English nouns that surface in concrete examples.
    "Roof", "Surfside", "Pool", "Mall", "Garage",
    "Park", "Mountain", "Building", "Lake",
    # Inflected variants of existing entries — Stabilization (Stabilized),
    # Acceleration (Acceleration Clause exists already), etc.
    "Stabilization", "Refinancing", "Underwrite",
    "Eviction", "Convey",
    # Codified statute references that aren't standalone entries.
    "United States Code", "US Code", "United States",
    # English conjunctions / words that PHRASE_RE picks up as acronyms.
    "OR", "AND", "OF", "BY",
    # Common compound plurals that are artifacts of bare-singular entries.
    "Commercial Mortgages", "US Treasuries", "Retail Tenants",
    "Retail Tenant",
    # Specific Lease-form shorthand that's already covered by an entry.
    "NNN Lease",  # Triple Net Lease + NNN both exist; NNN Lease combines them
    # Inflected variants of existing entries
    "Escalations",  # Escalation Clause exists
    # Federal agencies / acronyms used in passing.
    "DOJ", "DHS", "USCIS", "DOL", "DOI", "IRS",
    # Big-city shorthand used in concrete examples.
    "NYC", "LA", "SF", "DC", "ATL",
    # More US states surfaced in geographic examples.
    "New Mexico", "Alaska",
    # Verb inflections of base concepts — Foreclose (of Foreclosure)
    # is normal English usage and shouldn't be flagged when prose
    # uses it as a verb.
    "Foreclose", "Sell",
}

# High-risk multi-meaning glossary names. When these auto-link, the linker
# can't tell whether the context matches the intended sense. Surfaced for
# human review one occurrence at a time.
GENERIC_HOMONYM_HIGH_RISK = {
    # Cross-domain financial/legal
    "Property", "Title", "Will", "Trust", "Note", "Mark", "Bill",
    "Call", "Put", "Spread", "Yield", "Lock", "Cap", "Floor", "Bridge",
    "Float", "Wrap", "Spot", "Long", "Short", "Stock",
    # Real-estate-specific generic terms
    "Lot", "Block", "Class", "Grade", "Site", "Unit", "Plot",
    # AI / cross-tech
    "Agent", "Attention", "Model", "Prompt", "Layer", "Token", "Weight",
}

# Category-cluster definitions per industry. Categories in the same cluster
# are "obviously related"; cross-cluster links surface as semantic-risk warnings.
# Update as the audit reveals noise patterns. Each industry's clusters are a
# partition of its full category list (every category appears in exactly one).
CATEGORY_CLUSTERS = {
    "realEstate": {
        "money": {"Financing & Lending", "Tax", "Market & Investment", "Valuation & Appraisal"},
        "paper": {"Transactions", "Title & Ownership", "Law & Regulation"},
        "physical": {"Property Types", "Development", "Leasing", "Management & Operations"},
    },
    "finance": {
        "instruments": {"Instruments", "Pricing & Valuation", "Risk", "Quantitative"},
        "execution": {"Trading & Execution", "Market Structure", "Settlement & Operations"},
        "context": {"Indexes & Benchmarks", "Corporate Actions", "Regulation"},
    },
    "pharma": {
        "science": {"Mechanism", "Diagnostics", "Clinical"},
        "operations": {"Manufacturing", "Pharmacovigilance"},
        "business": {"Commercial / Market Access", "Regulatory", "Digital Health"},
    },
    "ai": {
        "modeling": {"Architecture", "Training", "Inference", "Models", "Concepts"},
        "evaluation": {"Eval", "Alignment", "Safety", "Research", "Frontier", "Agents"},
        "infrastructure": {"Hardware", "Manufacturing", "Memory", "Interconnect",
                           "Packaging", "Software", "Infrastructure"},
        "context": {"Company", "Industry", "Regulation"},
    },
    "law": {
        "private": {"Contract", "Tort", "Property", "IP", "Corporate", "Employment", "Family"},
        "public": {"Criminal", "Constitutional", "Regulatory", "Immigration"},
        "procedural": {"Procedure", "Bankruptcy", "Tax"},
    },
}


def load_terms(industry):
    path = INDUSTRY_PATHS.get(industry)
    if path is None:
        sys.exit(f"Unknown industry '{industry}'. Choices: {sorted(INDUSTRY_PATHS)}")
    if not path.exists():
        sys.exit(f"Glossary not found: {path}")
    with path.open() as f:
        return json.load(f)


def live_links(body, current_term, all_terms):
    """Replica of Sources/Models/Hyperlinks.swift:computeAttributedText.

    Returns a list of (start, end, target_term_name) for every range the
    in-app linker would wrap as a hyperlink. Same rules:
      - Sort longest-first so multi-word matches win over substrings.
      - Skip self-references and 1-char tokens.
      - Word-boundary lookarounds reject \\w-or-hyphen on either side.
      - Optional plural suffix (e?s).
      - Case-sensitive iff term has no lowercase chars (acronyms strict).
      - Track linked spans, skip overlapping shorter matches.
    """
    if not body:
        return []
    candidates = sorted(
        (t for t in all_terms if t["term"] != current_term and len(t["term"]) >= 2),
        key=lambda t: -len(t["term"]),
    )
    linked_spans = []
    out = []
    for c in candidates:
        name = c["term"]
        has_lower = any(ch.islower() for ch in name)
        flags = re.IGNORECASE if has_lower else 0
        pattern = r"(?<![\w-])" + re.escape(name) + r"(?:e?s)?(?![\w-])"
        try:
            regex = re.compile(pattern, flags)
        except re.error:
            continue
        for m in regex.finditer(body):
            s, e = m.span()
            if any(not (e <= ls or s >= le) for ls, le in linked_spans):
                continue
            linked_spans.append((s, e))
            out.append((s, e, name))
    return out


def _is_sentence_start(body, pos):
    if pos == 0:
        return True
    i = pos - 1
    while i >= 0 and body[i].isspace():
        i -= 1
    if i < 0:
        return True
    return body[i] in ".!?\n"


def _phrase_is_word_of_entry(phrase, name_lookup):
    """True if `phrase` shares a contiguous word-slice with any existing
    entry name — either the phrase is a sub-slice OF an entry name
    ("Common" inside "Tenancy in Common", "Exit Cap" inside "Exit Cap Rate")
    OR an entry name is a sub-slice of the phrase ("Servicing Rights" entry
    inside "Mortgage Servicing Rights" phrase). In both cases the Swift
    linker resolves the entry name where it appears in prose, even if the
    audit's PHRASE_RE captured a longer or shorter span.
    """
    phrase_lower = phrase.lower()
    phrase_words = re.split(r"[ \-&]+", phrase_lower)
    for name in name_lookup:
        name_lower = name.lower()
        if name_lower == phrase_lower:
            return False  # exact match — not a sub-word case
        name_words = re.split(r"[ \-&]+", name_lower)
        # Direction 1: phrase is a slice of entry name
        if len(phrase_words) <= len(name_words):
            for i in range(len(name_words) - len(phrase_words) + 1):
                if name_words[i:i + len(phrase_words)] == phrase_words:
                    return True
        # Direction 2: entry name is a slice of the phrase, but only when
        # the entry is multi-word (single-word entries already match via
        # the +s/+es stem check, and skipping them here keeps the heuristic
        # tight — we don't want "Mortgage" entry to swallow every phrase
        # that contains the word "mortgage").
        if len(name_words) >= 2 and len(name_words) <= len(phrase_words):
            for i in range(len(phrase_words) - len(name_words) + 1):
                if phrase_words[i:i + len(name_words)] == name_words:
                    return True
    return False


def _closest_entry(phrase, name_lookup):
    """Suggest closest existing entry by substring containment.
    Cheap heuristic — returns first hit, None if no overlap."""
    phrase_lower = phrase.lower()
    for name in name_lookup:
        n_lower = name.lower()
        if phrase_lower in n_lower or n_lower in phrase_lower:
            if name.lower() != phrase_lower:
                return name
    return None


def detect_dangling(entry, all_terms, name_lookup):
    """Capitalised multi-word phrases (mid-sentence) that LOOK like terms but
    have no matching entry. Suggests the closest existing entry where possible."""
    violations = []
    name_set_lower = {n.lower() for n in name_lookup}
    seen = set()
    for field in BODY_FIELDS:
        body = entry.get(field, "") or ""
        if not body:
            continue
        for m in PHRASE_RE.finditer(body):
            phrase = m.group(1)
            if _is_sentence_start(body, m.start()):
                continue
            if phrase in DANGLING_DENYLIST:
                continue
            # Also suppress +s/+es plurals of denylist entries ("Sections" of
            # the denylisted "Section", "Mortgagees" of an acronym, etc.).
            if phrase.endswith("s") and phrase[:-1] in DANGLING_DENYLIST:
                continue
            if phrase.endswith("es") and phrase[:-2] in DANGLING_DENYLIST:
                continue
            if phrase.lower() in name_set_lower:
                continue  # would link, no problem
            # The Swift linker accepts +s and +es plural suffixes via (?:e?s)?
            # in Hyperlinks.swift. Try BOTH stems — greedy `e?s$` strips "es"
            # first ("Mortgages" → "Mortgag"), which misses the +s case
            # ("Mortgages" → "Mortgage"). Check the +s stem too.
            phrase_lower = phrase.lower()
            stemmed = False
            if phrase_lower.endswith("es") and phrase_lower[:-2] in name_set_lower:
                stemmed = True  # +es plural matches an entry
            elif phrase_lower.endswith("s") and phrase_lower[:-1] in name_set_lower:
                stemmed = True  # +s plural matches an entry
            if stemmed:
                continue
            # PHRASE_RE can't follow lowercase connector words ("Tenancy in
            # Common", "Letter of Intent", "Notice of Pending Action") so a
            # matched fragment may be the tail of a multi-word entry whose
            # full form the Swift linker handles. If the phrase appears as a
            # whole word inside an entry name, suppress the dangling flag.
            if _phrase_is_word_of_entry(phrase, name_lookup):
                continue
            key = (phrase, field)
            if key in seen:
                continue
            seen.add(key)
            suggestion = _closest_entry(phrase, name_lookup)
            msg = f"'{phrase}' in {field} looks like a term but has no entry"
            if suggestion:
                msg += f" (closest: '{suggestion}')"
            violations.append({"kind": "dangling-link", "msg": msg})
    return violations


def detect_self_link(entry, all_terms):
    """The Swift linker already skips exact-name self-refs. The remaining
    style smell: the entry's own name repeated through its own prose.
    Fires only when total occurrences across plain+snappy+detail is >=2,
    so the natural opening sentence ('An ARM has...') doesn't trip the rule.
    """
    violations = []
    self_name = entry["term"]
    pattern = r"(?<![\w-])" + re.escape(self_name) + r"(?:e?s)?(?![\w-])"
    has_lower = any(c.islower() for c in self_name)
    flags = re.IGNORECASE if has_lower else 0
    total = 0
    for field in BODY_FIELDS:
        body = entry.get(field, "") or ""
        if not body:
            continue
        total += len(re.findall(pattern, body, flags=flags))
    if total >= 2:
        violations.append({
            "kind": "self-link",
            "msg": f"'{self_name}' appears {total}x across its own body fields — prefer 'it' on repeat mentions",
        })
    return violations


def detect_canonical_drift(entry, name_lookup):
    """A bare first word of a multi-word entry appears in body, capitalised,
    NOT followed by its remainder. E.g. 'Sharpe' in prose but the entry is
    'Sharpe Ratio'. Case-sensitive on purpose — lowercase 'risk' or 'put' is
    almost always normal English, not a drift candidate."""
    by_first_word = defaultdict(list)
    for name in name_lookup:
        parts = name.split()
        if len(parts) < 2:
            continue
        first = parts[0]
        # Only flag if the first word starts with uppercase — that's a real
        # naming convention signal. "Sharpe" → drift; "risk" → English.
        if not first[0].isupper():
            continue
        by_first_word[first].append(name)

    bare_entries = set(name_lookup)

    violations = []
    seen = set()
    for field in BODY_FIELDS:
        body = entry.get(field, "") or ""
        if not body:
            continue
        for first_word, candidates in by_first_word.items():
            if first_word in bare_entries:
                continue
            # Common English words that lead a multi-word entry create constant
            # false-positive drift signals ("Common attributes…", "Class buildings…").
            # Mirror the dangling-link denylist here.
            if first_word in DANGLING_DENYLIST:
                continue
            # Case-sensitive match — "Sharpe" yes, "sharpe" no.
            pattern = re.compile(r"(?<![\w-])" + re.escape(first_word) + r"(?![\w-])")
            for m in pattern.finditer(body):
                rest = body[m.end():m.end() + 60]
                follows = False
                for c in candidates:
                    parts = c.split(" ", 1)
                    if len(parts) < 2:
                        continue
                    tail = parts[1]
                    if rest.lstrip().lower().startswith(tail.lower()):
                        follows = True
                        break
                if follows:
                    continue
                # Skip sentence-start positions — first-word capitalisation is normal there.
                if _is_sentence_start(body, m.start()):
                    continue
                key = (first_word, field)
                if key in seen:
                    continue
                seen.add(key)
                violations.append({
                    "kind": "canonical-drift",
                    "msg": f"'{first_word}' in {field}: short form of {candidates[:3]} — won't auto-link",
                })
                break
    return violations


def _inflected_variants(name):
    """Generate likely inflected forms of a single-word entry name.
    Returns a list of (variant, kind) tuples. Skips multi-word names —
    inflection of compounds is rare and harder to detect reliably."""
    if " " in name or "-" in name or len(name) < 3:
        return []
    base = name
    variants = []
    # Possessive ('s)
    variants.append((base + "'s", "possessive"))
    # Past tense / past participle — only for verb-like names (heuristic: any).
    if base.endswith("e"):
        variants.append((base + "d", "past tense"))
        variants.append((base[:-1] + "ing", "gerund"))
    elif base.endswith("y") and len(base) > 1 and base[-2] not in "aeiou":
        variants.append((base[:-1] + "ied", "past tense"))
        variants.append((base[:-1] + "ies", "plural"))  # y→ies, not handled by linker's +s
        variants.append((base + "ing", "gerund"))
    else:
        variants.append((base + "ed", "past tense"))
        variants.append((base + "ing", "gerund"))
    return variants


def detect_inflected_forms(entry, all_terms, name_lookup):
    """Find gerund/past-tense/possessive/ies-plural forms of OTHER existing
    entries appearing in this entry's body. The linker's `(?:e?s)?` only catches
    +s/+es plurals — these variants slip through.

    One report per (variant, host_term, source_term).
    """
    violations = []
    self_name = entry["term"]
    other_names = [n for n in name_lookup if n != self_name]
    seen = set()
    for field in BODY_FIELDS:
        body = entry.get(field, "") or ""
        if not body:
            continue
        for source_name in other_names:
            for variant, kind in _inflected_variants(source_name):
                pattern = r"(?<![\w-])" + re.escape(variant) + r"(?![\w-])"
                # Acronyms (LIBOR, SOFR) keep case-sensitive matching; mixed-case
                # are case-insensitive (Mortgage's → mortgage's still counts).
                has_lower = any(c.islower() for c in source_name)
                flags = re.IGNORECASE if has_lower else 0
                if re.search(pattern, body, flags=flags):
                    key = (variant.lower(), source_name)
                    if key in seen:
                        continue
                    seen.add(key)
                    violations.append({
                        "kind": "inflected-form",
                        "msg": f"'{variant}' ({kind} of '{source_name}') in {field} — won't auto-link",
                    })
                    break  # one variant per (source_name, entry)
    return violations


def aggregate_repeated_dangling(all_terms, name_lookup, threshold=3):
    """Corpus-wide scan: capitalised proper-noun phrases that appear N+ times
    across the corpus and aren't entries. Reported once per phrase, attached
    to the first entry where they appear.

    Returns a dict: term_name -> list of {"kind", "msg"} violations.
    The threshold defaults to 3 — fewer occurrences are handled by detect_dangling.
    """
    name_set_ci = {n.lower() for n in name_lookup}
    phrase_counts = Counter()
    phrase_first_seen = {}  # phrase -> (entry_name, field)

    for entry in all_terms:
        for field in BODY_FIELDS:
            body = entry.get(field, "") or ""
            if not body:
                continue
            for m in PHRASE_RE.finditer(body):
                phrase = m.group(1)
                if phrase in DANGLING_DENYLIST:
                    continue
                # Also suppress +s/+es plurals of denylist entries.
                if phrase.endswith("s") and phrase[:-1] in DANGLING_DENYLIST:
                    continue
                if phrase.endswith("es") and phrase[:-2] in DANGLING_DENYLIST:
                    continue
                # Skip plural form of existing entries — linker handles +s/+es
                if phrase.lower() in name_set_ci:
                    continue
                p_lower = phrase.lower()
                if p_lower.endswith("es") and p_lower[:-2] in name_set_ci:
                    continue
                if p_lower.endswith("s") and p_lower[:-1] in name_set_ci:
                    continue
                # Mirror detect_dangling's whole-word-of-entry suppression so
                # multi-word entries with lowercase connectors don't leak
                # phantom dangle counts into the aggregate.
                if _phrase_is_word_of_entry(phrase, name_lookup):
                    continue
                if _is_sentence_start(body, m.start()):
                    continue
                phrase_counts[phrase] += 1
                if phrase not in phrase_first_seen:
                    phrase_first_seen[phrase] = (entry["term"], field)

    out = defaultdict(list)
    for phrase, count in phrase_counts.items():
        if count < threshold:
            continue
        host_term, host_field = phrase_first_seen[phrase]
        out[host_term].append({
            "kind": "repeated-dangling",
            "msg": f"'{phrase}' appears {count}x corpus-wide with no entry — likely missing term",
        })
    return out


def _cluster_for(industry, category):
    clusters = CATEGORY_CLUSTERS.get(industry, {})
    for cluster_name, cats in clusters.items():
        if category in cats:
            return cluster_name
    return None


def detect_semantic_risk(entry, all_terms, name_lookup, industry):
    """Three sub-flags surfaced as 'semantic-risk-*':
       (a) Auto-linked term is in GENERIC_HOMONYM_HIGH_RISK — high homonym risk.
       (b) Auto-linked term's category is in a different cluster than host's.
    Both are low-precision warnings — the author reads, decides, moves on."""
    violations = []
    host_cat = entry.get("category", "")
    host_cluster = _cluster_for(industry, host_cat)
    for field in BODY_FIELDS:
        body = entry.get(field, "") or ""
        if not body:
            continue
        for s, e, target_name in live_links(body, entry["term"], all_terms):
            target = name_lookup[target_name]
            ctx_start = max(0, s - 25)
            ctx_end = min(len(body), e + 25)
            ctx = body[ctx_start:ctx_end].replace("\n", " ").strip()
            # (a) Generic homonym auto-linked
            if target_name in GENERIC_HOMONYM_HIGH_RISK:
                violations.append({
                    "kind": "semantic-risk-generic",
                    "msg": f"'{target_name}' auto-linked in {field}; verify intent: …{ctx}…",
                })
            # (b) Cross-cluster category jump
            target_cat = target.get("category", "")
            target_cluster = _cluster_for(industry, target_cat)
            if (host_cluster and target_cluster
                    and host_cluster != target_cluster):
                violations.append({
                    "kind": "semantic-risk-category",
                    "msg": (f"'{target_name}' ({target_cat}/{target_cluster}) "
                            f"linked from {entry['term']} ({host_cat}/{host_cluster})"),
                })
    return violations


def detect_homonym_shadow(all_terms):
    """Verify the longest-first sort actually wins over substring matches.
    Synthesise a body containing the long term and confirm live_links picks it.
    Catches future regressions if the sort key ever breaks."""
    violations = []
    names = sorted({t["term"] for t in all_terms}, key=len)
    name_to_term = {t["term"]: t for t in all_terms}
    for i, short in enumerate(names):
        for long in names[i + 1:]:
            if not re.search(r"(?<!\w)" + re.escape(short) + r"(?!\w)",
                             long, flags=re.IGNORECASE):
                continue
            test_body = f"Discussion of {long} in context."
            picks = [t for _, _, t in live_links(test_body, "", all_terms)]
            if long not in picks:
                violations.append({
                    "kind": "homonym-shadow",
                    "msg": f"'{short}' shadows '{long}' — longest-first sort failing",
                    "term": long,
                    "letter": name_to_term[long]["letter"],
                })
    return violations


def cross_industry_homonyms():
    """Term names appearing in 2+ industries. Info-only — surfaces the table
    so the author consciously decides framing for each shared name."""
    by_name = defaultdict(list)
    for industry, path in INDUSTRY_PATHS.items():
        if not path.exists():
            continue
        with path.open() as f:
            terms = json.load(f)
        for t in terms:
            by_name[t["term"]].append(industry)
    return {n: sorted(set(industries)) for n, industries in by_name.items()
            if len(set(industries)) > 1}


def link_density(entry, all_terms):
    total = 0
    for field in BODY_FIELDS:
        body = entry.get(field, "") or ""
        total += len(live_links(body, entry["term"], all_terms))
    return total


RANK_FOR = {
    "dangling-link":           1,
    "repeated-dangling":       1,
    "self-link":               2,
    "canonical-drift":         3,
    "inflected-form":          3,
    "semantic-risk-generic":   4,
    "semantic-risk-category":  4,
    "homonym-shadow":          5,
    "high-density":            7,
    "zero-link":               8,
}

SEV_LABEL = {
    1: "DANGLING-LINK / REPEATED-DANGLING",
    2: "SELF-LINK",
    3: "CANONICAL-DRIFT / INFLECTED-FORM",
    4: "SEMANTIC-RISK",
    5: "HOMONYM-SHADOW",
    6: "CROSS-INDUSTRY-HOMONYM",
    7: "HIGH-DENSITY",
    8: "ZERO-LINK",
    99: "OK",
}


def audit_entry(entry, all_terms, name_lookup, industry):
    """Returns (severity, violations_list) for one entry."""
    violations = []
    violations.extend(detect_dangling(entry, all_terms, name_lookup))
    violations.extend(detect_self_link(entry, all_terms))
    violations.extend(detect_canonical_drift(entry, name_lookup))
    violations.extend(detect_inflected_forms(entry, all_terms, name_lookup))
    violations.extend(detect_semantic_risk(entry, all_terms, name_lookup, industry))
    if not violations:
        return 99, []
    worst = min(RANK_FOR[v["kind"]] for v in violations)
    return worst, violations


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("industry", nargs="?", choices=sorted(INDUSTRY_PATHS),
                   help="Industry to audit. Omit when using --all or --cross-industry-only.")
    p.add_argument("--all", action="store_true",
                   help="Audit all industries in sequence.")
    p.add_argument("--cross-industry-only", action="store_true",
                   help="Show only the cross-industry homonym table and exit.")
    p.add_argument("--top", type=int, default=None,
                   help="Show only the top N entries by severity.")
    p.add_argument("--letter", type=str, default=None,
                   help="Filter to a single letter (e.g. 'B').")
    p.add_argument("--csv", action="store_true",
                   help="Emit CSV instead of human-readable text.")
    p.add_argument("--include-clean", action="store_true",
                   help="Also list entries with no violations.")
    p.add_argument("--repeated-threshold", type=int, default=3,
                   help="Minimum corpus-wide occurrences for repeated-dangling check (default 3).")
    args = p.parse_args()

    if args.cross_industry_only:
        _print_cross_industry()
        return

    if args.all and args.industry:
        sys.exit("Pass either an industry name OR --all, not both.")
    if not args.all and not args.industry:
        sys.exit("Specify an industry, --all, or --cross-industry-only.")

    if args.all:
        for industry in sorted(INDUSTRY_PATHS):
            if INDUSTRY_PATHS[industry].exists():
                args.industry = industry
                _run_one(args)
        _print_cross_industry()
        return
    _run_one(args)


def _print_cross_industry():
    shared = cross_industry_homonyms()
    if not shared:
        print("\n=== CROSS-INDUSTRY HOMONYMS ===\nNone.")
        return
    print(f"\n=== CROSS-INDUSTRY HOMONYMS ({len(shared)}) ===")
    print(f"{'Term':<40} Industries")
    print(f"{'-' * 40} {'-' * 30}")
    for name in sorted(shared):
        print(f"{name:<40} {', '.join(shared[name])}")


def _run_one(args):
    terms = load_terms(args.industry)
    name_lookup = {t["term"]: t for t in terms}

    # Density pass — used both for per-entry zero/high checks and the summary.
    densities = {t["term"]: link_density(t, terms) for t in terms}

    # Homonym-shadow is global (scans whole industry once).
    shadow_violations = detect_homonym_shadow(terms)
    shadow_by_term = defaultdict(list)
    for v in shadow_violations:
        shadow_by_term[v["term"]].append({"kind": v["kind"], "msg": v["msg"]})

    # Repeated-dangling is corpus-wide. One report per phrase, attached to the
    # entry where it first appears.
    repeated_by_term = aggregate_repeated_dangling(terms, name_lookup,
                                                   threshold=args.repeated_threshold)

    rows = []
    for t in terms:
        if args.letter and t["letter"] != args.letter.upper():
            continue
        severity, violations = audit_entry(t, terms, name_lookup, args.industry)
        # Add homonym-shadow if present.
        if shadow_by_term.get(t["term"]):
            violations.extend(shadow_by_term[t["term"]])
            severity = min(severity, RANK_FOR["homonym-shadow"])
        # Add repeated-dangling if this entry is the first occurrence of any.
        if repeated_by_term.get(t["term"]):
            violations.extend(repeated_by_term[t["term"]])
            severity = min(severity, RANK_FOR["repeated-dangling"])
        # Density buckets.
        d = densities[t["term"]]
        if d >= HIGH_DENSITY_THRESHOLD:
            violations.append({"kind": "high-density",
                               "msg": f"{d} live links (threshold {HIGH_DENSITY_THRESHOLD})"})
            severity = min(severity, RANK_FOR["high-density"])
        if d == 0:
            violations.append({"kind": "zero-link",
                               "msg": "no terms in this entry's body would auto-link"})
            severity = min(severity, RANK_FOR["zero-link"])
        if severity == 99 and not args.include_clean:
            continue
        rows.append({
            "term": t["term"],
            "letter": t["letter"],
            "severity": severity,
            "violations": violations,
            "density": d,
            "category": t.get("category", ""),
        })

    rows.sort(key=lambda r: (r["severity"], r["term"]))

    if args.top:
        rows = rows[: args.top]

    total = len(terms)
    total_links = sum(densities.values())
    avg = total_links / total if total else 0
    zero_n = sum(1 for d in densities.values() if d == 0)
    high_n = sum(1 for d in densities.values() if d >= HIGH_DENSITY_THRESHOLD)

    if args.csv:
        print("severity,letter,term,density,category,kind,violation")
        for r in rows:
            for v in r["violations"] or [{"kind": "ok", "msg": "ok"}]:
                msg = v["msg"].replace('"', '""')
                print(f"{r['severity']},{r['letter']},\"{r['term']}\","
                      f"{r['density']},\"{r['category']}\",{v['kind']},\"{msg}\"")
        return

    print(f"\n=== Hyperlink audit — {args.industry.upper()} ===")
    print(f"Entries: {total}    Live links: {total_links}    Avg/entry: {avg:.2f}")
    print(f"Zero-link entries: {zero_n}    High-density (>={HIGH_DENSITY_THRESHOLD}): {high_n}")
    print(f"Showing: {len(rows)} entries needing review\n")

    current_sev = None
    for r in rows:
        if r["severity"] != current_sev:
            current_sev = r["severity"]
            print(f"\n--- {SEV_LABEL[current_sev]} ---")
        density_tag = f" [{r['density']}]" if r["density"] else " [0]"
        print(f"  [{r['letter']}] {r['term']}{density_tag}")
        for v in r["violations"]:
            print(f"        • {v['msg']}")


if __name__ == "__main__":
    main()
