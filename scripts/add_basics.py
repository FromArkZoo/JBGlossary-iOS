"""Append 65 foundational biology/chemistry terms to glossary.json.

Idempotent: skips entries whose `term` already exists (case-insensitive match).
Sorts the final list by (letter asc, term asc) for stable output.
"""
import json
from pathlib import Path

GLOSSARY = Path(__file__).parent.parent / "PharmaGlossary" / "Resources" / "glossary.json"


def entry(term, full, snappy, detail, sources, indications=None, plain=""):
    """Build an entry dict. Letter is derived from the term's first character."""
    letter = term[0].upper()
    return {
        "letter": letter,
        "term": term,
        "full": full,
        "plain": plain,
        "snappy": snappy,
        "detail": detail,
        "indications": indications or ["General"],
        "category": "Mechanism",
        "sources": sources,
    }


# ============================================================================
# BATCH 1 — Molecular biology core (14)
# ============================================================================
BATCH_MOL_BIO = [
    entry(
        "DNA", "Deoxyribonucleic Acid",
        "The double-helix molecule that stores the genetic instructions for building and running every living thing.",
        "DNA is a long chain of four chemical letters — A, T, G, C — twisted into the famous double helix discovered by Watson and Crick in 1953. Stretches of DNA called genes encode the proteins that do the work of the cell. Modern medicine reads, writes, and edits DNA: gene therapy delivers corrected DNA, CRISPR rewrites it, and sequencing reads it cheaply enough to be a routine clinical test.",
        ["NHGRI", "NIH"],
    ),
    entry(
        "Gene", "",
        "A stretch of DNA that contains the recipe for one specific protein (or RNA molecule) that does a job in the body.",
        "Humans have roughly 20,000 protein-coding genes, far fewer than scientists once expected. A defective gene can cause disease — sickle cell, cystic fibrosis, hemophilia — and gene therapies like Luxturna and Zolgensma deliver working copies to fix the underlying cause. You'll hear 'gene' constantly in pharma: gene panels for diagnosis, gene targets for new drugs, gene editing for next-gen therapies.",
        ["NHGRI"],
    ),
    entry(
        "Genome", "",
        "The complete set of DNA in an organism — every gene plus all the non-coding stretches in between.",
        "The human genome was first fully sequenced in 2003 at a cost of about $3 billion; today it costs a few hundred dollars. Whole-genome sequencing is becoming standard in oncology to match patients to targeted therapies, and in rare disease to identify the single mutation causing an unexplained illness. Companies like Illumina, Pacific Biosciences, and Oxford Nanopore make the machines that read genomes at industrial scale.",
        ["NHGRI"],
    ),
    entry(
        "Chromosome", "",
        "A tightly packaged bundle of DNA — humans have 23 pairs, including the X and Y that determine biological sex.",
        "Each chromosome contains hundreds to thousands of genes wound around scaffold proteins called histones. Extra or missing chromosomes cause major syndromes: an extra chromosome 21 causes Down syndrome, and broken chromosomes drive many cancers — the Philadelphia chromosome behind chronic myeloid leukemia gave rise to Gleevec, one of pharma's iconic targeted therapies.",
        ["NHGRI"],
    ),
    entry(
        "Allele", "",
        "One of the alternative versions of a gene — for instance, the gene for eye color comes in blue, brown, green, and other alleles.",
        "Most humans inherit two alleles per gene, one from each parent. Some alleles are dominant (one copy is enough to show the trait), some recessive (you need both copies). Pharmacogenomics — tailoring drugs to a patient's specific alleles — is becoming routine: certain CYP2D6 alleles, for example, change how fast people metabolize codeine, antidepressants, and beta-blockers.",
        ["NHGRI"],
    ),
    entry(
        "Codon", "",
        "A three-letter 'word' of DNA or RNA that codes for one amino acid in a protein.",
        "There are 64 possible codons (4 letters × 4 × 4) and 20 amino acids, so the genetic code is redundant — multiple codons can specify the same amino acid. Three codons mean 'stop translating here.' A single-letter typo that changes a codon can cause disease: the mutation behind sickle cell anemia swaps one codon, changing one amino acid in hemoglobin.",
        ["NHGRI"],
    ),
    entry(
        "Nucleotide", "",
        "The single chemical letter that makes up DNA and RNA — chain millions of them together and you get a genome.",
        "Each nucleotide has three parts: a sugar, a phosphate, and one of four bases (A, T, G, C in DNA; A, U, G, C in RNA). When pharma talks about 'oligonucleotide' drugs — antisense therapies, siRNAs, mRNA vaccines — these are short stretches of synthetic nucleotides designed to silence, replace, or instruct genes. The chemistry of modifying nucleotides for stability is one of the unsung breakthroughs behind modern RNA medicine.",
        ["NIH"],
    ),
    entry(
        "Base Pair", "",
        "Two DNA letters paired across the helix — A always with T, G always with C — like a rung on a twisted ladder.",
        "The human genome is about 3 billion base pairs long. The strict pairing rules (A-T, G-C) mean each strand of DNA carries the full information needed to copy the other, which is how cells faithfully replicate their DNA before dividing. Sequencing technology reads off the base pairs one at a time, and editing tools like CRISPR can swap one base pair for another with single-letter precision (base editing).",
        ["NHGRI"],
    ),
    entry(
        "Transcription", "",
        "The first step of using a gene: cells copy a stretch of DNA into a mobile RNA message that can leave the nucleus.",
        "Transcription is the gateway to making any protein. Enzymes called RNA polymerases read DNA and produce a complementary mRNA strand, which then gets translated into protein elsewhere. Many drugs work by tweaking transcription — corticosteroids, for example, change which genes get transcribed in immune cells. 'Transcription factors' are the master regulators that switch genes on and off, and they're a big drug-discovery frontier (historically considered 'undruggable,' now slowly opening up).",
        ["NIH"],
    ),
    entry(
        "Translation", "",
        "The second step of using a gene: ribosomes read an mRNA message and assemble the protein it specifies, amino acid by amino acid.",
        "Translation happens at ribosomes, which scan along the mRNA three letters at a time and grab the matching amino acid for each codon. Several major antibiotics — tetracyclines, macrolides like azithromycin, and aminoglycosides — work by jamming bacterial ribosomes and stopping translation. Disrupting human translation is a newer frontier in oncology, where rapidly dividing cancer cells are unusually dependent on protein synthesis.",
        ["NIH"],
    ),
    entry(
        "mRNA", "Messenger RNA",
        "The working copy of a gene — a short-lived RNA message that ferries instructions from the DNA archive to the protein-making machinery.",
        "mRNA was the unsung hero of the COVID-19 response: Pfizer/BioNTech's Comirnaty and Moderna's Spikevax both deliver synthetic mRNA encoding the spike protein, which your cells briefly produce to train your immune system. The platform is now being applied to flu, RSV, cancer vaccines, and rare-disease protein replacement. Moderna and BioNTech own most of the IP and manufacturing know-how.",
        ["NIH", "FDA"],
    ),
    entry(
        "tRNA", "Transfer RNA",
        "The little adapter molecules that physically deliver each amino acid to the ribosome during protein assembly.",
        "Each tRNA carries one specific amino acid and recognizes the matching codon on the mRNA — they're the dictionary that turns a three-letter codon into a real amino acid. Cells have dozens of different tRNAs. Disorders of tRNA metabolism cause a growing list of mitochondrial and neurological diseases, and tRNA-based therapeutics (e.g., for cystic fibrosis nonsense mutations) are an emerging biotech frontier.",
        ["NIH"],
    ),
    entry(
        "rRNA", "Ribosomal RNA",
        "The structural and catalytic RNA that makes up the bulk of the ribosome — the protein-synthesis machine itself.",
        "Despite the name 'protein synthesis,' it's actually rRNA — not protein — that catalyzes the chemical bond-forming step inside ribosomes. Bacterial rRNA differs enough from human rRNA that drugs can selectively poison bacterial ribosomes without harming us; that's the basis for entire antibiotic classes. Sequencing rRNA (especially the 16S gene in bacteria) is the foundation of modern microbiome research.",
        ["NIH"],
    ),
    entry(
        "miRNA", "MicroRNA",
        "Tiny RNA molecules — about 22 letters long — that fine-tune which genes get expressed by silencing matching mRNAs.",
        "miRNAs were discovered in 1993 and won the 2024 Nobel Prize in Medicine. Each miRNA can regulate hundreds of genes, and abnormal miRNA patterns are a hallmark of cancer and many chronic diseases. miRNA-based diagnostics (looking at circulating miRNA in blood) are in development for early cancer detection, and several miRNA-targeting drugs have entered clinical trials.",
        ["NIH"],
    ),
]


