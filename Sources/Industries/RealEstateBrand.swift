import SwiftUI

let realEstateBrand = Brand(
    appStoreName: "JB Real Estate",
    displayName: "JB Real Estate",
    navigationTitle: "JB Real Estate",
    titlePrefix: "JB",
    titleBody: "Real Estate",
    subtitle: "decoding property jargon",
    tagline: nil,
    entryNoun: "entries",
    dataResource: "glossary_realEstate",
    primaryColor: Color(red: 0.659, green: 0.349, blue: 0.243),       // #A8593E earthy clay
    primaryDarkColor: Color(red: 0.475, green: 0.243, blue: 0.165),   // #793E2A deeper clay
    bgColor: PGColors.bg,
    urlScheme: "realEstate",
    aboutParagraphs: [
        "JB Real Estate is a generalist's reference for the language of property — residential and commercial, lending and leasing, valuation, title, development, tax, and the regulatory plumbing underneath. The jargon you encounter when you buy or rent a home, sign a lease, sit through a closing, evaluate a deal, or read a syndication memo.",
        "Entries summarise publicly available material from federal housing agencies, industry trade bodies, and standards organisations. They are written for orientation in plain English, not as legal, tax, or investment advice."
    ],
    aboutDisclaimer: "Educational reference. Not real estate, legal, tax, or investment advice. US-focused; rules vary by state and city.",
    aboutSources: [
        BrandSource(
            heading: "Federal housing & lending agencies",
            items: ["HUD", "FHA", "Fannie Mae", "Freddie Mac", "Ginnie Mae", "FHFA", "VA", "USDA Rural Housing"]
        ),
        BrandSource(
            heading: "Consumer protection & financial regulation",
            items: ["CFPB", "FDIC", "OCC", "IRS"]
        ),
        BrandSource(
            heading: "Industry associations & standards",
            items: ["NAR", "MBA", "Appraisal Institute", "Appraisal Foundation", "CCIM Institute", "IREM", "ULI", "BOMA", "NAHB", "ALTA", "NCREIF", "Nareit"]
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
            subtitle: "Foundational real estate vocabulary",
            kind: .allowlist([
                // Residential ownership & buying
                "Real Estate", "Real Property", "Personal Property", "Fixture",
                "Deed", "Title", "Title Insurance", "Escrow", "Closing", "Closing Costs",
                "Down Payment", "Earnest Money", "Appraisal", "Inspection",
                "Pre-approval", "Pre-qualification",
                // Mortgages
                "Mortgage", "Fixed-Rate Mortgage", "Adjustable-Rate Mortgage",
                "Principal", "Interest", "Amortization", "Refinance",
                "FHA Loan", "VA Loan", "Conventional Loan", "Jumbo Loan",
                "PMI", "Loan-to-Value", "Debt-to-Income Ratio", "Credit Score",
                "Foreclosure", "Short Sale",
                // Title & ownership
                "Fee Simple", "Easement", "Encumbrance", "Lien",
                "Joint Tenancy", "Tenancy in Common", "Adverse Possession",
                "Warranty Deed", "Quitclaim Deed",
                // Leasing
                "Lease", "Landlord", "Tenant", "Rent", "Sublease", "Eviction",
                "Security Deposit", "Holdover Tenant",
                // Costs & carrying
                "Property Tax", "Homeowners Insurance", "HOA",
                "CC&Rs", "Condo", "Co-op",
                // Investment foundations
                "Cap Rate", "NOI", "Gross Rental Income", "Operating Expenses",
                "IRR", "Equity Multiple", "Cash-on-Cash Return",
                "REIT", "1031 Exchange",
                // Market structure
                "MLS", "Comp", "Listing Agent", "Buyer's Agent",
                "Commission", "Zoning", "Building Code"
            ])
        ),
        LensConfig(
            id: "residential",
            glyph: "R",
            title: "Residential",
            subtitle: "For homebuyers, renters, and homeowners",
            kind: .categoryFilter(
                categories: [
                    "Financing & Lending",
                    "Transactions",
                    "Title & Ownership",
                    "Tax",
                    "Law & Regulation"
                ],
                excludedTerms: []
            )
        ),
        LensConfig(
            id: "commercial",
            glyph: "C",
            title: "Commercial & Investment",
            subtitle: "Cap rates, NOI, syndication, underwriting",
            kind: .categoryFilter(
                categories: [
                    "Valuation & Appraisal",
                    "Market & Investment",
                    "Leasing",
                    "Development",
                    "Management & Operations"
                ],
                excludedTerms: []
            )
        )
    ],
    accentTint: nil,
    sourceURLs: [
        // Federal housing & lending agencies
        "HUD":                      URL(string: "https://www.hud.gov")!,
        "FHA":                      URL(string: "https://www.hud.gov/program_offices/housing/fhahistory")!,
        "Fannie Mae":               URL(string: "https://www.fanniemae.com")!,
        "Freddie Mac":              URL(string: "https://www.freddiemac.com")!,
        "Ginnie Mae":               URL(string: "https://www.ginniemae.gov")!,
        "FHFA":                     URL(string: "https://www.fhfa.gov")!,
        "VA":                       URL(string: "https://www.va.gov/housing-assistance/")!,
        "USDA Rural Housing":       URL(string: "https://www.rd.usda.gov/programs-services/single-family-housing-programs")!,
        // Consumer protection & financial regulation
        "CFPB":                     URL(string: "https://www.consumerfinance.gov")!,
        "FDIC":                     URL(string: "https://www.fdic.gov")!,
        "OCC":                      URL(string: "https://www.occ.gov")!,
        "IRS":                      URL(string: "https://www.irs.gov")!,
        // Industry associations & standards
        "NAR":                      URL(string: "https://www.nar.realtor")!,
        "MBA":                      URL(string: "https://www.mba.org")!,
        "Appraisal Institute":      URL(string: "https://www.appraisalinstitute.org")!,
        "Appraisal Foundation":     URL(string: "https://appraisalfoundation.org")!,
        "CCIM Institute":           URL(string: "https://www.ccim.com")!,
        "IREM":                     URL(string: "https://www.irem.org")!,
        "ULI":                      URL(string: "https://uli.org")!,
        "BOMA":                     URL(string: "https://www.boma.org")!,
        "NAHB":                     URL(string: "https://www.nahb.org")!,
        "ALTA":                     URL(string: "https://www.alta.org")!,
        "NCREIF":                   URL(string: "https://www.ncreif.org")!,
        "Nareit":                   URL(string: "https://www.reit.com")!,
        // Reference works
        "Investopedia":             URL(string: "https://www.investopedia.com")!,
        "Cornell LII":              URL(string: "https://www.law.cornell.edu")!
    ]
)
