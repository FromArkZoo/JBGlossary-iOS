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


# ============================================================================
# BATCH 2 — Commercial / Investment depth + audit-surfaced gaps (50 terms)
#
# Closes the largest remaining gaps from batch 1 audit:
#   - High-frequency dangles: Dodd-Frank Act (5x), HVAC (3x), CMBS (2x),
#     TCJA (2x), BRRRR (2x), Survey, Title Search.
# Adds Commercial/Investment depth (NNN Lease, Waterfall, Promote, GP/LP,
# Going-in Cap Rate, Exit Cap, Pro Forma, Cap-Ex, EGI, Vacancy/Occupancy),
# Title & Ownership depth (Tenancy by the Entirety, Community Property,
# Lis Pendens, Plat, Metes and Bounds), Development & Zoning vocabulary
# (Variance, Conditional Use Permit, Nonconforming Use, Setback, FAR),
# Fair-housing regulatory regime (Fair Housing Act, Section 8, Redlining,
# Steering, ADA), Tax (Step-up in Basis, Bonus Depreciation), and three
# core property types (Office, Retail, Industrial).
# ============================================================================

BATCH_2_DEPTH = [
    # --- Audit-surfaced corpus gaps ----------------------------------------
    entry(
        "Dodd-Frank Act", "Dodd-Frank Wall Street Reform and Consumer Protection Act",
        "The 2010 financial-reform law that created the CFPB and overhauled Mortgage lending rules after the 2008 crisis.",
        "2010 financial-reform statute creating the CFPB and rewriting mortgage origination rules.",
        "Dodd-Frank tightened residential Mortgage lending after the 2008 collapse. Created the CFPB and gave it rule-writing authority. Imposed the ability-to-repay rule and the Qualified Mortgage safe harbour (DTI cap, no risky features). Restricted Loan Officer compensation to prevent steering. Created mandatory escrows for higher-priced loans. Imposed risk-retention on private MBS issuers. The statute is sprawling; most retail-side impact for Real Estate flows through CFPB regulations (TRID, Reg Z, Reg X).",
        ["CFPB", "Cornell LII"],
        indications=["Residential", "Cross-sector"],
        category="Law & Regulation",
    ),
    entry(
        "HVAC", "Heating, Ventilation, and Air Conditioning",
        "The building system that keeps a property warm, cool, and ventilated — usually the biggest single capital item in an Operating Expense budget.",
        "Heating, cooling, and air-handling equipment — the largest single capital line in most buildings.",
        "HVAC dominates Capital Expenditure budgets in stabilised assets. Residential systems (forced air, heat pumps, mini-splits) run $5,000-$25,000 to replace. Commercial rooftop units, chillers, and VAV systems run $200,000+ on a mid-sized office. Replacement cycles run 12-25 years. Energy efficiency standards have tightened (SEER ratings, refrigerant phase-outs from R-22 to R-410A to R-32) — older systems become costly to maintain as parts and refrigerant get scarce. Tenant Improvements often retrofit HVAC zoning.",
        ["NAHB", "IREM"],
        indications=["Residential", "Commercial", "Multifamily"],
        category="Management & Operations",
    ),
    entry(
        "CMBS", "Commercial Mortgage-Backed Securities",
        "Bonds backed by pools of Commercial Real Estate mortgages — investors get paid from the rent and Principal of the underlying buildings.",
        "Bonds backed by pools of Commercial Real Estate mortgages.",
        "CMBS bundle Commercial Mortgages on office, retail, industrial, hotel, and Multifamily property into tranched securities sold to institutional investors. Senior tranches (AAA) absorb losses last; junior tranches (BB and below) absorb first. Loans inside CMBS are typically 10-year, fixed-rate, non-recourse, with strict prepayment penalties (defeasance or yield maintenance). Issuance peaked pre-2008, collapsed, recovered, and softened again post-2020 as office vacancies stressed legacy pools. Special servicers handle workouts when borrowers default.",
        ["NCREIF", "Investopedia"],
        indications=["Commercial", "Investment"],
        category="Financing & Lending",
    ),
    entry(
        "TCJA", "Tax Cuts and Jobs Act",
        "The 2017 federal tax law that cut corporate rates, capped the state and local tax deduction, and reshaped Real Estate tax treatment.",
        "2017 federal tax overhaul affecting depreciation, 1031 Exchange scope, and the SALT deduction.",
        "TCJA's Real Estate impacts run wide. Mortgage interest deduction was capped at $750,000 of acquisition debt (down from $1M); HELOC interest only deductible for substantial improvements. State and Local Tax (SALT) deduction capped at $10,000 — devastating in high-Property-Tax states. Section 199A pass-through deduction extended to qualified Real Estate businesses. Bonus Depreciation expanded to 100% then phasing down to zero by 2027. 1031 Exchange restricted to Real Property only; personal-property exchanges eliminated.",
        ["IRS", "Cornell LII"],
        indications=["Residential", "Investment", "Commercial"],
        category="Tax",
    ),
    entry(
        "BRRRR", "Buy, Rehab, Rent, Refinance, Repeat",
        "A real-estate investor strategy: buy cheap, fix up, rent out, Refinance to pull cash back out, and repeat with the next property.",
        "Investor strategy of buying distressed property, rehabbing, renting, refinancing equity out, repeating.",
        "BRRRR popularised through investor podcasts and forums (BiggerPockets) as a way to scale a rental portfolio with limited starting capital. Mechanics: buy below market (often distressed or auction), spend on Rehab to lift ARV, place a Tenant to stabilise income, Refinance against the new value to recapture invested cash, recycle into the next deal. Risks: Appraisal coming in low at refi, rate environment changes during seasoning, Tenant placement delays. Hard Money often funds the buy-and-rehab phase.",
        ["Investopedia"],
        indications=["Investment", "Residential"],
        category="Market & Investment",
    ),
    entry(
        "Survey", "Land Survey",
        "A professional measurement of property boundaries, structures, and Easements — produces a drawing used at Closing and for new construction.",
        "Boundary and improvement measurement of a property by a licensed surveyor.",
        "Surveys come in flavours of precision. A boundary survey marks the property lines (corner monuments, dimensions). An ALTA/NSPS Land Title Survey is the institutional standard for commercial transactions — boundary plus structures, Easements, encroachments, flood zone, and improvements. A mortgage location survey is cheaper, used for residential refi. Lenders often require a current survey at Closing. Surveys surface Encroachments, missing setbacks, and unrecorded Easements that Title Insurance might otherwise miss.",
        ["ALTA"],
        indications=["Residential", "Commercial", "Cross-sector"],
        category="Title & Ownership",
    ),
    entry(
        "Title Company", "",
        "A neutral third party that researches Title, issues Title Insurance, and handles the Escrow at Closing in most states.",
        "Neutral third party that researches Title, insures it, and runs the Escrow at Closing.",
        "Title companies sit at the centre of US residential Closings. The title search examines public records for Deeds, Liens, judgments, Easements, and Encroachments. The Title Insurance commitment outlines what the insurer will and won't cover. The escrow officer collects funds from Buyer and Lender, pays off prior loans, records the new Deed, and disburses the seller's proceeds. In attorney states (New York, Massachusetts, much of the Northeast), attorneys play this role instead. Compensation comes from title premiums and escrow fees.",
        ["ALTA", "CFPB"],
        indications=["Residential", "Commercial"],
        category="Title & Ownership",
    ),
    entry(
        "Title Search", "",
        "The historical review of public records that confirms who owns a property and what Liens or Easements attach to it.",
        "Examination of public records to confirm ownership and surface Encumbrances.",
        "The title search is the engine behind Title Insurance. A title abstractor or attorney pulls every recorded document affecting the property — Deeds, mortgages, judgment Liens, mechanic's Liens, tax Liens, Easements, court judgments — back to the original Land grant or a statutory cut-off. Gaps in the Chain of Title, unreleased Liens from prior owners, and forgeries are common issues to surface. The title commitment lists exceptions the insurer won't cover; clean Closings require curing those before funding.",
        ["ALTA"],
        indications=["Residential", "Commercial"],
        category="Title & Ownership",
    ),

    # --- Leasing depth -----------------------------------------------------
    entry(
        "Triple Net Lease", "NNN, NNN Lease",
        "A commercial Lease where the Tenant pays Rent plus all Property Tax, insurance, and maintenance — the Landlord nets the Rent.",
        "Commercial Lease shifting Property Tax, insurance, and maintenance costs to the Tenant.",
        "NNN is the standard for single-tenant Commercial Real Estate (drug stores, fast food, big-box retail). Rent is quoted at a low base because the Tenant bears the three nets: net of Property Tax, net of insurance, net of common-area maintenance. Multi-tenant NNN allocates shared costs pro-rata by leased square footage. Buyer underwriting focuses on tenant credit and remaining lease term — STORE Capital, Realty Income, and W.P. Carey built REITs around NNN portfolios. Compare Gross Lease and Modified Gross Lease.",
        ["NCREIF", "Investopedia"],
        indications=["Commercial", "Investment"],
        category="Leasing",
    ),
    entry(
        "Gross Lease", "Full Service Lease",
        "A commercial Lease where the Landlord pays all Operating Expenses out of the Rent — the Tenant just pays the headline number.",
        "Commercial Lease where the Landlord absorbs all Operating Expenses out of base Rent.",
        "Gross leases are common in Office buildings, especially Class A urban towers. The Tenant pays a single all-in Rent; the Landlord covers Property Tax, insurance, utilities, janitorial, repairs. Year-over-year cost increases hit the Landlord. To protect against that, gross leases often include expense stops — the Tenant absorbs operating-cost increases above a base-year benchmark. Compare Triple Net Lease (Tenant pays nets) and Modified Gross (split).",
        ["IREM", "NCREIF"],
        indications=["Commercial"],
        category="Leasing",
    ),
    entry(
        "Modified Gross Lease", "MG Lease",
        "A commercial Lease that splits Operating Expenses between Landlord and Tenant — somewhere between a Gross Lease and a Triple Net Lease.",
        "Commercial Lease splitting Operating Expenses between Landlord and Tenant.",
        "Modified Gross is a negotiation point, not a fixed formula. Common splits: Landlord covers Property Tax and structural insurance; Tenant covers utilities, janitorial, interior repairs. Or Landlord covers operating costs to a base year, Tenant absorbs increases (expense stops). Common in suburban Office and flex Industrial. The lease itself spells out which expenses sit on which side — careful drafting prevents post-Closing surprises. Compare Gross Lease (Landlord covers all) and Triple Net Lease (Tenant covers all).",
        ["IREM"],
        indications=["Commercial"],
        category="Leasing",
    ),
    entry(
        "Tenant Improvement", "TI, Build-Out",
        "Money the Landlord spends — or credits the Tenant for — to customise a leased space before the Tenant moves in.",
        "Landlord allowance or work funding interior customisation of leased space for a Tenant.",
        "TI dollars are heavily negotiated in Commercial Lease economics. The Landlord typically offers a per-square-foot allowance ($25-$150 PSF depending on market and Lease length) to fund Tenant-specific Build-Out — partitions, finishes, mechanical changes, IT cabling. The TI investment is amortised into the base Rent or treated as Lease-level Capital Expenditure by the Landlord. Long Leases justify higher TI; short Leases get little or none. Unused TI typically reverts to the Landlord.",
        ["IREM", "NCREIF"],
        indications=["Commercial"],
        category="Leasing",
    ),

    # --- Transactions depth ----------------------------------------------
    entry(
        "Letter of Intent", "LOI",
        "A short, mostly non-binding written summary of the key deal terms — Sale Price, deposit, contingencies, timing — used as the starting point for the formal purchase contract.",
        "Short, mostly non-binding summary of key deal terms before a formal purchase contract.",
        "LOIs save weeks of attorney drafting time when buyer and seller are still aligning on price and structure. In residential, the formal Purchase Agreement does the LOI work; in Commercial Real Estate, LOIs are nearly universal at the offer stage. The LOI sets Sale Price, deposit amount, Due Diligence period, financing contingency, exclusivity (typically 30-60 days), and broker commissions. Most provisions are non-binding except confidentiality, exclusivity, and (sometimes) broker fees. Binding LOIs exist — careful drafting matters.",
        ["NAR", "Cornell LII"],
        indications=["Commercial", "Investment"],
        category="Transactions",
    ),
    entry(
        "Pro Forma", "Proforma",
        "A projected income statement for a property — Rent, vacancy, Operating Expenses, NOI — showing what the buyer expects the investment to produce.",
        "Projected operating statement for a property over a defined hold period.",
        "Pro forma is the spreadsheet that underwrites any institutional commercial purchase. Top line: Gross Rental Income at market rents. Subtract vacancy, concessions, and bad debt → Effective Gross Income. Subtract Operating Expenses → NOI. Subtract debt service → cash flow to equity. Project annual growth (Rent escalations, expense inflation), Cap-Ex reserves, refinance assumptions, and Exit Cap Rate to model IRR. Aggressive pro formas with low Cap Rate exits and optimistic Rent growth are how deals lose money — sponsor track record at delivering against pro forma is what investors underwrite.",
        ["NCREIF", "ULI"],
        indications=["Commercial", "Investment", "Multifamily"],
        category="Market & Investment",
    ),
    entry(
        "Cap-Ex", "Capital Expenditures, CapEx",
        "Big spending on a property that improves or replaces a long-lived asset — roof, HVAC, parking lot — rather than routine repair.",
        "Major property spending on improvements or long-lived assets, distinct from Operating Expenses.",
        "The Cap-Ex line sits below NOI in the cash flow waterfall. Distinguishing Cap-Ex from Operating Expenses changes both tax treatment (depreciated over years vs. expensed immediately) and reported NOI. IRS rules under Sections 162 and 263 govern the line. Industry shorthand: roof replacement, HVAC, parking lot resurfacing, elevator modernisation, façade work all sit in Cap-Ex. Filter replacement, janitorial, painting, minor repairs sit in Operating Expenses. Pro forma builds a Replacement Reserve to fund predictable Cap-Ex cycles.",
        ["IRS", "NCREIF"],
        indications=["Commercial", "Investment", "Multifamily"],
        category="Management & Operations",
    ),
    entry(
        "Vacancy Rate", "",
        "The percentage of rentable units or square footage sitting empty — a key indicator of property and market health.",
        "Percentage of rentable units or square footage currently vacant.",
        "Vacancy bites NOI from both sides: lost Rent and continuing Operating Expenses. Underwriting includes a vacancy assumption (typically 5-10% for stabilised Multifamily, higher for Office or Retail) even when current occupancy runs higher. Distinguish physical vacancy (empty units) from economic vacancy (units leased below market or with concessions). Market vacancy rates published by CoStar, Yardi, and broker firms guide acquisition pricing. Sustained sub-3% market vacancy signals Rent growth ahead; sustained 15%+ signals oversupply.",
        ["NCREIF", "IREM"],
        indications=["Commercial", "Multifamily", "Investment"],
        category="Management & Operations",
    ),
    entry(
        "Occupancy Rate", "",
        "The flip side of Vacancy Rate — the percentage of units or square footage currently leased and paying Rent.",
        "Percentage of units currently leased — the complement of Vacancy Rate.",
        "Occupancy is the headline operating metric most owners report. Physical occupancy counts units with signed Leases. Economic occupancy reflects actual Rent collected, accounting for concessions, bad debt, and below-market Leases. A property running 96% physical but 88% economic occupancy is hiding concession-driven vacancy. Stabilised commercial property typically targets 92-95% occupancy. Lease-up properties post lower occupancy as units fill; lenders set occupancy hurdles before releasing reserve funds or converting construction debt to permanent.",
        ["NCREIF", "IREM"],
        indications=["Commercial", "Multifamily", "Investment"],
        category="Management & Operations",
    ),
    entry(
        "Effective Gross Income", "EGI",
        "The property's actual collected Rent — Gross Rental Income minus what's lost to vacancy, concessions, and bad debt.",
        "Gross Rental Income minus vacancy, concessions, and collection loss.",
        "EGI is the realistic top line of a property's income statement, sitting between Gross Rental Income (theoretical full-Rent at full occupancy) and NOI (after Operating Expenses). The gap between GRI and EGI shows up as the 'vacancy and collection loss' line — typically 5-10% in stabilised Multifamily, more in turnover-heavy or concession-driven markets. Sloppy underwriting confuses EGI and GRI; the latter inflates NOI by the vacancy adjustment that should sit between.",
        ["NCREIF", "IREM"],
        indications=["Commercial", "Multifamily", "Investment"],
        category="Management & Operations",
    ),
    entry(
        "Stabilized", "Stabilised",
        "A property that has reached its target Occupancy Rate and steady-state Operating Expenses — the point where Cap Rates and NOI become meaningful.",
        "Property at target Occupancy Rate and normalised Operating Expenses — fit for Cap Rate analysis.",
        "Stabilisation matters for both underwriting and lending. A newly developed Multifamily property typically takes 12-24 months to stabilise; commercial Office can take longer. Pre-stabilisation, NOI is depressed by Lease-up vacancy and ramping operating costs — so Cap Rate analysis distorts. Construction Loans usually convert to permanent financing only after a stabilisation hurdle (debt-service coverage, occupancy threshold). Acquisition underwriting often projects 'going-in' NOI off Stabilized assumptions, even if current operations haven't reached them.",
        ["NCREIF", "Fannie Mae"],
        indications=["Commercial", "Multifamily", "Development"],
        category="Market & Investment",
    ),
    entry(
        "Lease-up", "Lease-Up",
        "The period when a newly built or repositioned property fills with Tenants — from delivery to stabilised occupancy.",
        "Period between property delivery and Stabilized occupancy as Tenants are leased in.",
        "Lease-up risk is one of the largest variables in new development underwriting. Multifamily typically targets 15-25 units leased per month in active leasing — the 'absorption' rate that drives the lease-up curve. Office and Retail are slower and more idiosyncratic. Developers often offer concessions (months free, reduced Security Deposit, gift cards) to accelerate Lease-up. Lenders structure interest reserves and Replacement Reserves to fund the property through the lease-up period before debt service coverage covers itself.",
        ["NCREIF", "ULI"],
        indications=["Multifamily", "Commercial", "Development"],
        category="Market & Investment",
    ),

    # --- Investment structure: syndication & private partnerships -------
    entry(
        "Sponsor", "GP, General Partner",
        "The active manager of a Real Estate syndication — finds the deal, raises equity, oversees operations, and earns a Promote for performance.",
        "Active partner running a Real Estate syndication — origination, operations, and execution.",
        "The Sponsor is the GP in a typical Real Estate LP structure. Brings the deal, leads due diligence, executes the business plan, manages day-to-day operations, communicates with Limited Partners. Earns three layers of compensation: acquisition fee (1-2% of purchase price), asset-management fee (1-2% of equity per year), and a Promote (share of profits above an IRR hurdle). LPs underwrite the Sponsor's track record, alignment of interests, and reporting discipline as carefully as the deal itself. Bad Sponsors lose investor capital regardless of market.",
        ["ULI", "NCREIF"],
        indications=["Commercial", "Investment", "Multifamily"],
        category="Market & Investment",
    ),
    entry(
        "Limited Partner", "LP",
        "A passive investor in a Real Estate syndication — provides capital, takes pro-rata economics, no day-to-day involvement or operational liability.",
        "Passive investor in a Real Estate syndication contributing capital, exposed only to invested amount.",
        "LPs in Real Estate syndications hold limited partnership or LLC member interests. They contribute committed capital, receive periodic distributions and a final exit payout, but cannot bind the partnership or make operational decisions. Liability is capped at their invested capital — they don't sign personal guarantees on debt. LP-friendly terms include strong reporting, capital-call caps, removal rights for bad acts, and tax-distribution covenants. Most institutional LPs allocate to GPs they've backed across multiple cycles.",
        ["ULI", "Cornell LII"],
        indications=["Investment", "Commercial", "Multifamily"],
        category="Market & Investment",
    ),
    entry(
        "Waterfall", "",
        "The agreed order of cash distribution in a Real Estate syndication — return of LP capital first, then preferred returns, then Promote splits to the Sponsor.",
        "Tiered cash-distribution structure in a Real Estate syndication.",
        "A typical Multifamily waterfall: (1) Return of LP capital. (2) Preferred Return (often 7-9% annual to LPs on unreturned capital). (3) Catch-up to GP. (4) Tiered Promote splits — 70/30 LP/GP to a hurdle IRR, 60/40 above, 50/50 above the next hurdle. Each tier is computed in sequence; cash only reaches the next level once the prior tier is satisfied. Waterfalls reward sponsors for outperformance while protecting LP downside. Audit-grade waterfall modeling separates polished Sponsors from amateurs.",
        ["NCREIF", "ULI"],
        indications=["Commercial", "Investment", "Multifamily"],
        category="Market & Investment",
    ),
    entry(
        "Preferred Return", "Pref",
        "The minimum annual return — usually 7-9% — that LPs must receive before the Sponsor earns any Promote.",
        "Annual return rate paid to LPs before any Promote flows to the Sponsor.",
        "The Preferred Return (often 'pref') is the first economic tier after Return of Capital in a Waterfall. Common rates: 7-9% on Multifamily value-add deals, 6-8% on Core, higher on opportunistic. Cumulative vs non-cumulative matters — cumulative pref accrues unpaid amounts and compounds (LP friendly); non-cumulative resets each period (sponsor friendly). Some structures pay pref currently from cash flow; others defer to disposition. Pref does not guarantee LP returns — it just gates the Sponsor's Promote.",
        ["ULI", "NCREIF"],
        indications=["Commercial", "Investment", "Multifamily"],
        category="Market & Investment",
    ),
    entry(
        "Promote", "Carried Interest",
        "The Sponsor's outsized share of profits earned by hitting return hurdles — typically 20-40% above the Preferred Return.",
        "Sponsor's outsized share of profits above the Preferred Return — Real Estate's carried interest.",
        "Promote aligns the Sponsor with LP outcomes. A typical structure: 0% Promote up to the Preferred Return (LP gets 100%), then 20-40% Promote above. Multi-tiered Promotes scale up as IRR exceeds higher hurdles — 20% Promote above 8% IRR, 30% above 12%, 40% above 18%. Promote crystallises at disposition or refinance, not annually. Tax-wise, Promote on holdings of 3+ years is taxed as long-term Capital Gain — the Real Estate equivalent of carried interest, politically scrutinised but largely intact through 2024.",
        ["ULI", "IRS"],
        indications=["Commercial", "Investment", "Multifamily"],
        category="Market & Investment",
    ),
    entry(
        "Going-In Cap Rate", "",
        "The Cap Rate at the moment of acquisition — calculated from the in-place NOI divided by the purchase price.",
        "Cap Rate at purchase: current NOI divided by Sale Price.",
        "Going-in cap rate is the snapshot of yield at acquisition. A 5.5% going-in cap on a Multifamily deal means $5.50 of NOI per $100 of purchase price. Value-add Sponsors target a going-in cap below the Exit Cap Rate — they accept lower yield at purchase, expect to lift NOI through Rehab and re-tenanting, and exit at a higher NOI even at a higher Exit Cap. Going-in cap rates compress when investor capital floods in (2020-2021); they widen when rates rise (2022 onward).",
        ["NCREIF", "CCIM Institute"],
        indications=["Commercial", "Investment", "Multifamily"],
        category="Market & Investment",
    ),
    entry(
        "Exit Cap Rate", "Reversion Cap Rate",
        "The Cap Rate assumed at sale at the end of the hold period — drives the projected Sale Price in any underwriting model.",
        "Cap Rate assumed at projected exit sale, driving the residual value.",
        "Exit cap rate is the most sensitive assumption in any commercial Real Estate underwrite. A 25-basis-point change in Exit Cap moves residual value by 4-5% — enough to flip a deal from win to loss. Conservative underwriting prices Exit Cap above Going-In Cap Rate to reflect normal Cap Rate widening over a typical 5-7 year hold. Aggressive underwriting holds Exit Cap flat or compresses it — a red flag in pro formas. Sensitivity tables in offering memos quantify the range; LPs scrutinise.",
        ["NCREIF", "CCIM Institute"],
        indications=["Commercial", "Investment"],
        category="Market & Investment",
    ),
    entry(
        "Hold Period", "Investment Horizon",
        "How long an investor plans to own the property before selling — usually 3-7 years for value-add, 7-10+ for Core deals.",
        "Planned ownership duration before disposition or refinance.",
        "Hold period drives nearly every underwriting assumption: IRR sensitivity, Cap-Ex pacing, debt structure, refinance vs sale at exit. Value-add Multifamily typically targets a 3-5 year hold to execute the business plan, stabilise NOI, then sell into a competitive market. Core Office and Industrial deals stretch 7-10+ years. Long-hold Core-Plus capital may target indefinite holds with periodic refis to return capital. Forced sales during distressed market windows distort returns — Sponsors with patient LP capital can ride out cycles.",
        ["ULI", "NCREIF"],
        indications=["Commercial", "Investment"],
        category="Market & Investment",
    ),
    entry(
        "Replacement Reserve", "",
        "Money set aside each year — modeled in the pro forma — to fund predictable future Cap-Ex like roof, HVAC, and parking lot.",
        "Annual reserve funded out of NOI to cover future Capital Expenditures.",
        "Lenders often require a Replacement Reserve to fund predictable Cap-Ex without depleting cash flow. Typical reserves: $250-$300 per unit per year for stabilised Multifamily, $0.20-$0.40 per square foot for Office and Retail. Reserves accumulate in a Lender-controlled account and draw down for approved Cap-Ex items. Underwriting models that skip the reserve overstate cash flow to equity by 1-3% of NOI — a common pro forma flag for sloppy underwriting. Reserves below NOI but above true cash flow is the standard placement.",
        ["IREM", "Fannie Mae"],
        indications=["Commercial", "Multifamily", "Investment"],
        category="Management & Operations",
    ),

    # --- Title & Ownership depth ------------------------------------------
    entry(
        "Tenancy by the Entirety", "TBE",
        "A form of joint ownership available only to married couples — strongest creditor protection of any co-ownership form.",
        "Marital co-ownership form with right of survivorship and joint-creditor protection.",
        "Recognised in roughly half the states (Florida, New York, Ohio, Massachusetts among them). Tenancy by the Entirety requires marriage and treats the spouses as a single legal entity owning the property. A creditor of just one spouse cannot reach the property — creditors of both can. Right of survivorship at death is automatic. Divorce typically converts Tenancy by the Entirety to Tenancy in Common. The structure is favoured for primary-residence asset protection where state law allows.",
        ["Cornell LII", "Investopedia"],
        indications=["Residential", "Cross-sector"],
        category="Title & Ownership",
    ),
    entry(
        "Community Property", "",
        "In nine states, anything either spouse earns or buys during marriage is owned 50/50 — separately tracked from pre-marital or inherited property.",
        "Marital-property regime in nine states treating earnings during marriage as 50/50 owned.",
        "Community Property states: Arizona, California, Idaho, Louisiana, Nevada, New Mexico, Texas, Washington, Wisconsin. (Alaska, Tennessee, and a few others permit opt-in.) Anything acquired during marriage is community property regardless of titling; pre-marital property and inheritances remain separate. At death of one spouse, the survivor receives a full step-up in basis on the entire community-property home (versus 50% step-up in common-law states) — a major federal income-tax advantage. Divorce courts split community property equally.",
        ["Cornell LII", "IRS"],
        indications=["Residential", "Cross-sector"],
        category="Title & Ownership",
    ),
    entry(
        "Lis Pendens", "Notice of Pending Action",
        "A public-record filing warning anyone reading the Title that a lawsuit is pending against the property — freezes the market for it.",
        "Recorded notice that litigation involving the property is pending.",
        "Lis pendens (Latin: 'suit pending') gets recorded at the county registry the moment a lawsuit involving Real Property is filed. Any buyer or Lender who searches Title after that takes subject to the outcome of the suit. Common in Foreclosure, divorce, partition, and specific-performance cases. The lis pendens effectively kills the property's marketability until the litigation resolves. Wrongful lis pendens — filed without genuine claim to the property — can trigger slander-of-title liability and statutory damages in many states.",
        ["Cornell LII"],
        indications=["Residential", "Commercial", "Cross-sector"],
        category="Title & Ownership",
    ),
    entry(
        "Plat", "Plat Map",
        "A surveyor-drawn map showing how a subdivision is divided into Lots — the foundation document for every Lot's legal description.",
        "Recorded subdivision map showing Lot boundaries, dimensions, and Easements.",
        "Plat maps get recorded at the county recorder's office when a developer subdivides raw Land. Each Lot is assigned a number; the legal description in subsequent Deeds references the plat ('Lot 12, Block 4, Sunny Acres Subdivision, recorded in Plat Book 87, Page 23'). Plats show streets, Easements, Setbacks, drainage, and any common areas. Re-platting (changing the Lot lines after recording) requires municipal approval and re-recording. A clean Plat is the foundation of clean Title for any subdivided property.",
        ["ALTA", "NAHB"],
        indications=["Residential", "Land", "Development"],
        category="Title & Ownership",
    ),
    entry(
        "Metes and Bounds", "",
        "An older form of legal property description that walks the property boundary in surveyor's measurements — distances and compass bearings — instead of referencing a Plat.",
        "Property description by directional bearings and distances rather than a Plat reference.",
        "Metes and bounds descriptions read like a hike: 'Beginning at the iron pin at the SW corner of Lot 4, thence N 23°15' E along the east line of Smith property a distance of 247.50 feet to a stone monument...' Common in rural and pre-subdivision tracts, in original colonial-era US conveyances, and in irregularly shaped parcels. Surveyors interpret historical metes and bounds against current monumentation — discrepancies are common and a frequent source of boundary litigation. Modern subdivisions use Plat references for simplicity.",
        ["ALTA"],
        indications=["Land", "Residential"],
        category="Title & Ownership",
    ),

    # --- Development & Zoning vocabulary ---------------------------------
    entry(
        "Variance", "Zoning Variance",
        "An exception to a Zoning rule, granted by a local Board of Zoning Appeals when the rule would cause an unfair hardship for a specific Lot.",
        "Discretionary exception to a Zoning requirement, granted for hardship.",
        "Variances split into use variances (allow a use not normally permitted) and area variances (allow deviation from Setback, Lot coverage, height, parking, FAR). Use variances are rare and require strong hardship showings. Area variances are common — a narrow Lot, an odd shape, a topographic constraint. The applicant petitions the local Zoning Board of Appeals, neighbours get notice, a hearing follows. Granted variances run with the Land. Denied applications can be re-applied or appealed to court on a 'no rational basis' standard.",
        ["Cornell LII", "HUD"],
        indications=["Development", "Residential", "Commercial"],
        category="Development",
    ),
    entry(
        "Conditional Use Permit", "CUP, Special Use Permit",
        "A Zoning approval for a use not allowed by right, but allowed if specific conditions are met — like a daycare in a residential zone.",
        "Zoning approval for a use allowed only under specified conditions.",
        "Conditional uses are listed in the Zoning ordinance — they're permitted as of right only if the applicant can demonstrate compatibility with the neighbourhood and meet specific conditions (hours of operation, traffic mitigation, buffer landscaping, parking minimums). The local planning commission or board reviews; some jurisdictions require city council approval. Common conditional uses: schools, churches, daycares, group homes, gas stations, drive-throughs, cell towers. Granted CUPs run with the Land but can be revoked if conditions are violated.",
        ["Cornell LII"],
        indications=["Development", "Residential", "Commercial"],
        category="Development",
    ),
    entry(
        "Nonconforming Use", "Grandfathered Use",
        "A property use that was legal when established but no longer matches current Zoning — protected as 'grandfathered' from being shut down.",
        "Pre-existing use that predates current Zoning and remains legal under a grandfather clause.",
        "When Zoning changes — a residential street rezoned office, a corner store district rezoned single-family — pre-existing uses get grandfathered as nonconforming. They can continue but face restrictions: most ordinances cap expansion, prohibit replacement after destruction, and treat abandonment (6-12 months of non-use, often) as termination. Property values for nonconforming uses are bounded by the right to keep doing the same thing — but new investment is risky. Variance or rezoning can convert nonconforming to conforming where political will allows.",
        ["Cornell LII", "HUD"],
        indications=["Development", "Commercial", "Residential"],
        category="Development",
    ),
    entry(
        "Setback", "",
        "The minimum required distance between a building and the property line — front, side, and rear — set by local Zoning.",
        "Minimum distance between a building and the Lot line, set by Zoning.",
        "Setbacks shape the buildable envelope on every Lot. Single-family zones typically require 20-30 foot front, 5-15 foot side, 20-30 foot rear setbacks. Corner Lots have two front setbacks. Reduced setbacks are common in dense urban zones and for accessory structures. Building inside the setback creates an Encroachment requiring a Variance or removal. Setback violations are caught at Building Permit review or by a current Survey. Special setbacks apply to wetlands, slopes, easements, and historic districts.",
        ["NAHB", "HUD"],
        indications=["Residential", "Commercial", "Development"],
        category="Development",
    ),
    entry(
        "Floor Area Ratio", "FAR",
        "How much total building floor area can fit on a Lot, expressed as a multiplier of Lot size — FAR 2.0 means 200% of the Lot area can be built as floor space across all stories.",
        "Ratio of buildable floor area to Lot size, set by Zoning.",
        "FAR is the headline density control in urban Zoning. A 10,000 sq ft Lot with FAR 2.0 permits 20,000 sq ft of total floor area — could be 2 stories full-coverage, 4 stories at half-coverage, or some mix. Higher FAR means taller, denser buildings. Manhattan downtown FAR can exceed 15; suburban office parks run 0.3-0.5. Bonuses can lift base FAR (affordable-housing inclusion, public-space contribution, transit proximity). Developers maximise FAR to maximise per-Lot value — the metric drives Land prices in dense markets.",
        ["ULI", "NAHB"],
        indications=["Development", "Commercial", "Multifamily"],
        category="Development",
    ),

    # --- Fair Housing & regulatory regime --------------------------------
    # Fair Housing Act already exists in the corpus from the previous session;
    # the entry below covers the same ground with stronger historical detail
    # and was removed to avoid duplicate-content conflict (see Policy Rule 7).
    entry(
        "Section 8", "Housing Choice Voucher Program",
        "The federal rent-subsidy program that helps low-income Tenants pay private-market Rent — vouchers cover the gap between income and Rent.",
        "Federal rent subsidy paid to private Landlords on behalf of low-income Tenants.",
        "Section 8 (formally the Housing Choice Voucher Program, codified in Section 8 of the Housing Act of 1937 as amended) is the largest federal rental-assistance program — roughly 2.3 million households served. Tenants pay 30% of adjusted income; HUD pays the rest, up to a metro-area payment standard. Local public-housing authorities administer. Landlord acceptance is voluntary in most states; a growing list of states and cities bar Section-8 refusal as discrimination. Tenant turnover in Section-8 units is markedly lower than market — a feature that draws some private Landlords in.",
        ["HUD", "Cornell LII"],
        indications=["Affordable", "Residential", "Public Sector"],
        category="Law & Regulation",
    ),
    entry(
        "Redlining", "",
        "The historical (and illegal) practice of Lenders refusing Mortgages in mostly-minority neighbourhoods — drawn on actual red-line maps in the 1930s.",
        "Race-based denial of Mortgage credit by neighbourhood — illegal but historically structural.",
        "The Home Owners' Loan Corporation produced colour-coded residential security maps in the 1930s, marking minority neighbourhoods in red as 'hazardous.' Banks used the maps to deny Mortgages and insurance for decades — the structural source of much of the 21st-century US racial wealth gap. Modern Redlining is illegal under the Fair Housing Act and the Equal Credit Opportunity Act, but persistence has been documented: CFPB and DOJ have brought multiple Redlining cases against banks in the 2020s for branch placement, marketing, and Underwriting practices.",
        ["HUD", "CFPB"],
        indications=["Residential", "Affordable", "Cross-sector"],
        category="Law & Regulation",
    ),
    entry(
        "Steering", "",
        "An illegal Real Estate Agent practice of guiding Buyers toward or away from neighbourhoods based on protected characteristics — race, family status, religion.",
        "Illegal Agent practice of channeling Buyers toward or away from areas by protected class.",
        "Steering violates the Fair Housing Act. Examples: telling a Black Buyer that 'they'd be more comfortable' in one neighbourhood, declining to show listings outside a stereotyped 'family' or 'retiree' area, characterising school quality by demographic proxy. Steering can be subtle and is hard to prove — NAR ethics training emphasises identical service regardless of perceived characteristics. Newsday's 2019 fair-housing investigation in Long Island and subsequent enforcement actions revived public attention. Brokerages train and audit to manage liability.",
        ["HUD", "NAR"],
        indications=["Residential"],
        category="Law & Regulation",
    ),
    entry(
        "ADA", "Americans with Disabilities Act",
        "The 1990 federal law requiring public accommodations and most commercial properties to be accessible to people with disabilities.",
        "Federal accessibility law for public accommodations and many commercial properties.",
        "Title III of ADA covers public accommodations and commercial facilities — Retail, Office, restaurants, hotels, healthcare, daycares, and more. New construction and alterations must meet the ADA Standards for Accessible Design (entryways, restrooms, parking, signage, routes). Existing facilities must remove barriers where 'readily achievable.' DOJ enforces; private suits can recover attorney's fees. Multifamily residential under four units is exempt from ADA but covered by the Fair Housing Act's accessibility provisions for first-floor units in buildings of four or more.",
        ["Cornell LII", "HUD"],
        indications=["Commercial", "Residential"],
        category="Law & Regulation",
    ),

    # --- Tax depth ------------------------------------------------------
    entry(
        "Step-up in Basis", "Stepped-up Basis",
        "A tax rule that resets a property's cost basis to its market value at the owner's death — heirs sell with little or no Capital Gain.",
        "Reset of property's tax basis to fair market value at the owner's death.",
        "Step-up in basis is one of the largest tax breaks in US Real Estate. Heirs inherit at fair market value at date of death; if they sell shortly after, Capital Gain is minimal. A property bought for $200,000 forty years ago and worth $1.2M at owner's death gets stepped up to $1.2M basis — the heir avoids tax on $1M of appreciation. Community Property states grant a full step-up on both halves at the death of one spouse; common-law states grant only half-step-up. Political pressure to limit or eliminate step-up has not (through 2024) produced major reform.",
        ["IRS", "Cornell LII"],
        indications=["Residential", "Investment", "Cross-sector"],
        category="Tax",
    ),
    entry(
        "Bonus Depreciation", "",
        "A federal tax break that lets owners write off a big chunk of certain Real Estate improvements in the first year, instead of spreading over decades.",
        "First-year accelerated write-off of qualified property and certain improvements.",
        "Bonus Depreciation under IRC §168(k) sat at 100% from 2017 (TCJA) through 2022 — Cost Segregation studies surged in popularity to maximise first-year deductions. Phasedown: 80% in 2023, 60% in 2024, 40% in 2025, 20% in 2026, 0% in 2027 absent congressional action. Applies to property with 20-year-or-less recovery period — typically 5, 7, and 15-year personal-property components inside a building (carpeting, cabinets, parking lots, landscaping) identified through Cost Segregation. Real Property (39-year commercial, 27.5-year residential rental) doesn't qualify directly.",
        ["IRS", "Cornell LII"],
        indications=["Investment", "Commercial"],
        category="Tax",
    ),

    # --- Property Types: commercial breadth ------------------------------
    entry(
        "Office", "Office Property",
        "A commercial building leased to businesses for white-collar work — single-tenant to high-rise, urban core to suburban park.",
        "Commercial property leased to businesses for professional work.",
        "Office property covers Class A (newest, best-located, premium rents), Class B (older but well-maintained), Class C (older, deferred maintenance). Subtypes: urban core high-rise (CBD), suburban office park, medical office building (MOB), creative/flex office. Post-2020 remote-work shift hit Class B and Class C harder than Class A; sub-leasing surged. Lease terms typically run 5-10 years with Tenant Improvement allowances. NOI calculations use Effective Gross Income net of vacancy and concessions; underwriting weights tenant credit and remaining lease term heavily.",
        ["NCREIF", "BOMA", "ULI"],
        indications=["Commercial", "Investment"],
        category="Property Types",
    ),
    entry(
        "Retail", "Retail Property",
        "A commercial building leased to stores, restaurants, and services — strip centres, big boxes, malls, urban street retail.",
        "Commercial property leased to consumer-facing stores, restaurants, and services.",
        "Retail subtypes: neighbourhood centre (grocery-anchored), community centre (junior anchor + smaller tenants), power centre (big-box tenants), regional and super-regional mall, lifestyle centre, outlet centre, urban street retail. E-commerce pressure has hit mall and Class B retail hardest; grocery-anchored neighbourhood centres have proven resilient. NNN Leases dominate single-tenant retail. Co-tenancy clauses (a tenant's right to break Lease if an anchor leaves) shape multi-tenant centre risk. Mixed-Use redevelopment of dead malls is a growing 2020s theme.",
        ["NCREIF", "ULI"],
        indications=["Commercial", "Investment"],
        category="Property Types",
    ),
    entry(
        "Industrial", "Industrial Property",
        "A commercial building used for manufacturing, warehousing, distribution, or research — usually low-rise, high-clear-height, accessible to highways.",
        "Commercial property used for production, storage, distribution, or research.",
        "Industrial subtypes: warehouse/distribution (the e-commerce darling), bulk warehouse (mega-boxes), light manufacturing, flex/R&D, cold storage, last-mile (small infill near urban consumers). Clear heights, dock-door counts, trailer parking, and column spacing drive functionality and rent. Tenant credit varies: large logistics firms (Amazon, FedEx, Walmart) anchor institutional portfolios; smaller industrial users dominate secondary markets. Industrial NOI grew faster than any other Commercial Real Estate sector 2018-2022 before normalising. Sale-leasebacks are common — owners free up capital while remaining as tenants.",
        ["NCREIF", "ULI", "BOMA"],
        indications=["Industrial", "Commercial", "Investment"],
        category="Property Types",
    ),

    # --- Investment metrics: development & financing structure ----------
    entry(
        "Yield-on-Cost", "YOC, Development Yield",
        "The Cap Rate on a development project — projected stabilised NOI divided by total project cost — used to decide whether to build new versus buy existing.",
        "Stabilised NOI as a percentage of total project cost in a development.",
        "Yield-on-Cost is the development-equivalent of Cap Rate. A 7% YOC on a Multifamily project means stabilised NOI returns $7 per $100 of total project cost (Land, hard construction, soft costs, financing, fees). YOC must exceed the market Going-In Cap Rate by a 'development spread' (typically 100-200 basis points) to compensate for execution risk versus buying an existing stabilised property. Spreads compress in hot markets, widen in distressed cycles. YOC sensitivity tables in offering memos show how cost overruns or NOI shortfalls move the metric.",
        ["NCREIF", "ULI"],
        indications=["Development", "Commercial", "Investment"],
        category="Market & Investment",
    ),
    entry(
        "Capital Stack", "",
        "The layered structure of all the money funding a Real Estate deal — senior debt at the bottom, equity at the top, with mezzanine and preferred equity sometimes filling in between.",
        "Layered structure of all debt and equity funding a Real Estate deal.",
        "From safest to riskiest: Senior debt (50-65% of project cost, lowest rate, first claim on cash and collateral) → Mezzanine debt (5-15%, higher rate, secured by entity rather than property) → Preferred Equity (5-15%, fixed return ahead of common equity) → Common Equity (the Sponsor and LP capital, residual claim). Each layer prices according to its risk position. Restructuring during distress works down the stack — lender forbearance, mezz capitalisation, equity wipe-out. Sophisticated capital-stack design is the heart of institutional Real Estate finance.",
        ["NCREIF", "ULI"],
        indications=["Commercial", "Investment"],
        category="Financing & Lending",
    ),
]