# ============================================================================
# BATCH 2 — Proteins, enzymes, immune molecules (11)
# ============================================================================
BATCH_PROTEIN = [
    entry(
        "Protein", "",
        "The molecular workhorses of the cell — long chains of amino acids that fold into precise shapes to do almost every job in the body.",
        "There are tens of thousands of distinct proteins in the human body: enzymes that catalyze reactions, antibodies that fight infection, hemoglobin that carries oxygen, collagen that holds tissues together, the receptors and channels on cell surfaces. Most modern drugs work by binding a specific protein to switch its activity on or off. Biologics — including all monoclonal antibodies, insulin, and clotting factors — are themselves proteins, manufactured in bioreactors.",
        ["NIH"],
    ),
    entry(
        "Peptide", "",
        "A short chain of amino acids — basically a tiny protein, usually under 50 amino acids long.",
        "Peptide drugs sit between small molecules and full-size protein biologics: easier to manufacture than antibodies, more selective than small molecules. Insulin (51 amino acids) is the original peptide drug; modern blockbusters include the GLP-1 agonists Ozempic/Wegovy (semaglutide) and Mounjaro/Zepbound (tirzepatide), all peptides delivered by weekly injection. Oral peptide formulations (Rybelsus) are an active development frontier.",
        ["NIH", "FDA"],
    ),
    entry(
        "Amino Acid", "",
        "The 20 chemical building blocks that proteins are made of — string them together in different orders and you get every protein in nature.",
        "Nine of the 20 amino acids are 'essential' — your body can't make them, so you have to get them from food. Genetic code dictates the order amino acids are linked together for each protein, and that order determines how the protein folds and what it does. Single amino-acid changes from a mutation can be devastating: sickle cell, cystic fibrosis, and many cancers all trace to a swap of one amino acid in one critical protein.",
        ["NIH"],
    ),
    entry(
        "Alanine", "",
        "One of the 20 standard amino acids — small, simple, and the second-most-common in the average protein.",
        "Alanine is non-essential (your body makes it from pyruvate) and used by muscle to shuttle nitrogen to the liver via the alanine cycle. In drug design, swapping a residue to alanine ('alanine scanning') is a classic technique for figuring out which amino acid in a protein matters most for binding to a target.",
        ["NIH"],
    ),
    entry(
        "Glycine", "",
        "The smallest amino acid — just a hydrogen atom for its side chain — and a major inhibitory neurotransmitter in the spinal cord.",
        "Because glycine is so small, it lets protein chains bend and pivot in ways no other amino acid permits; it's overrepresented at hinges in protein structures. Glycine receptors are the target of strychnine poisoning and a focus of research into chronic pain. Glycine is also a building block of glutathione, the body's main antioxidant.",
        ["NIH"],
    ),
    entry(
        "Lysine", "",
        "An essential amino acid with a positively charged side chain — important for collagen, calcium absorption, and immune function.",
        "Lysine residues on proteins are favorite spots for chemical modifications that regulate function: acetylation, methylation, ubiquitination. Cancer drugs targeting lysine modifications — HDAC inhibitors like vorinostat, EZH2 inhibitors like Tazverik — are an established class. Lysine is also a common conjugation site for antibody-drug conjugates, where the linker chemistry attaches to lysines on the antibody backbone.",
        ["NIH"],
    ),
    entry(
        "Enzyme", "",
        "A protein that speeds up a specific chemical reaction in the body without being used up itself — biology's catalysts.",
        "Enzymes drive every metabolic process: digestion, DNA replication, signal transduction, drug metabolism. Many drugs are 'enzyme inhibitors' — statins block HMG-CoA reductase to lower cholesterol; ACE inhibitors block angiotensin-converting enzyme to lower blood pressure; protease inhibitors block HIV's protease enzyme. Enzyme replacement therapies (Cerezyme, Aldurazyme) treat rare metabolic diseases where patients lack a working copy of one critical enzyme.",
        ["NIH"],
    ),
    entry(
        "Antibody", "",
        "A Y-shaped protein the immune system makes to recognize and neutralize a specific foreign target — a virus, a toxin, a cancer marker.",
        "Each antibody binds one specific target (the antigen) with extraordinary precision. Pharma has industrialized antibody production: monoclonal antibodies — Humira, Keytruda, Dupixent, Opdivo — are some of the best-selling drugs in history, generating tens of billions in annual revenue. They're manufactured in large bioreactors using engineered mammalian cells, and the high cost of making them is a perennial theme in drug-pricing debates.",
        ["NIH", "FDA"],
    ),
    entry(
        "Antigen", "",
        "Anything the immune system recognizes as foreign and mounts a response against — most commonly a protein on a virus, bacterium, or tumor cell.",
        "Vaccines work by exposing the immune system to an antigen (or instructions to make one, in mRNA vaccines) so it learns to recognize the real pathogen later. In oncology, 'tumor antigens' are the cancer-specific markers that immunotherapies and cell therapies (CAR-T) train the immune system to attack — CD19 on B-cell leukemias, BCMA on multiple myeloma, HER2 on certain breast cancers.",
        ["NIH"],
    ),
    entry(
        "Epitope", "",
        "The exact patch on an antigen that an antibody actually grabs onto — usually just a few amino acids' worth of surface.",
        "A single antigen can have multiple epitopes, and different antibodies target different ones. 'Epitope mapping' is a routine step in antibody drug development to confirm where on a target protein an antibody binds. The fast-evolving spike-protein epitopes of SARS-CoV-2 are why successive COVID variants escaped earlier antibodies and required updated vaccines.",
        ["NIH"],
    ),
    entry(
        "Immunoglobulin", "Ig",
        "The technical name for an antibody — comes in five flavors (IgG, IgA, IgM, IgD, IgE) that handle different jobs in the immune system.",
        "IgG is the most abundant in blood and the format used for nearly all therapeutic monoclonal antibodies. IgE drives allergic reactions and is the target of Xolair (omalizumab). IgA dominates at mucosal surfaces (gut, airways). 'IVIG' — pooled human immunoglobulin given by IV — is a treatment for many autoimmune and immunodeficiency conditions and is one of the most lucrative blood-derived products globally.",
        ["NIH"],
    ),
]


