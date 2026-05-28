import SwiftUI

let pharmaBrand = Brand(
    appStoreName: "JB Healthcare Glossary",
    displayName: "JB Healthcare",
    navigationTitle: "JB Healthcare",
    titlePrefix: "JB",
    titleBody: "Healthcare",
    subtitle: "decoding healthcare jargon",
    tagline: nil,
    entryNoun: "entries",
    dataResource: "glossary_pharma",
    primaryColor: Color(red: 0.545, green: 0.180, blue: 0.122),       // #8B2E1F oxblood
    primaryDarkColor: Color(red: 0.467, green: 0.137, blue: 0.094),   // deeper oxblood
    bgColor: PGColors.bg,
    urlScheme: "pharma",
    aboutParagraphs: [
        "JB Healthcare is a generalist's reference for the language of healthcare — the drugs, biology, regulation, payers, and public-health jargon you encounter in news, earnings calls, regulatory filings, and conferences.",
        "Entries summarize publicly available information from the authoritative sources listed below. They are written for orientation, not for clinical decision-making."
    ],
    aboutDisclaimer: "This is reference material. It is not medical advice.",
    aboutSources: [
        BrandSource(
            heading: "US health agencies",
            items: ["FDA — Food and Drug Administration",
                    "NIH — National Institutes of Health",
                    "NCI — National Cancer Institute",
                    "NHGRI — National Human Genome Research Institute",
                    "CDC — Centers for Disease Control and Prevention",
                    "CMS — Centers for Medicare & Medicaid Services",
                    "HRSA — Health Resources and Services Administration"]
        ),
        BrandSource(
            heading: "International",
            items: ["WHO — World Health Organization",
                    "EMA — European Medicines Agency",
                    "ICH — International Council for Harmonisation"]
        ),
        BrandSource(
            heading: "Health economics & access",
            items: ["ICER — Institute for Clinical and Economic Review",
                    "ISPOR — Professional Society for Health Economics and Outcomes Research"]
        )
    ],
    lenses: [
        LensConfig(
            id: "basics",
            glyph: "B",
            title: "Basics",
            subtitle: "Foundational biology & chemistry",
            kind: .allowlist([
                // Already present
                "RNA", "Mutation", "siRNA", "Ligand", "Receptor", "Agonist", "Antagonist",
                "MAb", "Apoptosis", "Insulin",
                // Mol bio
                "DNA", "Gene", "Genome", "Chromosome", "Allele", "Codon", "Nucleotide",
                "Base Pair", "Transcription", "Translation",
                "mRNA", "tRNA", "rRNA", "miRNA",
                // Protein/enzyme
                "Protein", "Peptide", "Amino Acid", "Alanine", "Glycine", "Lysine",
                "Enzyme", "Antibody", "Antigen", "Epitope", "Immunoglobulin",
                // Cell
                "Cell", "Nucleus", "Mitochondria", "Ribosome", "Endoplasmic Reticulum",
                "Golgi Apparatus", "Cytoplasm", "Cell Membrane", "Mitosis", "Meiosis",
                // Chemistry
                "Atom", "Molecule", "Ion", "Isotope", "Isomer", "Polymer", "Monomer",
                "Hydrogen Bond", "Covalent Bond", "Acid", "Base", "pH", "Buffer",
                // Physiology
                "Hormone", "Neurotransmitter", "Cytokine", "Chemokine", "Lipid",
                "Fatty Acid", "Cholesterol", "Triglyceride", "Carbohydrate", "Glucose",
                "Glycogen", "Metabolism", "ATP", "Glycolysis", "Krebs Cycle"
            ])
        ),
        LensConfig(
            id: "policy",
            glyph: "P",
            title: "Policy",
            subtitle: "Regulation, pricing, access",
            kind: .categoryFilter(
                categories: ["Regulatory", "Commercial / Market Access", "Health Systems & Payers"],
                excludedTerms: ["MSL", "Loss of Exclusivity", "Patent Cliff", "NCI", "HEOR", "Gross-to-Net", "Phase 4"]
            )
        )
    ],
    accentTint: Color(red: 0.784, green: 0.714, blue: 0.541),          // #C8B68A editorial complement
    sourceURLs: [
        "NCI Dictionary of Cancer Terms": URL(string: "https://www.cancer.gov/publications/dictionaries/cancer-terms")!,
        "FDA":              URL(string: "https://www.fda.gov")!,
        "NIH":              URL(string: "https://www.nih.gov")!,
        "NIH MedlinePlus":  URL(string: "https://medlineplus.gov")!,
        "CMS Glossary":     URL(string: "https://www.cms.gov/apps/glossary")!,
        "NHGRI":            URL(string: "https://www.genome.gov")!,
        "NIH NIMH":         URL(string: "https://www.nimh.nih.gov")!,
        "CDC":              URL(string: "https://www.cdc.gov")!,
        "WHO":              URL(string: "https://www.who.int")!,
        "NIH NIA":          URL(string: "https://www.nia.nih.gov")!,
        "ICH GCP":          URL(string: "https://www.ich.org/page/efficacy-guidelines")!,
        "HRSA":             URL(string: "https://www.hrsa.gov")!,
        "ISPOR":            URL(string: "https://www.ispor.org")!,
        "ICER":             URL(string: "https://icer.org")!,
        "ICH E9":           URL(string: "https://www.ich.org/page/efficacy-guidelines")!,
        "CMS":              URL(string: "https://www.cms.gov")!,
        "EMA":              URL(string: "https://www.ema.europa.eu")!,
        "ICH":              URL(string: "https://www.ich.org")!,
        "NCI":              URL(string: "https://www.cancer.gov")!,
    ]
)
