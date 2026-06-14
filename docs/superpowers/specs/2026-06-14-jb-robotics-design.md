# JB Robotics — Industry Design Spec

**Date:** 2026-06-14
**Status:** Approved (brainstorm) — ready for implementation plan
**Branch:** `robotics-industry`
**Target:** 7th industry in the JB Glossary suite (`~/JBGlossary-iOS`)

---

## 1. Overview & positioning

JB Robotics is the **physical / embodied-systems** glossary for the suite: the
robot itself, the autonomy stack that drives it, and the deployed world it
lives in (autonomous vehicles, drones, the factory floor, and the companies
building it).

**Reader model — comprehensive corpus, depth via tiers, breadth via lenses.**
We do not pick an audience at the corpus level. Instead:

- The existing per-term **tiers serve depth**: `plain` (jargon-free, for the
  generalist) → `snappy` (the working definition) → `detail` (goes fully
  technical, for the practitioner). One entry serves a news-reader and an
  engineer at different reading depths.
- The **lenses serve the *way in*** (see §6): a generalist on-ramp, the
  perception–action stack, an Embodied-AI frontier card, and the deployed
  world.

**Positioning line:** `titleBody: "Robotics"`, subtitle
**"decoding robots & autonomy"**, App Store name **JB Robotics**.

**Why it earns a place next to JB AI:** the differentiation is sharp on
everything physical — kinematics, control theory, actuators, ROS, perception
hardware, mechanical design — none of which exists in JB AI. The only overlap
is a thin, hot band at embodied AI, handled deliberately in §4.

---

## 2. Architecture integration (how it plugs in)

JB Robotics follows the established single-app / industry-picker / per-industry
IAP pattern. No framework changes. Adding the industry means:

1. **`Sources/Industries/IndustryConfig.swift`** — add `case robotics` to
   `IndustryID`; append a `.robotics` entry to `IndustryConfig.all` with IAP
   product id `com.jamesbrowne.JBGlossary.robotics`. Display order: append
   after `insurance` (last).
2. **`Sources/Industries/RoboticsBrand.swift`** — new `let roboticsBrand =
   Brand(...)` (see §7). Unique filename (Xcode forbids same-named sources in a
   target).
3. **`Targets/Robotics/Resources/glossary_robotics.json`** — the corpus
   (`dataResource: "glossary_robotics"`).
4. **`Targets/Robotics/Resources/Assets.xcassets/`** — AppIcon (1024²),
   AccentColor colorset (amber), LaunchBackground (keep cream `#F5EFE6`).
5. **`Targets/Robotics/Resources/Info.plist`** + `PrivacyInfo.xcprivacy` —
   mirror the AI target; `CFBundleDisplayName: JB Robotics`.
6. **`project.yml`** — add a `Robotics` target block mirroring `AI`; run
   `xcodegen generate`.
7. **`Configuration.storekit`** — add the robotics IAP and include it in the
   master `com.jamesbrowne.JBGlossary.all` unlock.

The `Term` schema (`Sources/Models/Glossary.swift`) is reused **unchanged**:
`letter, term, full, plain, snappy, detail, indications[], category, sources[],
aliases[]`.

---

## 3. Scope

### In scope — full coverage
- **Core robotics (always in):** mechanics/structures, actuation & drives,
  kinematics & dynamics, power & embedded compute, locomotion, manipulation,
  sensing, perception, control, planning & navigation, software & simulation
  (ROS/ROS2, MoveIt, Gazebo, Isaac, URDF), form factors (arms, cobots,
  AMR/AGV, humanoid, quadruped, SCARA, delta), safety & standards.
- **Embodied AI** (the frontier band): RL, imitation learning, teleoperation,
  sim-to-real, domain randomization, diffusion policy, VLA / vision-language-
  action models, foundation models for robotics.
- **Autonomous vehicles / self-driving** — SAE autonomy levels, AV sensor
  stacks, ADAS, AV-specific perception & planning.
- **Aerial / drones (UAS)** — multirotor/fixed-wing, flight control, BVLOS,
  UTM, drone-specific regulation.
- **Industrial automation beyond robots** — PLC, SCADA, MES, fieldbus, motion
  control, the wider factory-floor stack robots plug into.
- **Notable companies & platforms** — Boston Dynamics, Figure, Tesla Optimus,
  Unitree, NVIDIA Isaac, ROS distros, etc., as named entries.

### Out of scope (non-goals for v1)
- Cross-industry hyperlinks (the linker resolves `robotics://` within this
  industry only — see §4).