# ============================================================================
# BATCH 3 — Cell biology (10)
# ============================================================================
BATCH_CELL = [
    entry(
        "Cell", "",
        "The smallest unit of life — the building block every tissue, organ, and organism is made of.",
        "Humans have roughly 30 trillion cells in about 200 distinct types: neurons, skin cells, immune cells, liver cells, and so on. Most drugs ultimately act inside or on the surface of cells. Cell therapy — engineering and infusing living cells as a drug — is one of pharma's hottest frontiers: CAR-T cancer therapies (Kymriah, Yescarta), stem-cell treatments, and TIL therapies (Amtagvi) all deliver living cells rather than molecules.",
        ["NIH"],
    ),
    entry(
        "Nucleus", "",
        "The cell's command center — the membrane-bound compartment that houses the chromosomes and where DNA is read and copied.",
        "The nucleus is the defining feature of eukaryotic cells (animals, plants, fungi) and what separates them from bacteria. Many drugs target processes that happen in the nucleus: chemotherapies that damage DNA, hormone therapies whose receptors travel into the nucleus to switch genes on or off, and emerging gene-editing tools like CRISPR that have to physically enter the nucleus to reach their target.",
        ["NIH"],
    ),
    entry(
        "Mitochondria", "",
        "The cell's power plants — small organelles that burn glucose and fat to produce ATP, the energy currency of every living thing.",
        "Mitochondria have their own small genome — a relic of their origin as ancient bacteria absorbed by larger cells billions of years ago — which means they can have their own mutations causing 'mitochondrial diseases' (a major focus in pediatric rare-disease drug development). Many cancer drugs target mitochondrial pathways, and mitochondrial damage from drugs like statins and certain antiretrovirals explains some of their best-known side effects.",
        ["NIH"],
    ),
    entry(
        "Ribosome", "",
        "The molecular machine that builds proteins by reading mRNA and stringing together amino acids in the right order.",
        "Each cell has millions of ribosomes, all working in parallel. They're made mostly of rRNA with some scaffold proteins. Several major antibiotic classes — macrolides, tetracyclines, aminoglycosides, oxazolidinones — work by gumming up bacterial ribosomes while leaving human ribosomes alone. New oncology research targets the human ribosome as a vulnerability in fast-growing cancers.",
        ["NIH"],
    ),
    entry(
        "Endoplasmic Reticulum", "ER",
        "A maze of membranes inside the cell where proteins destined for the cell surface or for export get folded, modified, and quality-checked.",
        "When the ER gets overwhelmed with misfolded proteins, it triggers the 'unfolded protein response' — a stress signal implicated in diabetes, neurodegeneration, and cancer. ER stress is a hot drug target. Cystic fibrosis 'modulator' drugs like Trikafta work in part by helping the misfolded CFTR protein get past ER quality control and reach the cell surface.",
        ["NIH"],
    ),
    entry(
        "Golgi Apparatus", "",
        "The cell's shipping department — a stack of flattened sacs that processes, packages, and sorts proteins before sending them to their final destinations.",
        "Many secreted proteins get their sugar coatings (glycosylation) added in the Golgi, and getting glycosylation right is one of the hardest parts of manufacturing biologics — a key reason why biosimilars are not exactly identical to the originator drugs and need their own clinical trials. Disorders of Golgi function cause a growing list of rare 'congenital disorders of glycosylation.'",
        ["NIH"],
    ),
    entry(
        "Cytoplasm", "",
        "The jelly-like fluid that fills the inside of a cell, holding all the organelles and where most of the cell's chemistry happens.",
        "Cytoplasm is where glycolysis happens, where most protein synthesis occurs, and where signaling cascades from cell-surface receptors get relayed inward. When pharma talks about whether a drug is 'cell-permeable,' they mean: can it cross the cell membrane and reach targets in the cytoplasm? Most small molecules can; most biologics (antibodies, peptides) cannot, which limits them to extracellular or surface targets.",
        ["NIH"],
    ),
    entry(
        "Cell Membrane", "",
        "The thin oily skin around every cell — controls what gets in and out and is studded with receptors and channels for sensing the outside world.",
        "Cell membranes are made of a phospholipid bilayer with embedded proteins. The surface receptors on cell membranes — GPCRs, kinase receptors, ion channels — are the targets of about half of all approved drugs. Cell membranes are also a barrier: getting drugs across them (or designing drug-delivery systems like lipid nanoparticles for mRNA vaccines) is an entire field of pharmaceutical science.",
        ["NIH"],
    ),
    entry(
        "Mitosis", "",
        "How a cell divides into two identical daughter cells — the engine behind growth, healing, and (when it runs out of control) cancer.",
        "Mitosis copies the chromosomes and pulls them apart into two new nuclei. Many of the oldest chemotherapy drugs — vinblastine, paclitaxel (Taxol), the platinum agents — work by jamming mitosis in fast-dividing cells. The trade-off: they also hit normal fast-dividing cells in hair, gut, and bone marrow, which causes the classic chemo side effects.",
        ["NIH"],
    ),
    entry(
        "Meiosis", "",
        "The special form of cell division that makes sperm and eggs — chromosomes get shuffled and the count is halved so kids inherit one set from each parent.",
        "Errors in meiosis are the source of most chromosomal disorders: Down syndrome (extra chromosome 21), Turner syndrome, Klinefelter syndrome. The 'crossing over' that happens in meiosis is the reason siblings look different — it shuffles parental DNA at random. Meiosis defects in egg quality with maternal age are a major driver of the success rates that IVF clinics quote.",
        ["NIH"],
    ),
]


