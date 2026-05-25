"""Idempotently merge US real-estate terms into Targets/RealEstate/Resources/glossary_realEstate.json.

Mirrors scripts/add_law_terms.py and scripts/add_finance_terms.py — append-only,
case-insensitive dedup against existing terms, sort by (letter asc, term asc) on
write. Each batch is a Python list built via the entry() helper.

Voice: plain English for a generalist (renter, homebuyer, novice investor,
journalist, business owner). Snappy ~12 words, must make sense WITHOUT prior
domain knowledge. Detail 40–80 words with a concrete anchor (typical deal,
common contract clause, federal program, common law concept).

Authoring rules — read docs/CLARITY_POLICY.md before adding entries.
Critical rules to remember:
  Rule 4 — wrong-context auto-links: watch "agent", "title", "trust",
           "interest", "lot", "rate", "principal" in prose.
  Rule 4b — do NOT inline-expand acronyms in prose (USPAP, RESPA, TILA, etc.);
            the entry's `full` field already shows the expansion in the UI.
  Rule 5  — avoid possessives ("Lender's", "Buyer's") + gerund/past tense in
            prose if a linkable alternative exists.
  Rule 6  — if a proper noun appears 3+ times corpus-wide without an entry,
            it almost certainly needs one — author it.

Usage:
    python scripts/add_real_estate_terms.py
    python scripts/add_real_estate_terms.py --batches 1     # specific batch
    python scripts/add_real_estate_terms.py --dry-run       # preview only
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

GLOSSARY = Path(__file__).parent.parent / "Targets" / "RealEstate" / "Resources" / "glossary_realEstate.json"

# Keep in sync with Sources/Industries/RealEstateBrand.swift `lenses[].kind`
# category lists. Leasing is declared but no entries exist yet — adding here.
VALID_CATEGORIES = {
    "Property Types",
    "Financing & Lending",
    "Transactions",
    "Valuation & Appraisal",
    "Law & Regulation",
    "Title & Ownership",
    "Development",
    "Leasing",
    "Management & Operations",
    "Tax",
    "Market & Investment",
}

# Free-form labels currently in use across the Real Estate corpus.
VALID_INDICATIONS = {
    "Residential", "Multifamily", "Commercial", "Industrial", "Hospitality",
    "Land", "Specialty", "Affordable", "Public Sector", "Cross-sector",
    "Development", "Investment",
}


def entry(term, full, plain, snappy, detail, sources, indications=None, category="Transactions"):
    assert category in VALID_CATEGORIES, f"Unknown category '{category}' for term '{term}'"
    indications = indications or ["Residential"]
    for ind in indications:
        assert ind in VALID_INDICATIONS, f"Unknown indication '{ind}' for term '{term}'"
    return {
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


# ============================================================================
# BATCH 1 — Foundational basics + top dangling targets (50 terms)
#
# Targets the Basics-allowlist holes in RealEstateBrand.swift (Real Property,
# Personal Property, Fixture, Inspection, Lease, Landlord, Tenant, Rent,
# Sublease, Easement, Encumbrance, Joint Tenancy, Tenancy in Common, Warranty
# Deed, Fee Simple, Adverse Possession, Zoning, IRR, REIT, 1031 Exchange...)
# plus the highest-frequency dangling-link targets surfaced by
# `audit_hyperlinks.py --repeated-threshold 3` (Interest 13x, Trust 7x, Lot 6x,
# Multifamily 4x, LLC, TILA, RESPA, FICO, Settlement Statement, Good Faith
# Estimate).
# ============================================================================

BATCH_1_FOUNDATIONS = [
    # --- Title & Ownership: foundational property concepts -------------------
    entry(
        "Real Property", "",
        "The Land itself plus anything permanently attached — buildings, fences, the bedrock under your feet.",
        "Land and everything permanently affixed to it — the legal opposite of Personal Property.",
        "Real property covers Land, structures, and Fixtures bolted into the land. It is the bundle of rights that gets conveyed by Deed, taxed via Property Tax, and recorded in the county registry. Movable items the seller takes when leaving (furniture, free-standing appliances) are Personal Property, not real property. Purchase contracts spell out which items count as Fixtures and travel with the sale.",
        ["Cornell LII", "Investopedia"],
        indications=["Residential", "Commercial", "Cross-sector"],
        category="Title & Ownership",
    ),
    entry(
        "Personal Property", "Chattel",
        "Anything you own that isn't Real Property — your furniture, your car, the curtains you can unscrew and take.",
        "Movable property not permanently attached to Land — historically called chattel.",
        "Personal property is everything the homeowner can carry away without removing screws or breaking plaster. Free-standing appliances, furniture, art, drapes hung on rods that simply lift off. The line between personal property and a Fixture decides countless purchase-contract disputes — typical tests look at attachment method, intent, and whether removal causes damage. Mortgages don't usually cover personal property; secured loans on movables follow Article 9 of the UCC instead.",
        ["Cornell LII", "Investopedia"],
        indications=["Residential", "Commercial", "Cross-sector"],
        category="Title & Ownership",
    ),
    entry(
        "Fixture", "",
        "An item once Personal Property that's been so attached to a building it now counts as part of the Real Property.",
        "Personal Property that's been affixed to Real Property and now travels with it.",
        "A ceiling fan was personal property in the box at the hardware store. Once wired into the joists, courts treat it as a fixture — it stays with the house when sold. Common disputes: chandeliers, built-in bookshelves, mounted televisions, washer/dryer hookups. Three-part test: method of attachment, adaptation to the property, intent at the time of installation. Purchase contracts list specific items to exclude (often the kitchen refrigerator) or include to avoid post-Closing arguments.",
        ["Cornell LII", "NAR"],
        indications=["Residential", "Commercial"],
        category="Title & Ownership",
    ),
    entry(
        "Fee Simple", "Fee Simple Absolute",
        "The most complete form of ownership — you can use the Land, sell it, leave it to heirs, with no time limit.",
        "Absolute ownership of Real Property with no time limit and full transfer rights.",
        "Fee simple is the default form of US Real Property ownership. The holder can occupy, sell, mortgage, lease, or devise the property without expiration. Restrictions still apply: Zoning, Property Tax, Easements, CC&Rs, and Eminent Domain all bind a fee simple owner. Compare leasehold (a tenant under a Lease has possession but not ownership) and life estate (ownership ends at the holder's death). Almost all single-family homes in the US are sold fee simple.",
        ["Cornell LII", "Investopedia"],
        indications=["Residential", "Commercial", "Cross-sector"],
        category="Title & Ownership",
    ),
    entry(
        "Joint Tenancy", "Joint Tenancy with Right of Survivorship",
        "Two or more owners hold equal shares — and when one dies, the survivors automatically inherit that share without Probate.",
        "Co-ownership with right of survivorship — share passes to co-owners on death, skipping probate.",
        "Joint tenancy requires the 'four unities': equal time of acquisition, identical Deed, equal share, equal possession. The defining feature is survivorship — at death the deceased's interest evaporates and is absorbed by the surviving joint tenants. Common among spouses (though many states use Tenancy by the Entirety for spouses with stronger creditor protection). Selling or mortgaging a share can break the joint tenancy and convert it into Tenancy in Common.",
        ["Cornell LII", "Investopedia"],
        indications=["Residential", "Cross-sector"],
        category="Title & Ownership",
    ),
    entry(
        "Tenancy in Common", "TIC",
        "Two or more owners hold the property together — but each share passes to the owner's heirs at death, not to the co-owners.",
        "Co-ownership where each share is independently inheritable and transferable.",
        "Tenancy in common is the default form when a Deed conveys to multiple buyers without specifying Joint Tenancy. Shares can be unequal (60/40, 70/30) and each owner can sell or will their interest independently. Common in investment partnerships and unmarried co-buyers. No survivorship — a deceased owner's share goes through Probate to heirs, who become new co-tenants. Co-tenants share rights to possess the whole property, regardless of percentage ownership.",
        ["Cornell LII", "Investopedia"],
        indications=["Residential", "Commercial", "Investment"],
        category="Title & Ownership",
    ),
    entry(
        "Adverse Possession", "",
        "A doctrine letting someone who openly occupies another's Land for years eventually claim legal ownership.",
        "Acquiring Title to Real Property through long, open, hostile possession.",
        "The squatter's law. Requirements vary by state but generally need possession that is open and notorious, continuous, exclusive, hostile (without permission), and lasting for a statutory period (typically 5–20 years). The classic case: a fence built three feet over the property line, undisturbed for the statute. Some states require payment of Property Tax during the period. Once perfected, adverse possession ripens into legal Title and is typically confirmed by a Quiet Title action.",
        ["Cornell LII", "Investopedia"],
        indications=["Residential", "Cross-sector"],
        category="Title & Ownership",
    ),
    entry(
        "Warranty Deed", "General Warranty Deed",
        "A Deed where the seller promises clean Title — and stays on the hook if any defect surfaces later.",
        "Deed conveying property with full Title warranties — seller liable for any prior defect.",
        "The strongest Deed in residential transactions. The grantor promises six common-law covenants: seisin (owns what's being conveyed), right to convey, against encumbrances, quiet enjoyment, warranty (defend against claims), and further assurances. Liability extends back through all prior owners, not just the grantor. A defect from 1950 can still make today's grantor pay. Title Insurance backs the practical risk; the warranty deed is the legal promise. Compare Quitclaim Deed — which conveys whatever interest the grantor has, with no guarantee.",
        ["Cornell LII", "ALTA"],
        indications=["Residential", "Commercial"],
        category="Title & Ownership",
    ),
    entry(
        "Easement", "",
        "A right to use part of someone else's Land for a specific purpose — like a shared driveway or a utility line.",
        "Limited right to use another party's Real Property for a defined purpose.",
        "Easements run with the Land — they bind future owners, not just the current one. Common types: utility easements (power, water, sewer), access easements (driveways crossing a neighbour's Lot), conservation easements (restricting development). Created by Deed, prescription (long use, like Adverse Possession), or necessity (landlocked parcels). Title Insurance and Inspections should surface recorded easements; unrecorded prescriptive easements are a litigation risk. A holder who oversteps the scope becomes a trespasser.",
        ["Cornell LII", "ALTA"],
        indications=["Residential", "Commercial", "Cross-sector"],
        category="Title & Ownership",
    ),
    entry(
        "Encumbrance", "",
        "Any legal claim or restriction on a property that limits what the owner can do — a Mortgage, Lien, Easement, or use restriction.",
        "Any third-party claim or restriction on Real Property that limits the owner's rights.",
        "Encumbrances split into financial claims (Mortgage, Lien) and use restrictions (Easement, CC&Rs, lease, Zoning overlays). Title searches and Title Insurance focus on disclosing all recorded encumbrances before Closing. Not every encumbrance kills a deal — buyers expect to take property subject to utility easements and CC&Rs. But undisclosed encumbrances (an old judgment Lien from a prior owner) are the kind of defect Title Insurance is built to cover. Sellers warrant the property free of undisclosed encumbrances in a Warranty Deed.",
        ["Cornell LII", "ALTA"],
        indications=["Residential", "Commercial", "Cross-sector"],
        category="Title & Ownership",
    ),
    entry(
        "Encroachment", "",
        "When a structure or improvement crosses the property line onto a neighbour's Land — a fence, an overhanging eave, an extending driveway.",
        "Physical intrusion of a structure or improvement onto neighbouring property.",
        "An encroachment is a survey problem with legal teeth. Even a few inches can complicate Title Insurance, frustrate Sale, or — left long enough — ripen into Adverse Possession against the original owner. Common culprits: fences built without surveys, additions extending past setbacks, roof overhangs, driveways. Discovered through a current Survey (often required by Lenders). Remedies: removal, monetary settlement, granting an Easement to legalise the encroachment, or buying the affected strip of Land.",
        ["Cornell LII", "ALTA"],
        indications=["Residential", "Commercial"],
        category="Title & Ownership",
    ),
    entry(
        "Trust", "",
        "A legal arrangement where one party holds property for another's benefit — common for estate planning, asset protection, and lending.",
        "Legal arrangement where a trustee holds property for the benefit of beneficiaries.",
        "In real estate, trusts appear in three main flavours. (1) Living trust — homeowners retitle Real Property into a revocable trust to skip Probate at death. (2) Land trust — used to mask ownership in public records (popular in Illinois, Florida). (3) Deed of Trust — a financing instrument used in roughly half the states instead of a Mortgage, with a trustee holding Title until the loan is paid. Trusts also hold property in REITs, in Title Insurance escrows, and inside complex syndication structures.",
        ["Cornell LII", "IRS"],
        indications=["Residential", "Commercial", "Investment", "Cross-sector"],
        category="Title & Ownership",
    ),
    entry(
        "LLC", "Limited Liability Company",
        "A flexible business entity that lets investors own property together while shielding personal assets from lawsuits.",
        "Pass-through entity combining corporate liability shield with partnership-style taxation.",
        "The default vehicle for holding investment Real Property. Owners are 'members'; profits pass through to personal tax returns unless the LLC elects corporate treatment. Liability is contained to the LLC's assets — a slip-and-fall judgment against the property can't usually reach the member's other holdings. Each property is often held in a separate single-purpose LLC to wall off risk. Lenders frequently require personal guarantees from members for smaller deals, partially eroding the shield. Annual filings and operating agreements add overhead small landlords sometimes skip.",
        ["IRS", "Cornell LII"],
        indications=["Residential", "Commercial", "Investment"],
        category="Title & Ownership",
    ),

    # --- Property Types: physical building blocks -----------------------------
    entry(
        "Lot", "",
        "A defined parcel of Land — usually a single building site with marked boundaries and a recorded Deed.",
        "An individual parcel of Land with surveyed boundaries.",
        "A lot is the basic unit of Land subdivision. Lots have a recorded plat map, dimensions, frontage, area, and a unique tax parcel number. Lot size and shape interact with Zoning to dictate what can be built: setbacks, lot coverage maximums, floor-area ratio, minimum lot size for the use. Corner lots, flag lots, and odd-shaped lots often face different rules. Developers buy raw acreage and subdivide it into lots before selling to builders or end buyers.",
        ["Investopedia", "NAHB"],
        indications=["Residential", "Land", "Development"],
        category="Property Types",
    ),
    entry(
        "Land", "",
        "The ground itself — a parcel without buildings, often bought for future Development, agriculture, or speculation.",
        "Unimproved ground sold as raw acreage or platted Lots.",
        "Raw land is the riskiest, lowest-cash-flowing slice of Real Property. No tenants, no income, but full carrying costs (Property Tax, insurance, debt service). Value depends on entitlements (Zoning, utilities, road access), future Development potential, and demographic growth. Land loans run shorter (5–10 years) and demand larger Down Payments (25–50%) than improved property. Categories: residential infill lots, recreational, timber, farmland, ranch, transitional (path-of-growth), urban redevelopment.",
        ["NAR", "USDA Rural Housing"],
        indications=["Land", "Development", "Investment"],
        category="Property Types",
    ),
    entry(
        "Multifamily", "",
        "A residential building with more than one separate dwelling unit — duplexes, apartment buildings, garden communities.",
        "Residential property with two or more dwelling units under one Title.",
        "Multifamily ranges from 2–4 unit small-rental properties (financeable as 'residential' with conventional 1–4 unit Mortgages) up to institutional apartment complexes of hundreds of units (financed commercially through Fannie Mae or Freddie Mac multifamily programs). The asset class is favoured for stable cash flow, scalable management, and inflation-tracking Rent growth. Subtypes: garden-style (low-rise, surface parking), mid-rise (4–7 stories), high-rise (8+), student housing, senior housing, affordable, market-rate.",
        ["Fannie Mae", "Freddie Mac", "NCREIF"],
        indications=["Multifamily", "Investment", "Affordable"],
        category="Property Types",
    ),
    entry(
        "Mixed-Use", "",
        "A building or development combining residential, retail, and sometimes office space — the apartment over the corner store.",
        "Single property combining residential and commercial uses, often by floor.",
        "Mixed-use comes in three flavours. Vertical mixed-use stacks uses by floor (street-level retail, residential above) — the typical urban mid-rise. Horizontal mixed-use spreads complementary uses across a single master-planned site. Live/work units blend the two within a single unit. Zoning increasingly favours mixed-use to support walkability and reduce car trips. Financing is more complex than single-use: Lenders look at separate operating proformas per use and may split debt by use to access cheaper Multifamily financing.",
        ["ULI", "NAHB"],
        indications=["Residential", "Commercial", "Development"],
        category="Property Types",
    ),

    # --- Financing & Lending: core mortgage mechanics -----------------------
    entry(
        "Interest", "",
        "The cost of borrowing money — paid by the borrower to the Lender, usually each month as part of the Mortgage payment.",
        "The lender's charge for the use of borrowed Principal.",
        "Interest is the price of money over time, calculated against the current outstanding Principal balance. Each Mortgage payment splits between Interest and Principal under an Amortization schedule — early payments are mostly Interest, late payments mostly Principal. Mortgage interest is deductible against federal income tax up to the cap set by the 2017 TCJA. The interest rate, the Index, the Margin, and any Rate Cap are the parameters that determine how much Interest is owed and when it can move.",
        ["IRS", "CFPB", "Federal Reserve"],
        indications=["Residential", "Commercial", "Cross-sector"],
        category="Financing & Lending",
    ),
    entry(
        "Loan-to-Value", "LTV",
        "How big the loan is compared to the property's value — a 90% LTV means borrowing 90% of the price.",
        "The loan amount expressed as a percentage of the property's Appraised Value.",
        "LTV is the headline risk metric in residential lending. Below 80% LTV, the borrower typically skips PMI. Above 80%, mortgage insurance is required on Conventional Loans. FHA Loans permit LTV up to 96.5%; VA Loans permit 100%; jumbo loans rarely exceed 90%. Commercial LTV ranges 50–75% depending on asset class and lender appetite. LTV is calculated against the lower of Sale Price or Appraised Value — a common surprise when an Appraisal comes in below the contract price.",
        ["CFPB", "Fannie Mae", "Freddie Mac"],
        indications=["Residential", "Commercial", "Cross-sector"],
        category="Financing & Lending",
    ),
    entry(
        "Debt-to-Income Ratio", "DTI",
        "How much of a borrower's monthly income goes to debt payments — Lenders use it to judge whether they can afford the Mortgage.",
        "Monthly debt obligations divided by gross monthly income, expressed as a percentage.",
        "Two DTI flavours matter to mortgage underwriting. Front-end DTI (housing ratio) compares Principal, Interest, Property Tax, Homeowners Insurance, and HOA fees against income — typical cap 28%. Back-end DTI adds all other debt (auto, student, credit card, child support) — typical cap 36–43%. Qualified Mortgage rules under the Dodd-Frank Act cap DTI at 43% for the safe harbour. Higher DTI sometimes clears with compensating factors (large Down Payment, high Credit Score, reserves).",
        ["CFPB", "Fannie Mae"],
        indications=["Residential"],
        category="Financing & Lending",
    ),
    entry(
        "HELOC", "Home Equity Line of Credit",
        "A revolving credit line secured by the home — borrow what you need, pay it down, borrow again, up to a set limit.",
        "Revolving credit line secured by the Equity in a primary residence.",
        "A HELOC has a draw period (usually 10 years) when the borrower pulls funds and pays interest-only on what's drawn. Then a repayment period (10–20 years) when no new draws are allowed and Principal amortises. Rates are usually variable, tied to the prime rate plus a Margin. Common uses: home improvements, debt consolidation, education, emergency reserves. Lender ratios typically permit combined-LTV up to 80–90% (first Mortgage + HELOC vs. Appraised Value). The home backs the debt — Default risks Foreclosure.",
        ["CFPB", "Federal Reserve"],
        indications=["Residential"],
        category="Financing & Lending",
    ),
    entry(
        "Hard Money", "Hard Money Loan",
        "A short-term, high-Interest loan from a private Lender — used by investors who need speed, not the best rate.",
        "Short-term, asset-based loan from a private lender at high Interest rates.",
        "Hard money lenders care about the property, not the borrower's W-2. Decisions in days, fund in weeks, with LTV typically capped at 65–75% of After-Repair Value (ARV). Rates run 8–15% with 2–4 points up front. Used by fix-and-flip investors, BRRRR strategists, and developers who need bridge financing while a project gets permitted or stabilised. Terms run 6–24 months. Bank takeouts replace hard money once the property is stabilised and qualifies for conventional financing.",
        ["Investopedia"],
        indications=["Investment", "Residential", "Commercial"],
        category="Financing & Lending",
    ),
    entry(
        "Loan Officer", "LO",
        "The person at a bank or Mortgage company who guides borrowers through the application — collects paperwork, quotes rates, submits to underwriting.",
        "Front-line lender employee who originates Mortgages and walks borrowers through application.",
        "Loan officers work for banks, credit unions, or mortgage banks and offer that institution's products. Compare a Mortgage Broker, who shops across many lenders. LO compensation is typically a basis-point payment on closed loans, regulated under Dodd-Frank to prevent steering borrowers toward higher-rate products. NMLS licensing required. The LO controls timing — clean files close in 30–45 days, sloppy ones drag to 60+. The relationship matters most when a deal needs an exception or a tight Closing date.",
        ["CFPB", "NAR"],
        indications=["Residential", "Commercial"],
        category="Financing & Lending",
    ),
    entry(
        "Mortgage Broker", "",
        "An independent middleman who shops a borrower's application across many Lenders to find the best rate and program.",
        "Independent intermediary placing borrowers with one of many wholesale lenders.",
        "Mortgage brokers do not lend their own money. They take an application, submit it to wholesale channels at multiple lenders, and place the loan where pricing and program fit best. Compensation comes from the lender (lender-paid) or borrower (borrower-paid), regulated under Dodd-Frank to prevent yield-spread kickbacks. Useful for borrowers who don't fit a single lender's box — self-employed, jumbo, foreign income, recent credit events. Loses the relationship advantage of working with a single Loan Officer at a portfolio lender.",
        ["CFPB", "NAR"],
        indications=["Residential", "Commercial"],
        category="Financing & Lending",
    ),
    entry(
        "FICO", "FICO Score",
        "The most widely used Credit Score in US lending — a number from 300 to 850 that summarises a borrower's credit history.",
        "Industry-standard Credit Score model used by most US mortgage lenders.",
        "FICO scores aggregate five factors: payment history (35%), amounts owed (30%), length of credit history (15%), new credit (10%), credit mix (10%). Mortgage underwriting typically pulls FICO from all three bureaus and uses the middle score for the highest-scoring borrower on the application. Conventional Loans usually need 620+; FHA Loans accept 580+ with 3.5% Down Payment, or 500+ with 10%; VA Loans have no statutory minimum but lender overlays often require 620. Higher scores unlock lower rates and lower PMI premiums.",
        ["CFPB", "Fannie Mae"],
        indications=["Residential"],
        category="Financing & Lending",
    ),
    entry(
        "Mortgage Note", "Promissory Note",
        "The legal IOU signed at Closing — the borrower's written promise to repay the Mortgage on agreed terms.",
        "Borrower's written promise to repay a Mortgage on stated terms.",
        "The mortgage note (the promise to pay) and the Mortgage or Deed of Trust (the security instrument) work as a pair at Closing. The note states the Principal, Interest rate, payment schedule, prepayment terms, and remedies on Default. The security instrument pledges the property as collateral and records in the public record. Notes are negotiable instruments — Lenders sell them on the secondary market to Fannie Mae, Freddie Mac, and private MBS issuers. The buyer (servicer) collects payments under the same note terms.",
        ["CFPB", "Cornell LII"],
        indications=["Residential", "Commercial"],
        category="Financing & Lending",
    ),
    entry(
        "Recourse Loan", "",
        "A loan where the Lender can chase the borrower's other assets — wages, savings, other property — if the collateral isn't enough to cover the debt after Foreclosure.",
        "Loan where the lender can pursue the borrower personally if the collateral falls short.",
        "Most US residential Mortgages are non-recourse in some states (California, Arizona) and recourse in others (Texas, Florida) — the state's anti-deficiency statutes decide. Commercial Real Estate loans default to recourse unless explicitly structured as non-recourse with limited 'bad-boy' carve-outs (fraud, bankruptcy filing, environmental issues). Investors often pay 25–50 basis points more for non-recourse to wall off personal assets. Recourse status changes behaviour in distress: non-recourse borrowers walk away more readily; recourse borrowers fight harder.",
        ["Cornell LII", "Investopedia"],
        indications=["Residential", "Commercial", "Investment"],
        category="Financing & Lending",
    ),
    entry(
        "Short Sale", "",
        "Selling a home for less than what's owed on the Mortgage, with the Lender agreeing to accept the shortfall instead of foreclosing.",
        "Sale of property for less than the outstanding Mortgage with lender approval.",
        "A short sale is the polite alternative to Foreclosure. The owner negotiates with the Lender to accept a Sale Price below the loan balance and forgive the deficiency. Approval takes weeks to months — the lender wants proof of hardship, valuation evidence, and a buyer at market price. Forgiven debt is typically taxable as income, though the Mortgage Forgiveness Debt Relief Act provided periodic exemptions during the post-2008 crisis. Credit impact is significant but less severe than a completed Foreclosure.",
        ["CFPB", "Fannie Mae"],
        indications=["Residential"],
        category="Financing & Lending",
    ),

    # --- Law & Regulation: consumer-protection regulatory regimes ---------
    entry(
        "TILA", "Truth in Lending Act",
        "A federal law making Lenders disclose the full cost of credit in standard form — APR, finance charges, payment schedule.",
        "Federal disclosure law standardising how Lenders quote the cost of credit.",
        "Enacted 1968, now living inside Regulation Z. TILA forces lenders to disclose APR, total finance charges, payment schedule, and right of rescission on standardised forms. Residential Mortgage disclosures fold into the TRID combined disclosure (Loan Estimate + Closing Disclosure) since 2015. Violations carry private rights of action: rescission within three years on refinances, statutory damages on disclosure errors. The CFPB administers and enforces TILA against bank and non-bank lenders.",
        ["CFPB", "Cornell LII"],
        indications=["Residential"],
        category="Law & Regulation",
    ),
    entry(
        "RESPA", "Real Estate Settlement Procedures Act",
        "A federal law regulating how settlement charges are disclosed and banning kickbacks between Lenders, title companies, and Agents.",
        "Federal law governing settlement disclosures and prohibiting referral kickbacks.",
        "Enacted 1974. RESPA forces standardised settlement-cost disclosure (now folded into the TRID Loan Estimate and Closing Disclosure since 2015), regulates Escrow accounts, and bans Section 8 kickbacks for referrals of settlement services. The line between marketing arrangements and illegal kickbacks remains the most litigated area — the CFPB has fined title companies, Lenders, and Agents tens of millions for violations. Borrowers also get a right to switch settlement providers and limits on Escrow over-collection.",
        ["CFPB", "HUD", "Cornell LII"],
        indications=["Residential"],
        category="Law & Regulation",
    ),
    entry(
        "Zoning", "",
        "The local-government rulebook that says what can be built where — residential here, commercial there, height limits everywhere.",
        "Municipal regulation dividing Land into use districts with specific building rules.",
        "Zoning sits at the intersection of local politics and property values. Ordinances divide a city into residential, commercial, industrial, and mixed-use districts, then layer in lot-size minimums, setbacks, height limits, floor-area ratios, and parking requirements. Variances and conditional-use permits handle case-by-case exceptions. State-level reform has been chipping at single-family-only zoning since 2019 (Oregon, California, Minnesota). Federal pre-emption is rare; the Fair Housing Act limits exclusionary zoning where it discriminates by protected class.",
        ["HUD", "Cornell LII"],
        indications=["Residential", "Commercial", "Development"],
        category="Law & Regulation",
    ),

    # --- Transactions: paper trail of buying & selling --------------------
    entry(
        "Inspection", "",
        "A buyer's visual examination of a property's condition — roof, foundation, plumbing, electrical, HVAC, pests — usually conducted by a licensed Inspector.",
        "Visual examination of property condition by a licensed Inspector during Due Diligence.",
        "Inspections happen after the offer is accepted, during the Due Diligence window. A general home inspection runs 2–4 hours and surfaces visible defects; specialty inspections (sewer scope, mold, radon, pest, foundation, roof) add focus. The report is the buyer's leverage to negotiate repairs, credits, or to walk away under the Inspection contingency. Inspections aren't an Appraisal — they assess condition, not value. New construction gets the same scrutiny; many serious defects only emerge after the first year of use.",
        ["NAR", "CFPB"],
        indications=["Residential", "Commercial"],
        category="Transactions",
    ),
    entry(
        "Realtor", "",
        "A real estate Agent who is a member of NAR and pledges to follow its Code of Ethics — not every Agent is a Realtor.",
        "Real estate Agent who belongs to the National Association of Realtors.",
        "NAR has roughly 1.5 million members nationwide. Membership requires adherence to a 17-article Code of Ethics enforced through state-level boards. The trademark distinguishes Realtors from the broader pool of licensed Agents — but state licensure, not NAR membership, is what legally permits practice. The 2024 Burnett v. NAR settlement restructured commission practices: buyer Agents can no longer be paid through MLS-listed cooperative commissions; Buyer Representation Agreements with explicit fees are now standard.",
        ["NAR"],
        indications=["Residential", "Commercial", "Cross-sector"],
        category="Transactions",
    ),
    entry(
        "Settlement Statement", "ALTA Settlement Statement",
        "A line-by-line tally of every dollar at Closing — who pays what to whom — given to both Buyer and Seller.",
        "Itemised list of all charges and credits at Closing for Buyer and Seller.",
        "Pre-TRID this was the HUD-1 statement, used for both residential and commercial. Since 2015, residential transactions use the Closing Disclosure; the ALTA Settlement Statement remains the standard for commercial deals and many investor purchases. The form shows Sale Price, Lender charges, title fees, recording fees, transfer taxes, Property Tax prorations, HOA prorations, and the final cash to close. Both sides sign at Closing. Discrepancies between Loan Estimate and final settlement statement above certain tolerances trigger TILA rescission rights.",
        ["CFPB", "ALTA"],
        indications=["Residential", "Commercial"],
        category="Transactions",
    ),
    entry(
        "Good Faith Estimate", "GFE",
        "The pre-TRID disclosure form giving borrowers an early estimate of Closing Costs — now replaced by the Loan Estimate for residential loans.",
        "Pre-2015 mortgage cost disclosure, replaced by the Loan Estimate under TRID.",
        "From 1974 (RESPA) until October 2015, lenders had to give a Good Faith Estimate within three business days of application — itemising every Closing Cost. The TRID rule consolidated GFE and the early TILA disclosure into the Loan Estimate. Commercial Real Estate loans, reverse mortgages, and certain home-equity loans still use GFE-style disclosures. The term remains common shorthand in industry conversation even though the form itself is retired for most residential business.",
        ["CFPB", "HUD"],
        indications=["Residential"],
        category="Transactions",
    ),

    # --- Leasing: rental basics ------------------------------------------
    entry(
        "Lease", "",
        "A written contract giving a Tenant the right to occupy a property for a set time in exchange for Rent.",
        "Contract conveying possession of property for a defined term in exchange for Rent.",
        "Leases bridge residential and commercial real estate but the conventions differ. Residential leases run 6–24 months, often on state-promulgated forms, with security deposits, Eviction procedures, and habitability warranties baked in by state Landlord-Tenant law. Commercial leases run 3–15+ years, are heavily negotiated, and shift many costs (Property Tax, insurance, maintenance) to the Tenant under NNN structures. The Lease binds successor owners — buying a leased property means stepping into the Landlord's shoes.",
        ["Cornell LII", "NAR"],
        indications=["Residential", "Commercial", "Multifamily"],
        category="Leasing",
    ),
    entry(
        "Landlord", "Lessor",
        "The owner who rents out a property to a Tenant — collects Rent, handles repairs, follows Landlord-Tenant law.",
        "Property owner who leases to a Tenant — also called the lessor.",
        "Landlord obligations vary sharply by state. All states recognise an implied warranty of habitability (safe, sanitary, weather-tight). Many require specific notice periods for entry, limits on Security Deposit, mandatory disclosure of lead paint (federal) and local conditions. Eviction processes are court-supervised — self-help (changing locks, removing belongings) is almost universally illegal. Commercial landlords have more contractual freedom; residential landlords face stricter consumer-protection rules and fair-housing scrutiny.",
        ["Cornell LII", "HUD"],
        indications=["Residential", "Commercial", "Multifamily"],
        category="Leasing",
    ),
    entry(
        "Tenant", "Lessee",
        "The person or business renting a property under a Lease — pays Rent, follows the rules, has the right to possess the space.",
        "Person or entity occupying leased property in exchange for Rent.",
        "Tenants get rights that pre-empt many private contract terms. The right to a habitable dwelling, quiet enjoyment, security-deposit protection, and proper Eviction procedure all flow from state and (in some cities) local statute. Commercial tenants have weaker statutory rights — they negotiate protections into the Lease. Subleases let a tenant transfer occupancy to a third party, usually with Landlord consent. Holdover tenants who stay past lease expiration become month-to-month or trigger Eviction depending on Landlord response.",
        ["Cornell LII", "HUD"],
        indications=["Residential", "Commercial", "Multifamily"],
        category="Leasing",
    ),
    entry(
        "Rent", "",
        "The regular payment a Tenant makes to the Landlord in exchange for using the property.",
        "Periodic payment from Tenant to Landlord under a Lease.",
        "Residential rent is usually paid monthly in advance. Commercial rent can be monthly or quarterly, often with annual escalations tied to CPI or fixed percentages. Late fees, NSF fees, and acceleration clauses appear in the Lease. Rent control laws cap residential rent increases in some cities (New York, San Francisco, Los Angeles) — usually with vacancy decontrol and tenant-protected categories. Commercial rent is typically quoted on a per-square-foot annual basis ($/SF/year) in the US.",
        ["Cornell LII", "HUD"],
        indications=["Residential", "Commercial", "Multifamily"],
        category="Leasing",
    ),
    entry(
        "Sublease", "",
        "When a Tenant rents the property out to someone else for part or all of the remaining Lease term.",
        "Tenant's rental of the leased premises to a third party for some or all of the term.",
        "The Tenant remains liable to the Landlord under the original Lease, while the subtenant pays the original Tenant. Most leases require Landlord consent for sublease, sometimes with reasonable-consent standards (especially commercial) or absolute discretion (typical residential). Assignment, by contrast, transfers the whole Lease — original Tenant exits entirely. Commercial sublease is common when companies downsize but face long remaining terms; rent gap (sublease rent below contract rent) is the original Tenant's loss to bear.",
        ["Cornell LII"],
        indications=["Residential", "Commercial"],
        category="Leasing",
    ),
    entry(
        "Security Deposit", "",
        "Money the Tenant pays upfront, held by the Landlord to cover damage or unpaid Rent at the end of the Lease.",
        "Upfront deposit held by Landlord to secure Tenant performance under the Lease.",
        "State statutes cap residential security deposits at 1–2 months of Rent and require return (with itemised deductions) within 14–60 days of move-out. Some states require the deposit to sit in an interest-bearing escrow account, with interest paid to the Tenant. Wrongful withholding triggers statutory damages — often 2–3x the deposit plus attorney's fees. Commercial deposits face fewer statutory constraints; landlords often demand letters of credit or guarantees in addition to or instead of cash deposits.",
        ["Cornell LII", "HUD"],
        indications=["Residential", "Multifamily"],
        category="Leasing",
    ),
    entry(
        "Holdover Tenant", "",
        "A Tenant who stays in the property after the Lease has ended — without a new agreement.",
        "Tenant remaining in possession after Lease expiration without a renewal.",
        "Landlords have two options. Accept Rent and treat the holdover as a month-to-month tenancy under the prior terms (most common). Refuse Rent and proceed with Eviction, often at penalty rent — many commercial leases set holdover Rent at 150–200% of the prior contract rate. Residential statutes vary by state on the conversion default. Holdover Tenants retain habitability protections and Eviction-procedure rights even though the original Lease has expired.",
        ["Cornell LII"],
        indications=["Residential", "Commercial"],
        category="Leasing",
    ),

    # --- Management & Operations: running an income property --------------
    entry(
        "Homeowners Insurance", "HO Insurance",
        "A homeowner's property and liability insurance — covers damage to the house, contents, and lawsuits for accidents on the property.",
        "Combined property and liability coverage for owner-occupied residential property.",
        "Required by virtually every Mortgage. Standard HO-3 policies cover the dwelling (replacement cost), other structures, personal property, loss of use, personal liability, and medical payments. Common exclusions: flood (requires NFIP or private flood policy), earthquake, normal wear, intentional acts. Premium drivers: location (wildfire, hurricane, hail), construction type, claims history, deductible. Coastal and wildfire states (Florida, California, Louisiana) face insurer pullbacks; carriers of last resort (Citizens, FAIR Plan) fill the gap at higher cost.",
        ["CFPB", "HUD"],
        indications=["Residential"],
        category="Management & Operations",
    ),
    entry(
        "Operating Expenses", "OpEx",
        "The recurring costs of running an income property — Property Tax, insurance, utilities, repairs, management, but not Mortgage payments.",
        "Recurring property costs subtracted from Gross Rental Income to compute NOI.",
        "Operating expenses split into fixed (Property Tax, insurance) and variable (utilities, repairs, management, payroll). They explicitly exclude debt service (Interest + Principal), capital expenditures (roof, HVAC replacement), depreciation, and income tax — those sit below the NOI line. Investors model operating expenses as a percentage of effective gross income; the 'OpEx ratio' typically runs 30–50% for stabilised Multifamily, 20–35% for industrial, higher for older properties or hospitality. Detailed line-item proformas are the bedrock of commercial underwriting.",
        ["NCREIF", "IREM"],
        indications=["Commercial", "Multifamily", "Investment"],
        category="Management & Operations",
    ),
    entry(
        "Gross Rental Income", "GRI",
        "The total Rent a property would collect if every unit were occupied at market rate — before any vacancies or expenses.",
        "Potential Rent at full occupancy and market rates, before vacancy and expenses.",
        "Gross rental income is the top line of the property income statement. Subtract vacancy and collection loss to get effective gross income. Then subtract Operating Expenses to get NOI. The gap between gross and effective is the property's economic occupancy — physical occupancy minus concessions, bad debt, and below-market leases. Underwriting models flag concession-driven vacancy as a value risk: a property running 95% physical occupancy but giving two months free per Lease has effective economic occupancy closer to 80%.",
        ["NCREIF", "IREM"],
        indications=["Multifamily", "Commercial", "Investment"],
        category="Management & Operations",
    ),

    # --- Market & Investment: return metrics ----------------------------
    entry(
        "IRR", "Internal Rate of Return",
        "The annualised return on a property investment, accounting for the timing of every cash flow in and out.",
        "Annualised return that makes the net present value of cash flows equal zero.",
        "IRR is the dominant return metric in Commercial Real Estate underwriting. Unlike Cap Rate (a snapshot of stabilised yield), IRR captures the full deal arc — Down Payment, ongoing distributions, capital expenditures, refinance proceeds, and Sale at exit. Levered IRR (after debt service) is what equity investors care about; unlevered IRR (before financing) lets analysts compare deals across capital structures. Multifamily value-add deals typically target 15–20% levered IRR over a 5–7 year hold; core deals target 8–12%.",
        ["NCREIF", "Investopedia"],
        indications=["Commercial", "Investment", "Multifamily"],
        category="Market & Investment",
    ),
    entry(
        "Equity Multiple", "EM",
        "How many times the investor gets their money back over the deal's life — a 2.0x equity multiple means doubling the original investment.",
        "Total distributions divided by total invested equity over the holding period.",
        "Equity multiple is IRR's plain-English cousin. It ignores timing — a 2.0x over five years and a 2.0x over fifteen years look identical on equity multiple but very different on IRR. Both metrics get reported side-by-side in syndication offering memos. Typical Multifamily value-add targets: 1.7–2.2x equity multiple alongside 15–20% IRR. Core deals target 1.4–1.7x at 8–12% IRR. The metric is intuitive to first-time investors who get confused by IRR's compounding math.",
        ["NCREIF", "Investopedia"],
        indications=["Commercial", "Investment", "Multifamily"],
        category="Market & Investment",
    ),
    entry(
        "REIT", "Real Estate Investment Trust",
        "A public or private company that owns income-producing Real Estate — investors buy shares like a stock and receive a slice of the Rent.",
        "Tax-advantaged entity that owns and operates income-producing property and distributes most earnings to shareholders.",
        "REITs pay no corporate income tax if they distribute at least 90% of taxable income to shareholders, hold at least 75% of assets in Real Estate, and earn at least 75% of income from rents or mortgage interest. Listed REITs trade on stock exchanges (Equinix, Simon, Prologis, AvalonBay). Non-traded and private REITs offer the same tax structure without daily liquidity. Subcategories: equity REITs (own buildings), mortgage REITs (own loans), hybrid. The structure dates to 1960, designed by Congress to democratise Real Estate Investment.",
        ["IRS", "Nareit", "SEC"],
        indications=["Investment", "Commercial", "Multifamily"],
        category="Market & Investment",
    ),

    # --- Tax: investment tax mechanics ---------------------------------
    entry(
        "1031 Exchange", "Like-Kind Exchange",
        "A tax move letting an investor sell one Real Estate property and buy another without immediately paying Capital Gain tax — if specific rules are followed.",
        "Tax-deferred swap of one investment property for another under IRC §1031.",
        "Section 1031 of the Internal Revenue Code defers federal Capital Gain on sale of investment Real Estate if proceeds reinvest into 'like-kind' Real Estate within tight timelines: 45 days to identify replacement property, 180 days to close. A Qualified Intermediary holds proceeds — the investor cannot touch the cash. Primary residences don't qualify; investment property does. Boot (unequal trade value, cash taken out, debt relief) is taxable. The 2017 TCJA restricted 1031 to Real Property only; personal property exchanges no longer qualify.",
        ["IRS", "Cornell LII"],
        indications=["Investment", "Commercial", "Multifamily"],
        category="Tax",
    ),
    entry(
        "Special Assessment", "",
        "A one-time charge on property owners — by a city or an HOA — for specific improvements like a new sewer line, sidewalk, or roof replacement.",
        "One-time charge for specific property improvements, levied by HOA or municipality.",
        "Municipal special assessments fund public improvements that benefit a defined district — sidewalks, sewer mains, sometimes lighting. They appear as a separate line on the Property Tax bill or as a private bond payment. HOA and Condo special assessments cover capital projects (roof, elevator, parking lot) that exceed the reserve fund. Buyers should ask for two years of HOA financials and minutes to see pending special assessments — an unfunded $30,000 roof can derail a deal. Disclosure is mandatory in most states.",
        ["NAR", "HUD"],
        indications=["Residential", "Multifamily"],
        category="Tax",
    ),
]


BATCHES = {
    1: BATCH_1_FOUNDATIONS,
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
