"""Append compound medical terms to glossary.json.

These are high-frequency phrases that appear in existing entry detail text
(disease subtypes, cell types, trial phases, treatment modalities) but lack
their own entries — so the linker either grabs a misleading substring (e.g.
"cell" inside "non-small-cell lung cancer") or leaves the phrase unlinked.
Adding them as standalone entries lets the existing longest-match-wins linker
do the right thing.

Idempotent: skips entries whose `term` already exists (case-insensitive match).
Sorts the final list by (letter asc, term asc) for stable output.
"""
import json
from pathlib import Path

GLOSSARY = Path(__file__).parent.parent / "PharmaGlossary" / "Resources" / "glossary.json"


def entry(term, full, snappy, detail, sources, indications, category="Mechanism", plain=""):
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
# DISEASE SUBTYPES — cancer, rare disease, GI, ID, cardio
# ============================================================================
DISEASES = [
    entry(
        "Non-Small-Cell Lung Cancer", "NSCLC",
        "The most common form of lung cancer (about 85% of cases) — split into adenocarcinoma, squamous, and large-cell subtypes.",
        "NSCLC is where most precision oncology drama plays out: targetable mutations like EGFR, ALK, ROS1, KRAS G12C, and MET each have approved targeted therapies, and PD-1/PD-L1 immunotherapy (Keytruda, Opdivo) is now standard in many lines. Companies routinely segment NSCLC trials by mutation status — a Keytruda earnings discussion will sound completely different from a Tagrisso one even though they're both NSCLC drugs.",
        ["NCI Dictionary of Cancer Terms", "NIH"],
        ["Oncology"], "Clinical",
    ),
    entry(
        "Small-Cell Lung Cancer", "SCLC",
        "The aggressive 15% of lung cancers — fast-growing, strongly tied to smoking, and historically chemo-only.",
        "SCLC's natural history is grim: it spreads early and chemo response is usually short-lived. Recent additions are atezolizumab (Tecentriq) and durvalumab (Imfinzi) added to chemo, plus the DLL3-targeting bispecific tarlatamab (Imdelltra) approved 2024 — the first novel mechanism in this space in decades. SCLC commentary on biotech earnings calls focuses heavily on novel targets because the unmet need is so high.",
        ["NCI Dictionary of Cancer Terms"],
        ["Oncology"], "Clinical",
    ),
    entry(
        "Hemophilia A", "",
        "An inherited bleeding disorder caused by missing or defective Factor VIII — almost exclusively affects males via X-linked inheritance.",
        "Hemophilia A is the more common form (about 80% of hemophilia cases). Standard care is recombinant Factor VIII infusions; Hemlibra (emicizumab) revolutionized treatment with subcutaneous prophylaxis. Gene therapy arrived in 2023 with BioMarin's Roctavian, the first one-time gene therapy for the condition. The hemophilia franchise is one of the highest-revenue rare-disease categories in pharma.",
        ["NIH", "FDA"],
        ["Rare Disease"], "Clinical",
    ),
    entry(
        "Hemophilia B", "",
        "The Factor IX-deficient form of hemophilia — about 20% of hemophilia cases, also X-linked, also predominantly male.",
        "Treatment paralleled hemophilia A historically (Factor IX replacement instead of VIII), then leapt ahead in 2022 when CSL/uniQure's Hemgenix became the first FDA-approved gene therapy for any form of hemophilia, with a $3.5M price tag making it one of the most expensive drugs ever launched. Pfizer's Beqvez followed in 2024. Hemophilia B is a smaller market than A but a key proof-point for the AAV gene-therapy platform.",
        ["NIH", "FDA"],
        ["Rare Disease"], "Clinical",
    ),
    entry(
        "Duchenne Muscular Dystrophy", "DMD",
        "A devastating X-linked genetic disease that destroys muscle tissue progressively — boys typically lose the ability to walk by their early teens.",
        "DMD is caused by mutations in the dystrophin gene, the largest gene in the human genome. The space has been one of the most contentious in biotech: Sarepta's exon-skipping drugs (Exondys 51, Vyondys 53, Amondys 45) got approved despite controversial efficacy data, and their gene therapy Elevidys won full FDA approval in 2024 after a complicated review. DMD investment commentary is dominated by FDA flexibility, parent advocacy pressure, and the unmet need vs trial-design tension.",
        ["NIH", "FDA"],
        ["Rare Disease", "Neurology"], "Clinical",
    ),
    entry(
        "Cystic Fibrosis", "CF",
        "A genetic disease that thickens mucus in the lungs and pancreas — devastating in earlier eras, transformed by recent CFTR-modulator drugs.",
        "Vertex Pharmaceuticals essentially owns the CF franchise: Trikafta (elexacaftor/tezacaftor/ivacaftor) became standard of care for ~90% of patients and turned a brutal pediatric disease into something far more manageable. The Trikafta franchise generates ~$10B annually. Vertex's next-gen vanzacaftor combo and casgevy gene-edited approaches keep the pipeline rolling. CF is a textbook example of how targeted small-molecule chemistry can rewrite a disease.",
        ["NIH", "FDA"],
        ["Rare Disease", "Respiratory"], "Clinical",
    ),
    entry(
        "Sickle Cell Anemia", "",
        "An inherited blood disorder where a single mutation causes red cells to deform into a rigid sickle shape, blocking blood vessels and causing crippling pain crises.",
        "Sickle cell affects millions globally, mostly people of African ancestry. After decades of underinvestment, 2023 brought two competing gene therapies: Vertex/CRISPR Therapeutics' Casgevy (the first CRISPR-edited drug ever approved) and bluebird bio's Lyfgenia. Both run ~$2.2-3.1M with intensive transplant-style preparation. Adavosertib (Oxbryta) was withdrawn 2024 over mortality data — a setback for the small-molecule approach.",
        ["NIH", "FDA"],
        ["Rare Disease"], "Clinical",
    ),
    entry(
        "Multiple Sclerosis", "MS",
        "An autoimmune disease where the immune system attacks the myelin coating around nerves, causing fatigue, numbness, vision problems, and mobility loss.",
        "MS treatment ranges from older interferons (Avonex, Rebif) to oral options (Tecfidera, Gilenya) to high-efficacy infused antibodies (Ocrevus, Kesimpta, Tysabri). Roche's Ocrevus is the dominant brand globally. The market is mature but innovation continues — BTK inhibitors are in late-stage trials (Sanofi's tolebrutinib, Roche's fenebrutinib) chasing the progressive forms where current drugs work less well.",
        ["NIH", "FDA"],
        ["Neurology", "Immunology"], "Clinical",
    ),
    entry(
        "Ulcerative Colitis", "UC",
        "An inflammatory bowel disease that causes chronic inflammation and ulcers in the colon and rectum — separate from but often discussed alongside Crohn's.",
        "UC drug development closely tracks the broader IBD playbook: TNF blockers (Humira, Remicade) gave way to integrin and IL-23 mechanisms (Entyvio, Skyrizi, Tremfya), then to oral small molecules (Rinvoq, Xeljanz, Velsipity, Zeposia). Pfizer, AbbVie, J&J, Takeda, and BMS all have meaningful UC franchises. Expect biosimilar pressure on Humira/Remicade revenue lines on every IBD-heavy earnings call.",
        ["NIH", "FDA"],
        ["Gastroenterology", "Immunology"], "Clinical",
    ),
    entry(
        "Crohn's Disease", "",
        "An inflammatory bowel disease that can affect any part of the digestive tract, causing pain, diarrhea, weight loss, and bowel-wall damage.",
        "Crohn's runs on the same drug pipeline as ulcerative colitis but the patient experience is more variable — disease can hit the small bowel, large bowel, or both. Major brands include Humira, Remicade, Stelara, Skyrizi, Entyvio, Rinvoq. The IL-23 class (Skyrizi, Tremfya) has been gaining share in recent years. Crohn's commentary is part of the broader 'IBD switching' narrative as patients cycle through mechanisms.",
        ["NIH", "FDA"],
        ["Gastroenterology", "Immunology"], "Clinical",
    ),
    entry(
        "Hepatitis B", "HBV",
        "A chronic viral infection of the liver that can lead to cirrhosis and liver cancer — managed with antivirals but not yet routinely curable.",
        "Hep B treatment is dominated by Gilead's tenofovir-based antivirals (Vemlidy, Viread) — they suppress the virus indefinitely but rarely clear it. Functional cure is the holy grail and a busy biotech research area: GSK, Arrowhead, Vir Biotechnology, and Aligos all have late-stage candidates using siRNA, capsid inhibitors, or therapeutic vaccines. Vaccine prevention (recombinant Engerix-B/Heplisav-B) is highly effective and routine in pediatric immunization.",
        ["NIH", "FDA", "WHO"],
        ["Infectious Disease"], "Clinical",
    ),
    entry(
        "Hepatitis C", "HCV",
        "A bloodborne viral liver infection that became routinely curable after 2014's Sovaldi/Harvoni revolution — one of pharma's all-time blockbuster stories.",
        "Gilead's sofosbuvir-based regimens (Sovaldi, Harvoni, Epclusa) and AbbVie's Mavyret cure 95%+ of hep C in 8-12 weeks of pills. Pricing for these drugs sparked the modern drug-pricing debate (Sovaldi launched at $1,000/pill). The market collapsed under its own success — fewer patients to treat each year as the prevalent pool gets cured. Gilead's hep C revenue went from $19B in 2015 to under $2B by 2020.",
        ["NIH", "FDA"],
        ["Infectious Disease"], "Clinical",
    ),
    entry(
        "Non-Hodgkin Lymphoma", "NHL",
        "The umbrella name for dozens of distinct cancers of the lymphatic system — collectively the seventh-most-common cancer in the US.",
        "NHL is split mainly into B-cell and T-cell lymphomas, with diffuse large B-cell lymphoma (DLBCL) and follicular lymphoma being the most common. Treatment runs from rituximab-based chemo combos to BTK inhibitors (Imbruvica, Calquence, Brukinsa), CAR-T therapies (Yescarta, Breyanzi, Kymriah), bispecifics (Lunsumio, Epkinly), and ADCs (Polivy). Different NHL subtypes have completely different drug regimens — a generic 'lymphoma' headline rarely tells you what's actually moving.",
        ["NCI Dictionary of Cancer Terms"],
        ["Oncology"], "Clinical",
    ),
    entry(
        "Atrial Fibrillation", "AFib",
        "An irregular, often fast heartbeat caused by chaotic electrical signals in the upper chambers — the most common heart-rhythm problem and a leading cause of stroke.",
        "AFib management splits into rate/rhythm control (beta blockers, amiodarone, ablation procedures) and stroke prevention via anticoagulation. The DOAC class (Eliquis, Xarelto, Pradaxa, Savaysa) has largely replaced warfarin and is one of the highest-revenue cardio drug categories. Eliquis (apixaban, BMS/Pfizer) is the leader. Factor XI inhibitors are the next wave — promising lower bleeding risk than DOACs in late-stage trials.",
        ["NIH", "FDA"],
        ["Cardiovascular"], "Clinical",
    ),
]