# ============================================================================
# BATCH 4 — Chemistry (13)
# ============================================================================
BATCH_CHEM = [
    entry(
        "Atom", "",
        "The smallest unit of an element — protons, neutrons, and electrons arranged in a tiny solar-system-like structure.",
        "Everything in pharma is ultimately atoms: a small-molecule drug typically has 20-50 atoms, a protein biologic has tens of thousands. The arrangement of atoms determines what a drug binds to and what it does. Modern computational chemistry simulates drug-protein interactions one atom at a time, and AI-driven drug discovery (Insilico, Recursion, Iambic) leans on this atom-level simulation.",
        ["NIH"],
    ),
    entry(
        "Molecule", "",
        "Two or more atoms held together by chemical bonds — water, glucose, aspirin, DNA, antibodies all are molecules of varying sizes.",
        "Pharma divides drugs into 'small molecules' (generally under 900 daltons in molecular weight, like aspirin or atorvastatin — orally available, factory-synthesized) and 'large molecules' or biologics (antibodies, proteins, nucleic acids — usually injected, made in living cells). The economics of these two categories are completely different: small molecules go generic cheaply, biologics face complex biosimilar competition.",
        ["NIH"],
    ),
    entry(
        "Ion", "",
        "An atom or molecule with an electrical charge because it has lost or gained electrons — sodium, calcium, and potassium ions are the ones biology cares about most.",
        "Cells use ion gradients across membranes to fire nerve signals, contract muscles, and trigger insulin release. Ion-channel drugs are a huge pharma category: calcium-channel blockers for blood pressure (amlodipine, diltiazem), sodium-channel blockers as anesthetics and antiarrhythmics, potassium-channel modulators in diabetes (sulfonylureas) and seizures.",
        ["NIH"],
    ),
    entry(
        "Isotope", "",
        "Versions of the same element that differ only in how many neutrons they have — chemically identical, but some are radioactive.",
        "Pharma uses isotopes for two big things. Radiolabeled isotopes power diagnostic and therapeutic radiopharmaceuticals — PET tracers for imaging, and actinium-225 or lutetium-177 conjugates that deliver radiation directly to tumor cells (Pluvicto for prostate cancer is a recent blockbuster). Stable heavy isotopes (deuterium) are used in 'deuterated' drugs like Austedo, where swapping hydrogen for deuterium can slow metabolism and improve dosing.",
        ["NIH", "FDA"],
    ),
    entry(
        "Isomer", "",
        "Molecules with the same chemical formula but different 3D shapes — and often dramatically different effects in the body.",
        "The classic cautionary tale is thalidomide: one isomer was a sedative, the other caused devastating birth defects, and the original drug was a 50-50 mix. Modern drug development almost always isolates a single 'enantiomer' (mirror-image isomer) to avoid this. Switching from a racemic mixture to a single enantiomer is a common life-cycle-extension play — Lexapro is the active enantiomer of Celexa, Nexium is the active enantiomer of Prilosec.",
        ["FDA"],
    ),
    entry(
        "Polymer", "",
        "A long molecule made by linking many small repeating units (monomers) together — proteins, DNA, starch, plastics are all polymers.",
        "In pharma, synthetic polymers underpin drug delivery: PLGA microspheres for sustained-release injectables (long-acting antipsychotics, GLP-1s in development), polyethylene glycol (PEGylation) attached to proteins to extend their circulation time, and polymer-based hydrogels for ocular implants. The lipid 'polymers' in mRNA vaccines' lipid nanoparticles are arguably one of the most consequential pharma polymer applications of the past decade.",
        ["FDA"],
    ),
    entry(
        "Monomer", "",
        "The single repeating subunit that gets chained together to form a polymer — amino acids are the monomers of proteins, nucleotides of DNA.",
        "When biotech engineers a new protein or RNA drug, they're choosing the order of the monomer building blocks. Synthetic monomer chemistry also matters in pharma: the monomers in PEG, PLGA, and lipid nanoparticles all have to be carefully purified and characterized for regulatory approval. Trace impurities at the monomer stage can cause downstream issues with drug stability or immunogenicity.",
        ["FDA"],
    ),
    entry(
        "Hydrogen Bond", "",
        "A weak chemical attraction between a hydrogen atom and certain neighboring atoms — individually small, but biology stacks them by the millions to hold things together.",
        "Hydrogen bonds are what zip the two strands of the DNA double helix together, what makes water behave like water, and what drives the precise folding of every protein. In drug design, getting the right pattern of hydrogen bonds between drug and target is often the difference between a tight-binding clinical candidate and an inactive molecule. AI-driven structure-based design is essentially an industrial-scale optimization of hydrogen-bond patterns.",
        ["NIH"],
    ),
    entry(
        "Covalent Bond", "",
        "A strong chemical bond where two atoms share electrons — the glue holding most biological molecules together.",
        "Most drugs bind their targets reversibly, but a growing class of 'covalent inhibitors' forms a permanent covalent bond with the target. Examples include aspirin (covalently modifies COX enzymes), the proton-pump inhibitors (Nexium, Prilosec), and several KRAS inhibitors in oncology (Lumakras, Krazati). Covalent drugs can be exquisitely selective and long-lasting but require careful safety design to avoid off-target reactivity.",
        ["FDA"],
    ),
    entry(
        "Acid", "",
        "A chemical that releases hydrogen ions in water — sour-tasting, often corrosive, and central to many physiological processes.",
        "Stomach acid (hydrochloric acid, pH ~1.5-3.5) is one of the most concentrated acids in nature, and managing it is a multi-billion-dollar pharma category — H2 blockers (famotidine), proton-pump inhibitors (omeprazole, esomeprazole). 'Acidosis' (blood too acidic) is a medical emergency. Drug formulators care about acidity because the protonation state of a molecule changes its solubility and how it gets absorbed.",
        ["NIH"],
    ),
    entry(
        "Base", "",
        "The chemical opposite of an acid — accepts hydrogen ions, often slippery to the touch, and balances the body's pH.",
        "In biology, 'base' has two unrelated meanings: chemistry bases (like sodium bicarbonate, antacids) and DNA bases (the four letters A, T, G, C). Pharma cares about both. Many drugs are weak bases or weak acids, and their behavior in the body — absorption, distribution, excretion — depends heavily on the local pH at each step.",
        ["NIH"],
    ),
    entry(
        "pH", "",
        "A 0-14 scale for how acidic or basic something is — 7 is neutral, lower is more acidic, higher is more basic.",
        "Different parts of the body sit at different pH: blood at 7.35-7.45, stomach at 1.5-3.5, urine 4.5-8. Drug absorption depends heavily on pH because it changes whether a molecule is charged or neutral. Tumor microenvironments tend to be slightly acidic, which has been exploited in some 'pH-sensitive' antibody and nanoparticle designs that release their payload only in the tumor.",
        ["NIH"],
    ),
    entry(
        "Buffer", "",
        "A chemical mixture that resists changes in pH — what keeps your blood at a precise 7.4 even when you eat, exercise, or hold your breath.",
        "Blood's main buffer system is bicarbonate, regulated by the lungs (CO2) and kidneys. Pharmaceutical formulations almost always include buffers to keep the drug stable at a specific pH during storage and infusion. Choice of buffer can affect injection-site comfort and drug stability — Humira's reformulation to a citrate-free buffer in 2018 was a big deal for patients who'd previously found injections painful.",
        ["FDA"],
    ),
]