# ============================================================================
# BATCH 2b — Post-batch-2 paired-entry fixes (12 terms, Rule 7)
#
# Audit after batch 2 surfaced shorthand variants (LP 10x, GP 3x, FAR 6x,
# NNN 3x, Dodd-Frank 3x bare) of newly added entries — Rule 7 dictates
# that both forms should exist and one should be a stub. These are the
# stub siblings, plus a handful of additional real entries (SALT, Class A,
# Class B, Class C, Common Area, Capital Expenditure) the audit caught
# as separate corpus gaps.
# ============================================================================

BATCH_2B_PAIRED_FIXES = [
    entry(
        "LP", "Limited Partner",
        "Common shorthand for a Limited Partner — the passive investor in a Real Estate syndication.",
        "Standard shorthand for Limited Partner in a Real Estate syndication.",
        "LP is industry shorthand for Limited Partner in a Real Estate private partnership or LLC. The LP contributes capital and receives passive economics; the GP runs the deal. Offering memos and waterfall language reference LPs constantly. Multiple LP classes can exist in larger deals — institutional LPs with different fee terms than high-net-worth LPs, for example. See Limited Partner for the operational mechanics of LP economics, rights, and protections.",
        ["ULI"],
        indications=["Investment", "Commercial"],
        category="Market & Investment",
    ),
    entry(
        "GP", "General Partner",
        "Common shorthand for the General Partner — the Sponsor running a Real Estate syndication.",
        "Standard shorthand for the active Sponsor in a Real Estate syndication.",
        "GP is shorthand for General Partner — the active partner in a limited-partnership or LLC structure. In Real Estate parlance the GP and Sponsor are interchangeable terms. The GP holds operational control, signs personal guarantees on Recourse Loans, and earns the Promote above the Preferred Return. GPs face fiduciary duties to LPs that are often modified by the partnership agreement; some structures use waivers that LPs scrutinise carefully. See Sponsor for the broader role.",
        ["ULI", "Cornell LII"],
        indications=["Investment", "Commercial"],
        category="Market & Investment",
    ),
    entry(
        "FAR", "Floor Area Ratio",
        "Common shorthand for Floor Area Ratio — the multiplier of Lot size that caps total building floor area under Zoning.",
        "Standard shorthand for Floor Area Ratio in Zoning analysis.",
        "FAR is the Zoning vocabulary for building density. Pronounced 'far' as one syllable in industry use. Cities publish FAR caps by district — Manhattan downtown FAR can exceed 15; suburban Office parks run 0.3-0.5. Higher-FAR Zoning multiplies Land value because more revenue-generating square footage can fit on the same parcel. See Floor Area Ratio for full mechanics, bonus structures, and how FAR interacts with Setback and height limits.",
        ["ULI", "NAHB"],
        indications=["Development", "Commercial", "Multifamily"],
        category="Development",
    ),
    entry(
        "NNN", "Triple Net Lease",
        "Common shorthand for a Triple Net Lease — the commercial Lease where the Tenant pays Property Tax, insurance, and maintenance on top of base Rent.",
        "Standard shorthand for a Triple Net Lease in Commercial Real Estate.",
        "NNN is universal industry shorthand for a Triple Net Lease. The three nets — Property Tax, insurance, common-area maintenance — sit on the Tenant. NNN deals trade on the strength of tenant credit and remaining Lease term; single-tenant NNN REITs (Realty Income, STORE Capital, W.P. Carey) built entire businesses around the structure. See Triple Net Lease for the full economics and how NNN compares to Gross Lease and Modified Gross Lease.",
        ["NCREIF"],
        indications=["Commercial", "Investment"],
        category="Leasing",
    ),
    entry(
        "Dodd-Frank", "Dodd-Frank Act",
        "Common shorthand for the Dodd-Frank Act — the 2010 financial-reform law that reshaped Mortgage lending.",
        "Standard shorthand for the Dodd-Frank Wall Street Reform Act.",
        "Dodd-Frank is the industry shorthand for the Dodd-Frank Act, named after Senator Chris Dodd and Representative Barney Frank. The shorthand dominates day-to-day conversation in Mortgage compliance and consumer-finance circles. See Dodd-Frank Act for the substantive mortgage-lending provisions: CFPB creation, Qualified Mortgage rules, ability-to-repay, Loan Officer compensation restrictions.",
        ["CFPB", "Cornell LII"],
        indications=["Residential", "Cross-sector"],
        category="Law & Regulation",
    ),
    entry(
        "Capital Expenditure", "CapEx, Cap-Ex",
        "The full spelling of Cap-Ex — big spending on a property that improves or replaces a long-lived asset.",
        "Full spelling of Cap-Ex — major spending on improvements or long-lived property assets.",
        "Capital Expenditure is the formal accounting term that Cap-Ex shortens. IRS rules under Sections 162 and 263 govern whether spending is capitalised (depreciated over years) or expensed immediately. The line between Capital Expenditure and Operating Expenses changes both tax treatment and reported NOI. See Cap-Ex for the practical roster of which property items qualify and how Replacement Reserves fund them in stabilised property.",
        ["IRS", "NCREIF"],
        indications=["Commercial", "Investment", "Multifamily"],
        category="Management & Operations",
    ),
    entry(
        "SALT", "State and Local Tax",
        "The combined state and local taxes a homeowner pays — capped at $10,000 of federal deduction since the 2017 TCJA.",
        "Combined state and local tax burden — federal deduction capped at $10,000 since TCJA.",
        "Before 2018, homeowners could deduct unlimited Property Tax plus state income tax against federal income. The TCJA capped the SALT deduction at $10,000 — a major hit to high-Property-Tax states (New York, New Jersey, California, Illinois, Massachusetts). High-income owners in those states lost five-to-six-figure deductions. Multiple states designed workaround entity-level pass-through taxes for business income (PTET), but residential homeowners have no equivalent escape. SALT-cap repeal has been a recurring political flashpoint; through 2024 the cap survived intact.",
        ["IRS", "Cornell LII"],
        indications=["Residential", "Investment"],
        category="Tax",
    ),
    entry(
        "Class A", "",
        "The highest grade of commercial property — newest, best-located, premium finishes, top rents and lowest vacancy.",
        "Top grade of commercial property — newest, best-located, premium rents.",
        "Class A property anchors institutional portfolios. Defined relative to local market: a Class A building in suburban Phoenix differs from a Class A in midtown Manhattan. Common attributes: built or substantially renovated in the last 15-20 years, prime location with strong access, full amenity package, blue-chip tenant roster, premium asking Rent (top quartile of submarket). Class A trades at the tightest Cap Rates because risk is lowest. Pension funds, sovereign wealth, and listed REITs concentrate here.",
        ["NCREIF", "BOMA"],
        indications=["Commercial", "Investment"],
        category="Property Types",
    ),
    entry(
        "Class B", "",
        "The middle grade of commercial property — older but well-maintained, decent locations, market-average rents.",
        "Middle grade of commercial property — older, well-kept, market-rate Rents.",
        "Class B is where most US Commercial Real Estate sits. Buildings 20-40 years old, dated finishes, functional but unspectacular. Cap Rates trade 75-150 basis points wider than Class A for the same submarket. Value-add Sponsors target Class B for renovation to lift NOI toward Class A pricing — light Rehab on common areas, unit interiors, mechanical systems. Class B office took the biggest 2020-2023 occupancy hit as Class A absorbed flight-to-quality demand.",
        ["NCREIF", "BOMA"],
        indications=["Commercial", "Investment"],
        category="Property Types",
    ),
    entry(
        "Class C", "",
        "The lower grade of commercial property — older, deferred maintenance, secondary locations, below-market Rents.",
        "Lower grade of commercial property — older, sometimes deferred-maintenance, below-market rents.",
        "Class C property earns the widest Cap Rates and the highest yield-on-cost — at the cost of higher Tenant turnover, more management intensity, and meaningful Cap-Ex needs. Often 40+ years old with deferred maintenance, functional obsolescence, and locations away from prime corridors. Workforce-housing Multifamily and value-add Class C office are common Sponsor strategies. Class C suffers most in down cycles and recovers slowest in up cycles. Lender appetite is thinner — bridge debt and Hard Money fill more of the capital stack.",
        ["NCREIF", "BOMA"],
        indications=["Commercial", "Multifamily", "Investment"],
        category="Property Types",
    ),
    entry(
        "Common Area", "",
        "Parts of a Multifamily, Office, or Retail property shared by all Tenants — lobbies, hallways, parking, elevators, lawns — funded by Common Area Maintenance charges.",
        "Shared-use property areas funded by Common Area Maintenance charges.",
        "Common areas exist anywhere multiple Tenants share a building or development. Multifamily: lobby, hallways, fitness room, leasing office, pool. Office: lobby, restrooms, hallways, elevators, parking deck. Retail centre: parking lot, sidewalks, landscaping, pylon signs. CAM charges allocate maintenance, utilities, insurance, and Property Tax for these areas to Tenants pro-rata. NNN Leases pass CAM straight through; Gross Leases absorb it into base Rent. CC&Rs govern common area use in Condo, HOA, and Co-op contexts.",
        ["IREM", "BOMA"],
        indications=["Commercial", "Multifamily"],
        category="Management & Operations",
    ),
    entry(
        "Tenancy", "",
        "The right and condition of holding property as a Tenant under a Lease — also the collective term for the various co-ownership forms (Joint Tenancy, Tenancy in Common, Tenancy by the Entirety).",
        "Right or condition of holding property as Tenant — also the collective term for co-ownership forms.",
        "Two distinct senses share the word. (1) Leasehold tenancy: the Tenant's possessory right under a Lease — periodic (month-to-month), term (fixed Lease), sufferance (Holdover Tenant), at will. (2) Co-ownership tenancy: the umbrella for Joint Tenancy, Tenancy in Common, and Tenancy by the Entirety — the various forms of multi-owner Title. Context disambiguates. The shared root makes sense — both senses describe the right of holding, just from different angles (occupying versus owning).",
        ["Cornell LII"],
        indications=["Residential", "Commercial", "Cross-sector"],
        category="Title & Ownership",
    ),
    entry(
        "Rehab", "Rehabilitation",
        "An investor or developer's renovation of a property — somewhere between cosmetic touch-up and full gut renovation — done to lift value or Rent.",
        "Renovation work intended to lift property value or rentable Rent.",
        "Rehab spans light cosmetic (paint, flooring, fixtures) to heavy structural (mechanical replacement, walls, layout changes, additions). Investor business plans frame Rehab as the value-creation engine in BRRRR and value-add Multifamily strategies: buy below-market, Rehab to lift the After-Repair Value (ARV), Refinance against the new value, recycle equity into the next deal. Hard Money frequently funds the buy-and-rehab phase; permanent debt takes out the rehab loan once the property is leased and stabilised.",
        ["Investopedia"],
        indications=["Investment", "Residential", "Multifamily"],
        category="Market & Investment",
    ),
    entry(
        "Qualified Mortgage", "QM",
        "A category of Mortgage created by the Dodd-Frank Act with conservative terms — capping DTI and banning risky features — that gives Lenders a legal safe harbour.",
        "Mortgage meeting CFPB safe-harbour rules under Dodd-Frank — capped DTI, no risky features.",
        "Qualified Mortgage rules under the Dodd-Frank Act and CFPB's Regulation Z give Lenders protection from ability-to-repay lawsuits if they originate within the QM box. Original 2014 rules: DTI cap 43%, no interest-only, no negative amortisation, no balloon payment (except small Lenders), points and fees under 3% of loan. The 2020 'general QM' overhaul replaced the DTI cap with a price-based test. GSE-eligible loans automatically count as QM through the 'patch' (now expired post-2021 reforms). Non-QM lending exists but carries more litigation risk.",
        ["CFPB", "Cornell LII"],
        indications=["Residential"],
        category="Financing & Lending",
    ),
]