# ============================================================================
# CELL TYPES & TREATMENT MODALITIES
# ============================================================================
MODALITIES = [
    entry(
        "B-cell", "",
        "The antibody-producing white blood cell — central to the adaptive immune system and the target of much of immunology and oncology drug development.",
        "B-cells make the antibodies that recognize and neutralize pathogens, and they're the cell of origin for many lymphomas and leukemias. Drugs that deplete B-cells (rituximab, ocrelizumab) treat conditions ranging from lymphoma to multiple sclerosis to rheumatoid arthritis. CAR-T therapies targeting CD19 (a B-cell marker) revolutionized treatment of B-cell leukemias and lymphomas. BTK inhibitors (Imbruvica, Calquence, Brukinsa) block a key B-cell signaling enzyme.",
        ["NIH"],
        ["Immunology", "Oncology"], "Mechanism",
    ),
    entry(
        "T-cell", "",
        "The white blood cell that coordinates immune response and directly kills infected or cancerous cells — the workhorse of cellular immunity.",
        "T-cells split into helper (CD4+) cells that orchestrate immune response and killer (CD8+) cells that destroy targets. T-cells are the engine of modern cancer immunotherapy: PD-1/PD-L1 inhibitors (Keytruda, Opdivo) release the brakes on tumor-fighting T-cells, CAR-T therapies engineer patient T-cells to attack cancer, and bispecifics (BiTEs) physically yoke T-cells to tumor cells. T-cell exhaustion and infiltration are key concepts in oncology immunotherapy commentary.",
        ["NIH"],
        ["Immunology", "Oncology"], "Mechanism",
    ),
    entry(
        "Gene Therapy", "",
        "Treatment that delivers a working copy of a gene (or instructions to fix one) directly into patient cells — fixing disease at its DNA-level root cause.",
        "Approved gene therapies include Luxturna for retinal disease, Zolgensma for spinal muscular atrophy, Hemgenix and Beqvez for hemophilia B, Roctavian for hemophilia A, and Elevidys for Duchenne muscular dystrophy. Most use AAV (adeno-associated virus) as the delivery vector. Pricing routinely exceeds $2-3M per one-time treatment, raising payer-coverage debates. Gene therapy commentary on biotech earnings calls focuses on durability of effect, immunogenicity to AAV, and re-dosing prospects.",
        ["NIH", "FDA"],
        ["Rare Disease"], "Mechanism",
    ),
    entry(
        "Cell Therapy", "",
        "Treatment using living cells as the active ingredient — most commonly engineered immune cells trained to attack cancer.",
        "CAR-T therapies (Kymriah, Yescarta, Breyanzi, Tecartus, Carvykti, Abecma) are the leading examples — patient T-cells are genetically modified to recognize a tumor antigen, then infused back. TIL therapy (Amtagvi, approved 2024) uses tumor-infiltrating lymphocytes for melanoma. Stem-cell transplants are an older form. Cell therapies are logistically intense — manufacturing happens per-patient with multi-week vein-to-vein turnaround times — which is why allogeneic 'off-the-shelf' approaches are an active development frontier.",
        ["NIH", "FDA"],
        ["Oncology"], "Mechanism",
    ),
    entry(
        "Stem Cell", "",
        "An undifferentiated cell that can both renew itself and develop into specialized cell types — the source of every tissue in the body.",
        "Hematopoietic stem-cell transplants (bone marrow transplants) are decades-old and used for blood cancers and severe immune disorders. Embryonic and induced pluripotent stem cells (iPSCs) underpin newer regenerative therapies in development for Parkinson's, diabetes (Vertex's VX-880 and zimislecel), and macular degeneration. The field has long been dogged by hype-vs-evidence tension; most actual approvals to date are in transplant rather than the 'grow-a-new-organ' future scenarios.",
        ["NIH"],
        ["Rare Disease"], "Mechanism",
    ),
]