# ============================================================================
# BATCH 5 — Physiology and biochemistry (15)
# ============================================================================
BATCH_PHYSIO = [
    entry(
        "Hormone", "",
        "A chemical messenger released by one tissue that travels through the bloodstream to give instructions to distant tissues.",
        "Insulin, thyroid hormone, cortisol, estrogen, testosterone, growth hormone — these and dozens of others coordinate metabolism, growth, reproduction, and stress responses. Hormone replacement and hormone-blocking drugs are entire pharma franchises: insulin and GLP-1s in diabetes, levothyroxine for thyroid, anti-estrogens (tamoxifen, fulvestrant) and anti-androgens (enzalutamide) in cancer, GnRH analogs in fertility and prostate cancer.",
        ["NIH"],
    ),
    entry(
        "Neurotransmitter", "",
        "A chemical messenger that nerve cells use to talk to each other across the tiny gap between them.",
        "Serotonin, dopamine, norepinephrine, GABA, glutamate, acetylcholine — these are the workhorses, and most CNS drugs work by tweaking their levels or receptor activity. SSRIs raise serotonin, antipsychotics block dopamine, benzodiazepines amplify GABA, ketamine and esketamine block glutamate's NMDA receptor. The neurotransmitter framework explains why pharmacology in psychiatry, neurology, and pain medicine all rests on a relatively small number of molecular systems.",
        ["NIH"],
    ),
    entry(
        "Cytokine", "",
        "A small signaling protein released by immune cells to coordinate inflammation, infection response, and immune-cell communication.",
        "Cytokines are the targets of many of the biggest-selling biologics: TNF-alpha (blocked by Humira, Enbrel, Remicade in autoimmune disease), IL-6 (blocked by Actemra in rheumatoid arthritis and COVID), IL-17 (blocked by Cosentyx, Taltz in psoriasis), IL-23 (blocked by Skyrizi, Tremfya). 'Cytokine storm' — runaway cytokine release — is the dangerous overshoot that drives the worst outcomes in severe COVID and CAR-T side effects.",
        ["NIH"],
    ),
    entry(
        "Chemokine", "",
        "A specific subfamily of cytokines whose job is to summon immune cells to a particular location — they're the 'come here' signals of inflammation.",
        "Chemokines and their receptors steer immune cells through tissues during infection, wound healing, and (problematically) tumor growth and metastasis. Maraviroc — an HIV drug — works by blocking the CCR5 chemokine receptor. Mogamulizumab targets the chemokine receptor CCR4 in T-cell lymphomas. Chemokine pathways are a perennial drug-discovery target in autoimmunity and oncology.",
        ["NIH", "FDA"],
    ),
    entry(
        "Lipid", "",
        "Fats and fat-related molecules — cholesterol, triglycerides, phospholipids — that store energy, build cell membranes, and act as signaling molecules.",
        "Cardiovascular drugs aimed at lipids are one of pharma's all-time biggest categories: statins (Lipitor, Crestor) for cholesterol, fibrates and omega-3s for triglycerides, PCSK9 inhibitors (Repatha, Praluent) and the newer Inclisiran for hard-to-treat high cholesterol. Lipid nanoparticles are also the delivery vehicle that made mRNA vaccines possible at scale.",
        ["NIH", "FDA"],
    ),
    entry(
        "Fatty Acid", "",
        "The long carbon chains that make up most of the lipids in your body — saturated and unsaturated, depending on the chemical bonds.",
        "Omega-3 fatty acids (EPA, DHA from fish oil) are the basis of Vascepa (icosapent ethyl), shown in REDUCE-IT to lower cardiovascular events. Free fatty acids in blood are a marker of metabolic health. Drugs that change how the body burns fat (rather than how it stores it) are an active research area in obesity and NASH/MASH (where Madrigal's Rezdiffra became the first approved drug in 2024).",
        ["NIH", "FDA"],
    ),
    entry(
        "Cholesterol", "",
        "A waxy lipid your body needs in small amounts — for cell membranes and to make hormones — but trouble in large amounts in the wrong places.",
        "LDL ('bad') cholesterol is the lab number that drives statin prescribing — the higher it is, the higher cardiovascular risk, and lowering it pharmacologically reduces heart attacks and strokes. Statins were the bestselling drug class in pharma history. PCSK9 inhibitors and Inclisiran target the same lipid pathway via different mechanisms, and oral PCSK9 inhibitors are in late-stage development.",
        ["NIH"],
    ),
    entry(
        "Triglyceride", "",
        "The chemical form most fat is stored in — three fatty acids attached to a glycerol backbone — and a separate cardiovascular risk factor from cholesterol.",
        "High triglycerides are associated with metabolic syndrome and pancreatitis at extreme levels. Vascepa (icosapent ethyl, a purified omega-3) and various fibrates lower triglycerides. The newer ANGPTL3 inhibitor Evkeeza (evinacumab) lowers both LDL and triglycerides in patients with rare genetic lipid disorders.",
        ["NIH", "FDA"],
    ),
    entry(
        "Carbohydrate", "",
        "Sugars and starches — your body's preferred quick-burn fuel and the main thing your blood glucose levels respond to.",
        "Carbohydrate metabolism is the central drama of diabetes: type 2 diabetes is fundamentally a problem of how the body handles glucose. SGLT2 inhibitors (Jardiance, Farxiga) cause the kidneys to dump excess glucose into urine. Carbohydrate counting is a daily practice for anyone on insulin. Drugs that slow carbohydrate absorption (acarbose, miglitol) were once a class of their own but have been largely supplanted by GLP-1s and SGLT2s.",
        ["NIH"],
    ),
    entry(
        "Glucose", "",
        "The simple sugar your cells run on — when blood glucose is too high (diabetes) or too low (hypoglycemia), things go badly.",
        "Glucose metering — fingersticks and now continuous glucose monitors (Dexcom, Abbott's Libre) — is the daily reality of type 1 and increasingly type 2 diabetes. Insulin lowers glucose; GLP-1 agonists, SGLT2 inhibitors, metformin, and sulfonylureas all reduce blood glucose by different mechanisms. Glucose is also the raw material that gets metabolized through glycolysis to make ATP.",
        ["NIH"],
    ),
    entry(
        "Glycogen", "",
        "The storage form of glucose — long branching chains kept in liver and muscle for quick-access fuel.",
        "Liver glycogen is what keeps your blood sugar steady between meals; muscle glycogen powers exertion. 'Glycogen storage diseases' are rare inherited conditions where one of the enzymes for handling glycogen is missing — Pompe disease (treated with Sanofi's Lumizyme/Nexviazyme and now newer enzyme replacements) is the best-known example.",
        ["NIH"],
    ),
    entry(
        "Metabolism", "",
        "All the chemical reactions in your body that turn food into energy and building blocks — and that also break down (or activate) the drugs you take.",
        "Drug metabolism is dominated by liver enzymes, especially the cytochrome P450 family — CYP3A4, CYP2D6, CYP2C19. Genetic variation in these enzymes makes some people 'fast metabolizers' and others 'slow metabolizers' of common drugs, which is why pharmacogenomic testing is becoming routine before prescribing certain antidepressants, anticoagulants, and cancer drugs. Drug-drug interactions are mostly stories about one drug inducing or inhibiting another's metabolism.",
        ["NIH", "FDA"],
    ),
    entry(
        "ATP", "Adenosine Triphosphate",
        "The energy currency of every cell — your body makes and uses your body weight in ATP every day.",
        "ATP powers muscle contraction, nerve firing, biosynthesis, and active transport across membranes. Nearly all of it comes from breaking down glucose and fat in mitochondria. Many cancer cells reorganize their metabolism around ATP supply, and drugs that disrupt these reprogrammed pathways are a growing oncology focus. ATP-competitive kinase inhibitors — drugs that block enzymes by occupying their ATP-binding pocket — are an entire major class of cancer therapy.",
        ["NIH"],
    ),
    entry(
        "Glycolysis", "",
        "The series of chemical steps that breaks one glucose molecule into two pyruvates, with a small ATP payoff and no oxygen needed.",
        "Glycolysis is biology's fastest way to get energy from glucose, which is why it's revved up in cancer cells (the 'Warburg effect'). PET imaging exploits this: tumors greedily take up the radiolabeled glucose analog FDG, making them light up on scans. Drugs that target glycolytic enzymes specifically in cancer cells are an active research area but have struggled to deliver clinical wins.",
        ["NIH"],
    ),
    entry(
        "Krebs Cycle", "Citric Acid Cycle / TCA Cycle",
        "The mitochondrial chemical loop that finishes burning the products of glycolysis to extract most of the ATP from glucose and fat.",
        "Discovered by Hans Krebs in 1937, this cycle is universal across aerobic life. Several Krebs cycle intermediates are now recognized as signaling molecules with roles in cancer (succinate, fumarate, 2-hydroxyglutarate). The IDH mutations that drive certain leukemias and gliomas distort the Krebs cycle, and IDH inhibitors (Tibsovo, Idhifa) are an FDA-approved targeted-therapy class built on this insight.",
        ["NIH"],
    ),
]


def main():
    all_new = BATCH_MOL_BIO + BATCH_PROTEIN + BATCH_CELL + BATCH_CHEM + BATCH_PHYSIO
    print(f"Drafted {len(all_new)} new entries")

    existing = json.loads(GLOSSARY.read_text())
    existing_terms_lower = {t["term"].lower() for t in existing}

    to_add = []
    skipped = []
    for e in all_new:
        if e["term"].lower() in existing_terms_lower:
            skipped.append(e["term"])
        else:
            to_add.append(e)

    print(f"  → adding: {len(to_add)}")
    print(f"  → skipping (already present): {len(skipped)}: {skipped}")

    merged = existing + to_add
    # Sort by (letter, term) for stable diffs
    merged.sort(key=lambda t: (t["letter"], t["term"].lower()))

    GLOSSARY.write_text(json.dumps(merged, indent=2, ensure_ascii=False) + "\n")
    print(f"  → wrote {len(merged)} total entries to {GLOSSARY.name}")


if __name__ == "__main__":
    main()
