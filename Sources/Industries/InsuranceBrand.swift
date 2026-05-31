import SwiftUI

let insuranceBrand = Brand(
    appStoreName: "JB Insurance",
    displayName: "JB Insurance",
    navigationTitle: "JB Insurance",
    titlePrefix: "JB",
    titleBody: "Insurance",
    subtitle: "decoding insurance jargon",
    tagline: nil,
    entryNoun: "entries",
    dataResource: "glossary_insurance",
    primaryColor: Color(red: 0.110, green: 0.365, blue: 0.420),       // #1C5D6B deep teal
    primaryDarkColor: Color(red: 0.078, green: 0.271, blue: 0.310),   // #14454F deeper teal
    bgColor: PGColors.bg,
    urlScheme: "insurance",
    aboutParagraphs: [
        "JB Insurance is a generalist's reference for the language of risk and protection — the premiums, deductibles, claims, and fine print behind life, health, auto, home, and business cover, plus the underwriting, actuarial, reinsurance, and regulatory machinery underneath. The jargon you meet when you choose a health plan, file a claim, read a homeowners policy, shop for life cover, or sit across from an adjuster.",
        "Entries summarise publicly available material from US insurance regulators, actuarial bodies, and industry trade groups. They are written for orientation in plain English, not as insurance, legal, tax, or financial advice."
    ],
    aboutDisclaimer: "Educational reference. Not insurance, legal, tax, or financial advice. US-focused; rules vary by state.",
    aboutSources: [
        BrandSource(
            heading: "Regulators & government",
            items: ["NAIC", "FIO", "CMS", "DOL", "FEMA"]
        ),
        BrandSource(
            heading: "Actuarial & standards bodies",
            items: ["SOA", "CAS", "AAA", "Verisk"]
        ),
        BrandSource(
            heading: "Ratings & market",
            items: ["AM Best", "Lloyd's"]
        ),
        BrandSource(
            heading: "Industry associations",
            items: ["III", "NAMIC", "APCIA"]
        ),
        BrandSource(
            heading: "Reference works",
            items: ["Investopedia", "Cornell LII"]
        )
    ],
    lenses: [
        LensConfig(
            id: "basics",
            glyph: "B",
            title: "Basics",
            subtitle: "Foundational insurance vocabulary",
            kind: .allowlist([
                // Core mechanics
                "Premium", "Deductible", "Coverage", "Policy", "Claim",
                "Policyholder", "Insurer", "Insured", "Named Insured",
                "Beneficiary", "Claimant", "Underwriting", "Actuary",
                "Peril", "Hazard", "Indemnity", "Liability", "Risk",
                "Exclusion", "Endorsement", "Rider", "Coinsurance", "Copay",
                "Subrogation", "Reinsurance", "Loss Ratio", "Policy Limit",
                "Declarations Page", "Grace Period", "Lapse", "Binder",
                "Premium", "Quote", "Actual Cash Value", "Replacement Cost",
                // Lines of business
                "Life Insurance", "Health Insurance", "Auto Insurance",
                "Homeowners Insurance", "Renters Insurance", "Disability Insurance",
                "Liability Insurance", "Term Life Insurance", "Whole Life Insurance",
                "Annuity", "Umbrella Insurance", "Flood Insurance",
                // Health-plan basics
                "Premium Tax Credit", "Out-of-Pocket Maximum", "HMO", "PPO",
                "Network", "Formulary", "Prior Authorization", "Open Enrollment",
                // Auto / home specifics
                "Collision Coverage", "Comprehensive Coverage", "Liability Coverage",
                "Dwelling Coverage", "Personal Liability",
                // People & process
                "Agent", "Broker", "Adjuster", "Loss", "Settlement",
                "Cash Value", "Beneficiary", "Premium Finance"
            ])
        ),
        LensConfig(
            id: "policies",
            glyph: "P",
            title: "Policies & Claims",
            subtitle: "Coverage, claims, liability, and health benefits",
            kind: .categoryFilter(
                categories: [
                    "Coverage & Policies",
                    "Claims & Settlement",
                    "Law & Liability",
                    "Health & Benefits"
                ],
                excludedTerms: []
            )
        ),
        LensConfig(
            id: "risk",
            glyph: "R",
            title: "Risk & Pricing",
            subtitle: "Underwriting, actuarial pricing, and risk transfer",
            kind: .categoryFilter(
                categories: [
                    "Underwriting & Risk",
                    "Pricing & Actuarial",
                    "Reinsurance & Risk Transfer"
                ],
                excludedTerms: []
            )
        ),
        LensConfig(
            id: "markets",
            glyph: "M",
            title: "Markets & Regulation",
            subtitle: "Solvency, regulation, and how cover is sold",
            kind: .categoryFilter(
                categories: [
                    "Regulation & Solvency",
                    "Distribution & Markets"
                ],
                excludedTerms: []
            )
        )
    ],
    accentTint: nil,
    sourceURLs: [
        // Regulators & government
        "NAIC":          URL(string: "https://www.naic.org")!,
        "FIO":           URL(string: "https://home.treasury.gov/policy-issues/financial-markets-financial-institutions-and-fiscal-service/federal-insurance-office")!,
        "CMS":           URL(string: "https://www.cms.gov")!,
        "DOL":           URL(string: "https://www.dol.gov/agencies/ebsa")!,
        "FEMA":          URL(string: "https://www.fema.gov/flood-insurance")!,
        // Actuarial & standards bodies
        "SOA":           URL(string: "https://www.soa.org")!,
        "CAS":           URL(string: "https://www.casact.org")!,
        "AAA":           URL(string: "https://www.actuary.org")!,
        "Verisk":        URL(string: "https://www.verisk.com")!,
        // Ratings & market
        "AM Best":       URL(string: "https://www.ambest.com")!,
        "Lloyd's":       URL(string: "https://www.lloyds.com")!,
        // Industry associations
        "III":           URL(string: "https://www.iii.org")!,
        "NAMIC":         URL(string: "https://www.namic.org")!,
        "APCIA":         URL(string: "https://www.apci.org")!,
        // Reference works
        "Investopedia":  URL(string: "https://www.investopedia.com")!,
        "Cornell LII":   URL(string: "https://www.law.cornell.edu")!
    ]
)