# ============================================================================
# TRIAL / REGULATORY / CLINICAL
# ============================================================================
TRIALS = [
    entry(
        "Phase 1 Trial", "",
        "The first-in-human stage of drug development — small, focused on safety and dosing rather than whether the drug actually works.",
        "Phase 1 trials typically enroll 20-100 healthy volunteers (or patients with the target disease in oncology) and last several months. Endpoints are pharmacokinetics (how the body handles the drug), pharmacodynamics (what the drug does to the body), and the maximum tolerated dose. A clean Phase 1 readout is necessary but far from sufficient — most drugs that pass Phase 1 still fail later. Biotech earnings discussions of 'Phase 1 data' usually focus on safety signals and any early efficacy hints in oncology dose-escalation cohorts.",
        ["FDA", "NIH"],
        ["General"], "Regulatory",
    ),
    entry(
        "Phase 2 Trial", "",
        "Mid-stage trials in patients with the target disease — focused on whether the drug actually works at the doses chosen in Phase 1.",
        "Phase 2 typically enrolls 100-500 patients across several months to a couple of years. This is the 'go/no-go' decision point for most programs — if Phase 2 efficacy doesn't impress, Phase 3 investment is hard to justify. Successful Phase 2 readouts often drive significant biotech stock moves; failures kill programs. The Phase 2-to-Phase 3 attrition rate is the single highest in drug development.",
        ["FDA", "NIH"],
        ["General"], "Regulatory",
    ),
    entry(
        "Phase 3 Trial", "",
        "Large, expensive late-stage trials that produce the data the FDA actually wants to see — usually thousands of patients across many sites.",
        "Phase 3 is where most drug development money is spent. Trials run 1-4 years, cost hundreds of millions, and are designed to prove the drug works better than (or at least as well as) the existing standard of care. Top-line Phase 3 readouts are major catalysts for both biotech stocks and pharma franchises. Phase 3 failure can wipe billions off market caps overnight (see 2024's gantenerumab Alzheimer's failure for Roche).",
        ["FDA", "NIH"],
        ["General"], "Regulatory",
    ),
    entry(
        "Side Effect", "",
        "Any unintended effect of a drug beyond its main therapeutic action — ranges from mild (nausea, dry mouth) to dangerous (organ damage, death).",
        "Every drug has side effects and the entire drug-approval framework is fundamentally a benefit-vs-risk calculation. Common terms you'll hear: 'adverse event' (the formal regulatory term), 'tolerability' (the patient experience), 'black box warning' (the most serious labeling requirement), and 'discontinuation rate' (how often patients quit due to side effects). Many drug-launch failures trace to side-effect profiles being too punishing relative to the benefit — see 2022's Aduhelm and many other examples.",
        ["FDA"],
        ["General"], "Pharmacovigilance",
    ),
    entry(
        "Standard of Care", "SOC",
        "The treatment that's currently considered best practice for a given condition — the benchmark new drugs need to beat (or match with better tolerability).",
        "Standard of care evolves over time and varies by region — what's SOC in the US may not be elsewhere due to drug approval timing or pricing. Trial designs choose SOC as the comparator arm whenever ethically possible (placebo-controlled trials in serious diseases are increasingly rare). 'Front-line' or '1L' SOC is a particularly contested space because that's where most patients start — reorganizing the SOC of a major indication is one of the highest-value things a new drug can do.",
        ["FDA", "NIH"],
        ["General"], "Clinical",
    ),
    entry(
        "Breakthrough Therapy", "",
        "An FDA designation that fast-tracks development of a drug that shows substantial improvement over existing treatments for a serious condition.",
        "Breakthrough Therapy designation gets a drug intensified FDA support, more frequent meetings, and rolling review of submitted data — meaningfully accelerating time to market when it works. Designation isn't a guarantee of approval but is a strong positive signal. About 30-40% of recent novel approvals have had Breakthrough Therapy at some point. Companies announce designation as a milestone because investors recognize it as derisking.",
        ["FDA"],
        ["General"], "Regulatory",
    ),
]

