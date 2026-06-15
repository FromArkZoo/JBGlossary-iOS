# JB Glossary — iOS

**JB Glossary** is a native SwiftUI reference app that turns dense professional jargon into clean, searchable, italic-typed cards. One app, seven industries — Healthcare, AI, Finance, Law, Real Estate, Insurance, and Robotics — sharing a single engine, each its own corpus unlocked as an in-app purchase. **7,111 terms across seven books** — six live on the App Store, Robotics shipping in v2.2.

<p align="center">
  <a href="https://apps.apple.com/app/id6768070422"><img src="https://developer.apple.com/assets/elements/badges/download-on-the-app-store.svg" alt="Download JB Glossary on the App Store" height="52"></a>
</p>

Free to download — browse A–D in every industry, unlock a full industry for $2.99, or get all seven with the $9.99 master unlock.

| Healthcare | AI | Finance | Law | Real Estate | Insurance | Robotics |
|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| <img src="Targets/Pharma/Resources/Assets.xcassets/AppIcon.appiconset/icon-1024.png" width="80"> | <img src="Targets/AI/Resources/Assets.xcassets/AppIcon.appiconset/icon-1024.png" width="80"> | <img src="Targets/Finance/Resources/Assets.xcassets/AppIcon.appiconset/icon-1024.png" width="80"> | <img src="Targets/Law/Resources/Assets.xcassets/AppIcon.appiconset/icon-1024.png" width="80"> | <img src="Targets/RealEstate/Resources/Assets.xcassets/AppIcon.appiconset/icon-1024.png" width="80"> | <img src="Targets/Insurance/Resources/Assets.xcassets/AppIcon.appiconset/icon-1024.png" width="80"> | 🤖 |
| 786 terms | 976 terms | 722 terms | 836 terms | 803 terms | 609 terms | 2,379 terms |
| Drugs, biology, regulation | AI / ML concepts | Markets + instruments | US law (14 categories, 4 lenses) | Property, finance, leasing | Life, health, auto, home, liability | Robots, autonomy, embodied AI |

---

## JB Healthcare

A generalist's reference for the language of healthcare — the drugs, biology, mechanisms of action, regulation, payers, and public-health jargon you meet in news, earnings calls, and regulatory filings. Two-axis filter (indication × category), oncology-deep.

<p align="center">
  <img src="screenshots/jb-pharma/iphone-17-pro-max/1_home.png" width="22%">
  <img src="screenshots/jb-pharma/iphone-17-pro-max/2_filter.png" width="22%">
  <img src="screenshots/jb-pharma/iphone-17-pro-max/3_basics.png" width="22%">
  <img src="screenshots/jb-pharma/iphone-17-pro-max/4_term_Antibody.png" width="22%">
</p>

- [Support](https://fromarkzoo.github.io/JBGlossary-iOS/support.html) · [Privacy](https://fromarkzoo.github.io/JBGlossary-iOS/privacy.html)

## JB AI

The same engine, retuned for the AI/ML vocabulary — agents, model architectures, training regimes, the stuff that fills frontier-lab posts.

<p align="center">
  <img src="screenshots/jb-ai/iphone-17-pro-max/1_home.png" width="22%">
  <img src="screenshots/jb-ai/iphone-17-pro-max/2_filter.png" width="22%">
  <img src="screenshots/jb-ai/iphone-17-pro-max/3_basics.png" width="22%">
  <img src="screenshots/jb-ai/iphone-17-pro-max/4_term_Attention.png" width="22%">
</p>

- [Support](https://fromarkzoo.github.io/JBGlossary-iOS/support.html) · [Privacy](https://fromarkzoo.github.io/JBGlossary-iOS/privacy.html)

## JB Finance

722 finance terms covering markets, instruments, valuation, risk, regulation, and trading. The vocabulary you need to read a sell-side report, follow a Fed meeting, or understand a derivatives prospectus.

- [Support](https://fromarkzoo.github.io/JBGlossary-iOS/support.html) · [Privacy](https://fromarkzoo.github.io/JBGlossary-iOS/privacy.html)

## JB Law

836 US-law terms across 14 categories, with four reading lenses (Basics, Civil & Business, Public, Family) so first-year material and practitioner-grade terms don't drown each other out.

<p align="center">
  <img src="screenshots/jb-law/iphone-17-pro-max/1_home.png" width="22%">
  <img src="screenshots/jb-law/iphone-17-pro-max/2_filter.png" width="22%">
  <img src="screenshots/jb-law/iphone-17-pro-max/3_basics.png" width="22%">
  <img src="screenshots/jb-law/iphone-17-pro-max/4_term_HabeasCorpus.png" width="22%">
</p>

- [Support](https://fromarkzoo.github.io/JBGlossary-iOS/support.html) · [Privacy](https://fromarkzoo.github.io/JBGlossary-iOS/privacy.html)

## JB Real Estate

803 real estate terms across 11 categories — Property Types, Financing & Lending, Transactions, Valuation & Appraisal, Title & Ownership, Leasing, Development, Management & Operations, Tax, Market & Investment, Law & Regulation. Three lenses (Basics, Residential, Commercial & Investment). The highest hyperlink density of any industry — 12+ live cross-references per entry.

- [Support](https://fromarkzoo.github.io/JBGlossary-iOS/support.html) · [Privacy](https://fromarkzoo.github.io/JBGlossary-iOS/privacy.html)

## JB Insurance

The sixth book — a deep-teal reference for the language of risk and protection: life, health, auto, home, and commercial cover, plus the underwriting, actuarial, reinsurance, and regulatory machinery underneath. 609 terms across nine categories in three clusters (policyholder / risk / market) and four lenses (Basics, Policies & Claims, Risk & Pricing, Markets & Regulation). Sits at the intersection of the Finance, Healthcare, and Real Estate books, raising cross-reference density across the whole suite.

<p align="center">
  <img src="screenshots/jb-insurance/iphone-17-pro-max/1_home.png" width="22%">
  <img src="screenshots/jb-insurance/iphone-17-pro-max/4_term_Deductible.png" width="22%">
</p>

- [Support](https://fromarkzoo.github.io/JBGlossary-iOS/support.html) · [Privacy](https://fromarkzoo.github.io/JBGlossary-iOS/privacy.html)

---

## How it's built

One workspace, six targets, one shared engine. Each industry pairs its own JSON corpus with the same SwiftUI reader: italic-first typography, two-axis filter, A–Z navigation, full-text search, share sheet, automatic hyperlinks between entries.

```
Sources/                                shared engine (models, views, design system)
Targets/Pharma/Resources/               pharma corpus + icon + colour
Targets/AI/Resources/                   AI corpus + icon + colour
Targets/Finance/Resources/              finance corpus + icon + colour
Targets/Law/Resources/                  law corpus + icon + colour
Targets/RealEstate/Resources/           real estate corpus + icon + colour
Targets/Insurance/Resources/            insurance corpus + icon + colour
project.yml                             XcodeGen spec (one unified app, runtime industry switch)
```

### Run a target

```bash
xcodegen generate
open JBGlossary.xcodeproj         # one app, one scheme → ⌘R, then pick the industry from the in-app picker
```

### Add or edit terms

Each app reads a flat `glossary.json` of `{letter, term, full, definition, category, indication?}`. Drop a new entry in, rebuild, the store re-decodes on launch.

---

Built and authored by [James Browne](https://github.com/FromArkZoo).
