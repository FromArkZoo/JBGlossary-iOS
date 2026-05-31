"""Idempotently merge US insurance terms into Targets/Insurance/Resources/glossary_insurance.json.

Mirrors scripts/add_real_estate_terms.py — append-only, case-insensitive dedup
against existing terms, sort by (letter asc, term asc) on write. Each batch is a
Python list built via the entry() helper.

Voice: plain English for a generalist (policyholder, patient choosing a health
plan, new homeowner, small-business owner, journalist). Snappy ~18–30 words,
must make sense WITHOUT prior domain knowledge. Detail 40–80 words with a
concrete anchor (a typical policy, a common claim, a federal program, a market
mechanic) and a "where you'd hear it" beat.

Authoring rules — read docs/CLARITY_POLICY.md and docs/CONTENT_STYLE_GUIDE.md
before adding entries. Critical rules to remember:
  Rule 4  — wrong-context auto-links. Insurance is unusually homonym-heavy:
            watch "agent", "policy", "claim", "interest", "premium", "rate",
            "title", "carrier", "rider", "loss", "principal", "trust", "risk",
            "limit" in prose. Rephrase when the everyday sense is meant.
  Rule 4b — do NOT inline-expand acronyms in prose (NAIC, ERISA, COBRA, NFIP);
            the entry's `full` field already shows the expansion in the UI.
  Rule 5  — avoid possessives ("insurer's", "insured's") + gerund/past tense in
            prose if a linkable alternative exists.
  Rule 6  — if a proper noun appears 3+ times corpus-wide without an entry,
            it almost certainly needs one — author it.

Usage:
    python3 scripts/add_insurance_terms.py
    python3 scripts/add_insurance_terms.py --batches 1     # specific batch
    python3 scripts/add_insurance_terms.py --dry-run       # preview only
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

GLOSSARY = Path(__file__).parent.parent / "Targets" / "Insurance" / "Resources" / "glossary_insurance.json"

# Keep in sync with Sources/Industries/InsuranceBrand.swift `lenses[].kind`
# category lists, and with scripts/audit_hyperlinks.py CATEGORY_CLUSTERS.
# Nine categories in three clusters (policyholder / risk / market).
VALID_CATEGORIES = {
    # policyholder cluster
    "Coverage & Policies",
    "Claims & Settlement",
    "Law & Liability",
    "Health & Benefits",
    # risk cluster
    "Underwriting & Risk",
    "Pricing & Actuarial",
    "Reinsurance & Risk Transfer",
    # market cluster
    "Regulation & Solvency",
    "Distribution & Markets",
}

# Multi-select line of business. Keep in sync with the indications filter.
VALID_INDICATIONS = {
    "Life & Annuities",
    "Health",
    "Auto",
    "Home & Property",
    "Commercial & Liability",
    "Reinsurance",
    "Cross-sector",
}


def entry(term, full, plain, snappy, detail, sources,
          indications=None, category="Coverage & Policies", aliases=None):
    assert category in VALID_CATEGORIES, f"Unknown category '{category}' for term '{term}'"
    indications = indications or ["Cross-sector"]
    for ind in indications:
        assert ind in VALID_INDICATIONS, f"Unknown indication '{ind}' for term '{term}'"
    out = {
        "letter": term[0].upper(),
        "term": term,
        "full": full,
        "plain": plain,
        "snappy": snappy,
        "detail": detail,
        "indications": indications,
        "category": category,
        "sources": sources,
    }
    if aliases:
        out["aliases"] = aliases
    return out


# ============================================================================
# BATCH 1 — Core mechanics & policy anatomy (Coverage & Policies + the most-
# referenced foundational terms). These are the highest-frequency link targets
# the rest of the corpus points back to, so they're authored first.
# ============================================================================

BATCH_1_CORE = [
    entry(
        "Insurance", "",
        "A deal where many people pay small amounts into a shared pot so the unlucky few who suffer a big loss get paid from it.",
        "A contract that trades a small, certain payment — the premium — for protection against a large, uncertain loss.",
        "Insurance pools money from many policyholders so the few who suffer fires, crashes, illnesses, or deaths are paid from the common fund. You pay a premium; in exchange the insurer promises to cover specified losses up to a policy limit. It is the financial backbone behind mortgages, car keys, hospital visits, and business deals — every lender, landlord, or regulator who demands proof of coverage is relying on this bargain.",
        ["III", "NAIC"],
        indications=["Cross-sector"],
        category="Coverage & Policies",
    ),
    entry(
        "Policy", "",
        "The written contract that spells out exactly what your insurance covers, what it won't, and what you both must do.",
        "The legal contract between insurer and insured setting out coverage, limits, exclusions, conditions, and the premium owed.",
        "A policy is the rulebook for the whole relationship. It bundles the declarations page (your specifics), the insuring agreement (the promise to pay), exclusions (the gaps), conditions (your duties), and definitions. When an adjuster says \"it's not covered,\" they are reading this document. Disputes over a denied claim almost always come down to a clause buried in the policy that one side read differently than the other.",
        ["III", "NAIC"],
        indications=["Cross-sector"],
        category="Coverage & Policies",
    ),
    entry(
        "Premium", "",
        "The price you pay — monthly or yearly — to keep your insurance switched on.",
        "The amount the policyholder pays the insurer for coverage, set by underwriting and actuarial pricing of the risk.",
        "Premium is the meter running on every policy. Insurers set it by estimating how likely you are to file a claim and how big it might be, then adding expenses and profit. Miss enough payments and the policy can lapse, leaving you uncovered. On an earnings call you'll hear insurers report \"gross written premium\" as the headline measure of how much business they wrote that year.",
        ["III", "NAIC"],
        indications=["Cross-sector"],
        category="Coverage & Policies",
    ),
    entry(
        "Deductible", "",
        "The slice of a loss you pay yourself before the insurer pays the rest.",
        "A fixed amount the insured absorbs on each claim before coverage kicks in; higher deductibles mean lower premiums.",
        "If your car repair costs $3,000 and your deductible is $500, you pay $500 and the insurer pays $2,500. It keeps small nuisance claims off the books and gives you a reason to drive carefully. Choosing a higher figure lowers your premium because you're shouldering more of the risk. Health, auto, and homeowners policies all use this tool, though health plans layer on coinsurance and copays too.",
        ["III", "NAIC"],
        indications=["Auto", "Home & Property", "Health"],
        category="Coverage & Policies",
    ),
    entry(
        "Coverage", "",
        "The protection your policy actually provides — the specific losses it promises to pay for.",
        "The scope of protection a policy grants: which perils, people, and property it pays for, up to stated limits.",
        "Coverage is what you're buying. A homeowners policy might pay for fire and theft but not flood; an auto policy splits protection into liability, collision, and comprehensive. Agents talk about \"gaps in coverage\" when a real-world loss falls outside every section of the policy. Reading which coverages you have — and at what limit — is the difference between a paid claim and an unpleasant surprise.",
        ["III", "NAIC"],
        indications=["Cross-sector"],
        category="Coverage & Policies",
    ),
    entry(
        "Claim", "",
        "A formal request asking your insurer to pay for a loss the policy covers.",
        "A demand by the insured (or a third party) for payment under the policy after a covered loss occurs.",
        "Filing a claim starts the payout process: you report the loss, an adjuster investigates, and the insurer pays, partly pays, or denies. Filing too many makes your premium rise or renewal harder. The word also means the eventual cost an insurer bears: \"claims came in higher than expected this quarter\" is the line that sinks an insurance stock when catastrophes strike.",
        ["III", "NAIC"],
        indications=["Cross-sector"],
        category="Claims & Settlement",
    ),
    entry(
        "Insurer", "Insurance Carrier",
        "The company that takes your premium and promises to pay your covered losses.",
        "The company that accepts the risk, collects premiums, and pays claims; also called the carrier or underwriter.",
        "The insurer is the party on the hook. It pools your premium with thousands of others, invests the float, and pays out when covered losses hit. Regulators watch its solvency closely because a failed insurer leaves policyholders stranded. You'll hear it called the \"carrier\" in agent-speak, and a single large risk may be split among several carriers, each taking a layer.",
        ["NAIC", "AM Best"],
        indications=["Cross-sector"],
        category="Distribution & Markets",
        aliases=["Carrier"],
    ),
    entry(
        "Insured", "",
        "The person or business the policy protects — usually you.",
        "The person or entity whose interests a policy protects and who is entitled to file claims under it.",
        "The insured is who the coverage is for. On a homeowners policy it's the homeowner; on a commercial policy it might be a company plus its officers. The named insured (the one listed on the declarations page) has the most rights and duties, while additional insureds get a narrower slice. When a policy says \"the insured must cooperate,\" it means you must help the adjuster investigate the claim.",
        ["III", "NAIC"],
        indications=["Cross-sector"],
        category="Coverage & Policies",
    ),
    entry(
        "Policyholder", "",
        "The person who owns the insurance policy and pays the premiums.",
        "The party who owns the contract, pays the premium, and holds the rights to renew, cancel, or change it.",
        "Policyholder and insured often describe the same person, but not always — a company can be the policyholder of a group life plan covering its employees, who are the insureds. In a mutual insurer the policyholders are also the owners and may receive dividends. When commentators talk about \"policyholder-friendly\" states, they mean places where regulation tilts toward consumers in disputes over claims and rates.",
        ["NAIC", "III"],
        indications=["Cross-sector"],
        category="Coverage & Policies",
    ),
    entry(
        "Named Insured", "",
        "The exact person or business written on the front page of the policy, with the fullest rights.",
        "The party explicitly listed on the declarations page, holding the broadest coverage and the core duties under the policy.",
        "Being the named insured matters when a claim is contested. This party can make changes, receives notices, and enjoys coverage that may not extend to everyone in the household or company. Spouses, resident relatives, or subsidiaries may be covered automatically or only as added parties. Commercial policies often debate who should be the named insured versus an additional insured, because the distinction decides who controls the claim.",
        ["NAIC", "Cornell LII"],
        indications=["Cross-sector"],
        category="Coverage & Policies",
    ),
    entry(
        "Additional Insured", "",
        "Someone added to your policy so they're protected too — often a landlord or business partner who demands it.",
        "A party other than the named insured granted coverage under the policy, usually by endorsement to satisfy a contract.",
        "Landlords, lenders, and clients routinely require that they be named on a tenant's or contractor's liability policy, so that it responds if they're sued over the work. The status is added by endorsement and usually doesn't raise the limit — the added party shares the coverage of the named insured. Construction contracts live and die on whether this language was drafted correctly.",
        ["NAIC", "Cornell LII"],
        indications=["Commercial & Liability"],
        category="Coverage & Policies",
    ),
    entry(
        "Beneficiary", "",
        "The person who collects the money when a life insurance policy pays out.",
        "The person or entity designated to receive the proceeds of a life insurance policy or annuity when the insured dies.",
        "You name a beneficiary when you buy life insurance — a spouse, child, trust, or charity. Primary beneficiaries get paid first; contingent ones inherit only if the primary has died. Keeping the designation current is critical: proceeds go to whoever is named on the form, not whoever a will lists, which is why divorces and remarriages trigger so many disputed payouts. The named beneficiary generally takes the money free of income tax.",
        ["III", "Investopedia"],
        indications=["Life & Annuities"],
        category="Coverage & Policies",
    ),
    entry(
        "Claimant", "",
        "Whoever is asking the insurer to pay — you, or the person you injured.",
        "The party making a claim for payment, whether the policyholder (first-party) or an injured outsider (third-party).",
        "In a first-party claim the claimant is the insured asking their own carrier to pay, as when you report a stolen laptop. In a third-party claim the claimant is the outsider you harmed — the driver you rear-ended files against your liability coverage. Adjusters separate the two because their duties differ: they owe good faith to their own insured, and only fair dealing to a third-party claimant.",
        ["NAIC", "Cornell LII"],
        indications=["Cross-sector"],
        category="Claims & Settlement",
    ),
    entry(
        "Policy Limit", "Limit of Liability",
        "The most your insurer will pay for a covered loss, no matter how big the actual bill.",
        "The maximum the insurer will pay under a coverage, per claim or in aggregate; losses above it fall back on the insured.",
        "If your liability limit is $300,000 and a court awards $500,000, you personally owe the $200,000 gap — the reason people buy umbrella insurance to stack a higher limit on top. Limits come in flavours: per-occurrence caps each event, while an aggregate limit caps the total a policy pays over its term. Choosing limits is the single biggest lever on both your premium and your protection.",
        ["III", "NAIC"],
        indications=["Cross-sector"],
        category="Coverage & Policies",
        aliases=["Limit"],
    ),
    entry(
        "Sublimit", "",
        "A smaller cap inside your policy that limits payment for one specific kind of loss.",
        "A cap below the overall policy limit applying to a particular category of loss, such as jewellery or water damage.",
        "Your homeowners policy might carry a $300,000 limit overall but a $1,500 sublimit on jewellery, so a stolen engagement ring is barely covered. Sublimits hide in the fine print and surprise people at claim time. To restore full value you schedule the item — listing it specifically for an extra premium. Commercial policies use sublimits heavily for floods, earthquakes, and cyber losses.",
        ["III", "NAIC"],
        indications=["Home & Property", "Commercial & Liability"],
        category="Coverage & Policies",
    ),
    entry(
        "Coinsurance", "",
        "The share of a covered bill you keep paying even after the deductible — often a percentage.",
        "A cost-sharing percentage the insured pays after the deductible; in property, a clause penalising under-insurance.",
        "In health insurance, 20% coinsurance means after your deductible you pay a fifth of each bill until you hit the out-of-pocket maximum. In property insurance the word means something different: a coinsurance clause requires you to insure a building to a set percentage of its value (often 80%) or the insurer pays only part of even a small loss. Same word, two traps for the unwary.",
        ["CMS", "III"],
        indications=["Health", "Home & Property"],
        category="Coverage & Policies",
    ),
    entry(
        "Copay", "Copayment",
        "A flat fee — say $25 — you hand over at the doctor or pharmacy, with insurance covering the rest.",
        "A fixed dollar amount the insured pays for a covered health service, separate from the deductible and coinsurance.",
        "A $30 copay for a primary-care visit or $10 for a generic drug is predictable, which is why plans use copays for routine care — you know the cost before you walk in. Copays may or may not count toward your deductible, but they do count toward the out-of-pocket maximum. You'll see them printed on your insurance card next to the network type so the front desk knows what to collect.",
        ["CMS", "III"],
        indications=["Health"],
        category="Health & Benefits",
    ),
    entry(
        "Out-of-Pocket Maximum", "",
        "The yearly ceiling on what you can be forced to spend before insurance pays everything.",
        "The annual cap on a member's combined deductible, copays, and coinsurance; beyond it the health plan pays 100%.",
        "Once your spending on covered, in-network care hits the out-of-pocket maximum, the plan pays the full cost of everything else that year. It's the real measure of financial protection a health plan offers — far more than the premium or deductible alone. The Affordable Care Act caps how high it can go. Hit it after a major surgery and the rest of the year's covered care costs you nothing.",
        ["CMS", "III"],
        indications=["Health"],
        category="Health & Benefits",
    ),
    entry(
        "Exclusion", "",
        "A loss your policy specifically refuses to cover, listed in black and white.",
        "A clause carving a peril, property, or circumstance out of coverage; the first place an adjuster looks to deny a claim.",
        "Every policy has exclusions — flood and earthquake on a standard homeowners policy, intentional acts, war, normal wear and tear. They exist to keep premiums affordable and to push uninsurable or specialist risks into separate policies. When a claim is denied, the denial letter cites the exclusion by number. Knowing yours is how you discover you need a flood policy or a separate rider before the loss, not after.",
        ["III", "NAIC"],
        indications=["Cross-sector"],
        category="Coverage & Policies",
    ),
    entry(
        "Endorsement", "Policy Endorsement",
        "An add-on that changes your policy — adding, removing, or tweaking what's covered.",
        "A written amendment to a policy that adds, restricts, or modifies coverage; also called a rider in life and health.",
        "Add a home office, schedule a wedding ring, or buy back flood coverage and the insurer issues an endorsement that becomes part of the contract. It can expand coverage or quietly cut it, so reading the change at renewal matters. Standardised industry forms mean the same numbered amendment carries identical wording across many carriers, which is why agents quote them by code.",
        ["NAIC", "Verisk"],
        indications=["Cross-sector"],
        category="Coverage & Policies",
        aliases=["Endorsements"],
    ),
    entry(
        "Rider", "",
        "An optional extra you bolt onto a life or health policy to widen what it covers.",
        "An add-on to a life or health policy that adds a benefit or coverage, the life-and-health cousin of an endorsement.",
        "A waiver-of-premium rider keeps your life policy in force if you become disabled; a child rider covers your kids; an accelerated death benefit rider lets a terminally ill insured tap the payout early. They let one base policy be tailored without buying a whole new contract, each adding a little premium. In property and casualty the same idea is called an endorsement.",
        ["III", "Investopedia"],
        indications=["Life & Annuities", "Health"],
        category="Coverage & Policies",
    ),
    entry(
        "Declarations Page", "Dec Page",
        "The front page of your policy listing who's covered, for what, and for how much.",
        "The summary page of the policy stating the named insured, coverages, limits, deductibles, premium, and policy period.",
        "The declarations page — \"the dec page\" — is the cheat sheet agents pull up first. It personalises the standard policy form with your name, address, vehicle or building, the coverages you bought, their limits and deductibles, and the premium. A lender asking for \"proof of insurance\" usually wants this page. If a fact here is wrong, the policy may not respond the way you expect when you file a claim.",
        ["NAIC", "III"],
        indications=["Cross-sector"],
        category="Coverage & Policies",
        aliases=["Declarations"],
    ),
    entry(
        "Insuring Agreement", "",
        "The core promise of the policy — the sentence where the insurer says what it will pay for.",
        "The section of a policy stating the central promise of the insurer to pay for specified losses in exchange for premium.",
        "Everything else in the policy — exclusions, conditions, definitions — modifies this one promise. Broad insuring agreements (\"we cover all risks of direct physical loss\") start wide and then carve back through exclusions; narrow ones (\"we cover these named perils\") start small. Coverage lawyers read the insuring agreement first to see whether a loss even gets in the door before the exclusions are argued.",
        ["Cornell LII", "Verisk"],
        indications=["Cross-sector"],
        category="Coverage & Policies",
    ),
    entry(
        "Conditions", "",
        "The fine-print duties you must meet — like reporting a loss promptly — or the insurer can refuse to pay.",
        "Policy provisions setting out the duties and procedures the insured must follow for coverage to apply.",
        "Notify the insurer promptly, cooperate with the investigation, protect property from further damage, submit a proof of loss on time — these strings are attached to every grant of coverage. Break a material one and the insurer may deny an otherwise valid claim. This section is also where you find how disputes are resolved, how other insurance is coordinated, and the right of the insurer to inspect or audit.",
        ["Cornell LII", "NAIC"],
        indications=["Cross-sector"],
        category="Coverage & Policies",
    ),
    entry(
        "Policy Period", "Policy Term",
        "The window of time your coverage is active — usually six months or a year.",
        "The span between the effective and expiration dates of a policy during which covered losses are eligible for payment.",
        "A loss has to happen inside the policy period to be covered — or, for claims-made policies, be reported inside it. Auto policies often run six months, homeowners and commercial policies a year. The renewal that arrives before expiration starts a fresh period, sometimes at a new rate. Gaps between periods are dangerous: a single uninsured day can void a mortgage or leave a crash uncovered.",
        ["NAIC", "III"],
        indications=["Cross-sector"],
        category="Coverage & Policies",
        aliases=["Policy Term"],
    ),
    entry(
        "Effective Date", "",
        "The day your coverage switches on.",
        "The calendar date coverage under a policy begins; losses before it are not covered even if the premium is paid.",
        "Coverage doesn't exist until the effective date, which is why buyers time it to the moment they take the car keys or close on a house. Backdating is generally barred to stop people insuring a loss that already happened. Lenders and motor-vehicle offices check it against the purchase to be sure there was never an uninsured gap.",
        ["NAIC", "III"],
        indications=["Cross-sector"],
        category="Coverage & Policies",
    ),
    entry(
        "Expiration Date", "",
        "The day your coverage runs out unless you renew.",
        "The date coverage under a policy ends; without renewal or extension, the insured is bare from that moment on.",
        "Miss the expiration date without renewing and you're uninsured the next morning, even if you never meant to cancel. Carriers send renewal offers weeks ahead; ignoring them is the most common way people accidentally let coverage drop. Claims-made liability policies make the date doubly important because reporting a claim after expiration — without tail coverage — leaves old work unprotected.",
        ["NAIC", "III"],
        indications=["Cross-sector"],
        category="Coverage & Policies",
    ),
    entry(
        "Renewal", "",
        "Continuing your policy for another term, usually with an updated price.",
        "An offer from the insurer to continue coverage for a new policy period, often at a re-rated premium based on recent experience.",
        "Most personal policies renew automatically unless you or the insurer opts out. The renewal premium reflects a fresh look at your claims, credit-based insurance score, and market-wide rate changes — which is why a clean year can still bring an increase after a region's catastrophe losses. Reading the renewal, not just paying it, is how you catch coverage that was quietly trimmed or a deductible that crept up.",
        ["NAIC", "III"],
        indications=["Cross-sector"],
        category="Coverage & Policies",
    ),
    entry(
        "Nonrenewal", "",
        "When the insurer decides not to offer you another term at the end of this one.",
        "A decision by the insurer to end coverage at expiration rather than offer a renewal, distinct from mid-term cancellation.",
        "Nonrenewal isn't a cancellation — your current policy runs to its expiration date — but you must find a new carrier before it ends. Insurers nonrenew after too many claims, or when they pull out of a whole region, as many did from wildfire- and hurricane-exposed states. State law sets how much advance notice you're owed, giving you time to shop before going bare.",
        ["NAIC", "III"],
        indications=["Cross-sector"],
        category="Regulation & Solvency",
    ),
    entry(
        "Cancellation", "",
        "Ending a policy before its term is up — by you or the insurer.",
        "Termination of a policy before its expiration date, by the insured or, for limited reasons, by the insurer.",
        "You can usually cancel anytime and get back the unused premium. An insurer's power to cancel mid-term is tightly limited by state law — typically only for non-payment, fraud, or a big rise in the risk — because pulling coverage out from under someone is drastic. After a short initial window, most policies can't be cancelled for ordinary claims; the insurer must wait and nonrenew instead.",
        ["NAIC", "Cornell LII"],
        indications=["Cross-sector"],
        category="Coverage & Policies",
    ),
    entry(
        "Lapse", "",
        "Losing your coverage because you stopped paying the premium.",
        "Termination of a policy for non-payment of premium, leaving the insured uncovered until reinstatement or rebuy.",
        "Miss a premium past the grace period and the policy lapses — coverage stops, and a loss the next day isn't paid. A lapsed life policy can sometimes be reinstated by catching up payments and proving you're still healthy, but a lapse in auto coverage flags you as high-risk and raises your next premium. Lenders monitor for lapses and may force-place expensive coverage if yours drops.",
        ["III", "NAIC"],
        indications=["Life & Annuities", "Auto"],
        category="Coverage & Policies",
    ),
    entry(
        "Grace Period", "",
        "Extra days after a missed payment when your coverage still counts.",
        "A short window after the premium due date during which coverage continues and a late payment keeps the policy alive.",
        "Life insurance typically grants a 30- or 31-day grace period; if the insured dies during it, the insurer pays the benefit minus the owed premium. Health and other policies have their own grace windows, lengthened for subsidised marketplace plans. The grace period is the safety net between a missed payment and a full lapse — pay inside it and nothing is lost.",
        ["CMS", "III"],
        indications=["Life & Annuities", "Health"],
        category="Coverage & Policies",
    ),
    entry(
        "Reinstatement", "",
        "Bringing a lapsed policy back to life by catching up and, sometimes, re-proving you qualify.",
        "Restoring a lapsed policy to active status, usually by paying overdue premium and meeting the requirements of the insurer.",
        "After a life policy lapses, reinstatement may require back premiums plus interest and fresh evidence of insurability — a health questionnaire or exam — because your health may have changed. There's usually a time limit, often three to five years. Reinstating is generally cheaper than buying a new policy at your now-older age, so it's worth doing if you can still qualify.",
        ["III", "Investopedia"],
        indications=["Life & Annuities"],
        category="Coverage & Policies",
    ),
    entry(
        "Binder", "",
        "Temporary proof you're covered right now, before the full policy paperwork arrives.",
        "A short-term agreement providing immediate coverage while the formal policy is being written and issued.",
        "When you buy a car at noon, the agent issues a binder so you can legally drive it home before the printed policy exists. A binder carries the same coverage as the policy it stands in for, but only for a set period — often 30 to 90 days — until the real document is issued or declined. Lenders accept a binder as proof of insurance at a closing.",
        ["NAIC", "III"],
        indications=["Auto", "Home & Property"],
        category="Coverage & Policies",
    ),
    entry(
        "Quote", "",
        "An estimated price for a policy, based on the details you give the insurer.",
        "A non-binding estimate from the insurer of the premium for a described risk, subject to underwriting before it becomes a policy.",
        "You give an insurer your age, address, car, or health details and it returns a quote — the likely premium. Quotes are estimates: the final price can change once underwriting verifies the facts and pulls your records. Comparing quotes across carriers is the core of shopping for insurance, but matching the coverages and limits behind each number matters more than the headline price.",
        ["III", "NAIC"],
        indications=["Cross-sector"],
        category="Distribution & Markets",
    ),
    entry(
        "Application", "",
        "The form where you tell the insurer about yourself so it can decide whether and how to cover you.",
        "The form on which a prospective insured discloses the facts underwriters use to accept, price, or decline the risk.",
        "The application is the foundation of utmost good faith: answer honestly, because a material misrepresentation here can let the insurer rescind the policy and refuse a claim later. Underwriters lean on it to classify the risk and set the premium. For life and disability cover the application may trigger a medical exam and a check of prescription and claims databases before an offer is made.",
        ["NAIC", "Cornell LII"],
        indications=["Cross-sector"],
        category="Underwriting & Risk",
    ),
    entry(
        "Indemnity", "",
        "The core idea that insurance restores you to where you were before the loss — no better, no worse.",
        "The principle that insurance compensates actual loss to make the insured whole, without allowing a profit from misfortune.",
        "Indemnity is why a claim pays the depreciated value of a five-year-old roof, not the cost of a brand-new house. It stops insurance becoming a betting slip: you can't collect more than you lost, and insurable interest plus the indemnity principle keep people from profiting on a loss. Life insurance is the great exception — a life has no market value, so those policies pay a fixed agreed sum instead.",
        ["Cornell LII", "III"],
        indications=["Cross-sector"],
        category="Law & Liability",
    ),
    entry(
        "Insurable Interest", "",
        "The requirement that you'd actually suffer if the insured thing were lost — you can't insure a stranger's car.",
        "A stake in the insured person or property such that its loss would cause the policyholder genuine financial harm.",
        "Insurable interest stops insurance becoming gambling: you can insure your own house, your spouse's life, or your business partner, but not a celebrity you've never met. In property cover the interest must exist at the time of loss; in life insurance, at the time the policy is bought. Courts void policies sold without it, a rule that traces back centuries to stamp out wagering on strangers' deaths.",
        ["Cornell LII", "III"],
        indications=["Cross-sector"],
        category="Law & Liability",
    ),
    entry(
        "Utmost Good Faith", "Uberrimae Fidei",
        "The duty of both sides to deal honestly and hide nothing important when an insurance contract is made.",
        "The doctrine that insurer and insured must each disclose all material facts honestly when forming the contract.",
        "Insurance leans on this higher duty of candour because the insured knows facts the insurer can't easily check — your health, your driving, the wiring in your warehouse. Conceal or misstate something material and the insurer may rescind the policy. The doctrine also binds the insurer to deal fairly, the seed of the bad-faith claims that punish carriers who deny coverage without reason.",
        ["Cornell LII", "Lloyd's"],
        indications=["Cross-sector"],
        category="Law & Liability",
    ),
    entry(
        "Material Misrepresentation", "",
        "A false answer big enough that, had the insurer known the truth, it would have charged more or said no.",
        "An untrue statement on an application important enough to have changed the decision of the insurer to cover or price the risk.",
        "Forget to mention a speeding ticket and it may not matter; hide a heart condition on a life application and the insurer can rescind the policy and deny the death claim. The test is materiality — whether the truth would have changed the underwriting decision. Insurers must usually act within a contestability window, after which even a misstatement can no longer undo the policy.",
        ["Cornell LII", "NAIC"],
        indications=["Cross-sector"],
        category="Law & Liability",
    ),
    entry(
        "Rescission", "",
        "The insurer unwinding a policy as if it never existed, usually because the application lied.",
        "Cancelling a policy from inception for material misrepresentation or concealment, returning premium and denying claims.",
        "Rescission is the nuclear option: the insurer voids the contract back to day one, refunds the premiums, and treats every claim as uncovered. It's reserved for material misrepresentation or fraud on the application and is hardest to use after the contestability period closes. Health insurers were largely barred from rescinding coverage over honest mistakes by the Affordable Care Act, curbing a once-common practice after big claims.",
        ["Cornell LII", "CMS"],
        indications=["Cross-sector"],
        category="Law & Liability",
    ),
    entry(
        "Subrogation", "",
        "After paying your claim, the insurer steps into your shoes to chase whoever actually caused the loss.",
        "The right of the insurer, after paying a claim, to pursue the third party responsible and recover what it paid out.",
        "If another driver totals your car, your insurer may pay you and then subrogate — sue or bill the at-fault driver's insurer to get its money back. Successful subrogation can return your deductible to you. The principle stops the wrongdoer escaping just because you had insurance, and it keeps you from collecting twice. Health insurers subrogate too, clawing back from accident settlements they helped fund.",
        ["Cornell LII", "III"],
        indications=["Cross-sector"],
        category="Claims & Settlement",
    ),
    entry(
        "Salvage", "",
        "What's left of the damaged property after a claim — which the insurer can sell to recoup some of the payout.",
        "The remaining value of property the insurer pays for in full, which it may take and sell to offset the loss.",
        "When an insurer declares a crashed car a total loss and pays its value, it takes the wreck and sells it for salvage, often to a rebuilder or parts yard. The recovery offsets the claim cost. A salvage title then warns future buyers the car was once written off. The same idea applies to fire-damaged inventory or a sunk boat the insurer paid out and now owns.",
        ["III", "NAIC"],
        indications=["Auto", "Home & Property"],
        category="Claims & Settlement",
    ),
    entry(
        "Loss", "",
        "The damage, injury, or cost that triggers a claim.",
        "The harm an insurance policy responds to — damage, injury, liability, or death — measured in dollars for settlement.",
        "Loss is the event insurance exists to soften: a kitchen fire, a fender-bender, a hospital stay, a lawsuit. Insurers track \"incurred losses\" — what claims will ultimately cost — against the premium they collected, the ratio that decides whether a line of business makes money. A \"total loss\" means the damage exceeds the property's value, so the insurer pays the value rather than repairing.",
        ["NAIC", "III"],
        indications=["Cross-sector"],
        category="Claims & Settlement",
    ),
    entry(
        "Occurrence", "",
        "A single covered event — like one accident — that the policy treats as one loss.",
        "An event, or series of related events, that causes covered loss and counts as one incident against the policy limit.",
        "How you count occurrences decides how much coverage you have. One car crash injuring three people is usually one occurrence, capped by the per-occurrence limit; a chemical leak over months might be one occurrence or many, a distinction litigated for millions. Liability policies pair a per-occurrence limit with a larger aggregate limit so a string of separate events can't blow through the year's coverage at once.",
        ["Cornell LII", "Verisk"],
        indications=["Commercial & Liability"],
        category="Coverage & Policies",
    ),
    entry(
        "Occurrence Policy", "",
        "Liability cover that pays for any harm that happened while the policy was active — even if the claim comes years later.",
        "A liability policy that responds to injury or damage taking place during its term, no matter when the claim is filed.",
        "Buy an occurrence policy for 2024 and it covers an injury caused in 2024 even if the lawsuit lands in 2030 — the trigger is when the harm happened, not when the claim arrives. That makes old policies valuable forever and removes the need for tail coverage. It's the opposite of a claims-made policy, and it's why contractors and manufacturers prize occurrence forms for long-tail risks.",
        ["Verisk", "Cornell LII"],
        indications=["Commercial & Liability"],
        category="Coverage & Policies",
    ),
    entry(
        "Claims-Made Policy", "",
        "Liability cover that only pays if the claim is reported while the policy is active.",
        "A liability policy that responds only to claims first made and reported during its term, often with a retroactive date.",
        "Doctors and professionals usually carry claims-made coverage: it's cheaper at first but the trigger is when the claim is filed, not when the mistake happened. Let the policy end and an old error becomes uninsured unless you buy tail coverage. A retroactive date sets how far back covered acts can reach. Switching carriers requires careful handling so no period falls through the gap.",
        ["Verisk", "Cornell LII"],
        indications=["Commercial & Liability"],
        category="Coverage & Policies",
        aliases=["Claims-Made"],
    ),
    entry(
        "Retroactive Date", "",
        "On claims-made cover, the earliest date a mistake can have happened and still be covered.",
        "The cut-off date on a claims-made policy before which wrongful acts are not covered, even if the claim is timely.",
        "A claims-made policy with a retroactive date of 2019 won't cover a mistake made in 2018, no matter when the claim arrives. Keeping the same retroactive date when you renew or switch carriers preserves coverage for your whole career; resetting it forward creates a dangerous gap. Buyers of professional liability watch this date as closely as the limit itself.",
        ["Verisk", "Cornell LII"],
        indications=["Commercial & Liability"],
        category="Coverage & Policies",
    ),
    entry(
        "Tail Coverage", "Extended Reporting Period",
        "An extension that lets you report old claims after a claims-made policy ends.",
        "An extended reporting period on a claims-made policy that covers claims filed after expiration for prior covered acts.",
        "When a doctor retires or switches insurers, tail coverage keeps the old claims-made policy responsive to lawsuits that surface later over past treatment. Without it, every patient encounter becomes uninsured the day the policy lapses. The tail can be costly — often a multiple of the annual premium — but for long-tail professions it's the difference between a clean exit and lingering personal exposure.",
        ["Verisk", "III"],
        indications=["Commercial & Liability"],
        category="Coverage & Policies",
    ),
    entry(
        "First-Party Coverage", "",
        "Insurance that pays you for your own losses.",
        "Coverage that pays the insured directly for their own damage or loss, as opposed to liability owed to outsiders.",
        "Collision coverage that fixes your own car, the dwelling coverage that rebuilds your own house, the health plan that pays your own hospital bill — these are first-party. The insurer owes its own policyholder a duty of good faith in handling them. First-party claims contrast with third-party liability claims, where the policy pays someone else you harmed.",
        ["Cornell LII", "III"],
        indications=["Cross-sector"],
        category="Coverage & Policies",
    ),
    entry(
        "Third-Party Coverage", "",
        "Insurance that pays other people for harm you caused them.",
        "Liability coverage that pays outsiders the insured is legally responsible for injuring or whose property they damaged.",
        "When you rear-end another driver, your liability coverage is third-party — it pays the other driver, not you. The injured outsider is the third party (you and the insurer are the first two). These policies also pay to defend you against the resulting lawsuit. The insurer's duty to a third-party claimant is fair dealing, a notch below the good faith it owes its own insured.",
        ["Cornell LII", "III"],
        indications=["Commercial & Liability", "Auto"],
        category="Law & Liability",
    ),
    entry(
        "Peril", "",
        "The specific cause of a loss — fire, theft, a windstorm, a crash.",
        "A cause of loss a policy may cover or exclude, such as fire, theft, wind, water, or collision.",
        "Perils are the dangers themselves; coverage is defined by which ones the policy names. A named-perils policy lists exactly what's covered — fire, lightning, hail — and nothing else. An open-perils or all-risk form flips it, covering every cause except those excluded. Flood and earthquake are the famous ones standard homeowners policies leave out, sold instead through separate programs.",
        ["III", "Verisk"],
        indications=["Home & Property", "Cross-sector"],
        category="Coverage & Policies",
    ),
    entry(
        "Hazard", "",
        "A condition that makes a loss more likely or worse — a frayed wire, an icy step, a smoker's habit.",
        "A condition that increases the chance or severity of a loss from a peril; underwriters grade physical, moral, and morale hazards.",
        "If fire is the peril, the stacked oily rags in the basement are the hazard. Underwriters sort the kinds: physical ones are tangible (bald tyres, old wiring), moral ones are dishonest motives (insuring a failing business hoping it burns), and morale ones are carelessness born of having coverage. Spotting them lets insurers price, exclude, or require fixes before they'll write the risk.",
        ["III", "SOA"],
        indications=["Cross-sector"],
        category="Underwriting & Risk",
    ),
    entry(
        "Risk", "",
        "The chance that something bad and costly happens — the thing insurance exists to manage.",
        "The uncertainty of loss that insurance prices and transfers; in industry slang, also the policy or exposure itself.",
        "Risk is the raw material of insurance. Actuaries measure it, underwriters select and price it, and reinsurers spread it. The word does double duty: \"this risk\" can mean a specific policy or building an underwriter is evaluating. Pooling many independent risks makes the average loss predictable even though any single one isn't — the statistical magic that lets the whole industry function.",
        ["SOA", "III"],
        indications=["Cross-sector"],
        category="Underwriting & Risk",
    ),
    entry(
        "Exposure", "",
        "How much potential loss an insurer is on the hook for — the size of the bet it took.",
        "The measure of potential loss an insurer carries, by policy, peril, or region; the base on which premium is calculated.",
        "An insurer measures hurricane exposure as the total it could pay if one storm hit every coastal home it covers. The word also names the rating base — payroll for workers' comp, sales for product liability, square footage for a building — that scales the premium. Managing accumulated exposure in one zip code or one peril is why carriers buy reinsurance and cap how much they'll write in a single area.",
        ["SOA", "Verisk"],
        indications=["Cross-sector"],
        category="Underwriting & Risk",
    ),
    entry(
        "Actual Cash Value", "ACV",
        "What damaged property was worth at the moment it was lost — its replacement cost minus wear and tear.",
        "A settlement basis equal to replacement cost minus depreciation, paying what the property was actually worth when lost.",
        "Total your ten-year-old roof and an actual cash value policy pays for a ten-year-old roof, not a new one — replacement cost less depreciation. It's cheaper to buy but leaves a gap you cover out of pocket. Many homeowners later wish they'd paid more for replacement cost coverage, especially on roofs, where insurers increasingly impose actual cash value to limit their payouts.",
        ["III", "NAIC"],
        indications=["Home & Property", "Auto"],
        category="Claims & Settlement",
        aliases=["ACV"],
    ),
    entry(
        "Replacement Cost", "",
        "Enough money to buy a brand-new equivalent of what you lost, with no deduction for age.",
        "A settlement basis paying the full cost to repair or replace damaged property with new, without deducting depreciation.",
        "Replacement cost coverage rebuilds your roof or repays your stolen TV at today's price for a new one, unlike actual cash value which docks for age. Insurers often pay the depreciated amount first and release the rest once you actually replace the item, to keep the indemnity principle honest. It costs more in premium but spares you the depreciation gap after a major loss.",
        ["III", "NAIC"],
        indications=["Home & Property"],
        category="Claims & Settlement",
    ),
    entry(
        "Depreciation", "",
        "The drop in an item's value as it ages and wears — subtracted when a policy pays actual cash value.",
        "The decline in property value from age, wear, and obsolescence, deducted from replacement cost to reach actual cash value.",
        "A claims adjuster paying actual cash value depreciates your loss: a sofa half through its useful life is paid at roughly half its new price. The recoverable portion is what a replacement-cost policy holds back and releases once you rebuild. Arguments over how fast a roof or appliance wears are among the most common sticking points in property claims.",
        ["III", "NAIC"],
        indications=["Home & Property", "Auto"],
        category="Claims & Settlement",
    ),
    entry(
        "Proof of Loss", "",
        "The sworn statement of what you lost and what it was worth, filed to back up a claim.",
        "A formal, often sworn, statement the insured submits documenting the loss and its value to support a claim payment.",
        "After a fire or theft the insurer asks for a proof of loss — an itemised, signed account of what was damaged and its value, with receipts or photos. It must usually be filed within a set number of days, a condition that can sink a late claim. Adjusters use it to verify the claim; a knowingly inflated proof of loss is insurance fraud.",
        ["NAIC", "Cornell LII"],
        indications=["Cross-sector"],
        category="Claims & Settlement",
    ),
    entry(
        "Duty to Defend", "",
        "The promise by your insurer to hire and pay lawyers to fight a covered lawsuit against you.",
        "A liability insurer's obligation to provide and fund a legal defence for claims that potentially fall within coverage.",
        "The duty to defend is broader than the duty to pay: an insurer must defend a lawsuit if any allegation might be covered, even if it later proves it owes nothing. Defence costs often dwarf the eventual settlement, so this promise is a big part of a liability policy's value. Refuse to defend wrongly and the insurer risks a bad-faith judgment far above the policy limit.",
        ["Cornell LII", "III"],
        indications=["Commercial & Liability"],
        category="Law & Liability",
    ),
    entry(
        "Bad Faith", "",
        "When an insurer treats you unfairly — denying or dragging out a valid claim — and can be punished for it.",
        "Unreasonable handling of a claim or defence by an insurer, exposing it to damages beyond the policy limit.",
        "Insurers owe their policyholders good faith and fair dealing. Deny a clearly covered claim, lowball a settlement, or refuse to defend without grounds and the insured can sue for bad faith, recovering not just the claim but extra-contractual and sometimes punitive damages. The threat keeps carriers honest and is why a reasonable but wrong denial is defensible while an arbitrary one is dangerous.",
        ["Cornell LII", "NAIC"],
        indications=["Cross-sector"],
        category="Law & Liability",
    ),
    entry(
        "Aggregate Limit", "",
        "The total an insurer will pay over the whole policy term, across all claims combined.",
        "The maximum a policy pays for all covered losses during its term, separate from the per-occurrence limit on each event.",
        "A general liability policy might carry a $1 million per-occurrence limit and a $2 million aggregate: any one claim is capped at a million, and once total payouts reach two million the policy is exhausted for the year. A string of claims can burn through the aggregate and leave you bare before renewal. Knowing how much aggregate is left is vital when a second loss follows a first.",
        ["Verisk", "III"],
        indications=["Commercial & Liability"],
        category="Coverage & Policies",
    ),
    entry(
        "Self-Insured Retention", "SIR",
        "A chunk of each loss a business pays itself before its liability policy responds — like a big deductible.",
        "An amount the insured pays out of pocket on each claim before the liability policy attaches, common in commercial cover.",
        "Larger companies take a self-insured retention to lower premiums and keep control of small claims: they handle and pay losses up to, say, $250,000, and the insurer only steps in above that. Unlike a deductible, the insured usually manages the claim within the retention itself. It's a halfway house between buying full coverage and self-insuring entirely, and it signals an insurer that the buyer has skin in the game.",
        ["Verisk", "III"],
        indications=["Commercial & Liability"],
        category="Coverage & Policies",
        aliases=["SIR"],
    ),
    entry(
        "Umbrella Insurance", "",
        "Extra liability coverage that sits on top of your home and auto policies for catastrophic claims.",
        "A policy adding a layer of liability limit above auto, home, or business coverage, plus some broader protection.",
        "When a lawsuit blows past your auto or homeowners liability limit, an umbrella policy picks up the next million or more — cheap protection for high-net-worth families and landlords. It also fills some gaps the underlying policies exclude. Umbrellas require you to carry minimum underlying limits first, then attach above them. The name fits: one policy spreads over several others to catch the rare, ruinous claim.",
        ["III", "NAIC"],
        indications=["Home & Property", "Auto", "Commercial & Liability"],
        category="Coverage & Policies",
        aliases=["Umbrella Policy"],
    ),
    entry(
        "Excess Insurance", "",
        "Coverage that only pays after an underlying policy limit is used up.",
        "A policy that responds above a stated attachment point, paying only once the underlying coverage is exhausted.",
        "A factory needing $50 million of liability cover stacks layers: a primary policy to $5 million, then excess policies for each band above. Each excess insurer pays only when the layer beneath is spent, so its premium is lower per dollar of limit. Towers of excess insurance are how big risks get covered when no single carrier wants the whole exposure.",
        ["Verisk", "III"],
        indications=["Commercial & Liability"],
        category="Coverage & Policies",
    ),
    entry(
        "Primary Insurance", "",
        "The first policy to pay a loss, before any excess or umbrella coverage gets involved.",
        "The coverage that responds first to a loss, paying from the first dollar above any deductible up to its own limit.",
        "In a tower of coverage the primary policy sits at the bottom and pays first; only when its limit is exhausted do excess and umbrella layers attach. Primary insurers also usually carry the duty to defend. When two policies could cover the same loss, \"other insurance\" clauses decide which is primary and which is excess — a fight that surfaces constantly in auto and commercial claims.",
        ["Verisk", "III"],
        indications=["Commercial & Liability", "Auto"],
        category="Coverage & Policies",
    ),
    entry(
        "Earned Premium", "",
        "The slice of premium an insurer has truly earned because that part of the coverage period has already passed.",
        "The portion of a prepaid premium an insurer has earned as time elapses, recognised as revenue over the policy period.",
        "Pay $1,200 for a year of cover and after one month the insurer has earned $100; the other $1,100 is unearned premium it would refund if you cancelled. Insurers report earned premium as revenue and measure their loss ratio against it. The distinction matters at cancellation and in accounting, where booking premium before it's earned overstates how well a carrier is really doing.",
        ["NAIC", "SOA"],
        indications=["Cross-sector"],
        category="Pricing & Actuarial",
    ),
    entry(
        "Unearned Premium", "",
        "The part of premium you've paid for coverage that hasn't happened yet — refundable if you cancel early.",
        "The prepaid premium covering the remaining policy period, held as a liability and refundable on cancellation.",
        "If you cancel a six-month auto policy after two months, the four months of unearned premium come back to you, minus any short-rate penalty. Insurers must hold unearned premium as a reserve — a liability on the balance sheet — because they still owe that coverage. Regulators watch the unearned premium reserve to be sure a carrier can deliver the protection it has already been paid for.",
        ["NAIC", "SOA"],
        indications=["Cross-sector"],
        category="Pricing & Actuarial",
    ),
    entry(
        "Pro Rata", "",
        "Splitting a premium or refund exactly in proportion to the time used — no penalty.",
        "Allocation of premium or refund strictly by the share of the policy period elapsed, with no extra charge.",
        "Cancel a policy and a pro rata refund returns the unearned premium based purely on days remaining — fair and proportional. Insurers use pro rata cancellation when they end the policy, but may use short rate, which keeps a little extra, when you cancel. The phrase also describes how two insurers covering the same loss split it in proportion to their limits.",
        ["NAIC", "III"],
        indications=["Cross-sector"],
        category="Pricing & Actuarial",
    ),
]


BATCHES = {
    1: BATCH_1_CORE,
}


def merge(batches_to_run, dry_run=False):
    existing = json.loads(GLOSSARY.read_text())
    existing_names = {t["term"].lower() for t in existing}

    new_entries = []
    for n in batches_to_run:
        batch = BATCHES.get(n)
        if batch is None:
            print(f"warning: batch {n} not found, skipping")
            continue
        for e in batch:
            key = e["term"].lower()
            if key in existing_names:
                print(f"skip: {e['term']} already exists")
                continue
            new_entries.append(e)
            existing_names.add(key)

    if dry_run:
        print(f"would merge {len(new_entries)} new entries; total would be {len(existing) + len(new_entries)}")
        return

    combined = existing + new_entries
    combined.sort(key=lambda t: (t["letter"], t["term"].lower()))
    GLOSSARY.write_text(json.dumps(combined, ensure_ascii=False, indent=2) + "\n")
    print(f"merged {len(new_entries)} new entries; total {len(combined)}")


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--batches", default=",".join(str(n) for n in BATCHES),
                   help="comma-separated batch numbers to run (default: all)")
    p.add_argument("--dry-run", action="store_true", help="preview without writing")
    return p.parse_args()


if __name__ == "__main__":
    args = parse_args()
    nums = [int(x) for x in args.batches.split(",") if x.strip()]
    merge(nums, dry_run=args.dry_run)