# ============================================================================
# GENETICS
# ============================================================================
GENETICS = [
    entry(
        "X-Linked", "",
        "A genetic trait carried on the X chromosome — affects males more often than females since males only have one X to fall back on.",
        "X-linked recessive conditions like hemophilia A, hemophilia B, Duchenne muscular dystrophy, and red-green colorblindness almost exclusively affect males because females have a backup X chromosome. Females can be 'carriers' who pass the gene without showing symptoms. Pharma drug development for X-linked diseases has been historically weighted toward male-pediatric populations — gene therapies for hemophilia and DMD are textbook examples.",
        ["NIH"],
        ["Rare Disease"], "Mechanism",
    ),
]


def main():
    all_new = DISEASES + MODALITIES + TRIALS + GENETICS
    print(f"Drafted {len(all_new)} new entries")

    existing = json.loads(GLOSSARY.read_text())
    existing_terms_lower = {t["term"].lower() for t in existing}

    to_add, skipped = [], []
    for e in all_new:
        if e["term"].lower() in existing_terms_lower:
            skipped.append(e["term"])
        else:
            to_add.append(e)

    print(f"  → adding: {len(to_add)}")
    if skipped:
        print(f"  → skipping (already present): {len(skipped)}: {skipped}")

    merged = existing + to_add
    merged.sort(key=lambda t: (t["letter"], t["term"].lower()))

    GLOSSARY.write_text(json.dumps(merged, indent=2, ensure_ascii=False) + "\n")
    print(f"  → wrote {len(merged)} total entries to {GLOSSARY.name}")


if __name__ == "__main__":
    main()