# ============================================================================
# BATCH 3 — Valuation depth, property-type breadth, tax & regulatory depth,
#           distress mechanics, state-specific items (50 terms)
# ============================================================================

BATCH_3_BREADTH = [
    # --- Valuation & Appraisal: the three approaches + obsolescence -------
    entry(
        "Sales Comparison Approach", "Market Approach",
        "An Appraisal method that values a property by what similar properties have recently sold for — the everyday approach for residential homes.",
        "Appraisal method valuing a property against recent sales of comparable properties.",
        "The sales comparison approach is the dominant residential Appraisal method. The Appraiser identifies three to six recent comparable sales (Comps), adjusts each upward or downward for differences in size, condition, location, age, and features, and reconciles the adjusted prices to estimate the subject's value. USPAP requires the Appraiser to bracket — using Comps that are both above and below the subject in each attribute. Strongest where there is a robust market of similar properties; weakest for unique properties or thin markets.",
        ["Appraisal Foundation", "Appraisal Institute"],
        indications=["Residential", "Commercial"],
        category="Valuation & Appraisal",
    ),
    entry(
        "Income Approach", "Income Capitalization Approach",
        "An Appraisal method that values an investment property by its expected NOI — divide NOI by Cap Rate to get value.",
        "Appraisal method valuing income property by capitalising expected NOI.",
        "The income approach dominates commercial and investment Appraisal. Two flavours. Direct capitalisation: a single year's NOI divided by a market Cap Rate produces value. Discounted Cash Flow: project annual NOI over the Hold Period, apply Discounted Cash Flow at a discount rate, add the reversion (exit Sale Price using an Exit Cap Rate), and sum to present value. Both flavours sit alongside Sales Comparison Approach for stabilised property; income approach gets primary weight for true investment assets.",
        ["Appraisal Foundation", "Appraisal Institute"],
        indications=["Commercial", "Investment", "Multifamily"],
        category="Valuation & Appraisal",
    ),
    entry(
        "Cost Approach", "Replacement Cost Approach",
        "An Appraisal method that values a property as the cost to rebuild it from scratch, minus Depreciation for age and wear, plus Land value.",
        "Appraisal method valuing improvements at replacement cost less Depreciation plus Land value.",
        "The cost approach works best for new or special-use property: a school, fire station, brand-new build, or unique property with no Comps. The Appraiser estimates the cost to construct an equivalent building today (Replacement Cost) or to reproduce the exact building (reproduction cost), subtracts accrued Depreciation (physical wear, Functional Obsolescence, External Obsolescence), and adds the Land's value to reach total value. For old, conventional property the cost approach is least reliable — accrued Depreciation estimates carry too much error.",
        ["Appraisal Foundation", "Appraisal Institute"],
        indications=["Commercial", "Residential", "Development"],
        category="Valuation & Appraisal",
    ),
    entry(
        "Highest and Best Use", "HBU",
        "The Appraiser's judgment of the most profitable, physically possible, and legally permitted use of a property — sometimes different from how it's used today.",
        "Most profitable, possible, legal, and supported use of a property as judged by the Appraiser.",
        "Highest and Best Use governs the entire Appraisal. Four tests: physically possible (Lot supports the use), legally permitted (Zoning, deed restrictions), financially feasible (market demand at viable Rents), maximally productive (highest value among feasible uses). A single-family home on a Lot zoned for higher-density Multifamily may have a higher-and-best-use as land for an apartment building — driving value above what the existing house would Sell for. Appraisers separate analysis as if vacant and as currently improved.",
        ["Appraisal Foundation", "Appraisal Institute"],
        indications=["Commercial", "Development", "Investment"],
        category="Valuation & Appraisal",
    ),
    entry(
        "Effective Age", "",
        "An Appraiser's judgment of a property's apparent age — based on condition and modernisation — rather than its calendar age.",
        "Apparent age judged from condition and updates, distinct from chronological age.",
        "A 1950 house gutted and modernised in 2022 might have an effective age of 5 years even though chronological age is 75. Effective Age drives the Depreciation deduction in the Cost Approach. A 1990 commercial building that has been kept in showroom condition could have effective age of 15; a poorly maintained 2010 building could have effective age of 25. Appraisers reconcile effective age against the property's economic life (typical service life for the type) to estimate accrued Depreciation as a percentage.",
        ["Appraisal Foundation"],
        indications=["Residential", "Commercial"],
        category="Valuation & Appraisal",
    ),
    entry(
        "Functional Obsolescence", "",
        "A loss in property value caused by outdated design, layout, or features — galleys kitchens, low ceilings, no garage, single bathrooms — that buyers no longer want.",
        "Loss in property value from outdated design, layout, or features inside the building.",
        "Functional obsolescence is the design-side cousin of physical Depreciation. Examples: 8-foot ceilings when the market expects 9-foot, single bathrooms in 4-bedroom homes, drive-through tellers in renovated banks turned offices, narrow Office floor plates that don't suit open-plan layouts, awkward elevator location. Curable functional obsolescence (the cost to fix is less than the value gained) gets accounted for as a renovation budget. Incurable functional obsolescence (cost exceeds gain) gets deducted as a value loss. Distinct from External Obsolescence (which comes from outside the property).",
        ["Appraisal Foundation", "Appraisal Institute"],
        indications=["Residential", "Commercial"],
        category="Valuation & Appraisal",
    ),
    entry(
        "External Obsolescence", "Economic Obsolescence",
        "A loss in property value caused by factors outside the property — a noisy highway next door, a dying retail strip, a declining neighbourhood — that the owner can't fix.",
        "Loss in property value from factors outside the property the owner can't change.",
        "External obsolescence is the third leg of Depreciation alongside physical wear and Functional Obsolescence. Examples: a new highway built behind a residential subdivision, an industrial plant moved next door to apartments, a regional employer's relocation gutting demand, neighbourhood decline pushing comparable values down. Always incurable from the property's perspective — the Appraiser deducts it as a value loss in the Cost Approach. The Income Approach and Sales Comparison Approach naturally pick up external obsolescence through depressed rents and falling Comps.",
        ["Appraisal Foundation", "Appraisal Institute"],
        indications=["Residential", "Commercial"],
        category="Valuation & Appraisal",
    ),

    # --- Property Types: breadth across commercial sectors --------------
    entry(
        "Hotel", "Hospitality Property",
        "A property with rooms rented by the night to travellers — Hotels are a commercial Real Estate asset class with the most volatile income of any sector.",
        "Commercial property renting rooms by the night — highest income volatility of any sector.",
        "Hotel underwriting differs from other Commercial Real Estate. Rent is set daily and reprices instantly with demand (yield management). Operating Expenses run 65-75% of revenue (versus 30-40% for Office) — labour, food and beverage, energy, brand fees, marketing. Performance metrics: ADR (Average Daily Rate), Occupancy Rate, RevPAR (Revenue per Available Room). Brand affiliation (Marriott, Hilton, Hyatt) and management contract terms matter as much as physical asset. Capital reserves run high — FF&E (furniture, fixtures, equipment) refresh cycles every 5-7 years.",
        ["NCREIF", "ULI"],
        indications=["Hospitality", "Commercial", "Investment"],
        category="Property Types",
    ),
    entry(
        "Self-Storage", "Storage Facility",
        "A property with rentable storage units for personal or business goods — small individual units rented month-to-month, low operating costs, recession-resilient.",
        "Commercial property of rentable storage units, mostly month-to-month — recession-resilient.",
        "Self-storage emerged as an institutional asset class through the 2000s and accelerated post-2010 with REITs like Public Storage, Extra Space, CubeSmart, and Life Storage. Operating Expenses are unusually low (often 25-35% of revenue) — minimal staffing (one office worker, automated gates), no Tenant Improvement, no HVAC in most unit types. Move-out cycles are constant but turnover costs are trivial. Demand is structural — household downsizing, life-event-driven (death, divorce, downsize, dislocation). Performed strongest in the sector through the 2008 recession and the 2020 pandemic.",
        ["NCREIF", "ULI"],
        indications=["Commercial", "Investment", "Specialty"],
        category="Property Types",
    ),
    entry(
        "Senior Housing", "Senior Living",
        "Residential property purpose-built for older adults — independent living, assisted living, memory care, skilled nursing — a specialty Commercial asset class.",
        "Specialty Multifamily for older adults across independent, assisted, memory care, and skilled-nursing tiers.",
        "Senior housing spans an acuity spectrum. Independent living (55+ communities, minimal services). Assisted living (meals, light medical, daily activities — most common subtype). Memory care (secured dementia units). Skilled nursing (medical care, Medicare/Medicaid reimbursed). Demand is demographically driven by ageing baby boomers. Operating intensity is high — labour 50-60% of revenue. Healthcare REITs (Welltower, Ventas, HCP) hold the largest institutional portfolios. Sector took a significant 2020-2021 hit from pandemic mortality and operating cost spikes; recovered through 2023.",
        ["NCREIF", "ULI"],
        indications=["Specialty", "Multifamily", "Investment"],
        category="Property Types",
    ),
    entry(
        "Student Housing", "Off-Campus Housing",
        "Multifamily property purpose-built for university students — typically rented by the bed rather than the unit, leased to match the academic calendar.",
        "Multifamily property built for and rented by the bed to university students.",
        "Student housing operates on a unique cycle. Pre-leasing begins in fall for the following academic year; near-full occupancy expected by spring for August move-in. Rent is quoted per bed, with shared common areas and bedrooms inside units. Parents typically co-sign or guarantee, lifting credit risk. Returns track university enrollment trends — Power 5 schools with strong enrollment growth attract institutional capital; mid-tier schools face structural decline. American Campus Communities and Education Realty Trust built the listed REIT sector; Blackstone took ACC private in 2022 for $13B.",
        ["NCREIF", "ULI"],
        indications=["Multifamily", "Specialty", "Investment"],
        category="Property Types",
    ),
    entry(
        "Mobile Home Park", "Manufactured Housing Community",
        "A property where Tenants rent the Land Lot — but own the manufactured home (mobile home) sitting on it — historically a workforce-housing asset with cult-like investor following.",
        "Property where Tenants rent the Lot but own the manufactured home — a workforce-housing asset.",
        "Mobile home parks combine the steady cash flow of Multifamily with the low operating cost of Self-Storage. The park owner provides Land, utilities, common areas, and infrastructure; the homeowner provides the dwelling. Tenants rarely move (relocating a mobile home costs $5,000-$10,000) — turnover and concessions are minimal. The sector was institutionalised in the 2010s as REITs (Sun Communities, Equity LifeStyle) consolidated mom-and-pop owners. Rent control and tenant-protection laws are tightening in several states — California, Florida, Oregon — creating regulatory risk for the asset class.",
        ["NCREIF", "Investopedia"],
        indications=["Multifamily", "Affordable", "Investment"],
        category="Property Types",
    ),
    entry(
        "Affordable Housing", "",
        "Residential property whose Rent is restricted by Land use covenants, government subsidies, or income limits to remain affordable to lower-income households.",
        "Residential property with Rent or Sale price restricted to remain affordable to lower-income households.",
        "Affordable housing in the US comes through three main channels. Federal Low-Income Housing Tax Credit (LIHTC) program — most common, subsidises new construction or substantial rehabilitation in exchange for 30+ year affordability covenants. Project-based Section 8 (HUD payments tied to specific buildings). Inclusionary Zoning (developer set-asides at below-market rents in exchange for density bonuses or fee waivers). All three carry deed restrictions or restrictive Covenants that survive ownership changes. Compliance monitoring is intense — annual income certifications, audits, and HUD inspections.",
        ["HUD", "IRS", "ULI"],
        indications=["Affordable", "Multifamily", "Public Sector"],
        category="Property Types",
    ),

    # --- Tax depth ----------------------------------------------------
    entry(
        "Section 121 Exclusion", "Primary Residence Exclusion, §121 Exclusion",
        "A federal tax break letting homeowners exclude up to $250,000 ($500,000 married filing jointly) of Capital Gain from the sale of a primary residence.",
        "Federal tax break excluding up to $250K/$500K Capital Gain on primary-residence sale.",
        "IRC §121 lets a homeowner exclude $250,000 ($500,000 married filing jointly) of Capital Gain from federal tax on the sale of a primary residence, provided the seller owned and used the home as principal residence for at least 24 months of the 60 months ending on the sale date. The exclusion can be reused every two years. Doesn't apply to investment property — that's where 1031 Exchange comes in. Partial exclusion is available for early sales due to change of employment, health, or unforeseen circumstances. The cap hasn't been adjusted for inflation since 1997 — high-price-market sellers increasingly exceed it.",
        ["IRS", "Cornell LII"],
        indications=["Residential"],
        category="Tax",
    ),
    entry(
        "Passive Loss", "Passive Activity Loss",
        "A tax loss from a Real Estate Investment that the IRS treats as passive — usable only against other passive income, not against W-2 wages.",
        "Tax loss from passive Real Estate activity, deductible only against passive income.",
        "Passive activity loss rules (IRC §469) limit how Real Estate Investment losses can shelter other income. Rentals are passive by default — even with active management. Suspended passive losses carry forward indefinitely and free up against future passive income or when the property is sold. Two key escapes. (1) Real Estate Professional status — 750+ hours and >50% of work time in Real Estate trades — converts rental losses to active, deductible against W-2. (2) $25,000 active-participation allowance for taxpayers under $150K AGI lets some rental losses offset ordinary income.",
        ["IRS", "Cornell LII"],
        indications=["Investment", "Residential"],
        category="Tax",
    ),
    entry(
        "Material Participation", "",
        "An IRS test for whether a taxpayer is actively involved enough in a business or property to escape the Passive Loss limits.",
        "IRS test for active involvement that exempts an activity from Passive Loss limitations.",
        "Material participation has seven tests under IRC §469; meeting any one qualifies. Most common: 500+ hours per year in the activity, OR substantially all participation in the activity, OR 100+ hours and no one else doing more. The hours bar combines with Real Estate Professional status to convert passive Real Estate losses to active. Material participation matters most for high-income investors trying to deduct paper losses from Bonus Depreciation against W-2 wages. IRS audits this hard — taxpayers should keep contemporaneous logs of hours.",
        ["IRS", "Cornell LII"],
        indications=["Investment", "Residential"],
        category="Tax",
    ),
    entry(
        "Real Estate Professional", "REP",
        "An IRS tax status for taxpayers spending 750+ hours and over half their working time in Real Estate trades — unlocks active deduction of rental losses against ordinary income.",
        "IRS tax status for full-time Real Estate workers, allowing active deduction of rental losses.",
        "Real Estate Professional status requires meeting both tests in IRC §469(c)(7): (1) more than half of the taxpayer's personal services in trades or businesses during the year are in Real Property trades, AND (2) 750+ hours of service in Real Property trades. Real Property trades include development, construction, brokerage, leasing, management, and operations. W-2 jobs that aren't Real Estate-related don't count. Once qualified, all rental activities can convert to active treatment (when also Materially Participating), unlocking losses against ordinary income — a major tax tool for high-income investors.",
        ["IRS", "Cornell LII"],
        indications=["Investment"],
        category="Tax",
    ),
    entry(
        "Carried Interest", "",
        "The cross-industry term for what Real Estate calls Promote — the Sponsor's share of profits above an investor return hurdle, taxed at lower long-term Capital Gain rates.",
        "Sponsor's share of profits above hurdles, taxed at long-term Capital Gain rates.",
        "Carried interest is the private-equity term that subsumes Real Estate's Promote, hedge-fund 20%, and venture-capital carry. Federal tax treats carry on holdings of three or more years as long-term Capital Gain — taxed at 20% rather than the 37% top ordinary rate. Many proposals to tax carry as ordinary income have failed (2016, 2017, 2021, 2022 negotiations). The TCJA tightened the rule by extending the holding-period threshold from 1 year to 3 years. Real Estate's typical 5-7 year Hold Period comfortably meets the 3-year bar.",
        ["IRS", "Cornell LII"],
        indications=["Investment", "Commercial"],
        category="Tax",
    ),
    entry(
        "Transfer Tax", "Real Estate Transfer Tax, Deed Tax",
        "A state or municipal tax owed when a property changes hands — calculated as a percentage of the Sale Price, usually paid at Closing.",
        "State or municipal tax on property transfers, calculated as a percentage of Sale Price.",
        "Transfer tax rates vary wildly. No transfer tax: Texas, Mississippi, Alaska, Idaho, Indiana, Louisiana, Missouri, Montana, New Mexico, North Dakota, Oregon, Utah, Wyoming. High transfer tax: Delaware (4%), Pennsylvania (2%), New York City (1.4% + state). Buyer-paid, seller-paid, or split depends on state custom — California typically seller-paid, New York buyer-paid for new construction. Mansion Tax (NYC, NJ, some others) adds an extra layer above price thresholds. Recorded with the Deed at Closing; failure to pay can cloud Title.",
        ["IRS", "Cornell LII"],
        indications=["Residential", "Commercial", "Cross-sector"],
        category="Tax",
    ),
    entry(
        "Mansion Tax", "",
        "An extra Transfer Tax on high-priced property sales — New York's is the highest-profile, layered above the standard transfer tax for sales above $1 million.",
        "Extra Transfer Tax on high-priced property sales, above standard transfer tax.",
        "New York's Mansion Tax: 1% on sales of $1M+ residential property, plus a graduated supplemental tax in NYC for sales above $2M reaching 3.9% on $25M+. New Jersey: 1% mansion tax on sales above $1M. Connecticut: graduated mansion tax up to 2.25%. The tax is the buyer's responsibility in most jurisdictions, hitting the cash-to-close calculation hard. Sellers occasionally offer concessions to offset. Politically popular as a 'tax the rich' lever; pricing levels have not been indexed for inflation, so the cap drifts down in real terms.",
        ["Cornell LII"],
        indications=["Residential"],
        category="Tax",
    ),
    entry(
        "Depreciation Recapture", "§1245 Recapture, §1250 Recapture",
        "A tax claw-back at the Sale of a depreciated property — gains attributable to prior Depreciation deductions are taxed at a higher rate than long-term Capital Gain.",
        "Tax claw-back at sale on gain previously deducted as Depreciation, at elevated rates.",
        "When a depreciated property sells, IRS recharacterises a portion of the gain as ordinary depreciation recapture rather than long-term Capital Gain. For Real Property under §1250, the recapture rate is capped at 25%. For personal-property components (carpeting, appliances, parking lot improvements identified through Cost Segregation) under §1245, recapture is at full ordinary rates — up to 37%. 1031 Exchange defers depreciation recapture along with Capital Gain. Step-up in Basis at death eliminates both.",
        ["IRS", "Cornell LII"],
        indications=["Investment", "Commercial"],
        category="Tax",
    ),

    # --- Law & Regulation: consumer & fair-lending depth ----------------
    entry(
        "ECOA", "Equal Credit Opportunity Act",
        "The federal law banning Lender discrimination based on race, religion, sex, marital status, age, or receipt of public assistance — applies to Mortgages and all consumer credit.",
        "Federal anti-discrimination law in lending — covers all protected classes in credit.",
        "Enacted 1974, codified at 15 USC §1691, implemented by CFPB's Regulation B. ECOA covers any extension of credit — Mortgages, auto loans, credit cards, business loans. Prohibited factors: race, colour, religion, national origin, sex, marital status, age (over 18), receipt of public-assistance income, exercise of consumer-protection rights. The CFPB has brought Redlining cases under ECOA against banks for branch placement, marketing, and Underwriting that disproportionately exclude minority neighbourhoods. Adverse-action notices required when an application is denied — listing specific reasons.",
        ["CFPB", "Cornell LII"],
        indications=["Residential", "Cross-sector"],
        category="Law & Regulation",
    ),
    entry(
        "HMDA", "Home Mortgage Disclosure Act",
        "The federal law requiring most Lenders to publicly report Mortgage application data — including race, income, and approval status — used by regulators to spot fair-lending violations.",
        "Federal mortgage-data disclosure law used to surface fair-lending violations.",
        "Enacted 1975. HMDA forces banks, credit unions, and most non-bank Lenders above a small threshold to report annually on each Mortgage application — geography (census tract), applicant demographics (race, ethnicity, sex, income), loan amount, action taken (approved, denied, withdrawn). CFPB publishes the data publicly. Fair-lending regulators and journalists analyse HMDA to spot disparate impact in lending. The 2015 HMDA rule expanded reporting to include pricing data — flagging high-cost loans that may reflect Steering or pricing discrimination.",
        ["CFPB", "Cornell LII"],
        indications=["Residential"],
        category="Law & Regulation",
    ),
    entry(
        "Regulation Z", "Reg Z",
        "The CFPB regulation that implements TILA — spelling out the specific disclosures, calculations, and timing every consumer Lender must follow.",
        "CFPB regulation implementing TILA — governs disclosure forms, timing, and calculations.",
        "Regulation Z lives at 12 CFR Part 1026 (formerly Federal Reserve's Regulation Z). Covers: APR calculation methodology, finance charge components, Loan Estimate and Closing Disclosure content (TRID), right of rescission for refinances (3-business-day cooling-off period), advertising rules (any rate quote triggers full disclosure), ability-to-repay and Qualified Mortgage rules under Dodd-Frank, Loan Officer compensation restrictions. Violations carry both private rights of action and CFPB enforcement. Frequent target of compliance officers, exam findings, and litigation.",
        ["CFPB", "Cornell LII"],
        indications=["Residential"],
        category="Law & Regulation",
    ),
    entry(
        "AFFH", "Affirmatively Furthering Fair Housing",
        "The Fair Housing Act provision requiring HUD funding recipients to actively work to overcome historical patterns of housing discrimination — not just refrain from discriminating.",
        "Fair Housing Act duty to actively dismantle segregation, not just refrain from discrimination.",
        "AFFH stems from Section 808 of the Fair Housing Act (1968). The 2015 Obama-era AFFH rule required local jurisdictions receiving HUD funds to conduct Assessments of Fair Housing — analysing local segregation, racially concentrated poverty, disparate access to opportunity — and adopt action plans. Trump suspended the rule in 2018, then formally repealed in 2020. Biden 2021 reinstated; the 2023 'AFFH 2.0' rule restored the assessment framework. Politically contentious — alternates with administrations. Localities historically resistant: zoning reforms that AFFH plans recommend conflict with single-family preservation.",
        ["HUD", "Cornell LII"],
        indications=["Public Sector", "Residential", "Affordable"],
        category="Law & Regulation",
    ),
    entry(
        "Blockbusting", "",
        "The illegal practice of frightening homeowners into selling cheap by claiming minorities are moving in, then reselling at higher prices to incoming buyers — a Fair Housing Act violation.",
        "Illegal Fair Housing Act practice of inducing panic sales through race-based scare tactics.",
        "Blockbusting was a structural tactic in mid-20th-century US neighbourhood turnover. Real Estate operators would buy one home in a white neighbourhood, list it to a Black family, then canvass remaining white homeowners with predictions of plummeting values, urging quick sales at below-market prices. The operator then resold at substantially higher prices to incoming Black buyers — turning neighbourhoods over within years. Banned under the Fair Housing Act since 1968. Still surfaces in subtler forms: agent solicitation flyers in 'changing' neighbourhoods, deceptive market characterisations, predatory cash-buyer outreach.",
        ["HUD", "Cornell LII"],
        indications=["Residential", "Cross-sector"],
        category="Law & Regulation",
    ),
    entry(
        "IRC", "Internal Revenue Code",
        "The federal tax code — Title 26 of the United States Code — that governs every federal tax rule touching Real Estate, from Mortgage interest deduction to 1031 Exchange.",
        "Title 26 of the US Code — the federal tax statute that governs Real Estate taxation.",
        "IRC sections that matter for Real Estate: §121 (Primary Residence Exclusion), §163 (Mortgage interest deduction), §164 (SALT deduction), §168 (Depreciation, including Bonus Depreciation), §199A (pass-through deduction), §263 (Capital Expenditure capitalisation), §469 (Passive Loss limits), §1031 (1031 Exchange), §1245/§1250 (Depreciation Recapture), §1411 (net investment income tax). Tax practitioners cite by section number constantly. The 2017 TCJA was the largest single rewrite of these sections since 1986; provisions are scheduled to sunset in 2026 absent congressional action.",
        ["IRS", "Cornell LII"],
        indications=["Investment", "Residential", "Commercial"],
        category="Tax",
    ),

    # --- Management & Operations: running an asset day-to-day -----------
    entry(
        "Property Manager", "PM",
        "The person or company that runs a Real Estate property day-to-day — handles Tenant relations, collects Rent, oversees maintenance, manages Operating Expenses.",
        "Person or firm running day-to-day operations of a Real Estate property.",
        "Property management splits into in-house (owner employs the PM) and third-party (separate management company under contract). Multifamily and Commercial Real Estate routinely use third-party PMs; small landlords often self-manage. Standard third-party fee: 3-5% of collected Rent for Multifamily, 1.5-3% for Office and Retail (negotiated lower at scale). The PM coordinates leasing, on-site staff, maintenance vendors, capital projects, financial reporting, and Tenant communications. IREM's CPM (Certified Property Manager) is the industry credential.",
        ["IREM", "BOMA"],
        indications=["Commercial", "Multifamily", "Investment"],
        category="Management & Operations",
    ),
    entry(
        "Lockbox", "Real Estate Lockbox",
        "A secure key holder mounted near a property's entrance — lets authorised Agents access vacant homes for showings without the Listing Agent physically present.",
        "Key holder mounted at a vacant home letting authorised Agents access for showings.",
        "Lockboxes accelerate the showing pipeline. Electronic lockboxes (Supra, SentriLock) dominate professional Real Estate — they log every entry by Agent ID, time, and duration. Mechanical combination lockboxes survive in lower-cost markets. The Listing Agreement typically authorises the Listing Agent to install a lockbox; sellers sometimes opt out for privacy or security. Access codes are managed through MLS membership systems with daily rotating credentials. Compromised codes are a recurring industry security issue; biometric mobile-phone-pairing lockboxes are emerging.",
        ["NAR"],
        indications=["Residential"],
        category="Management & Operations",
    ),
    entry(
        "Reserve Study", "Capital Reserve Study",
        "A professional analysis of an HOA or Condo association's long-term capital needs — Roof, HVAC, paving — and the funding required to meet them without Special Assessments.",
        "Analysis of an HOA's long-term Capital Expenditure needs and required reserve funding.",
        "Reserve studies became standard practice after high-profile assessment disputes in the 1990s. The study inventories building components (Roof, façade, paving, HVAC, elevators, pool, mechanical), estimates remaining useful life and replacement cost for each, then computes annual reserve contributions needed to fund replacements without Special Assessments. Required by statute in California, Florida, Nevada, and a growing list of states. The 2021 Surfside condo collapse intensified reserve-study scrutiny — Florida 2022 reforms mandate reserve funding for structural integrity items, no waiver permitted. Lender Underwriting increasingly looks for current reserve studies as part of HOA review.",
        ["NAHB", "IREM"],
        indications=["Residential", "Multifamily"],
        category="Management & Operations",
    ),

    # --- State-specific items -------------------------------------------
    entry(
        "Proposition 13", "Prop 13",
        "California's 1978 constitutional amendment capping Property Tax at 1% of purchase price, with annual reassessment increases limited to 2% — a structural shape of California Real Estate.",
        "California 1978 amendment capping Property Tax and limiting annual reassessment increases.",
        "Proposition 13 passed by 65% of California voters in June 1978. Three pillars: (1) Property Tax capped at 1% of assessed value. (2) Assessed value resets to market only at change of ownership or new construction — between, increases are limited to 2% per year regardless of market value. (3) Tax increases require two-thirds legislative or local-voter approval. Result: long-tenured homeowners pay a fraction of what neighbours who bought recently pay. Side effects: low residential turnover, sky-high Sale prices, lock-in effects, structural deficits in California public services. Repeal attempts repeatedly fail at the ballot box.",
        ["Cornell LII"],
        indications=["Residential"],
        category="Tax",
    ),
    entry(
        "Texas Homestead", "Homestead Exemption",
        "Texas's strong constitutional protection of a primary residence — caps Property Tax assessment growth, shields against most creditor claims, restricts forced sale.",
        "Texas constitutional protection of primary residence — tax cap, creditor shield, forced-sale restriction.",
        "Texas Homestead protections sit in Article XVI of the Texas Constitution. Three layers. Property Tax: assessed value growth on a primary residence capped at 10% per year through the Homestead exemption, plus a $40,000 (or higher) reduction in taxable value. Creditor protection: the homestead cannot be reached by most unsecured creditors — federal tax liens and Mortgages can; credit-card debt and most lawsuits cannot. Forced sale: severely restricted — only for Property Tax, Mortgage, mechanic's lien for improvements, or home-equity loans. The protection makes Texas a popular asset-protection state.",
        ["Cornell LII"],
        indications=["Residential"],
        category="Tax",
    ),
    entry(
        "Condo Conversion", "",
        "The process of turning a rental Multifamily building into individually-owned Condo units — Tenants get the right to buy their units, then the rest sell to the open market.",
        "Process converting a rental Multifamily into individually-owned Condo units.",
        "Condo conversion was a defining urban Real Estate move in the 1970s-1980s and revived periodically in hot markets. Local laws govern the process — Tenant protections (right of first refusal, relocation assistance, senior/disabled exemptions) vary widely. New York City and San Francisco have particularly tight rules. Economics work when Condo retail value per unit exceeds rental Sale Price by enough to cover conversion costs (legal, condo declaration, common-area renovation) and Tenant payouts. Tenants choosing not to buy must vacate or remain under rent-controlled terms depending on jurisdiction.",
        ["HUD", "Cornell LII"],
        indications=["Multifamily", "Residential"],
        category="Transactions",
    ),
    entry(
        "Citizens Insurance", "State-Run Insurer of Last Resort",
        "A state-created insurance company providing Homeowners Insurance in markets where private insurers won't write — Florida's is the largest, covering hurricane and flood risk many private carriers exit.",
        "State-run insurer of last resort for properties private carriers won't cover.",
        "Florida's Citizens Property Insurance Corporation, created in 2002, is the prototype. It writes Homeowners Insurance in coastal and high-risk areas where private carriers withdraw — and has grown to roughly 1.4 million policies (2024) amid hurricane-driven private-market collapse. California FAIR Plan is the wildfire equivalent (~250,000 policies, growing). Louisiana Citizens, Texas Windstorm Insurance Association similar. Premiums are state-set, often below true risk-adjusted price; deficits trigger assessments on all in-state property-insurance policyholders. Insurance of last resort by design — broader, deeper, costlier coverage than private market.",
        ["CFPB"],
        indications=["Residential"],
        category="Management & Operations",
    ),

    # --- Investment & finance depth: distress & complex structures -----
    entry(
        "Mezzanine", "Mezz, Mezzanine Debt",
        "A layer of debt that sits between senior debt and equity in the Capital Stack — higher rate than Mortgage, secured by an ownership pledge rather than the property itself.",
        "Subordinate debt secured by entity ownership pledge, sitting between senior debt and equity.",
        "Mezzanine debt fills the financing gap when a Sponsor's first Mortgage covers 50-65% LTV but the project needs 70-80% leverage. Mezz lenders take a pledge of the LLC membership interests in the property-owning entity — if Default occurs, the mezz lender forecloses on the LLC and steps into ownership without disturbing the senior Mortgage. Rates run 9-14% in 2024, with origination fees and exit fees on top. Intercreditor Agreements govern senior-versus-mezz rights at Default. Mezz preserves the senior Lender's cheap, low-LTV debt while still letting the Sponsor reach target leverage.",
        ["NCREIF", "ULI"],
        indications=["Commercial", "Investment"],
        category="Financing & Lending",
    ),
    entry(
        "Cap Rate Compression", "",
        "When investor capital flooding into Real Estate pushes purchase prices up faster than NOI grows — Cap Rates fall, meaning lower yield per dollar invested.",
        "Falling Cap Rates driven by investor demand outpacing NOI growth — yields compress.",
        "Cap Rate compression dominated 2015-2022 Commercial Real Estate. Institutional capital chasing yield in a low-interest-rate environment pushed Multifamily Going-In Cap Rates from 6% to 4% in many markets — meaning a property generating $1M of NOI sold for $25M instead of $16.7M. Aggressive Sponsor pro formas extrapolated continued compression into Exit Cap Rate assumptions; when rates spiked in 2022, compression reversed and Exit Caps widened by 100-200 basis points, gutting projected IRR on deals underwritten at peak.",
        ["NCREIF", "ULI"],
        indications=["Commercial", "Investment"],
        category="Market & Investment",
    ),
    entry(
        "NOI Growth", "",
        "The annual percentage increase in a property's NOI — the Sponsor's main lever for creating value above the going-in basis.",
        "Annual percentage increase in property NOI — main lever of Sponsor value creation.",
        "NOI growth combines several inputs. Rent growth (tracking or beating market). Vacancy reduction (closing the gap between physical and economic occupancy). Other-income growth (parking, fees, ancillary revenue). Operating Expense control (water conservation, utility submetering, vendor renegotiation). Aggressive value-add Sponsors target 4-8% annual NOI growth in Multifamily during the Hold Period; institutional Core operators target 2-3%. The math is unforgiving — a 1% NOI growth shortfall over a 5-year hold compounds to 5%+ value miss at exit, often the difference between win and loss.",
        ["NCREIF", "IREM"],
        indications=["Commercial", "Investment", "Multifamily"],
        category="Market & Investment",
    ),
    entry(
        "Discounted Cash Flow", "DCF",
        "A valuation method that projects every year's cash flow and the exit Sale Price, then discounts them back to present value using a target return rate.",
        "Valuation method discounting projected cash flows back to present value at a target rate.",
        "DCF dominates institutional Commercial Real Estate underwriting. The model projects 5-10 years of annual NOI (after Cap-Ex and Replacement Reserve), an Exit Cap Rate applied to year-N+1 NOI for reversion value, and discounts every cash flow back at a target unlevered return (often 7-12% depending on risk). The IRR that makes NPV equal zero is the deal's projected return. DCF is more sensitive than direct capitalisation to: Rent growth assumptions, Exit Cap Rate, discount rate. Sensitivity tables surround the base case. The Income Approach uses DCF as its primary methodology for stabilised property.",
        ["NCREIF", "Appraisal Institute"],
        indications=["Commercial", "Investment"],
        category="Valuation & Appraisal",
    ),
    entry(
        "Net Present Value", "NPV",
        "The value today of all future cash flows from an investment, discounted at a target return rate — a positive NPV means the investment beats the target return.",
        "Sum of all future cash flows discounted to present at a target return rate.",
        "NPV is DCF's headline output. Investors apply a discount rate equal to their required return (cost of capital, hurdle rate). If NPV is positive, the property's expected cash flows beat that hurdle; if negative, they fall short. In direct comparison terms, IRR answers 'what does this deal return' and NPV answers 'is that return high enough'. NPV depends entirely on the discount rate chosen — institutional LPs typically use 7-12% depending on strategy risk. NPV is most useful for comparing two deals against the same hurdle.",
        ["NCREIF", "Investopedia"],
        indications=["Commercial", "Investment"],
        category="Market & Investment",
    ),
    entry(
        "Distressed Asset", "Distressed Property",
        "A property whose owner can no longer service the debt or operate it profitably — opportunities for buyers with capital and patience to acquire below replacement cost.",
        "Property whose owner can't service debt or operate profitably — discount buying opportunity.",
        "Distressed assets surface in down cycles. Causes: maturity defaults (loan comes due in a high-rate environment, can't refinance), operating shortfalls (vacancy, declining Rents), sponsor mismanagement, structural obsolescence. The acquisition path varies. Direct purchase from the owner at distressed pricing. Note acquisition from the Lender (buy the Mortgage, then negotiate with the borrower or foreclose). Foreclosure auction. Deed in Lieu negotiations. REO purchases after Foreclosure. Distressed cycles (1990 Resolution Trust, 2008-2012, 2023-2024 office) generate the largest one-time Real Estate fortunes — and the largest losses for sellers.",
        ["NCREIF", "ULI"],
        indications=["Investment", "Commercial"],
        category="Market & Investment",
    ),
    entry(
        "Workout", "Loan Workout",
        "The negotiated restructuring of a Mortgage in Default — Lender and borrower agree to modified terms (rate reduction, term extension, Principal forgiveness) rather than Foreclose.",
        "Negotiated debt restructuring between Lender and defaulted borrower.",
        "Workouts cover a spectrum from light to heavy intervention. Forbearance: temporary pause in payments. Loan Modification: permanent change to rate, term, or Principal. Discounted payoff: borrower pays less than full balance in exchange for full release. Short Sale: sale below mortgage balance with Lender consent. Deed in Lieu: voluntary Title transfer to Lender. Workouts cost less than Foreclosure for both sides — saving legal fees, time, and property deterioration. Special Servicers in the CMBS world handle distressed Loans on behalf of bondholders. The 2008-2012 cycle made the term and practice mainstream.",
        ["CFPB", "Investopedia"],
        indications=["Residential", "Commercial", "Cross-sector"],
        category="Financing & Lending",
    ),
    entry(
        "Forbearance", "",
        "A temporary pause or reduction in Mortgage payments granted by the Lender during a borrower hardship — repayment is deferred but still owed.",
        "Temporary lender-approved pause or reduction in Mortgage payments during borrower hardship.",
        "Forbearance differs from Loan Modification — it's temporary, not permanent. Common in three scenarios: natural disaster (federal disaster declarations trigger automatic forbearance offers from federally backed Loans), economic shock (the 2020 CARES Act allowed up to 18 months of forbearance on federally backed Mortgages), individual hardship (job loss, medical). Repayment options at the end: lump sum (rarely used), repayment plan (catch-up over months), Loan Modification rolling missed payments into Principal, partial claim (FHA buys back missed payments). Credit reporting is paused or suppressed during the forbearance.",
        ["CFPB", "Fannie Mae"],
        indications=["Residential"],
        category="Financing & Lending",
    ),
    entry(
        "Loan Modification", "Mortgage Modification",
        "A permanent change to a Mortgage's terms — rate reduction, term extension, Principal forgiveness — designed to keep a struggling borrower in their home.",
        "Permanent restructuring of Mortgage terms to keep a struggling borrower in their home.",
        "Loan modifications became mainstream after 2008 through programs like HAMP (Home Affordable Modification Program, 2009-2016). Common modification levers: extend term to 30 or 40 years to lower payment, reduce Interest rate to current market, capitalise arrears into Principal, partial Principal forgiveness (rare, expensive for Lender). The borrower must demonstrate sustained hardship, then pass a trial-payment period (typically 3 months at the modified rate) before the modification becomes permanent. Federal programs require strict net-present-value tests — modification must cost Lender less than projected Foreclosure recovery.",
        ["CFPB", "HUD"],
        indications=["Residential"],
        category="Financing & Lending",
    ),

    # --- Title & Ownership: warranty/marketability ---------------------
    entry(
        "Marketable Title", "",
        "A Title clear enough of defects that a reasonably prudent buyer would accept it — the standard buyers can demand and Title Insurance helps ensure.",
        "Title clear enough of defects that a reasonably prudent buyer would accept it.",
        "Marketable title doesn't mean perfect title — it means clear of defects that would deter a reasonable buyer. Typical marketability bars: undisclosed Easements affecting use, off-record claims, gaps in the Chain of Title, unreleased prior Mortgages, unresolved Liens. Each state's Marketable Title Act (most states have one) lets the buyer reach back a statutory period (40 years, often) and treat anything older than that as cleared. Title companies issue marketable-title commitments before Closing; defects must be cured or insured around before funding. Purchase contracts typically require marketable title at Closing.",
        ["ALTA", "Cornell LII"],
        indications=["Residential", "Commercial"],
        category="Title & Ownership",
    ),
    entry(
        "Cloud on Title", "Title Cloud",
        "A pending claim or defect that makes Title less than marketable — anything from an unreleased Lien to a heir contesting Probate to a forged Deed in the chain.",
        "Pending claim or defect that makes Title less than marketable.",
        "Clouds on title surface in title searches: unreleased Mortgages from prior owners, Liens that never got removed, deceased owners whose interest never transferred, forgeries, Adverse Possession claims, missing signatures on historical Deeds, recordings under wrong legal description. Curing a cloud might mean: tracking down a prior owner for a release, filing Quitclaim Deeds from heirs, court-ordered Quiet Title actions, statutory cure proceedings. Title Insurance covers some clouds the title search missed; uncured clouds disclosed at Closing typically delay or kill the transaction.",
        ["ALTA", "Cornell LII"],
        indications=["Residential", "Commercial"],
        category="Title & Ownership",
    ),
    entry(
        "Special Warranty Deed", "Limited Warranty Deed",
        "A Deed where the seller warrants only the period of their own ownership — not the full Chain of Title — common in commercial transactions and tax sales.",
        "Deed warranting only against defects arising during seller's ownership, not prior chain.",
        "Special Warranty Deed is the middle ground between Warranty Deed (broad warranties going back forever) and Quitclaim Deed (no warranties at all). The grantor warrants only against defects that arose during their ownership — not defects predating it. Common in: commercial transactions where the seller refuses unlimited indemnification, tax sales (the state never had earlier history to warrant), estate sales by executors. Buyers protect against pre-grantor defects via Title Insurance. Texas, Florida, and some Western states call this 'Special Warranty Deed' as the dominant residential conveyance form, blurring the residential convention elsewhere.",
        ["ALTA", "Cornell LII"],
        indications=["Commercial", "Residential"],
        category="Title & Ownership",
    ),

    # --- Sale & Leaseback ---------------------------------------------
    entry(
        "Sale-Leaseback", "Sale-Leaseback Transaction",
        "A transaction where the property owner sells the building and simultaneously signs a long-term Lease to stay as a Tenant — freeing capital while keeping operational use.",
        "Owner-occupier sells the property and simultaneously becomes long-term Tenant under a Lease.",
        "Sale-leasebacks are a Commercial Real Estate financing tool. The owner (often a corporate operating business) frees up trapped capital by selling Real Estate to an investor (often a Triple Net Lease REIT) and signs a 10-25 year NNN Lease back at market or above-market Rent. Common in: retail chains, industrial manufacturing, healthcare, hotel operators. Tax considerations are complex — TCJA limits on rent deductibility for sale-leasebacks with above-market Rent. Lease-versus-buy analysis weighs the cost of capital trade-off. STORE Capital, Spirit Realty Capital, and Realty Income built large portfolios around sale-leaseback origination.",
        ["NCREIF", "Investopedia"],
        indications=["Commercial", "Investment"],
        category="Transactions",
    ),
    entry(
        "Trustee", "",
        "A neutral party holding legal Title to a property until a debt is paid — the structural role in a Deed of Trust in states that use that financing form instead of a Mortgage.",
        "Neutral third party holding legal Title under a Deed of Trust until the loan is repaid.",
        "In Deed of Trust states (California, Texas, Virginia, much of the West), a third-party Trustee holds bare legal Title while the borrower has equitable Title and possession. The Lender is the Beneficiary. On Default, the Trustee can conduct a non-judicial Foreclosure under the power-of-sale clause — substantially faster and cheaper than judicial Foreclosure in Mortgage states. Typical Trustees: title companies, trust companies, attorneys. The Trustee's duties are largely ministerial — record releases when loans are paid, conduct sales when Default occurs.",
        ["Cornell LII", "ALTA"],
        indications=["Residential", "Commercial"],
        category="Title & Ownership",
    ),
    entry(
        "Beneficiary", "",
        "The Lender named in a Deed of Trust — the party entitled to be paid back, with the right to direct the Trustee to Foreclose on Default.",
        "The Lender in a Deed of Trust — entitled to repayment and Foreclosure-direction rights.",
        "In a Deed of Trust, the Beneficiary is the Lender — the party entitled to repayment of the Mortgage. When the borrower pays in full, the Beneficiary directs the Trustee to record a reconveyance, clearing Title. When the borrower defaults, the Beneficiary directs the Trustee to commence non-judicial Foreclosure under the power-of-sale clause. Loan servicing rights can be sold; the new servicer becomes Beneficiary of record. In estate-planning Trusts and Title Insurance escrow trusts, 'beneficiary' refers to the person entitled to receive trust assets — same word, different mechanism.",
        ["Cornell LII"],
        indications=["Residential", "Commercial"],
        category="Title & Ownership",
    ),
    entry(
        "Concessions", "Lease Concessions, Rent Concessions",
        "Free or discounted Rent and other incentives Landlords offer to attract Tenants — months free, reduced Security Deposit, gift cards, TI allowances above market.",
        "Discounts or freebies Landlords offer to attract Tenants — months free, reduced deposit, TI bumps.",
        "Concessions surge in soft Lease-up markets and disappear in tight ones. Multifamily: 1-2 months free on a 12-month Lease is a typical recession-era concession (effectively 8-17% Rent discount net of the free months). Office and Retail: above-market Tenant Improvement allowances, free Rent periods of 6-12+ months on long Leases. Economic occupancy distinguishes properties running market-rate Rent from those papering over with concessions — physical occupancy can be 95% while effective occupancy is 80%. Underwriting models 'effective Rent' net of concessions, not 'face Rent'.",
        ["NCREIF", "IREM"],
        indications=["Commercial", "Multifamily"],
        category="Leasing",
    ),
]


BATCHES = {
    1: BATCH_1_FOUNDATIONS,
    2: BATCH_2_DEPTH,
    22: BATCH_2B_PAIRED_FIXES,  # post-batch-2 paired-entry fixes
    3: BATCH_3_BREADTH,
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
