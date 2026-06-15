# App Store Connect — In-App Purchase setup for JB Glossary v2

Create these **8 non-consumable** in-app purchases against the
`com.jamesbrowne.PharmaGlossary` app record in App Store Connect. The
product identifiers below MUST match exactly — they are hardcoded in
`Sources/Industries/IndustryConfig.swift` (7 industry IDs) and
`masterUnlockProductID` (1 master).

**v2.2 adds Robotics** — only `com.jamesbrowne.JBGlossary.robotics` is new.
Create it and attach it to the 2.2.0 version when submitting. The other 7
already exist and are approved. The $9.99 master already unlocks every
current and future industry, so it covers Robotics with no change.

**Monetization model**: every industry ships with letters **A–D free** as a
taster. Letters E–Z gated by the per-industry IAP at $2.99. The master
"All Industries" IAP at $9.99 unlocks E–Z across every current and future
industry — priced at ~3.3× the single-industry tier so multi-industry
users see a clear bundle discount vs. buying 2+ industries individually.

| Product ID | Reference Name | Display Name | Price (US) | Family Sharing |
|---|---|---|---|---|
| `com.jamesbrowne.JBGlossary.pharma` | Pharma | Unlock the rest of Pharma | $2.99 (Tier 3) | On |
| `com.jamesbrowne.JBGlossary.ai` | AI | Unlock the rest of AI | $2.99 (Tier 3) | On |
| `com.jamesbrowne.JBGlossary.law` | Law | Unlock the rest of Law | $2.99 (Tier 3) | On |
| `com.jamesbrowne.JBGlossary.finance` | Finance | Unlock the rest of Finance | $2.99 (Tier 3) | On |
| `com.jamesbrowne.JBGlossary.realEstate` | Real Estate | Unlock the rest of Real Estate | $2.99 (Tier 3) | On |
| `com.jamesbrowne.JBGlossary.insurance` | Insurance | Unlock the rest of Insurance | $2.99 (Tier 3) | On |
| `com.jamesbrowne.JBGlossary.robotics` | Robotics | Unlock the rest of Robotics | $2.99 (Tier 3) | On | ⟵ **NEW in v2.2** |
| `com.jamesbrowne.JBGlossary.all` | All Industries | Unlock All Industries | $9.99 (Tier 10) | On |

## Descriptions (used on the App Store IAP listing)

**Pharma** — Unlock the rest of the JB Glossary Pharma industry: letters
E–Z, the full set of pharma and healthcare terms beyond the free A–D
taster. One-time purchase, no subscription.

**AI** — Unlock the rest of the JB Glossary AI industry: letters E–Z, the
full set of AI, ML, and silicon terms beyond the free A–D taster. One-time
purchase, no subscription.

**Law** — Unlock the rest of the JB Glossary Law industry: letters E–Z,
the full set of US-law terms beyond the free A–D taster. One-time
purchase, no subscription.

**Finance** — Unlock the rest of the JB Glossary Finance industry: letters
E–Z, the full set of markets terms beyond the free A–D taster. One-time
purchase, no subscription.

**Real Estate** — Unlock the rest of the JB Glossary Real Estate industry:
letters E–Z, the full set of property, mortgage, and real estate investment
terms beyond the free A–D taster. One-time purchase, no subscription.

**Insurance** — Unlock the rest of the JB Glossary Insurance industry:
letters E–Z, the full set of life, health, auto, home, and commercial
insurance terms beyond the free A–D taster. One-time purchase, no
subscription.

**Robotics** — Unlock the rest of the JB Glossary Robotics industry:
letters E–Z, the full set of robotics, autonomy, and embodied-AI terms —
mechanics, control, perception, learning, self-driving, drones, and the
factory floor — beyond the free A–D taster. One-time purchase, no
subscription.

**All Industries** — Unlock the rest (E–Z) of every industry in JB
Glossary, current and future. One purchase covers your current and future
devices via Apple ID. Best value if you'd otherwise buy more than 3
individual industries.

## Review notes (for App Review)

> JB Glossary ships with letters A–D free across every industry as a
> "taster" — roughly 25–29% of each industry's terms are available without
> any purchase. Letters E–Z in
> each industry are gated behind a one-time non-consumable IAP at $2.99
> per industry. The "Unlock All Industries" $9.99 IAP grants the E–Z
> entitlement across every current and future industry. There are no
> subscriptions; every purchase is one-time. "Restore Purchases" is
> available from every paywall sheet, satisfying 3.1.1.
>
> The free anchor pattern is symmetric: no single industry is given away
> in full, so a user with no interest in (say) pharma isn't stuck with a
> free pharma glossary — they get a taster of every field instead.

## Local sandbox testing (already wired)

The project ships with `Configuration.storekit` and the scheme is
configured to use it (`scheme.storeKitConfiguration` in `project.yml`).
Running on the simulator from Xcode resolves all products against
the local config, so the paywall sheet shows real prices ($2.99 / $9.99)
and `Product.purchase()` simulates a transaction.

Sandbox testing on a real device requires an App Store Connect Sandbox
Tester account and the actual products created above. Add the tester in
ASC → Users and Access → Sandbox Testers, then sign into the device's
App Store with that account before launching.

## Grandfathering legacy Pharma users

`PurchaseManager.checkGrandfathering()` reads
`AppTransaction.originalAppVersion` on first v2 launch. If the original
version starts with `1.` (i.e., the user installed any pre-v2 Pharma
build — whether they paid or downloaded free), the master "All
Industries" entitlement is granted locally and persisted under
`jbglossary.grandfathered.masterUnlock` in `UserDefaults`. Existing
Pharma users get *more* than they had before — full Pharma plus AI, Law,
Finance, and all future industries — as a "thanks for being early"
upgrade.

The check is idempotent and retried on every launch until it succeeds
(simulator builds without a receipt can fail the AppTransaction call).