- General AI/ML theory that isn't embodiment-relevant (lives in JB AI).
- Deep mechanical/EE engineering math beyond what the `detail` tier needs for
  orientation.
- Localization, a Python scaffolder, or any framework refactor (per
  `RECIPE.md` §8 — don't shave the yak).

---

## 4. AI-overlap boundary policy

**Decision: standalone-complete, robotics-first framing.**

Because IAPs are independent and **hyperlinks resolve within a single
industry** (`robotics://term/...`, no cross-industry linking today), JB
Robotics must stand alone — a Robotics-only buyer cannot be sent to JB AI.

Therefore:
- JB Robotics **defines every embodied-AI term it needs itself** (~40–60 terms
  that also exist in JB AI), but **framed robotics-first** with robotics
  examples. Example: *diffusion policy* is framed as a manipulation/control
  policy that generates action trajectories — not as an image-generation model
  class.
- **JB AI is left untouched.** Its existing 28 "Robotics"-tagged entries and
  `RL` indication stay as-is. No re-authoring of a shipped, approved product.
- Since users never see both link-spaces at once, the name-level overlap is
  invisible and reads as genuinely different value.

Shared terms to (re-)author robotics-first include: Reinforcement learning,
Imitation learning, Behavioral cloning, Sim-to-real, Domain randomization,
Diffusion policy, VLA / Vision-Language-Action model, Foundation model (for
robotics), Teleoperation, Policy, Reward, Transformer (brief, embodiment-
framed), Neural network (brief).

---

## 5. Category taxonomy — 1st axis (`category`, exactly one per term)

20 categories (parity with JB AI's 19), grouped here only for readability — the
field stores a single flat category string:

**Foundations**
1. `Concepts` — umbrella/foundational terms (expected to be the largest bucket,
   as in JB AI).

**The body**
2. `Mechanics & Structures`
3. `Actuation & Drives`
4. `Kinematics & Dynamics`
5. `Power & Compute` (batteries, power electronics, embedded/edge compute,
   real-time)

**Motion & interaction**
6. `Locomotion`
7. `Manipulation`
8. `Form Factors`

**The stack / mind**
9. `Sensing`
10. `Perception`
11. `Control`
12. `Planning & Navigation`
13. `Software & Simulation`
14. `Learning & Embodied AI`

**The deployed world**
15. `Autonomous Vehicles`
16. `Aerial & Drones`
17. `Industrial Automation`
18. `Safety & Standards`
19. `Companies & Platforms`
20. `Industry & Deployment` (RaaS, market structure, integration, ops)

Category strings above are the **canonical values** authors must use verbatim
in `glossary_robotics.json` (lenses match on exact string equality).

---

## 6. Lens architecture — 5 lenses

Lenses are the filter cards. Order = display order. Lens 1 is a curated
`allowlist`; lenses 2–5 are `categoryFilter` over the §5 categories.

```
1. Basics            (allowlist)            "Foundational robotics vocabulary"
2. The Robot         (categoryFilter)       "Body, motion & power"
       → Mechanics & Structures, Actuation & Drives, Kinematics & Dynamics,
         Power & Compute, Locomotion, Manipulation, Form Factors
3. Sense & Control   (categoryFilter)       "The perception–action stack"
       → Sensing, Perception, Control, Planning & Navigation,
         Software & Simulation
4. Embodied AI  ★    (categoryFilter)       "Learning that drives physical action"
       → Learning & Embodied AI
         (frontier Concepts surfaced here via the Concepts→this mapping below)
5. Systems & Industry (categoryFilter)      "The deployed world"
       → Autonomous Vehicles, Aerial & Drones, Industrial Automation,
         Safety & Standards, Companies & Platforms, Industry & Deployment
```

**Glyphs** (single char on each card, matching the existing convention):
`B`, `R`, `S`, `E`, `Y` (or pick distinct legible letters at build time).

**Concepts handling:** `Concepts` is the umbrella bucket and is intentionally
**not** owned by a single lens (mirrors JB AI, where `Concepts` is filtered in
via multiple lenses). Frontier/embodied `Concepts` entries should be authored
to also carry the `Research/Frontier` indication so they surface under the
Embodied AI lens's intent; if a cleaner split is wanted at build time, promote
genuinely-frontier umbrella terms to the `Learning & Embodied AI` category
instead of `Concepts`. **Build-time rule:** every category in §5 must appear in
at least one lens's `categories` set except `Concepts`, which may be
deliberately broad.

---

## 7. Brand configuration (`RoboticsBrand.swift`)

Mirror `AIBrand.swift`/`InsuranceBrand.swift` structure. Key fields:

- `appStoreName: "JB Robotics"`, `displayName: "JB Robotics"`,
  `navigationTitle: "JB Robotics"`, `titlePrefix: "JB"`,
  `titleBody: "Robotics"`, `subtitle: "decoding robots & autonomy"`,
  `tagline: nil`, `entryNoun: "entries"`, `dataResource: "glossary_robotics"`,
  `urlScheme: "robotics"`.
- `primaryColor`: **signal amber-orange `#E06A1B`** →
  `Color(red: 0.878, green: 0.416, blue: 0.106)`.
- `primaryDarkColor`: hand-darkened amber `#B5530F` →
  `Color(red: 0.710, green: 0.325, blue: 0.059)`.
- `bgColor: PGColors.bg` (cream), `accentTint: nil` (derive).
- **Fallback** if amber reads too close to Real-Estate clay on the picker:
  graphite-steel `#3C4A57` → `Color(red: 0.235, green: 0.290, blue: 0.341)`.
  Decide by eyeballing the picker in §10.
- `aboutParagraphs` (2): generalist framing — "JB Robotics is a generalist's
  reference for the language of robots, autonomy, and embodied AI — the jargon
  you meet in the humanoid race, self-driving news, factory-automation pitches,
  and robotics research…" + a "publicly available material, orientation not
  engineering" disclaimer paragraph.
- `aboutDisclaimer`: "Educational reference. Not engineering, safety, or
  investment advice."
- `aboutSources` (BrandSource groups): **Standards & government** (IEEE RAS,
  NIST, ISO, SAE International, FAA); **Software & platforms** (ROS / Open
  Robotics, MoveIt, Gazebo, NVIDIA Isaac); **Research & industry** (arXiv
  cs.RO, DARPA, NASA, IFR — International Federation of Robotics); **Makers**
  (Boston Dynamics, etc.).
- `sourceURLs`: map every source name above to its URL (IEEE RAS
  `https://www.ieee-ras.org`, NIST `https://www.nist.gov`, ISO
  `https://www.iso.org`, SAE `https://www.sae.org`, FAA `https://www.faa.gov`,
  ROS `https://www.ros.org`, Open Robotics `https://www.openrobotics.org`,
  MoveIt `https://moveit.ai`, Gazebo `https://gazebosim.org`, NVIDIA Isaac
  `https://developer.nvidia.com/isaac`, arXiv `https://arxiv.org/list/cs.RO/recent`,
  DARPA `https://www.darpa.mil`, NASA `https://www.nasa.gov`, IFR
  `https://ifr.org`, Boston Dynamics `https://www.bostondynamics.com`).
- Keep the per-target `extension Brand { static let current = roboticsBrand }`
  if the target uses the RECIPE pattern; otherwise registration via
  `IndustryConfig.all` is sufficient (match whatever the AI/Insurance targets
  currently do — verify at build time).

---

## 8. 2nd axis — `indications` (application sectors, multiple per term)

Cross-cutting sector tags surfaced as filter chips (the existing two-axis
filter: category × indication). Canonical values:

`Manufacturing` · `Logistics & Warehouse` · `Humanoid` · `Medical & Surgical`
· `Agriculture` · `Defense & Security` · `Space` · `Service & Consumer` ·
`Mobility` (road/AV) · `Research/Frontier`

A term may carry several (e.g. *LiDAR* → `Mobility`, `Logistics & Warehouse`;
*end-effector* → `Manufacturing`, `Medical & Surgical`). Purely foundational
terms may carry none.

---

## 9. Corpus plan & authoring standards

**Launch target ≈ 900 entries**, taxonomy built with headroom to **1,200+** via
themed update batches (the JB AI 785 → 976 playbook).

**Rough category distribution at launch** (guidance, not a quota):
- Concepts ~140 · Perception ~60 · Control ~55 · Kinematics & Dynamics ~45 ·
  Learning & Embodied AI ~70 · Software & Simulation ~55 · Sensing ~55 ·
  Planning & Navigation ~50 · Manipulation ~45 · Locomotion ~40 ·
  Actuation & Drives ~45 · Mechanics & Structures ~40 · Form Factors ~40 ·
  Power & Compute ~35 · Autonomous Vehicles ~90 · Aerial & Drones ~50 ·
  Industrial Automation ~65 · Safety & Standards ~35 · Companies & Platforms
  ~40 · Industry & Deployment ~25. (≈ 1,075 ceiling list; trim to ~900 for v1.)

**Basics allowlist (lens 1)** ≈ 120–150 hand-picked recognizable foundations
spanning every area. Representative anchors (illustrative, not exhaustive):
Robot, Actuator, Servo, Motor, Encoder, Degree of freedom, End-effector,
Gripper, Joint, Link, Payload, Kinematics, Forward kinematics, Inverse
kinematics, Trajectory, Sensor, LiDAR, Depth camera, IMU, SLAM, Localization,
Mapping, Path planning, Obstacle avoidance, PID controller, Feedback control,
Degrees of autonomy, Autonomy level, ROS, Simulation, Digital twin, Cobot, AMR,
AGV, Humanoid, Quadruped, Manipulator, Teleoperation, Reinforcement learning,
Imitation learning, Sim-to-real, Drone, UAV, Self-driving, Sensor fusion,
Computer vision, Actuation, Torque, Gait, Grasping. Names must match the `term`
field exactly.

**Per-entry authoring bar** (follow existing `docs/CLARITY_POLICY.md` and
`docs/CONTENT_STYLE_GUIDE.md`):
- `plain`: one jargon-free sentence for a total novice.
- `snappy`: the crisp working definition.
- `detail`: 1–3 sentences that may go fully technical; include a concrete
  robotics example where it sharpens meaning.
- `full`: acronym expansion where applicable (LiDAR, SLAM, ROS, BVLOS, UTM,
  PLC, AMR, AGV, VLA, ADAS, …).
- `aliases`: curate conservatively for acronym/variant linking (e.g. `AMR` →
  "Autonomous Mobile Robot", `IK` → "Inverse kinematics").
- **Hyperlink density target ≥ 3 live cross-links per entry** — author in dense
  connected clusters, build the term list first, then write prose that
  references it. Verify with the repo's hyperlink audit script.

---

## 10. Build, wiring & verification checklist

1. Add `IndustryID.robotics` + `IndustryConfig.all` entry + IAP id.
2. Author `RoboticsBrand.swift` (§7).
3. Create `Targets/Robotics/` from the AI target; add amber AccentColor,
   placeholder AppIcon, Info.plist (`JB Robotics`), PrivacyInfo.
4. Add a `glossary_robotics.json` **stub (5–10 terms)** first to verify wiring
   end-to-end before batching content.
5. Add the `Robotics` target to `project.yml`; `xcodegen generate`.
6. Build: `xcodebuild -scheme Robotics -destination 'platform=iOS
   Simulator,name=iPhone 17 Pro Max' build`.
7. **Visual verify** on the sim (screenshot `xcrun simctl io booted screenshot
   /tmp/robotics.png`): header "JB **Robotics**" with amber italic accent;
   splash dots / favorites star amber; PGBackground wash amber; all 5 lens
   cards show correct title/subtitle; About renders robotics copy; tapping a
   term resolves `robotics://term/...` links. **Confirm amber vs. clay
   distinctness on the picker — switch to graphite fallback if needed.**
8. Batch the real corpus via a `scripts/add_robotics_terms.py` mirroring the
   existing `scripts/add_*` pattern; re-run the hyperlink audit; spot-check for
   wrong-context auto-links and slang masquerading as terms.
9. IAP: add `com.jamesbrowne.JBGlossary.robotics` ($2.99) to
   `Configuration.storekit` and the master unlock; create the ASC IAP record at
   ship time (`docs/ASC_IAP_SETUP.md`).
10. Tests: run the existing test target; add a decode/integrity test for
    `glossary_robotics.json` (valid categories, non-empty required fields,
    alias collisions) mirroring existing glossary tests.

---

## 11. Risks & open items
- **Amber vs. clay proximity** on the picker — resolved by the §10 step 7 eyeball
  + graphite fallback.
- **Concepts/Embodied-AI lens routing** — confirm the §6 handling renders the
  Embodied AI card with a meaningful, non-empty slice; adjust category
  assignment of frontier umbrella terms if thin.
- **Corpus freshness** — Companies & Platforms dates fastest; keep it a modest
  slice and refresh in update batches.
- **Scope creep on AVs** — AVs are a large field; cap v1 AV coverage at
  orientation depth (~90 terms) rather than mirroring a dedicated AV product.

---

## 12. Definition of done (v1 launch)
- `JB Robotics` builds and runs as the 7th picker industry with the amber (or
  graphite) brand applied throughout.
- ~900-entry `glossary_robotics.json` across all 20 categories; ≥3 avg live
  links/entry; 0 zero-link entries; all 5 lenses non-empty and correctly
  routed.
- IAP wired (`com.jamesbrowne.JBGlossary.robotics`, $2.99) + included in master.
- Glossary integrity test passes; hyperlink audit clean.
- App Store assets (icon, screenshots) prepared; ASC IAP record created at ship.
