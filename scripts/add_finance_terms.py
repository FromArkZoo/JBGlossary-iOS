"""Idempotently merge markets/finance terms into Targets/Finance/Resources/glossary.json.

Mirrors scripts/add_law_terms.py — append-only, case-insensitive dedup against
existing terms, sort by (letter asc, term asc) on write. Each batch is a
Python list built via the entry() helper which enforces category +
indication enums so we don't drift away from the lenses in FinanceBrand.swift.

Voice: Bloomberg-desk register for a generalist (citizen, journalist, business
owner). Snappy line ~12 words, present tense, must make sense WITHOUT prior
markets knowledge. Detail 50–75 words anchored on a real instrument, a desk
practice, a regulatory citation, or a famous market event. No prices,
no trade ideas, no "you should".

Usage:
    python scripts/add_finance_terms.py
    python scripts/add_finance_terms.py --batches 1,2     # run specific batches
    python scripts/add_finance_terms.py --dry-run         # preview without writing
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

GLOSSARY = Path(__file__).parent.parent / "Targets" / "Finance" / "Resources" / "glossary.json"

# Keep in sync with Targets/Finance/FinanceBrand.swift `lenses[].kind` category lists.
VALID_CATEGORIES = {
    "Instruments", "Pricing & Valuation", "Risk", "Market Structure",
    "Trading & Execution", "Settlement & Operations", "Regulation",
    "Indexes & Benchmarks", "Quantitative", "Corporate Actions",
}

VALID_INDICATIONS = {
    "Rates", "FX", "Equities", "Credit", "Commodities",
    "Derivatives", "Cross-asset", "Macro",
}


def entry(term, full, snappy, detail, sources, indications=None, category="Instruments", plain=""):
    assert category in VALID_CATEGORIES, f"Unknown category '{category}' for term '{term}'"
    indications = indications or ["Cross-asset"]
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
# BATCH 1 — Smoke test (20 terms covering all 8 asset-class tags
# and 8 of 10 categories — first-hour-on-the-desk vocabulary)
# ============================================================================

BATCH_SMOKE_TEST = [
    entry("Bid-Ask Spread", "",
        "Gap between what buyers offer and sellers accept — the dealer's cut.",
        "Quoted as the difference between bid (where a market-maker will buy) and offer (where they'll sell). Tightens with volume and competition; widens around news, illiquid hours, or stress. A penny S&P 500 spread costs retail almost nothing; a fifty-cent emerging-market bond spread is the trader's bread and butter. Regulators (MiFID II in Europe, Rule 605 in the US) require disclosure as a proxy for execution quality.",
        ["SEC", "ESMA"],
        indications=["Cross-asset"], category="Market Structure"),

    entry("Yield", "",
        "Return a bond pays as a percentage of its price.",
        "Several flavours: current yield (coupon over price), yield-to-maturity (the discount rate equating cash flows to price), yield-to-call (assumes the issuer redeems early). Inverse to price — when rates rise, bond prices fall. The Treasury's daily yield curve, posted by the Federal Reserve, is the global benchmark. Equity 'yield' (dividend over price) is a different beast.",
        ["Federal Reserve", "CFA Institute"],
        indications=["Rates"], category="Pricing & Valuation"),

    entry("Duration", "",
        "How much a bond's price moves for a one-percent rate shift, expressed in years.",
        "Macaulay duration is the weighted-average time to cash flows. Modified duration is what traders quote — a seven-year-duration bond loses roughly seven percent if yields rise one percent. Effective duration handles callable bonds and mortgage-backed securities. Portfolio managers target duration to express macro views; index funds match the benchmark duration to track. Long-duration assets got hammered in 2022 as the Fed hiked 525 basis points.",
        ["CFA Institute", "Federal Reserve"],
        indications=["Rates"], category="Risk"),

    entry("Convexity", "",
        "How a bond's duration itself changes as yields move — the second-order kicker.",
        "Duration alone is a first-order approximation. Convexity captures the curvature: positive convexity (most non-callable bonds) means the price gains more on a rate drop than it loses on an equivalent rise — good for the holder. Mortgage-backed securities have negative convexity because prepayment shortens duration in rallies, the dreaded MBS hedge flow that whipsaws Treasury markets.",
        ["CFA Institute"],
        indications=["Rates"], category="Risk"),

    entry("Basis Point", "",
        "Tiny unit traders use for yields and spreads — one one-hundredth of a percent.",
        "One basis point (often 'bp' or 'bip', pronounced 'beep') equals 0.01 percent. A 25 bp Fed hike is a quarter-percent move. Credit spreads, central-bank moves, swap rates, mortgage points — every fixed-income conversation runs in bps because percentage-of-a-percentage is too clumsy. 'Came in twelve wider' means the spread widened by twelve basis points.",
        ["Federal Reserve", "Bank of England"],
        indications=["Rates"], category="Pricing & Valuation"),

    entry("DV01", "Dollar Value of an 01",
        "Dollar P&L hit from a one-basis-point yield move — the rates trader's primary risk metric.",
        "Calculated from duration times price times 0.0001. A position with a hundred-thousand-dollar DV01 makes or loses that amount per basis point. Quoted in millions for big books. Used to size trades to risk limits, to compare positions across instruments, and to hedge: matching DV01s between cash bonds and swaps neutralises first-order rate risk. The 'PV01' variant is essentially the same number from the present-value direction.",
        ["CFA Institute", "ISDA"],
        indications=["Rates"], category="Risk"),

    entry("Repo", "Repurchase agreement",
        "Borrowing cash overnight against collateral — usually Treasuries.",
        "A repo is a sale with an agreement to buy back next day at a slightly higher price; the difference is the repo rate. The plumbing of short-term funding: dealers fund inventories, money funds park cash. Tri-party repo at BNY Mellon clears trillions daily. The September 2019 repo spike — rates briefly hit ten percent — forced the Fed to launch standing facilities. SOFR is calculated from repo activity.",
        ["Federal Reserve", "DTCC", "SIFMA"],
        indications=["Rates"], category="Instruments"),

    entry("FX Swap", "",
        "Exchange currencies now, agree to swap them back at a fixed forward rate.",
        "Two legs: spot exchange today, reverse exchange at maturity. Used by corporates to hedge cross-currency funding, by central banks (the Fed's swap lines with the ECB, Bank of Japan, Bank of England), and by anyone wanting to synthesise foreign-currency exposure without borrowing. The 'cross-currency basis' — the forward points implied minus what covered interest parity says — became a watched stress gauge after 2008 when banks lost access to dollar funding.",
        ["BIS", "Federal Reserve", "ICMA"],
        indications=["FX"], category="Instruments"),

    entry("Forward Points", "",
        "Premium or discount added to spot to get the forward FX rate.",
        "Derived from interest-rate differentials: borrow the high-rate currency, lend the low-rate one, and the forward must price arbitrage out (covered interest parity). Quoted as pips: USD/JPY at spot 150 with three-month forward points of -45 means the three-month forward is 149.55. Forwards above spot mean the base currency is at a premium; below means a discount. Tight in normal times, blow out in funding stress.",
        ["BIS", "Federal Reserve"],
        indications=["FX"], category="Pricing & Valuation"),

    entry("VWAP", "Volume-Weighted Average Price",
        "Average price weighted by traded volume across the day — the execution benchmark.",
        "Resets daily. Traders measure execution quality against VWAP: 'I bought five cents inside.' Brokers offer VWAP algos that slice an order across the day proportional to expected volume, minimising market impact for big trades. Index rebalances and ETF creations often target VWAP. Distinct from arrival-price benchmarks (Implementation Shortfall) which capture timing risk too.",
        ["NYSE", "SEC"],
        indications=["Equities"], category="Trading & Execution"),

    entry("TWAP", "Time-Weighted Average Price",
        "Average price across equal time slices — execution algo's simpler sibling to VWAP.",
        "TWAP algos chop an order into evenly-spaced child orders over a chosen window. Used when volume forecasts are unreliable, for less-liquid names, or when minimising signalling matters more than tracking volume. Easier to model and explain than VWAP. Common in crypto and small-cap equities. Critics note TWAP is gameable by predatory algos that detect the regular slicing pattern.",
        ["SEC", "FINRA"],
        indications=["Equities"], category="Trading & Execution"),

    entry("Implied Volatility", "IV",
        "The volatility the option market is pricing in — derived backwards from the option's premium.",
        "Black-Scholes (and successors) take inputs — spot, strike, time, rate, volatility — and output an option price. Invert the model on a traded option and the only unknown is volatility; that's IV, the market's forward-looking estimate. The VIX is a weighted IV reading off S&P 500 options. IV usually trades above realised volatility — the 'vol risk premium' that volatility sellers harvest.",
        ["CFA Institute", "CME Group"],
        indications=["Derivatives"], category="Pricing & Valuation"),

    entry("Delta", "",
        "How much an option's price moves for a one-point move in the underlying.",
        "A call's delta runs from 0 (deep out-of-the-money) to 1 (deep in-the-money); puts run 0 to -1. At-the-money options sit near plus or minus 0.5. Traders use delta to hedge: short a 0.5-delta call and buy fifty shares of the underlying to neutralise directional risk. Delta-hedging keeps shifting as the underlying moves — the gamma problem — generating the buy-high-sell-low flows that bleed long-volatility books.",
        ["ISDA", "CME Group"],
        indications=["Derivatives"], category="Risk"),

    entry("CDS Spread", "Credit Default Swap Spread",
        "Annual premium paid to insure a bond against default — basis points on notional.",
        "Buyer pays a quarterly premium (the spread), seller pays out if the reference name defaults. A 200 bp CDS on a ten-million notional costs two hundred thousand a year. Spreads widen when default looks more likely. iTraxx (Europe) and CDX (US) indexes track baskets. Blew out during the 2008 Lehman crisis and the 2023 SVB stress. Post-2009 reforms moved most trades to central clearing at LCH and ICE.",
        ["ISDA", "LCH", "ICE"],
        indications=["Credit"], category="Pricing & Valuation"),

    entry("Contango", "",
        "Futures price above spot — usually means storage costs or surplus inventory.",
        "Crude oil in storage-glut periods sits in contango: a one-month forward trades above near-month, the curve sloping upward. Holders of long futures roll into pricier contracts each month, paying the 'roll yield' penalty. The April 2020 negative WTI episode was contango taken to extremes — storage was so full that nearby contracts went negative. ETF investors in commodity products learn about contango the hard way.",
        ["CME Group", "ICE"],
        indications=["Commodities"], category="Pricing & Valuation"),

    entry("Backwardation", "",
        "Futures price below spot — usually means scarcity or strong demand for prompt delivery.",
        "The opposite of contango. Curve slopes downward. Common in commodities with seasonal demand (heating oil in winter), supply disruptions (oil after the 2022 Russia-Ukraine invasion), or storage costs that exceed convenience yield. Long futures holders earn positive roll yield, rolling cheaper. Backwardation is a generally bullish signal for the spot commodity — physical market is tight.",
        ["CME Group", "ICE"],
        indications=["Commodities"], category="Pricing & Valuation"),

    entry("SOFR", "Secured Overnight Financing Rate",
        "Overnight rate based on Treasury repo trades — the LIBOR replacement.",
        "Published daily by the New York Fed using actual transaction volume (roughly 1.5 trillion dollars daily), making it manipulation-resistant. Replaced USD LIBOR after the 2012 manipulation scandals; the formal cessation was June 2023. SOFR is risk-free (collateralised), so spreads to credit-sensitive benchmarks matter for swaps. Term SOFR (CME-published forward-looking rate) is used in business loans, and the Fed's standing repo facility helps pin the floor.",
        ["Federal Reserve", "CME Group", "Federal Reserve FRED"],
        indications=["Rates"], category="Indexes & Benchmarks"),

    entry("Settlement Date", "",
        "When ownership and cash actually change hands — distinct from the trade date.",
        "US equities moved to T+1 (one business day after trade) in May 2024, joining India and Canada. US Treasuries settle T+1. Most government bonds settle T+1 or T+2. FX spot is T+2 for most pairs (T+1 for USD/CAD). Fails to settle attract penalties under SEC Rule 204 and CSDR in Europe. The shorter cycle reduces counterparty risk but compresses post-trade processing time.",
        ["SEC", "DTCC", "ESMA"],
        indications=["Cross-asset"], category="Settlement & Operations"),

    entry("Yield Curve", "",
        "Yields plotted across maturities — the most-watched chart in markets.",
        "Usually upward-sloping: longer bonds yield more because investors demand a term premium. Inverted curve (short rates above long) has preceded every modern US recession with one false positive (1966). The 10-year-minus-2-year and 10-year-minus-3-month spreads are watched gauges. The Federal Reserve controls the short end via policy rates; the long end reflects growth and inflation expectations plus term premia. Bull steepeners, bear flatteners — every shape carries a macro meaning.",
        ["Federal Reserve", "Federal Reserve FRED", "Bank of England"],
        indications=["Rates", "Macro"], category="Pricing & Valuation"),

    entry("Fed Funds Rate", "",
        "The Fed's policy rate — what banks charge each other for overnight reserves.",
        "The Federal Open Market Committee (FOMC) sets a target range eight times a year. Since 2008 the Fed has implemented policy through interest on reserves (IORB) and the overnight reverse repo rate, which bracket the effective rate. Cuts in 2008 (from 5.25 percent to 0), hikes in 2022-23 (0 to 5.50 percent), and the path from here drive global asset prices. Watch the dot plot for the FOMC's own rate projections.",
        ["Federal Reserve", "Federal Reserve FRED"],
        indications=["Rates", "Macro"], category="Indexes & Benchmarks"),
]


# ============================================================================
# BATCH 2 — Rates basics (25 terms — bonds, yields, maturity, real vs nominal)
# ============================================================================

BATCH_RATES_BASICS = [
    entry("Bond", "",
        "Loan packaged as a tradable security — pays coupons until maturity, then principal back.",
        "Issuer (government, corporate, agency) sells bonds to raise capital; investors lend in exchange for coupon payments and repayment at maturity. Quoted as a percentage of par (100 = par; 95 = below par). Trading happens mostly OTC through dealer networks, not on exchanges. The US Treasury market is the largest and most liquid in the world — roughly 27 trillion dollars outstanding as of 2024.",
        ["SEC", "Federal Reserve"],
        indications=["Rates"], category="Instruments"),

    entry("Coupon", "",
        "Interest payment a bond pays at fixed intervals — usually twice a year.",
        "Set at issuance as a percentage of face value: a 4 percent coupon on a thousand-dollar bond pays forty dollars annually, typically twenty every six months. Zero-coupon bonds pay no periodic interest and are sold at deep discount instead. The term comes from physical bonds that had paper coupons clipped off and presented for payment — now all electronic.",
        ["CFA Institute", "SEC"],
        indications=["Rates"], category="Instruments"),

    entry("T-Bill", "Treasury Bill",
        "Short-term US government debt — matures in one year or less, issued at discount.",
        "Sold at auction by the Treasury weekly in 4-, 8-, 13-, 17-, 26-, and 52-week maturities. Pay no coupon — return is the gap between purchase price and face value at maturity. The three-month T-bill rate is the most common proxy for the risk-free rate in academic finance. Money funds hold trillions in T-bills as the safest dollar parking spot.",
        ["Federal Reserve", "Federal Reserve FRED"],
        indications=["Rates"], category="Instruments"),

    entry("T-Note", "Treasury Note",
        "Medium-term US government debt — 2, 3, 5, 7, or 10-year maturity, fixed coupon.",
        "Pays semiannual coupon. Auctioned monthly. The 10-year T-note is the most watched maturity in global markets — its yield benchmarks mortgage rates, swap spreads, and equity valuations. Sold in increments of a hundred dollars face value. Quoted in thirty-seconds: '100-08' means 100 and 8/32 of par. Total US Treasury Notes outstanding: roughly fourteen trillion in 2024.",
        ["Federal Reserve", "SEC"],
        indications=["Rates"], category="Instruments"),

    entry("T-Bond", "Treasury Bond",
        "Long-term US government debt — 20 or 30-year maturity, fixed coupon.",
        "Issued by the Treasury monthly via auction. Pays semiannual coupon, returns principal at maturity. The 30-year T-bond ('the long bond') is the longest standard Treasury maturity — its yield reflects inflation expectations and term premium far out the curve. Used by pension funds and insurance companies to match long-duration liabilities. Liquidity is thinner than the 10-year, so price moves can be sharper.",
        ["Federal Reserve"],
        indications=["Rates"], category="Instruments"),

    entry("Maturity", "",
        "Date a bond's principal is repaid — the end of the loan.",
        "Bonds are classified by time to maturity: bills (one year or less), notes (2-10 years), bonds (over 10 years), and perpetuals (no fixed maturity). Maturity drives a bond's sensitivity to rates — longer maturity, more duration, bigger price swings. 'Bullet maturity' means principal is repaid in one lump at the end; amortising bonds repay over the life. Maturities cluster around standard tenors for liquidity reasons.",
        ["SEC", "CFA Institute"],
        indications=["Rates"], category="Instruments"),

    entry("Face Value", "Par Value",
        "Amount the issuer repays at maturity — the bond's principal.",
        "Also called 'par value' or 'principal'. Most corporate and government bonds use a thousand-dollar face value; municipal bonds often five thousand; some sovereign bonds a hundred. Coupon payments are computed as a percentage of face value, not of market price. A bond trading at 95 means 95 percent of face — for a thousand-dollar bond, that's nine hundred and fifty dollars.",
        ["SEC", "CFA Institute"],
        indications=["Rates"], category="Instruments"),

    entry("Par", "",
        "Bond priced at exactly 100 percent of face value — neither at a premium nor a discount.",
        "Bonds issued at par sell at face value with a coupon equal to the prevailing yield. As market rates change, the bond trades to a premium (above par) if its coupon is now generous, or to a discount (below par) if it's stingy. 'Par swap' rates are the swap fixed leg that would make the swap value zero at inception.",
        ["CFA Institute"],
        indications=["Rates"], category="Pricing & Valuation"),

    entry("Premium", "",
        "Bond trading above par — usually because its coupon beats current market rates.",
        "A 5 percent coupon bond in a 3 percent yield environment trades at a premium — the high coupon makes the bond more valuable than face value. Holders pay extra upfront but recover it through the bigger coupon stream. Mathematically, the premium amortises down to zero by maturity. Most callable bonds trade close to par because issuers redeem early when premiums build up.",
        ["CFA Institute"],
        indications=["Rates"], category="Pricing & Valuation"),

    entry("Discount", "",
        "Bond trading below par — usually because its coupon lags current market rates.",
        "A 2 percent coupon bond in a 4 percent yield environment trades at a discount: the skimpy coupon makes the bond less valuable than face value. Holders pay less upfront and recoup the gap when face value is repaid at maturity. Original-issue discount (OID) bonds are issued below par on purpose. T-bills are pure discount instruments — no coupon, just gap to face.",
        ["CFA Institute", "SEC"],
        indications=["Rates"], category="Pricing & Valuation"),

    entry("Zero-Coupon Bond", "Zero",
        "Bond with no coupon — sold at deep discount, pays face value at maturity.",
        "All return comes from the spread between purchase price and the face value paid at maturity. The longer the maturity, the steeper the discount. STRIPS — separated trading of registered interest and principal — let dealers strip Treasury notes into zero-coupon pieces. Zero-coupon bonds have higher duration than coupon bonds of the same maturity, making them powerful tools for pension liability matching.",
        ["Federal Reserve", "CFA Institute"],
        indications=["Rates"], category="Instruments"),

    entry("YTM", "Yield to Maturity",
        "Total annualised return if you buy a bond today and hold to maturity.",
        "Solves for the discount rate that equates the bond's future cash flows (coupons plus face value) to its current market price. Implicitly assumes you reinvest each coupon at the same yield. Quoted as the headline yield in bond tables. Differs from current yield (coupon over price) which ignores principal gain or loss. Bond traders quote YTM, not current yield, for anything maturity-bearing.",
        ["CFA Institute", "SEC"],
        indications=["Rates"], category="Pricing & Valuation"),

    entry("Current Yield", "",
        "Annual coupon income divided by current bond price — simple yield.",
        "A 5 percent coupon bond trading at 95 has current yield of 5.26 percent (5 over 95). Misses two things YTM captures: the gain or loss to maturity, and the time value of intermediate coupons. Useful as a quick income check for the buy-and-hold investor but not a true total-return measure. Most quoted in retail brokerage screens; institutional desks use YTM.",
        ["SEC", "CFA Institute"],
        indications=["Rates"], category="Pricing & Valuation"),

    entry("Yield to Call", "YTC",
        "YTM calculated assuming the issuer redeems the bond at the earliest call date.",
        "Callable bonds let the issuer redeem early — typically when rates fall and the issuer can refinance cheaper. YTC computes the yield to that call date instead of final maturity. For premium-priced callable bonds, YTC is usually lower than YTM and is the realistic measure. The 'yield to worst' is the lower of YTC and YTM — what conservative analysts quote.",
        ["CFA Institute"],
        indications=["Rates"], category="Pricing & Valuation"),

    entry("Risk-Free Rate", "",
        "Theoretical rate of return with zero default risk — the foundation of every valuation model.",
        "Used as the discount rate floor in DCF analysis, the baseline for CAPM, and the input to option-pricing models. In practice, US Treasury yields proxy for the dollar risk-free rate; German Bunds for euro; Japanese government bonds for yen. Post-LIBOR transition, swap rates referenced to SOFR play this role for derivatives. 'Risk-free' is shorthand — no asset is fully default-free, but Treasuries are as close as it gets.",
        ["CFA Institute", "Federal Reserve"],
        indications=["Rates"], category="Pricing & Valuation"),

    entry("Real Rate", "Real Interest Rate",
        "Interest rate after stripping out expected inflation — the rate that grows purchasing power.",
        "Equals the nominal rate minus expected inflation (the Fisher equation). Negative real rates — a feature of 2020-21 — mean savers lose purchasing power even at positive nominal yields. TIPS (Treasury Inflation-Protected Securities) trade explicit real yields; the gap to nominal Treasuries is the breakeven inflation rate. Central banks track real rates closely because they're what actually constrains or stimulates economic activity.",
        ["Federal Reserve", "Federal Reserve FRED"],
        indications=["Rates", "Macro"], category="Pricing & Valuation"),

    entry("Nominal Rate", "Nominal Interest Rate",
        "The headline interest rate quoted in the market — includes both real return and expected inflation.",
        "Every yield in the financial press is nominal unless explicitly labelled 'real'. The Federal Reserve's policy target, mortgage rates, corporate bond yields, deposit rates — all nominal. Used in cash-flow calculations where the cash flows themselves are nominal (most bond coupons). Compare to real rates for purchasing-power analysis. The nominal-versus-real distinction matters most in high-inflation environments.",
        ["Federal Reserve"],
        indications=["Rates", "Macro"], category="Pricing & Valuation"),

    entry("Term Premium", "",
        "Extra yield long-dated bonds pay over rolling short bonds — compensation for locking up money.",
        "If investors only demanded expected average short rates over the bond's life, long yields would equal those expected averages. They don't — they include a term premium that compensates for inflation surprise, default risk, and inconvenience. The Federal Reserve's ACM model decomposes long yields into expected rates and term premium. Term premium turned negative after 2014 QE — unprecedented in modern history.",
        ["Federal Reserve", "BIS"],
        indications=["Rates", "Macro"], category="Pricing & Valuation"),

    entry("Reinvestment Risk", "",
        "Risk that future coupon income earns less than the original yield — falling-rate problem.",
        "When a bond pays a coupon, the holder needs somewhere to reinvest it. If rates have fallen since purchase, the new investment earns less than the original yield-to-maturity assumed. Longer coupon-paying bonds carry more reinvestment risk than zero-coupon bonds (which have none). Pension funds use immunisation strategies — matching asset duration to liability duration — partly to neutralise reinvestment risk.",
        ["CFA Institute"],
        indications=["Rates"], category="Risk"),

    entry("Floating Rate", "FRN",
        "Coupon that resets periodically based on a reference index — usually SOFR or EURIBOR.",
        "Floating-rate notes (FRNs) pay 'reference plus spread' — say, SOFR plus 80 basis points — with the coupon resetting quarterly or semiannually. Duration is roughly equal to the reset frequency, not the maturity, because the coupon adjusts with rates. Popular in rising-rate environments. Most corporate bank loans and many structured products are floating-rate. The 2023 LIBOR cessation forced trillions of contracts to migrate to SOFR-based equivalents.",
        ["ISDA", "Federal Reserve"],
        indications=["Rates"], category="Pricing & Valuation"),

    entry("Fixed Rate", "",
        "Coupon set at issuance and unchanged through the bond's life.",
        "The traditional bond structure: 5 percent coupon for 10 years, no resets. Investor takes interest-rate risk; issuer locks in funding cost. Most US Treasuries, most corporate bonds, and most municipal bonds are fixed-rate. Compare with floating-rate notes, where the coupon resets. Fixed-rate bond prices move inversely to rates because the coupon stream stays put while market yields shift.",
        ["SEC", "CFA Institute"],
        indications=["Rates"], category="Pricing & Valuation"),

    entry("Sovereign Debt", "",
        "Debt issued by a national government — typically the safest credit in its own currency.",
        "US Treasuries, UK Gilts, German Bunds, Japanese JGBs sit at the top of the sovereign credit hierarchy. Emerging-market sovereigns (Brazil, Turkey, South Africa) pay credit-spread premia reflecting default risk. Sovereign debt in a country's own currency is theoretically default-free (the government prints the currency) — but the 1998 Russia default and 2012 Greece restructuring proved exceptions. Hard-currency sovereign issuance carries higher risk than local-currency.",
        ["IMF", "BIS"],
        indications=["Rates", "Credit"], category="Instruments"),

    entry("Inflation-Linked Bond", "TIPS / Linker",
        "Bond whose principal adjusts with inflation — protects real purchasing power.",
        "US Treasury Inflation-Protected Securities (TIPS) are the largest market. Principal grows by CPI changes; coupons (set at a real rate) apply to the inflation-adjusted principal. UK index-linked Gilts and euro-area linkers (BTPei, OATei) work similarly. The break-even inflation rate — nominal Treasury yield minus TIPS yield — is the market's implied inflation expectation. Issued at 5-, 10-, and 30-year maturities; auctioned a handful of times each year.",
        ["Federal Reserve", "Bank of England"],
        indications=["Rates", "Macro"], category="Instruments"),

    entry("Treasury", "US Treasury",
        "Debt issued by the US Treasury Department — the world's largest fixed-income market.",
        "Includes bills, notes, bonds, TIPS, FRNs, and STRIPS. Issued via auction to primary dealers, who then distribute to the broader market. Total outstanding crossed 35 trillion in 2024. Treasuries function as the global risk-free benchmark, collateral for repo markets, central-bank reserve holdings, and the foundation of dollar-denominated valuation. Yields on different Treasury maturities form the US yield curve.",
        ["Federal Reserve", "SEC"],
        indications=["Rates"], category="Instruments"),

    entry("Government Bond", "Sovereign Bond",
        "Bond issued by a national or regional government to fund operations.",
        "Includes US Treasuries, UK Gilts, German Bunds, Japanese JGBs, French OATs — names vary by jurisdiction but mechanics are similar. National governments tap their own currency markets first; emerging-market sovereigns also issue in hard currency (USD or EUR) when needed. Local-currency sovereign bonds are the standard reference for that country's risk-free rate. Spreads between sovereigns measure relative credit and currency risk.",
        ["BIS", "Federal Reserve"],
        indications=["Rates"], category="Instruments"),
]


# ============================================================================
# BATCH 3 — Rates deep (25 terms — swaps, futures, repo facilities, reference rates)
# ============================================================================

BATCH_RATES_DEEP = [
    entry("Interest Rate Swap", "IRS",
        "Exchange of fixed coupon payments for floating, both on the same notional.",
        "The single largest derivatives market by notional — over 500 trillion globally. A standard swap exchanges fixed coupons for SOFR-linked floating (or EURIBOR/SONIA/TONAR), reset quarterly. Used by corporates to convert fixed-rate debt into floating exposure (or vice versa), by banks to hedge mortgage portfolios, and by hedge funds to express rate views. Centrally cleared at LCH and CME post-2012 Dodd-Frank reforms.",
        ["ISDA", "LCH", "BIS"],
        indications=["Rates"], category="Instruments"),

    entry("Swap Spread", "",
        "Gap between the swap rate and the Treasury yield at the same maturity.",
        "Quoted in basis points. A 10-year swap rate of 4.50 percent versus a 10-year Treasury at 4.30 percent gives a 20 bp swap spread. Negative swap spreads (common since 2015) reflect dealer balance-sheet costs from holding Treasury inventory, regulatory capital pressure, and net duration demand. Once seen as a credit signal, now a plumbing indicator.",
        ["Federal Reserve", "ISDA"],
        indications=["Rates"], category="Pricing & Valuation"),

    entry("OIS", "Overnight Index Swap",
        "Swap where the floating leg is the compounded overnight rate — minimal credit risk.",
        "The floating leg averages the daily overnight rate (SOFR in USD, ESTR in EUR, SONIA in GBP) over the period. Because overnight rates are collateralised, OIS contains almost no credit component — making the OIS curve the cleanest discount curve for derivative valuation. Post-2008, dealers price collateralised derivatives off OIS rather than LIBOR. Standard tenors run from one week to 30 years.",
        ["ISDA", "Federal Reserve"],
        indications=["Rates"], category="Instruments"),

    entry("SOFR-OIS Spread", "",
        "Gap between term SOFR rates and the compounded overnight SOFR — measures rate-volatility expectations.",
        "Term SOFR (CME-published) is a forward-looking estimate; OIS averages realised overnight SOFR. When markets expect significant policy moves or volatility, term SOFR includes a premium over OIS. Tracked by traders to gauge the market's anticipation of Fed action between meetings. Spreads compressed in 2024 as Fed policy stabilised.",
        ["CME Group", "Federal Reserve"],
        indications=["Rates"], category="Pricing & Valuation"),

    entry("FRA", "Forward Rate Agreement",
        "OTC contract locking in a future short-term interest rate.",
        "Buyer pays fixed and receives floating (or vice versa) over a future period — say, three-month SOFR starting in six months. Settles in cash at the period's start based on the gap between the agreed rate and the realised reference rate. Largely supplanted by IRS post-LIBOR transition for longer dates, but still used at short maturities and as building blocks for swap pricing.",
        ["ISDA", "BIS"],
        indications=["Rates"], category="Instruments"),

    entry("Eurodollar Futures", "ED Futures",
        "CME-listed futures on three-month USD LIBOR — discontinued after 2023 LIBOR cessation.",
        "Once the most liquid interest-rate futures contract in the world — trillions of notional weekly. Replaced by SOFR futures after the formal LIBOR cessation in June 2023. Last Eurodollar futures contracts expired in 2023. The name comes from dollar-denominated deposits held offshore (originally in London) — historically the underlying for LIBOR.",
        ["CME Group", "Federal Reserve"],
        indications=["Rates"], category="Instruments"),

    entry("SOFR Futures", "",
        "CME-listed futures on average SOFR over a future period.",
        "Two main contracts: 1-month SOFR futures (average daily SOFR over the contract month) and 3-month SOFR futures (compounded SOFR over a quarter). Replaced Eurodollar futures as the benchmark short-rate hedging tool post-LIBOR. Quarterly serial expiries out to 10 years. Used by banks to hedge floating-rate exposure, by traders to express Fed-policy views, and as inputs to forward-rate curves.",
        ["CME Group", "Federal Reserve"],
        indications=["Rates"], category="Instruments"),

    entry("Fed Funds Futures", "",
        "CME futures contracts referencing the monthly average effective federal funds rate.",
        "The cleanest market-implied probability of Fed policy moves. Each contract settles to one minus the average daily EFFR during the contract month. The difference between adjacent contracts is the market's expected move at that FOMC meeting. CME publishes the FedWatch tool that translates these prices into rate-change probabilities. Heavily watched by macro traders and Fed-watchers.",
        ["CME Group", "Federal Reserve"],
        indications=["Rates"], category="Instruments"),

    entry("Reverse Repo", "RRP",
        "Mirror of a repo — the cash lender's side of the transaction.",
        "Same trade as a repo, named from the other side: the party temporarily lending cash and receiving collateral 'does a reverse repo'. The Fed's Overnight Reverse Repo Facility (ON RRP) lets money funds and GSEs deposit cash at the Fed against Treasuries; balances peaked above 2.5 trillion in 2022-23 as excess liquidity sought a floor. ON RRP rate acts as the floor of the policy corridor.",
        ["Federal Reserve", "DTCC"],
        indications=["Rates"], category="Instruments"),

    entry("Tri-Party Repo", "",
        "Repo where a custodian bank handles settlement and collateral management.",
        "BNY Mellon clears the vast majority of US tri-party repo (trillions daily). The custodian holds the collateral, marks it to market, and substitutes one piece for another as needed. Reduces operational burden on the cash lender (typically a money fund) and lets dealers fund a portfolio rather than security-by-security. Distinct from bilateral repo (direct between counterparties) and cleared repo through FICC.",
        ["DTCC", "SIFMA"],
        indications=["Rates"], category="Settlement & Operations"),

    entry("IORB", "Interest on Reserve Balances",
        "Rate the Fed pays banks on reserves held at the Fed — sets the ceiling of the policy corridor.",
        "Introduced in 2008 (originally as IOER for excess reserves) to give the Fed control over short rates without draining reserves. Since 2021 it's the headline 'administered rate' the FOMC sets alongside the fed funds target range. With reserves abundant (over 3 trillion), banks won't lend below IORB in the interbank market — making IORB the effective ceiling. Currently the headline number watched at each FOMC meeting.",
        ["Federal Reserve", "Federal Reserve FRED"],
        indications=["Rates"], category="Indexes & Benchmarks"),

    entry("ON RRP Rate", "Overnight Reverse Repo Rate",
        "Rate the Fed pays counterparties on cash deposited at its overnight reverse repo facility.",
        "Sits below IORB by a few basis points. The floor of the policy corridor: non-bank cash holders (money funds, GSEs) won't accept lower rates in private markets when they can park cash at the Fed. Counterparties include the major money funds, GSEs like Fannie and Freddie, and primary dealers. Daily balances published by the New York Fed.",
        ["Federal Reserve"],
        indications=["Rates"], category="Indexes & Benchmarks"),

    entry("Standing Repo Facility", "SRF",
        "Fed facility that lends cash overnight against Treasury collateral at a pre-set rate.",
        "Launched July 2021 after the September 2019 repo spike. Lets primary dealers (and some banks) borrow from the Fed against Treasuries at a rate slightly above IORB, capping how high repo rates can spike. Counterparts to ON RRP: SRF caps the upside, ON RRP caps the downside. Combined, they form a tighter corridor for short rates.",
        ["Federal Reserve"],
        indications=["Rates"], category="Settlement & Operations"),

    entry("Discount Window", "",
        "Fed's traditional lending facility for banks needing emergency short-term funding.",
        "Three tiers: primary credit (healthy banks), secondary credit (weaker banks), seasonal credit (small banks with cyclical needs). Borrowing carries stigma — banks fear signalling weakness to counterparties — so usage is usually minimal except in crises. The March 2023 Bank Term Funding Program added a Discount Window-adjacent emergency facility after SVB. Primary credit rate is typically set 25 bp above IORB.",
        ["Federal Reserve"],
        indications=["Rates"], category="Settlement & Operations"),

    entry("EFFR", "Effective Federal Funds Rate",
        "Daily volume-weighted median rate at which banks lend reserves to each other overnight.",
        "Published daily by the New York Fed using transaction-level data from brokered fed funds trades. Stays inside the FOMC's target range thanks to IORB (ceiling) and ON RRP (floor). EFFR is what fed funds futures settle to. With reserves abundant, the interbank fed funds market is much smaller than pre-2008 — most volume is GSE lending to banks rather than bank-to-bank.",
        ["Federal Reserve", "Federal Reserve FRED"],
        indications=["Rates"], category="Indexes & Benchmarks"),

    entry("EURIBOR", "Euro Interbank Offered Rate",
        "Daily benchmark for euro interbank lending — still in use post-LIBOR reform.",
        "Published by the European Money Markets Institute (EMMI) using a hybrid methodology (transactions where possible, market-based estimates where not). Tenors from 1 week to 12 months. Underlies trillions in euro-denominated mortgages, swaps, and corporate loans. Survived the LIBOR reforms by overhauling methodology in 2019. ESTR (Euro Short-Term Rate) is the overnight risk-free complement.",
        ["ECB", "ESMA"],
        indications=["Rates"], category="Indexes & Benchmarks"),

    entry("ESTR", "Euro Short-Term Rate",
        "ECB-published overnight unsecured euro borrowing rate — euro-area equivalent of SOFR (but unsecured).",
        "Calculated from actual transactions reported by 50-plus large euro-area banks. Replaced EONIA in October 2019 as the recommended euro overnight benchmark. ESTR is unsecured (interbank borrowing), unlike SOFR which is collateralised by Treasuries. Underlies euro OIS swaps and post-LIBOR euro derivatives. ECB publishes ESTR daily by 9:00 CET.",
        ["ECB"],
        indications=["Rates"], category="Indexes & Benchmarks"),

    entry("SONIA", "Sterling Overnight Index Average",
        "Bank of England's overnight benchmark — sterling LIBOR replacement.",
        "Volume-weighted median of unsecured overnight sterling deposits at major banks. Replaced GBP LIBOR by end-2021. Underlies sterling OIS swaps and most new sterling floating-rate instruments. Backward-looking (rate known only after the day ends), so compounded-in-arrears methodology is used for term coupon calculations. Compare with Term SONIA, which is forward-looking and used in business loans.",
        ["Bank of England"],
        indications=["Rates"], category="Indexes & Benchmarks"),

    entry("TONAR", "Tokyo Overnight Average Rate",
        "Bank of Japan's overnight benchmark — yen LIBOR replacement.",
        "Volume-weighted median of unsecured overnight yen call market transactions. Replaced JPY LIBOR by end-2021. Used in yen OIS and post-LIBOR yen floating-rate instruments. Yen TONAR rates spent most of 2016-2024 near zero or negative due to BoJ ultra-loose policy; positive territory only after the March 2024 policy normalisation.",
        ["BIS"],
        indications=["Rates"], category="Indexes & Benchmarks"),

    entry("Term SOFR", "",
        "CME-published forward-looking version of SOFR — used in business loans.",
        "Calculated from SOFR derivatives (SOFR futures and OIS) to produce 1-, 3-, 6-, and 12-month rates known at the start of each period. Solves the practical problem that compounded-in-arrears SOFR isn't usable for business loans where borrowers need to know the rate upfront. Strict use restrictions: ARRC limits Term SOFR to specific cash-product use cases, not derivatives.",
        ["CME Group", "Federal Reserve"],
        indications=["Rates"], category="Indexes & Benchmarks"),

    entry("LIBOR", "London Interbank Offered Rate",
        "Discontinued benchmark — once the world's most-used reference rate for trillions in contracts.",
        "Published in five currencies (USD, GBP, EUR, JPY, CHF) and multiple tenors by the IBA. After the 2012 manipulation scandal exposed banks colluding on submissions, regulators forced replacement: most LIBOR settings ceased end-2021, and the final USD tenors stopped in June 2023. Legacy LIBOR contracts with no clear fallback got 'synthetic LIBOR' until 2024. Now historical only.",
        ["FCA", "ESMA"],
        indications=["Rates"], category="Indexes & Benchmarks"),

    entry("Negative Rates", "",
        "Interest rates below zero — depositors pay the bank to hold money.",
        "Adopted by the ECB (2014-2022), Bank of Japan (2016-2024), SNB (2015-2022), Riksbank, and Danish Nationalbank to fight deflation and stimulate lending. Pass-through to retail depositors was rare; banks ate the cost or charged corporates and large savers. Bond yields went negative across multi-trillion notional. Departed once inflation returned. Mechanically unusual: cash holding (zero rate) imposes a soft floor.",
        ["ECB", "BIS"],
        indications=["Rates", "Macro"], category="Pricing & Valuation"),

    entry("Inverted Yield Curve", "",
        "Yield curve where short rates exceed long rates — historically a recession signal.",
        "Most-watched inversion: 10-year Treasury yield below 2-year. Has preceded every US recession in the past 50 years with one false positive (1966). The 10y-3m spread also tracked. Inversions in 2022-23 were the deepest since the early 1980s. Mechanism: when investors expect future rate cuts, they bid up long bonds, pushing their yields below short rates anchored by current Fed policy.",
        ["Federal Reserve", "Federal Reserve FRED"],
        indications=["Rates", "Macro"], category="Pricing & Valuation"),

    entry("Bear Steepener", "",
        "Yield curve trade or shift where long yields rise faster than short yields.",
        "Typical when inflation expectations rise sharply or when the Fed signals it will let inflation run hot before tightening. The 2003 Greenspan 'measured pace' communication triggered a notorious bear steepener. Long bonds underperform short bonds. Opposite: bull flattener, when long yields fall and the curve flattens (typical of growth slowdowns).",
        ["Federal Reserve"],
        indications=["Rates"], category="Pricing & Valuation"),

    entry("Bull Flattener", "",
        "Yield curve flattening driven by long yields falling faster than short yields.",
        "Typical of growth scares: investors pile into long bonds for safety, pulling long yields down while the Fed hasn't moved yet. Long bonds outperform short bonds. Repeatedly seen in 2024 around recession-fear episodes. Opposite of bear steepener. The 'bull' label means falling yields (bonds rallying); 'flattener' means the curve flattens.",
        ["Federal Reserve"],
        indications=["Rates"], category="Pricing & Valuation"),
]


# ============================================================================
# BATCH 4 — FX spot & forwards (25 terms — pairs, parity, carry, fix mechanics)
# ============================================================================

BATCH_FX_SPOT = [
    entry("FX Spot", "Spot FX",
        "FX trade settling in two business days at the current market rate.",
        "The base of the FX market — over 7 trillion dollars in daily turnover globally (BIS 2022 survey). Most pairs settle T+2; USD/CAD and USD/MXN settle T+1. Spot rates fluctuate continuously across global trading hours, with London accounting for roughly 40 percent of volume. Dealers quote two-way prices (bid-offer) to clients; the largest pairs have spreads of a fraction of a basis point.",
        ["BIS"],
        indications=["FX"], category="Instruments"),

    entry("Currency Pair", "",
        "Two currencies quoted against each other — the price says how much of the quote currency buys one unit of the base.",
        "EUR/USD at 1.0850 means one euro buys 1.0850 US dollars. The base currency is first (EUR), the quote currency is second (USD). 'Major pairs' (EUR/USD, USD/JPY, GBP/USD, USD/CHF, AUD/USD, USD/CAD, NZD/USD) account for most volume. Cross pairs exclude USD (EUR/JPY, GBP/CHF). Exotic pairs include emerging-market currencies (USD/TRY, USD/ZAR).",
        ["BIS"],
        indications=["FX"], category="Instruments"),

    entry("Major Pair", "",
        "Currency pair involving USD and one of the other most-traded currencies.",
        "The seven majors: EUR/USD, USD/JPY, GBP/USD, USD/CHF, AUD/USD, USD/CAD, NZD/USD. EUR/USD alone is roughly a quarter of global FX turnover. Majors have the tightest spreads, deepest liquidity, and 24-hour pricing during the trading week. Cross pairs and exotic pairs trade at wider spreads with thinner liquidity.",
        ["BIS"],
        indications=["FX"], category="Instruments"),

    entry("Cross-Rate", "Cross",
        "Currency pair that doesn't include the US dollar — EUR/GBP, EUR/JPY, GBP/CHF.",
        "Derived from each currency's USD rate: EUR/JPY equals EUR/USD divided by USD/JPY... no, actually multiplied, since JPY is on the bottom of USD/JPY. Triangular arbitrage keeps cross rates consistent with major-pair rates. The most-traded crosses are EUR/JPY, EUR/GBP, and AUD/JPY. Spreads on crosses are wider than majors because dealers have to hedge through two USD legs.",
        ["BIS"],
        indications=["FX"], category="Instruments"),

    entry("Base Currency", "",
        "First currency in a pair quote — the one being priced.",
        "In EUR/USD, EUR is the base — the rate tells you how many dollars you'd pay for one euro. Conventions are sticky: EUR is always base against everything else; GBP is base against most things except EUR; USD is base against most non-major currencies. When the base currency strengthens, the pair's price rises. Reading FX news requires keeping the base straight.",
        ["BIS"],
        indications=["FX"], category="Instruments"),

    entry("Quote Currency", "Counter Currency",
        "Second currency in a pair — the unit the price is denominated in.",
        "In EUR/USD at 1.0850, USD is the quote currency: the price says 1.0850 USD per 1 EUR. The quote currency is what you pay (when buying the base) or receive (when selling the base). Profits and losses on a position accrue in the quote currency unless explicitly converted. Some quote-currency conventions are surprising: GBP/JPY is GBP-base/JPY-quote, with prices like 195.50.",
        ["BIS"],
        indications=["FX"], category="Instruments"),

    entry("Pip", "Percentage in Point",
        "Smallest standard increment of an FX quote — usually the fourth decimal place.",
        "EUR/USD moving from 1.0850 to 1.0851 is one pip up. Most pairs use four decimal places, making one pip 0.0001 of the quote currency. JPY pairs use two decimal places, so one pip is 0.01. 'Pipettes' (fifth decimal) are sub-pip resolution offered by some dealers. P&L on FX positions is naturally measured in pips times position size.",
        ["BIS"],
        indications=["FX"], category="Pricing & Valuation"),

    entry("Big Figure", "Handle",
        "Large unit of an FX quote — the digits before the decimal point.",
        "EUR/USD at 1.0850 has 'big figure' 1.08; a move to 1.0950 is a 'big figure' move. Used in trader shorthand: 'EUR-USD is 50/55 in the figure' means 1.0850 bid / 1.0855 offered. Big-figure changes are visually meaningful — round-number levels often act as support or resistance because algos and option strikes cluster there.",
        ["BIS"],
        indications=["FX"], category="Pricing & Valuation"),

    entry("Outright Forward", "FX Forward",
        "Single FX trade settling later than spot — locks in the rate today.",
        "Used by corporates to hedge known future cash flows: a UK importer expecting to pay 10 million dollars in three months sells GBP for USD forward today, fixing the conversion rate. Pricing comes from spot plus forward points (driven by the interest-rate differential). Distinct from an FX swap (which combines spot and forward legs) and from non-deliverable forwards (cash-settled).",
        ["BIS", "ISDA"],
        indications=["FX"], category="Instruments"),

    entry("NDF", "Non-Deliverable Forward",
        "FX forward settled in cash on the difference between agreed and realised spot — no currency change hands.",
        "Used for currencies with capital controls or thin onshore markets: BRL, CNY, INR, KRW, TWD. Settled in USD (or the convertible currency) based on the gap between the contract rate and a fixing rate on settlement day. London is the dominant NDF trading centre. Volumes have grown as EM hedging demand has scaled and onshore access remains restricted.",
        ["BIS", "ISDA"],
        indications=["FX"], category="Instruments"),

    entry("PPP", "Purchasing Power Parity",
        "Theory that exchange rates should equalise the cost of a basket of goods across countries.",
        "Long-run anchor for fair-value FX models. The Economist's 'Big Mac Index' is the popular illustration: a Big Mac costing $5 in the US and 4 pounds in the UK implies GBP/USD around 1.25 if PPP holds. In practice, PPP holds poorly over short and medium horizons because of trade frictions, non-tradeable goods, and capital flows. Useful as a long-run reversion benchmark, not a trading signal.",
        ["IMF", "OECD"],
        indications=["FX", "Macro"], category="Pricing & Valuation"),

    entry("Covered Interest Parity", "CIP",
        "Arbitrage condition: forward FX rate equals spot adjusted for the interest-rate differential.",
        "Mathematically, forward equals spot times (1 plus quote rate) divided by (1 plus base rate). When CIP holds exactly, there's no arbitrage between investing in one currency and hedging back to another. Persistent CIP deviations since 2008 — the 'cross-currency basis' — reflect post-crisis bank funding constraints. The USD basis widens during stress as global banks scramble for dollars.",
        ["BIS"],
        indications=["FX"], category="Pricing & Valuation"),

    entry("Uncovered Interest Parity", "UIP",
        "Theory: high-yield currencies should depreciate to offset the rate advantage.",
        "Predicts no excess return from borrowing low-yield currencies to invest in high-yield ones. Famously fails in practice: the carry trade has historically delivered positive excess returns over decades, including during the 2002-08 yen-funded carry bonanza. UIP failure underpins the long-running 'forward premium puzzle' in academic finance. Briefly held during 2008 and 2020 crises when carry trades unwound violently.",
        ["IMF", "BIS"],
        indications=["FX"], category="Pricing & Valuation"),

    entry("Carry Trade", "",
        "Borrow a low-yield currency, invest in a high-yield one — pocket the rate differential.",
        "Classic example: borrow JPY at 0.1 percent, invest in AUD at 4 percent, earn the 3.9-percent gap as carry. Works in calm markets; explodes in stress (2008 AUD/JPY fell 50 percent in months). Risk: the funding currency rallies in a flight-to-safety, wiping out months of carry in days. Hedge funds and macro strategies systematically run carry baskets, sized to risk metrics like volatility-adjusted carry.",
        ["BIS"],
        indications=["FX", "Macro"], category="Pricing & Valuation"),

    entry("Funding Currency", "",
        "Low-yield currency borrowed to finance carry positions.",
        "Traditional funding currencies: JPY (yen), CHF (Swiss franc), EUR (euro), USD (when Fed is cutting). Choice depends on the rate differential and the currency's behaviour during stress — JPY rallies in risk-off, making it a costly funding leg when carry unwinds. Mortgage-style: many corporates and households in Eastern Europe took on CHF or EUR mortgages pre-2008, then got hammered when those currencies rallied.",
        ["BIS"],
        indications=["FX"], category="Pricing & Valuation"),

    entry("Investment Currency", "Target Currency",
        "High-yield currency on the receiving end of a carry trade.",
        "Typical EM investment currencies: BRL, MXN, ZAR, TRY (when rates are high), IDR. G10 investment currencies: AUD, NZD, GBP, USD (during hiking cycles). The investment currency receives the carry but takes the credit/currency risk. When EM crises hit (Russia 1998, Turkey 2018), investment currencies depreciate sharply, often more than the accumulated carry.",
        ["BIS", "IMF"],
        indications=["FX"], category="Pricing & Valuation"),

    entry("Reserve Currency", "",
        "Currency that other central banks hold in their FX reserves — primarily the US dollar.",
        "USD makes up roughly 58 percent of allocated global reserves (IMF COFER, late 2024), down from 70 percent in 2000. EUR around 20 percent, JPY 6, GBP 5, CNY 2, plus smaller shares of CAD, AUD, CHF. Reserve status confers 'exorbitant privilege' — global demand for the currency keeps borrowing costs lower than economic fundamentals alone would suggest. Sanctions and de-dollarisation discussions are a recurring theme.",
        ["IMF", "BIS"],
        indications=["FX", "Macro"], category="Pricing & Valuation"),

    entry("Currency Peg", "",
        "Fixed exchange rate against another currency, maintained by central-bank intervention.",
        "Hong Kong dollar pegged to USD (since 1983), Saudi riyal pegged to USD, Danish krone pegged to EUR. The central bank stands ready to buy or sell its currency at the peg rate, using FX reserves to defend it. Pegs collapse when reserves run out or when the peg becomes economically untenable — Argentina abandoned its USD peg in 2002, the Swiss removed the EUR cap in 2015.",
        ["IMF"],
        indications=["FX", "Macro"], category="Pricing & Valuation"),

    entry("Crawling Peg", "",
        "Currency peg that adjusts gradually over time — a controlled depreciation or appreciation.",
        "Used by countries managing inflation differentials without abandoning the peg discipline. China ran a managed crawling peg/band against USD from 2005-2015. Vietnam, Nicaragua, and historically Brazil used crawling pegs to handle inflation. Distinct from a hard peg (fixed) and a free float (market-determined). Bands around the central rate let the currency wiggle without breaking the regime.",
        ["IMF"],
        indications=["FX", "Macro"], category="Pricing & Valuation"),

    entry("Floating Exchange Rate", "Free Float",
        "Exchange rate determined entirely by market forces — no central-bank intervention.",
        "USD, EUR, JPY, GBP all float freely. Central banks may intervene rhetorically or in extreme cases, but no formal target. Contrast with managed floats (Singapore, India intervene actively) and pegs. Free floats absorb shocks through price adjustments rather than reserve drains — the trade-off is more day-to-day volatility but no peg-collapse risk. Most developed-market currencies have floated since the 1973 Bretton Woods collapse.",
        ["IMF", "Federal Reserve"],
        indications=["FX", "Macro"], category="Pricing & Valuation"),

    entry("DXY", "Dollar Index",
        "ICE-published trade-weighted index of the US dollar against six major currencies.",
        "Weights: EUR 57.6 percent, JPY 13.6, GBP 11.9, CAD 9.1, SEK 4.2, CHF 3.6 (fixed since 1973). Quoted to two decimals — DXY at 105 means the dollar is 5 percent stronger than the 1973 baseline. Used as a quick read on dollar strength; included in many macro models. Tracks broad dollar direction but is heavy on European exposures and excludes major partners like CNY, KRW, INR.",
        ["ICE"],
        indications=["FX"], category="Indexes & Benchmarks"),

    entry("REER", "Real Effective Exchange Rate",
        "Trade-weighted exchange rate adjusted for inflation differentials.",
        "Published monthly by the BIS for 60-plus countries. Adjusts the nominal effective rate (basket of currencies weighted by trade) for relative price levels. Tracks competitiveness: a rising REER means the country's exports are getting pricier relative to peers. REER deviations from long-term averages flag potential currency mis-valuation. Central banks watch REER closely; it's a better fair-value gauge than nominal bilateral rates.",
        ["BIS", "IMF"],
        indications=["FX", "Macro"], category="Pricing & Valuation"),

    entry("Triangular Arbitrage", "",
        "Exploits inconsistencies between cross-rate quotes and the implied rate from two majors.",
        "If EUR/USD is 1.10, USD/JPY is 150, and EUR/JPY is 166, the implied EUR/JPY via the dollar legs is 165 — and an arbitrageur buys EUR/JPY at 165 and sells at 166 for risk-free profit. Algorithms close these gaps in milliseconds, so opportunities are vanishingly small in major pairs but persist in EM and exotic crosses. Reinforces price consistency across the FX matrix.",
        ["BIS"],
        indications=["FX"], category="Trading & Execution"),

    entry("CLS", "Continuous Linked Settlement",
        "FX settlement utility that eliminates Herstatt risk — both legs of a trade settle simultaneously.",
        "Founded 2002 in response to the 1974 Herstatt Bank collapse, where banks paid out one side of FX trades before failing on the other. CLS settles 18 currencies, processing roughly 2 trillion dollars daily through payment-versus-payment (PVP). Eliminates principal risk between settlement and receipt. Members include the biggest global banks; their customers settle indirectly via members. The plumbing nobody outside FX operations notices.",
        ["BIS", "DTCC"],
        indications=["FX"], category="Settlement & Operations"),

    entry("WM/Reuters Fix", "FX Fix",
        "Daily reference exchange rate calculated from a five-minute window around 4 PM London time.",
        "Used to value FX-denominated assets, set benchmark FX returns, and rebalance index funds. The 2013 manipulation scandal exposed banks colluding to push the fix rate to profit from client orders timed around the window — leading to billions in fines and methodology overhauls. The window is now five minutes (was one), with broader data sources to reduce manipulation risk. Indispensable for asset-management plumbing.",
        ["FCA", "BIS"],
        indications=["FX"], category="Indexes & Benchmarks"),
]


# ============================================================================
# BATCH 5 — FX options & EM (25 terms — vol products, EM currencies, crises)
# ============================================================================

BATCH_FX_OPTIONS_EM = [
    entry("FX Option", "",
        "Contract giving the right (not obligation) to exchange one currency for another at a future date.",
        "Quoted in volatility terms rather than price — dealers say 'EUR/USD 1-year vol at 7' rather than premium in dollars. Three main flavours: vanilla calls/puts, structured products (knock-in, knock-out), and exotics (digital, barrier). Used by corporates to hedge contingent exposures (the deal might not happen), by traders to express volatility views, and by central banks to manage reserves. Settled mostly OTC.",
        ["BIS", "ISDA"],
        indications=["FX", "Derivatives"], category="Instruments"),

    entry("Risk Reversal", "RR",
        "Difference in implied vol between out-of-money calls and puts — measures FX skew.",
        "A 25-delta risk reversal quotes vol of the 25-delta call minus vol of the 25-delta put. Positive RR means calls more expensive than puts — the market expects upside skew. EUR/USD RRs tend toward zero in calm markets; USD/JPY skew is famously persistent (puts more expensive — yen rallies in risk-off). Tracked by macro funds as a sentiment gauge.",
        ["BIS", "CME Group"],
        indications=["FX", "Derivatives"], category="Pricing & Valuation"),

    entry("ATM Straddle", "At-the-Money Straddle",
        "Long call + long put at the same at-the-money strike — pure volatility exposure.",
        "Standard quote for FX implied volatility: dealers price the ATM straddle and quote its vol, which becomes the headline vol number for that tenor. Delta-neutral at inception (call delta plus put delta sums to zero). Gains if the underlying moves a lot, loses if it stays still. Combined with risk reversals and butterflies, ATM straddles let dealers build the full FX volatility surface.",
        ["CME Group", "ISDA"],
        indications=["FX", "Derivatives"], category="Pricing & Valuation"),

    entry("25 Delta", "25D",
        "Strike convention — option struck so the call's delta is 0.25 (or put's is -0.25).",
        "FX vol surfaces are usually quoted at 25-delta call, 25-delta put, and ATM. The 10-delta points add wing detail for stress tests. 25-delta points sit roughly one standard deviation out-of-the-money — far enough to be meaningfully out-of-money, close enough to have decent liquidity. Most listed and OTC FX option flow concentrates around these points.",
        ["CME Group", "ISDA"],
        indications=["FX", "Derivatives"], category="Pricing & Valuation"),

    entry("Garman-Kohlhagen", "GK Model",
        "FX equivalent of Black-Scholes — accounts for two risk-free rates (one per currency).",
        "Extends Black-Scholes by replacing the single risk-free rate with the differential between the two currencies' rates. The forward rate (driven by interest-rate differential) plays the role of spot in equity option pricing. Published 1983. Used industry-wide for vanilla FX option pricing; more sophisticated models (Heston, SABR, local vol) handle the smile. The textbook reference for FX vanilla pricing.",
        ["CFA Institute", "ISDA"],
        indications=["FX", "Derivatives"], category="Quantitative"),

    entry("Vega", "",
        "Option's price sensitivity to a one-percent change in implied volatility.",
        "A 100-million notional option with vega of 50,000 dollars per vol point gains or loses 50,000 dollars when implied vol moves one percent. Highest for at-the-money options near expiry-equivalent vol levels. Vega-long books make money when vol rises (long vol); vega-short books profit from realised-vol below implied (the vol risk premium). Vol-trading desks manage vega the way rates desks manage DV01.",
        ["CFA Institute", "ISDA"],
        indications=["Derivatives"], category="Risk"),

    entry("EM", "Emerging Markets",
        "Mid-income, mid-development economies — distinct from advanced (DM) and frontier markets.",
        "MSCI's EM index defines the universe for most allocators: China, India, Brazil, Mexico, South Africa, Saudi Arabia, Korea, Taiwan, and others. Approximately 24 countries, 1,400 stocks. EM equity, bond, and currency markets carry higher beta to global risk sentiment than DM. The 'EM' label is increasingly contested for large economies like China and Korea, but MSCI's classification drives indexed flows so it sticks.",
        ["MSCI", "IMF"],
        indications=["FX", "Equities", "Macro"], category="Market Structure"),

    entry("Frontier Markets", "FM",
        "Markets less developed than EM — smaller, less liquid, often with capital controls.",
        "MSCI Frontier Markets index includes Nigeria, Kenya, Vietnam, Romania, Kazakhstan, Bahrain, and others — roughly 28 countries. Lower correlation with global markets, higher idiosyncratic risk, often dramatic returns (positive or negative). Liquidity constraints make institutional investing difficult. Some countries graduate to EM (UAE, Qatar 2014; Kuwait 2020); some get demoted (Argentina, Pakistan have bounced).",
        ["MSCI", "IMF"],
        indications=["FX", "Equities", "Macro"], category="Market Structure"),

    entry("Hard Currency", "",
        "Major reserve currency — USD, EUR, JPY, GBP, CHF — widely accepted for international payments.",
        "Distinguished from soft/local currencies in EM and frontier markets. Hard-currency sovereign debt (a Mexico USD bond, for example) carries different risk than local-currency debt (a Mexico MXN bond): hard-currency exposes the issuer to FX risk if revenues are local; local-currency exposes the investor to FX depreciation. Hard-currency EM debt is roughly 50 percent of the JPMorgan EMBI index.",
        ["IMF", "BIS"],
        indications=["FX"], category="Instruments"),

    entry("Local Currency", "Local Currency Debt",
        "Sovereign debt issued in the issuer's own currency — investor takes FX risk.",
        "Brazil's BRL bonds, Mexico's MXN bonds, Indonesia's IDR bonds. The issuer faces no currency mismatch (revenues match debt). The international investor bears FX depreciation risk and gets paid higher yields for it. The JPMorgan GBI-EM index tracks local-currency EM sovereign debt. Increasingly the larger share of EM sovereign issuance as governments build local capital markets.",
        ["IMF"],
        indications=["FX"], category="Instruments"),

    entry("Capital Controls", "",
        "Government restrictions on cross-border money flows — for stability or political reasons.",
        "Common in EM during crises: Malaysia 1998 (Asian crisis), Iceland 2008 (banking crisis), Greece 2015 (deposit flight), Russia 2022 (sanctions response). Forms include deposit reserve requirements, currency mismatches, outright bans on FX purchases, foreign-investment ceilings. The IMF historically opposed controls; the 2010s shifted to acknowledging temporary, targeted controls as macro tools. Tobin tax proposals are an academic relative.",
        ["IMF", "BIS"],
        indications=["FX", "Macro"], category="Regulation"),

    entry("CNH", "Offshore Renminbi",
        "Yuan traded outside mainland China — distinct exchange rate from onshore CNY.",
        "Hong Kong is the dominant CNH centre; London, Singapore, and Taipei also active. CNY trades within a daily band set by the PBoC's fixing; CNH floats more freely. The CNY-CNH spread widens during stress (capital flight pressure) and tightens in calm. CNH market includes spot, forwards, NDFs, options, and bonds (dim sum bonds). Critical plumbing for non-Chinese investors seeking yuan exposure.",
        ["BIS"],
        indications=["FX"], category="Indexes & Benchmarks"),

    entry("Currency Crisis", "",
        "Rapid currency depreciation driven by capital flight, sometimes triggering wider economic collapse.",
        "Pattern: capital flows reverse, FX reserves drain defending the currency, depreciation accelerates, dollar-denominated debt costs explode, inflation spikes, recession follows. 1992 ERM crisis (GBP, ITL forced out), 1994 Mexican peso, 1997-98 Asian crisis (THB, IDR, KRW), 1998 Russia, 2001 Argentina, 2018 Turkey. Pegged regimes are particularly vulnerable. IMF rescue packages typically follow.",
        ["IMF", "BIS"],
        indications=["FX", "Macro"], category="Risk"),

    entry("Sudden Stop", "",
        "Abrupt reversal of capital inflows to an emerging economy — typically triggers currency crisis.",
        "Coined by economist Guillermo Calvo. Mechanism: foreign investors lose confidence (whether for local reasons or global risk-off), pull capital out simultaneously, currency plunges, financing dries up for the country's banks and corporates. The 2013 Fed Taper Tantrum was a partial sudden stop for the 'Fragile Five' (Brazil, India, Indonesia, South Africa, Turkey). Reserves cushion the blow; debt structure determines damage.",
        ["IMF", "BIS"],
        indications=["FX", "Macro"], category="Risk"),

    entry("FX Intervention", "",
        "Central bank buying or selling its own currency in markets to influence the exchange rate.",
        "Tactics: spot transactions (most common), forward sales (off-balance-sheet), verbal intervention ('jawboning'). Effective when reserves are deep, intentions are credible, and intervention aligns with policy fundamentals. The Bank of Japan intervened twice in 2022 selling USD to support JPY (its first intervention in 24 years); the Swiss National Bank ran years of intervention to weaken the franc. G7 nations rarely intervene; EM does so routinely.",
        ["BIS", "IMF"],
        indications=["FX", "Macro"], category="Regulation"),

    entry("FX Reserves", "Foreign Exchange Reserves",
        "Foreign-currency assets held by central banks — backstop for intervention, debt service, imports.",
        "Mostly USD-denominated Treasuries (still around 58 percent of allocated reserves), with EUR, JPY, GBP, CNY making up most of the rest. China holds the largest reserve stockpile (3.2 trillion in 2024), Japan second, Switzerland fifth. Used for FX intervention, sovereign debt service, and import financing. Sanctions on Russian reserves in 2022 raised concerns about reserve-currency status and triggered some de-dollarisation flows.",
        ["IMF", "BIS"],
        indications=["FX", "Macro"], category="Instruments"),

    entry("Currency Board", "",
        "Strictest form of peg — domestic money supply fully backed by foreign reserves.",
        "Hong Kong's USD-pegged HKD has been a currency board since 1983: every HKD in circulation is backed by HKD7.75 of US dollar reserves. Argentina ran one 1991-2001 (pegged to USD) — collapsed in the 2001 crisis. Estonia, Lithuania ran them en route to euro. Eliminates central-bank discretion entirely; trades sovereignty for monetary stability.",
        ["IMF"],
        indications=["FX", "Macro"], category="Regulation"),

    entry("Dollarisation", "",
        "Economy adopts a foreign currency (usually USD) for domestic transactions.",
        "Ecuador (since 2000), El Salvador (2001), Panama, Zimbabwe (2009-2019). Full dollarisation eliminates monetary sovereignty: no central bank policy rate, no exchange rate. 'Partial dollarisation' is common in high-inflation economies — domestic deposits and contracts denominated in USD alongside the local currency. Reverses only with major political will (Zimbabwe relaunched ZWL in 2019).",
        ["IMF"],
        indications=["FX", "Macro"], category="Market Structure"),

    entry("Plaza Accord", "",
        "1985 G5 agreement to weaken the US dollar through coordinated FX intervention.",
        "Signed September 22 1985 at the Plaza Hotel in New York. The dollar had appreciated 50 percent against the yen and Deutsche mark over 1980-85, hurting US manufacturers. The five (US, Japan, West Germany, UK, France) agreed to sell dollars; USD fell roughly 50 percent against JPY over the next two years. Sometimes blamed for triggering Japan's late-1980s asset bubble.",
        ["IMF", "Federal Reserve"],
        indications=["FX", "Macro"], category="Regulation"),

    entry("Louvre Accord", "",
        "1987 follow-up to the Plaza Accord — G7 agreed the dollar's decline had gone far enough.",
        "Signed February 1987 at the Louvre in Paris. Aimed to stabilise the dollar around levels reached after Plaza. Mostly unsuccessful: intervention couldn't fully counter capital flows, and the October 1987 stock crash followed (some commentators link the two via the Accord's restrictive interest-rate dynamics). Marked the high-water mark of post-Bretton Woods coordinated G7 FX management.",
        ["Federal Reserve", "BIS"],
        indications=["FX", "Macro"], category="Regulation"),

    entry("Asian Financial Crisis", "1997 Asian Crisis",
        "Currency and banking crisis that started in Thailand and swept East Asia in 1997-98.",
        "Triggered when Thailand abandoned its USD peg in July 1997 (THB had been overvalued; capital flight forced the float). Contagion hit Indonesia, Korea, Malaysia, Philippines. Local-currency depreciation crushed dollar-denominated debt holders; banking systems collapsed; IMF bailouts followed with painful conditions. Lasting effects: massive reserve accumulation across Asia, ASEAN+3 cooperation, the rise of EM local-currency bond markets.",
        ["IMF", "BIS"],
        indications=["FX", "Macro"], category="Risk"),

    entry("Tequila Crisis", "Mexican Peso Crisis (1994)",
        "Mexican peso devaluation in December 1994 that triggered EM-wide capital flight.",
        "Mexico had been running a current account deficit funded by short-term USD-denominated debt (tesobonos). When the political environment soured and capital flowed out, reserves drained. The government devalued, then floated. Peso fell 50 percent in days. Argentina, Brazil hit by contagion. US-led 50-billion-dollar rescue package (Clinton, Rubin, Greenspan). Lasting effect: established the modern IMF crisis-response playbook.",
        ["IMF"],
        indications=["FX", "Macro"], category="Risk"),

    entry("Taper Tantrum", "",
        "May 2013 EM rout triggered by Bernanke's hint that the Fed would taper QE.",
        "Fed Chair Ben Bernanke testified May 22 2013 that the Fed might begin reducing asset purchases. EM currencies, bonds, and equities sold off sharply over the following months. The 'Fragile Five' (Brazil, India, Indonesia, South Africa, Turkey) saw the worst depreciation due to current-account vulnerabilities. The episode became a cautionary tale for Fed communication and shaped how central banks now signal policy changes.",
        ["Federal Reserve", "IMF"],
        indications=["FX", "Macro", "Rates"], category="Risk"),

    entry("SDR", "Special Drawing Rights",
        "IMF-created reserve asset — basket of USD, EUR, CNY, JPY, GBP.",
        "Allocated to IMF members in proportion to quotas; can be exchanged for hard currency among central banks. SDR weights (effective Aug 2022): USD 43.4, EUR 29.3, CNY 12.3, JPY 7.6, GBP 7.4. The SDR rate is calculated daily from a basket of short-term yields. Limited use outside official sector — periodic proposals to expand SDR for development finance haven't gained traction.",
        ["IMF"],
        indications=["FX", "Macro"], category="Indexes & Benchmarks"),

    entry("Trade Balance", "",
        "Difference between a country's exports and imports of goods and services.",
        "Trade surpluses (Germany, China, Japan historically) build FX reserves and tend to support the local currency; deficits (US, UK) require capital inflows to fund. The US has run persistent trade deficits since the 1970s, balanced by capital inflows into Treasuries and equities. Bilateral trade balances (US-China, etc.) are politically charged but economically less meaningful than overall balances.",
        ["IMF", "World Bank"],
        indications=["FX", "Macro"], category="Pricing & Valuation"),
]


# ============================================================================
# BATCH 6 — Equities single-name (25 terms — share types, valuation multiples, returns)
# ============================================================================

BATCH_EQUITIES_CASH = [
    entry("Equity", "",
        "Ownership stake in a company — residual claim after debts are paid.",
        "Equity-holders get whatever's left after creditors are made whole — the residual claim. In exchange they get voting rights (usually) and unlimited upside if the business grows. Public equity trades on stock exchanges as shares; private equity is owned by founders, employees, and investment firms. Global public equity market cap is roughly 110 trillion dollars (2024).",
        ["SEC", "CFA Institute"],
        indications=["Equities"], category="Instruments"),

    entry("Stock", "Share",
        "Unit of ownership in a corporation — a tradable slice of equity.",
        "Stocks (or 'shares') are issued by corporations to raise capital. Holders are shareholders, entitled to a share of profits (via dividends), votes on corporate matters, and residual value on liquidation. Common stock is the default flavour; preferred stock has bond-like priority. Stocks trade on exchanges (NYSE, Nasdaq, LSE) or OTC, with prices set continuously by buy and sell orders.",
        ["SEC", "NYSE", "Nasdaq"],
        indications=["Equities"], category="Instruments"),

    entry("Common Stock", "",
        "Standard equity — full voting rights, dividend eligibility, residual claim.",
        "What most people mean when they say 'stock'. One vote per share, dividends paid only after preferred holders get theirs, last in line for residual value on liquidation. Trades on exchanges. Companies typically issue one class of common stock, though many tech companies (Google, Meta, Snap) issue two or three classes with different voting rights — see dual-class share structures.",
        ["SEC"],
        indications=["Equities"], category="Instruments"),

    entry("Preferred Stock", "Preferreds",
        "Equity with bond-like features — fixed dividend, priority over common, usually non-voting.",
        "Sits between debt and common equity in the capital structure. Pays a fixed dividend (sometimes cumulative, meaning missed payments accumulate). Senior to common stock for dividends and liquidation; junior to all debt. Common in bank capital stacks (Tier 1 capital). Convertible preferreds can convert to common stock on certain triggers. Liquidity is thinner than common; most retail investors only encounter them via preferred ETFs.",
        ["SEC", "Federal Reserve"],
        indications=["Equities", "Credit"], category="Instruments"),

    entry("ADR", "American Depositary Receipt",
        "Foreign company's shares packaged for US trading — held by a US bank in custody.",
        "Lets US investors trade non-US stocks without dealing with foreign exchanges or currencies. JPMorgan, BNY Mellon, Citi, and Deutsche Bank are the major depositary banks. Three sponsorship levels: Level 1 (OTC, light disclosure), Level 2 (US exchange listing, SEC reporting), Level 3 (capital-raising via new shares). Many large foreign companies (Alibaba, Toyota, Novartis, Unilever) trade in the US via ADRs.",
        ["SEC", "NYSE"],
        indications=["Equities"], category="Instruments"),

    entry("GDR", "Global Depositary Receipt",
        "Equivalent of ADR but listed outside the US — typically London or Luxembourg.",
        "Same mechanics as ADR: a depositary bank holds the underlying foreign shares and issues receipts that trade in another jurisdiction. London Stock Exchange's International Order Book is the main GDR venue. Many Russian and Indian companies (back when they could) raised capital via London GDRs. Compliance and tax considerations drive the GDR/ADR choice for issuers.",
        ["LSEG", "SEC"],
        indications=["Equities"], category="Instruments"),

    entry("Free Float", "Float",
        "Number of shares actually available for public trading — excludes insider and strategic holdings.",
        "Shares held by founders, governments, strategic partners, employee plans subject to lock-up, and treasury stock get excluded. Index providers (S&P, MSCI, FTSE Russell) weight index constituents by free-float market cap, not total market cap. A company with 100 million shares outstanding but only 30 million publicly tradable has a 30 percent free float. Low-float stocks (Snap, many crypto-related listings) are prone to extreme price moves.",
        ["MSCI", "FTSE Russell"],
        indications=["Equities"], category="Market Structure"),

    entry("Authorised Shares", "",
        "Maximum number of shares a company is allowed to issue under its charter.",
        "Set in the corporate charter; can be increased with a shareholder vote. Distinct from outstanding shares (already issued) and float (publicly tradable). Boards typically keep authorised well above outstanding to allow flexibility for future issuance — stock-based compensation, acquisitions, secondary offerings. Disclosed on the balance sheet and in 10-K filings.",
        ["SEC"],
        indications=["Equities"], category="Corporate Actions"),

    entry("Outstanding Shares", "Shares Outstanding",
        "Total number of shares the company has issued and that are currently held by investors.",
        "Includes shares held by insiders, institutional investors, retail, and employee plans. Excludes treasury stock (shares the company has bought back and not retired). 'Diluted shares outstanding' adds shares from in-the-money options, warrants, and convertibles. Market cap equals share price times shares outstanding. Companies disclose monthly via 10-Q and 10-K filings.",
        ["SEC"],
        indications=["Equities"], category="Corporate Actions"),

    entry("Dual-Class Shares", "",
        "Share structure with multiple voting classes — typically founders retain control via supervoting shares.",
        "Google's GOOG (Class C, no votes) versus GOOGL (Class A, 1 vote) versus founder-held Class B (10 votes each). Meta, Snap, Pinterest, and many tech IPOs use similar structures. Critics argue it entrenches founders and weakens governance; supporters say it lets founders make long-term decisions free from quarterly pressure. S&P 500 has accepted dual-class since 2017; FTSE rules tightened then relaxed.",
        ["SEC", "NYSE"],
        indications=["Equities"], category="Corporate Actions"),

    entry("Dividend", "",
        "Cash payment from a corporation to its shareholders — slice of profits returned.",
        "Paid out of retained earnings, typically quarterly in the US (annually in some other markets). Decided by the board; can be cut or eliminated. Companies signal stability via dividend continuity — the 'Dividend Aristocrats' have raised payouts for 25+ consecutive years. Special dividends are one-off larger payouts. Stock dividends pay shares instead of cash. Most US dividends are taxed at preferential long-term capital-gains rates.",
        ["SEC", "Federal Reserve FRED"],
        indications=["Equities"], category="Corporate Actions"),

    entry("Dividend Yield", "",
        "Annual dividend as a percentage of share price — equity income measure.",
        "A 50-dollar stock paying a 2-dollar annual dividend has a 4 percent yield. Compared to bond yields as part of equity-versus-fixed-income allocation. Utility stocks and REITs typically have the highest yields (3-6 percent); growth stocks often pay nothing. Yields rise either by dividend increases or by share-price drops — a soaring yield can be a warning sign of falling price rather than improving payouts.",
        ["SEC", "CFA Institute"],
        indications=["Equities"], category="Pricing & Valuation"),

    entry("Payout Ratio", "",
        "Dividends as a percentage of earnings — how much profit is returned to shareholders.",
        "A 50 percent payout ratio means half of earnings go to dividends. Mature companies (utilities, consumer staples) run 50-70 percent; growth companies 0-20 percent. Above 100 percent is unsustainable — dividends are exceeding earnings. The flip side is reinvestment: low payout ratios mean retained earnings to fund growth. Tracked alongside buyback yield for total shareholder return analysis.",
        ["CFA Institute"],
        indications=["Equities"], category="Corporate Actions"),

    entry("EPS", "Earnings Per Share",
        "Net income divided by shares outstanding — corporate profitability per share.",
        "Most-watched single number on earnings releases. Companies report basic EPS (using outstanding shares) and diluted EPS (including potential shares from options and convertibles). Adjusted EPS excludes one-offs like restructuring charges; GAAP EPS includes everything. Stock prices move sharply when reported EPS beats or misses consensus estimates. Buybacks mechanically increase EPS by shrinking the denominator.",
        ["SEC", "CFA Institute"],
        indications=["Equities"], category="Pricing & Valuation"),

    entry("P/E Ratio", "Price-to-Earnings",
        "Share price divided by earnings per share — most common valuation multiple.",
        "A stock at 50 dollars with 5 dollars EPS trades at a 10 P/E — investors pay 10 dollars for every dollar of current earnings. Trailing P/E uses the past four quarters; forward P/E uses analyst forecasts. The S&P 500 has averaged a forward P/E around 17 over the past 30 years; tech stocks command higher multiples. High P/E suggests either expected growth or overvaluation; context required.",
        ["CFA Institute", "Federal Reserve FRED"],
        indications=["Equities"], category="Pricing & Valuation"),

    entry("PEG Ratio", "Price/Earnings-to-Growth",
        "P/E divided by earnings growth rate — adjusts valuation for growth.",
        "A stock with 30 P/E and 30 percent earnings growth has PEG of 1.0; a 30 P/E with 10 percent growth has PEG of 3.0. PEG below 1.0 suggested undervalued (Peter Lynch's heuristic). Highly sensitive to growth assumptions — small forecast errors swing PEG materially. Useful for comparing companies at different growth stages within a sector; less useful across vastly different business types.",
        ["CFA Institute"],
        indications=["Equities"], category="Pricing & Valuation"),

    entry("EV/EBITDA", "Enterprise Value to EBITDA",
        "Whole-company valuation multiple — captures both equity and debt.",
        "Enterprise value (market cap plus net debt) divided by EBITDA. Standard for comparing companies with different capital structures — a highly levered company's P/E understates its true cost; EV/EBITDA captures the debt. Common in private equity, M&A, and credit analysis. Industry-typical multiples: industrials 8-12x, tech 15-25x, utilities 8-10x. Used in LBO pricing and equity research valuation models.",
        ["CFA Institute"],
        indications=["Equities"], category="Pricing & Valuation"),

    entry("EBITDA", "Earnings Before Interest, Taxes, Depreciation, Amortisation",
        "Operating earnings before non-cash and financing charges — proxy for cash generation.",
        "Strips out capital-structure choices (interest), tax differences, and accounting policies (depreciation) to give a cleaner read on operating performance. Heavily used in M&A and leveraged finance (debt covenants are usually written against EBITDA). Critics call it 'earnings before bad stuff' — it can flatter unprofitable companies. Adjusted EBITDA further excludes 'one-offs', which can become permanent in some serial reporters' hands.",
        ["SEC", "CFA Institute"],
        indications=["Equities"], category="Pricing & Valuation"),

    entry("Free Cash Flow", "FCF",
        "Cash from operations minus capital expenditure — what's left for shareholders, debt holders, or growth.",
        "More conservative than EBITDA because it accounts for the actual capex needed to maintain the business. Sub-flavours: free cash flow to equity (after debt service), free cash flow to firm (before debt service). Discounted FCF (DCF) is the foundational valuation method. Companies report FCF in earnings releases; many investors prefer it to EPS because FCF is harder to manipulate via accounting choices.",
        ["SEC", "CFA Institute"],
        indications=["Equities"], category="Pricing & Valuation"),

    entry("Book Value", "Shareholders' Equity",
        "Accounting value of the company — assets minus liabilities on the balance sheet.",
        "Per-share book value equals total shareholders' equity divided by shares outstanding. P/B ratio (price-to-book) compares market value to book value. Banks and insurers trade close to book because their assets are largely financial; tech and brand-driven companies trade at multiples of book because their value sits in intangibles not on the balance sheet. Tangible book value excludes goodwill and intangibles.",
        ["SEC", "CFA Institute"],
        indications=["Equities"], category="Pricing & Valuation"),

    entry("ROE", "Return on Equity",
        "Net income divided by shareholders' equity — profitability per dollar of book value.",
        "DuPont decomposition breaks ROE into net margin times asset turnover times leverage — three drivers managers control differently. Sustained high ROE (over 15 percent) signals competitive advantage. Tech companies routinely exceed 25 percent; commodity businesses sit in single digits. Excessive leverage can inflate ROE without underlying improvement — why analysts compare ROE alongside ROIC and balance-sheet quality.",
        ["CFA Institute"],
        indications=["Equities"], category="Pricing & Valuation"),

    entry("ROIC", "Return on Invested Capital",
        "After-tax operating profit divided by capital employed — ROE without the leverage distortion.",
        "Strips out the financing decision: ROIC measures the business's return on its asset base regardless of how it's funded. Compared with weighted average cost of capital (WACC) — ROIC above WACC creates value, below destroys it. Favoured by long-horizon investors (Buffett, Munger) over ROE because it's harder to game with leverage. Best-in-class businesses sustain 20-percent-plus ROIC for decades.",
        ["CFA Institute"],
        indications=["Equities"], category="Pricing & Valuation"),

    entry("TSR", "Total Shareholder Return",
        "Combined return from share-price appreciation plus dividends reinvested.",
        "Standard measure of shareholder value creation over a period. Often used in executive compensation — TSR-linked performance shares pay out based on multi-year TSR versus peer group or index. Computed on a total-return basis: assume each dividend is reinvested at the ex-date price. The S&P 500 Total Return Index tracks TSR for the index. Distinguishes from price return (price-only, ignores dividends).",
        ["MSCI", "S&P Dow Jones Indices"],
        indications=["Equities"], category="Pricing & Valuation"),

    entry("Equity Risk Premium", "ERP",
        "Extra return investors demand for holding equities over risk-free bonds.",
        "Historically 4-6 percent over long horizons for US equities versus Treasuries. Drives equity valuation: discount rate equals risk-free rate plus ERP times beta (CAPM). Implied ERP can be back-solved from current market valuations; surveyed ERP comes from investor polls. The Fed Model compared equity earnings yield to bond yield as a relative-value gauge. ERP varies with risk appetite — collapses in bubbles, widens in crises.",
        ["CFA Institute", "Federal Reserve FRED"],
        indications=["Equities"], category="Pricing & Valuation"),

    entry("Buyback Yield", "Repurchase Yield",
        "Net stock buybacks as a percentage of market cap — shareholder return via share-count reduction.",
        "Companies returned roughly 950 billion to S&P 500 shareholders via buybacks in 2022 — more than dividends. Buybacks shrink share count, mechanically boosting EPS and dividend-per-share if total dividend pool is constant. The 'shareholder yield' (dividend yield plus buyback yield) is a broader payout measure than dividend yield alone. The 2022 US Inflation Reduction Act introduced a 1 percent excise tax on net buybacks.",
        ["SEC", "Federal Reserve FRED"],
        indications=["Equities"], category="Corporate Actions"),
]


# ============================================================================
# BATCH 7 — Equity derivatives (25 terms — options, swaps, futures, vol products)
# ============================================================================

BATCH_EQUITY_DERIVS = [
    entry("Equity Option", "Single-Stock Option",
        "Contract to buy or sell shares at a set price by a set date.",
        "Listed on options exchanges (CBOE, ISE, BOX in the US) in standard contracts of 100 shares. Vanilla flavours: American-style (exercisable any time) for single stocks, European-style (only at expiry) for most index options. Used to hedge, speculate, or generate income (covered calls). US-listed retail options volume hit record levels in 2021-22; institutional flow dominates index options.",
        ["SEC", "CME Group"],
        indications=["Equities", "Derivatives"], category="Instruments"),

    entry("Index Option", "",
        "Option on an equity index — cash-settled, European-style.",
        "SPX options (S&P 500) are the largest contract in the world by notional. Cash-settled because you can't deliver an index; the final settlement price comes from a special opening-rotation calculation. European-style (exercise only at expiry) avoids early-assignment risk. Used by institutional traders for portfolio hedging and macro positioning. Weekly, monthly, and quarterly expirations available; 0DTE (zero-days-to-expiry) options exploded in popularity post-2022.",
        ["CME Group", "CBOE" ],
        indications=["Equities", "Derivatives"], category="Instruments"),

    entry("Variance Swap", "Var Swap",
        "Pure exposure to realised variance — settles on the difference between realised and agreed variance.",
        "OTC product favoured by volatility traders. Notional set in 'vega' or 'variance units'. Linear in variance (not vol), making it different from straddles which require dynamic delta-hedging to extract vol. Crashed dramatically in March 2020 when realised vol spiked far above the strike — dealers who were short var swaps took huge losses. Now mostly cleared via dealer-to-dealer arrangements.",
        ["ISDA", "CME Group"],
        indications=["Equities", "Derivatives"], category="Instruments"),

    entry("Volatility Swap", "Vol Swap",
        "Like a variance swap but settles on realised volatility (square root of variance) — linear in vol.",
        "Less common than variance swaps because the math is harder for dealers to replicate — vol swaps require dynamic hedging in variance space and convexity adjustments. Used when traders want straight directional vol exposure without the convexity of var swaps. Quoted OTC; small market versus var swaps but a real product, especially in single-name equity vol.",
        ["ISDA"],
        indications=["Equities", "Derivatives"], category="Instruments"),

    entry("Equity Index Future", "Index Future",
        "Futures contract on an equity index — most liquid equity derivative.",
        "CME's E-mini S&P 500 futures (/ES) are the most-traded equity contract in the world — over a trillion dollars notional daily during active sessions. NDX, Russell 2000, Dow, MSCI futures also active. Used for index hedging, portfolio rebalancing, futures-vs-cash arbitrage, and synthetic equity exposure. Quarterly expirations (March, June, September, December). Settle to a special opening rotation price.",
        ["CME Group", "ICE"],
        indications=["Equities", "Derivatives"], category="Instruments"),

    entry("Single Stock Future", "SSF",
        "Futures contract on an individual stock — small market in the US, larger in Europe and Asia.",
        "Eurex and the Indian exchanges trade actively. The US OneChicago exchange shut in 2020 — single-stock futures never gained traction here, partly due to regulatory complexity (jointly overseen by SEC and CFTC). Offer leveraged single-name exposure without margin loans. CFDs and synthetic prime brokerage substitute in markets where SSFs are illiquid.",
        ["Eurex", "SEC"],
        indications=["Equities", "Derivatives"], category="Instruments"),

    entry("CFD", "Contract for Difference",
        "OTC contract that pays the price difference of an underlying without owning it.",
        "Popular in Europe and Asia for retail traders to get leveraged stock or FX exposure. Banned for US retail by the SEC. Cash-settled, no physical delivery. Traded against the broker as counterparty rather than on an exchange. The 2021 GameStop episode highlighted CFD risks — brokers like IG and Plus500 saw extreme retail losses. Spread plus financing cost is the broker's revenue.",
        ["FCA", "ESMA"],
        indications=["Equities"], category="Instruments"),

    entry("Equity Swap", "",
        "Total return on an equity for periodic cash payments — usually LIBOR-replacement-plus-spread.",
        "Used by hedge funds for leveraged equity exposure (prime brokerage), by corporates for share buybacks structured as accelerated programs, by funds for tax or regulatory arbitrage. The 2021 Archegos collapse was effectively a margin call on equity total-return swaps gone catastrophically wrong — Credit Suisse and others lost over 10 billion combined. ISDA-documented OTC contracts.",
        ["ISDA"],
        indications=["Equities", "Derivatives"], category="Instruments"),

    entry("Total Return Swap", "TRS",
        "One leg pays total return on an asset; the other pays a financing rate.",
        "Equity TRS is the most common flavour: hedge fund receives total return on a stock, pays SOFR plus spread to the bank. Lets the fund get equity exposure with bank-financing leverage and without owning shares. Used to circumvent shareholding disclosure requirements (Archegos), as a tax-efficient alternative to cash equity, and to lock in financing cost. Centrally cleared not common; mostly bilateral.",
        ["ISDA"],
        indications=["Equities", "Credit"], category="Instruments"),

    entry("Dispersion Trade", "",
        "Sell index volatility, buy single-stock volatility — profits if correlation falls.",
        "Decomposes index vol into single-stock vol times correlation. When correlation drops (stocks move idiosyncratically), realised index vol falls below the weighted average of single-stock vols, profiting the dispersion seller. Reverses when correlation spikes (typical of crashes). Hedge funds run systematic dispersion books. Sized in vega terms across the components.",
        ["ISDA", "CFA Institute"],
        indications=["Equities", "Derivatives"], category="Trading & Execution"),

    entry("Gamma", "",
        "Rate of change of delta — how an option's delta moves as the underlying moves.",
        "Long-gamma positions buy low and sell high mechanically — as the underlying rises, delta increases, requiring the hedger to sell more; as it falls, the reverse. Positive gamma benefits from realised volatility. Dealers paid short gamma (short options) lose money in volatile markets; long gamma profits. Gamma is highest for at-the-money options near expiry, which is why short-dated options have outsized hedging flows.",
        ["ISDA", "CFA Institute"],
        indications=["Derivatives"], category="Risk"),

    entry("Theta", "Time Decay",
        "Option's price decay per day — how much premium is lost to time passing.",
        "Negative for long options (option-buyers lose to theta), positive for short options. Accelerates as expiry approaches — particularly the last 30 days, and especially the last week. Short-premium strategies (iron condors, naked options) live or die on theta versus realised vol. Quoted as dollars per day for a position. Watched closely by retail options sellers who write covered calls for income.",
        ["CFA Institute"],
        indications=["Derivatives"], category="Risk"),

    entry("Rho", "",
        "Option's sensitivity to a one-percent change in interest rates.",
        "The least-watched Greek. Matters most for long-dated options where the discount rate has time to compound. Calls have positive rho (higher rates increase forward price, helping calls); puts have negative rho. Long-dated equity LEAPS see meaningful rho exposure; short-dated options have almost none. FX options and rate options have their own rho sensitivities to the two underlying rate environments.",
        ["CFA Institute"],
        indications=["Derivatives"], category="Risk"),

    entry("Volatility Smile", "",
        "Implied vol curve plotted against strike — typically lower in the middle, higher at wings.",
        "Reflects market pricing of fat-tail risk. The 1987 crash shifted equity vol smiles permanently — out-of-money puts price in crash risk that Black-Scholes doesn't capture. FX vol surfaces have symmetric smiles in major pairs, skewed smiles in EM. Rates options have smiles dependent on the strike convention. Local volatility, stochastic volatility, and SABR models attempt to fit smile shapes consistently.",
        ["ISDA", "CFA Institute"],
        indications=["Derivatives"], category="Pricing & Valuation"),

    entry("Skew", "Volatility Skew",
        "Asymmetry of the implied vol smile — equities skew left (puts pricier than calls).",
        "Single-stock equity skew widens around earnings (left-tail fear). Index skew widens in selloffs as protective put demand surges. Quoted as the vol differential between 25-delta puts and 25-delta calls, or as a slope of the smile. Skew tracking is core to vol arbitrage strategies. The post-1987 'permanent skew' in S&P options is a market-microstructure landmark.",
        ["CBOE", "ISDA"],
        indications=["Derivatives"], category="Pricing & Valuation"),

    entry("Term Structure of Volatility", "Vol Term Structure",
        "Implied vol across different option maturities — usually upward-sloping in calm markets.",
        "Short-dated vol typically prices lower than long-dated because the long maturity has more time for vol surprises. Inverts during stress — short vol spikes above long vol when crisis is acute. Tracked by VIX futures curve, which sometimes inverts ahead of recessions or events. Vol-arbitrage strategies trade calendar spreads (long one tenor, short another) to capture term-structure mispricings.",
        ["CBOE", "ISDA"],
        indications=["Derivatives"], category="Pricing & Valuation"),

    entry("Realised Volatility", "Historical Volatility",
        "Actual past volatility of the underlying — what 'really happened'.",
        "Computed from daily log returns, annualised by multiplying by the square root of 252 (trading days). Compare with implied vol to gauge the vol risk premium — the gap usually favours implied (sellers profit). Realised vol around earnings days, FOMC meetings, and macro shocks spikes far above its trend. High realised vol with stable implied vol means systematic options sellers are getting hurt.",
        ["CBOE", "CFA Institute"],
        indications=["Derivatives"], category="Quantitative"),

    entry("VVIX", "VIX of VIX",
        "Implied volatility of VIX futures — the vol of vol.",
        "Computed by CBOE from VIX options. Captures the market's expectation of how much VIX itself will move. VVIX spikes when traders rush into VIX call options for tail-risk hedging. Typically trades 80-120, well above VIX's typical 15-25 range, reflecting how much more violent VIX moves are than equity moves. Used in long-vol-of-vol strategies and as a sentiment gauge for crash hedging demand.",
        ["CBOE"],
        indications=["Derivatives"], category="Indexes & Benchmarks"),

    entry("Weekly Options", "Weeklies",
        "Options expiring weekly rather than monthly — most popular for major indexes and large stocks.",
        "SPX Weeklys (Monday, Tuesday, Wednesday, Thursday, Friday expirations) trade billions of dollars notional. Provide finer-grained expiry choice for short-dated hedging or speculation. Spurred the rise of 0-day-to-expiry (0DTE) trading. Listed by CBOE in the US, with similar products on other exchanges. Open interest concentrates around upcoming Friday expiries.",
        ["CBOE"],
        indications=["Equities", "Derivatives"], category="Instruments"),

    entry("Zero-DTE", "0DTE Options",
        "Options expiring the same day they're traded — exploded in popularity 2022-2024.",
        "Possible because of daily SPX expirations and CBOE listing rolling weeklies. Now roughly half of all SPX options volume. Used by traders for tactical exposure, theta-harvest strategies, and gamma plays. Critics argue 0DTE creates intraday market microstructure stress: dealer gamma hedging needs accelerate, contributing to V-shaped intraday moves. Regulatory scrutiny ongoing but no major restrictions yet.",
        ["CBOE", "SEC"],
        indications=["Equities", "Derivatives"], category="Trading & Execution"),

    entry("Pin Risk", "",
        "Risk near expiry that the underlying closes exactly at the strike — uncertain exercise.",
        "If a stock closes at exactly $50 on Friday and you're short a $50 call, you don't know if it'll be exercised — depends on each holder's discretion. Creates an unwanted long or short position Monday morning. Dealers manage pin risk by adjusting hedges close to expiry. The 'magnet effect' near round numbers ('pinning to strike') is real and tied to gamma hedging at the strike with highest open interest.",
        ["CBOE"],
        indications=["Equities", "Derivatives"], category="Risk"),

    entry("Synthetic Long", "",
        "Long call plus short put at the same strike — same payoff as owning the stock.",
        "Put-call parity in action: long call plus short put equals long stock minus PV of strike. Used to replicate equity exposure without borrowing, to manage tax timing, or to circumvent shareholding limits. The reverse — synthetic short — combines long put and short call. Conversion and reversal trades exploit small mispricings between cash and synthetic positions, mostly arbitraged away.",
        ["CFA Institute"],
        indications=["Equities", "Derivatives"], category="Trading & Execution"),

    entry("Stock Loan", "Securities Lending",
        "Temporary transfer of shares from a long-holder to a short-seller — a fee is paid.",
        "Custodian banks (State Street, BNY Mellon) and prime brokers run the lending. Long holders (pension funds, mutual funds, ETFs) lend their shares for extra income — typically 5-50 bps annualised, much higher for 'hard-to-borrow' names. The borrower (typically a short-seller or arbitrageur) returns the shares on demand. Stock-loan markets are opaque but essential plumbing for short-selling.",
        ["SEC", "FINRA"],
        indications=["Equities"], category="Market Structure"),

    entry("Short Squeeze", "",
        "Rapid price spike forces short-sellers to cover, accelerating the rally.",
        "Mechanism: high short interest plus a positive catalyst forces shorts to buy back shares to cover, pushing the price higher, forcing more covering. The 2008 Volkswagen squeeze (briefly the most valuable company in the world), the 2021 GameStop episode (driven by retail coordination on Reddit's WallStreetBets), and the AMC and Bed Bath & Beyond run-ups are the famous examples. Hedge funds short heavily-shorted names with caution.",
        ["SEC"],
        indications=["Equities"], category="Trading & Execution"),

    entry("Gamma Squeeze", "",
        "Dealer hedging of short call positions forces them to buy more stock as price rises — amplifies rally.",
        "Variation of short squeeze involving options. As a stock rallies into expiring call strikes, market-makers who sold those calls hedge by buying more stock to maintain delta neutrality, which pushes the price higher, requiring more buying. The 2021 GameStop episode combined classic short squeeze with gamma squeeze. Most pronounced near expiry when gamma is highest. Reverses violently if the underlying rolls over.",
        ["CBOE", "SEC"],
        indications=["Equities", "Derivatives"], category="Trading & Execution"),
]


# ============================================================================
# BATCH 8 — Credit bonds & spreads (25 terms — IG/HY, ratings, capital structure)
# ============================================================================

BATCH_CREDIT_BONDS = [
    entry("Credit Spread", "",
        "Extra yield a corporate bond pays over a comparable-maturity Treasury — compensation for default risk.",
        "Quoted in basis points. A 10-year corporate at 5.50 percent with the 10-year Treasury at 4.30 percent has a 120 bp spread. Tighter spreads reflect either credit improvement or risk appetite; wider spreads signal stress. The Bloomberg US Aggregate Corporate Index spread is the headline IG gauge; the high-yield equivalent OAS is its junk counterpart. Spreads gapped to crisis levels in 2008, 2020, and 2022.",
        ["Federal Reserve FRED", "ICE"],
        indications=["Credit"], category="Pricing & Valuation"),

    entry("Investment Grade", "IG",
        "Bonds rated BBB- or higher — institutional-portfolio eligible.",
        "Moody's: Aaa, Aa, A, Baa. S&P/Fitch: AAA, AA, A, BBB. The IG-HY boundary at BBB-/Baa3 is the most consequential threshold in credit — many institutional mandates and pension funds can hold only IG. Downgrades into HY (becoming 'fallen angels') trigger forced selling. IG corporates spread roughly 100-200 bps over Treasuries in calm markets; widens to 300-500 in crises.",
        ["SEC", "Federal Reserve FRED"],
        indications=["Credit"], category="Instruments"),

    entry("High Yield", "HY / Junk",
        "Bonds rated BB+ or below — higher default risk, higher coupon.",
        "Pejoratively 'junk' bonds. Yields several percentage points above IG. Mike Milken pioneered the modern HY market at Drexel in the 1980s. Issued by leveraged buyouts, fallen-angel companies, and natural HY issuers (telecoms, energy, retailers). HY spreads gap dramatically in stress — over 1,000 bps in 2008, briefly there in March 2020. HY ETFs (HYG, JNK) democratised retail HY exposure post-2007.",
        ["SEC", "ICE"],
        indications=["Credit"], category="Instruments"),

    entry("Fallen Angel", "",
        "IG bond downgraded to HY — forced selling by IG-only mandates often follows.",
        "Notable examples: Ford and GM in 2005 (took 25 percent of HY index overnight), Kraft Heinz in 2020, Boeing's near-downgrade scare in 2020-21 (avoided). The mechanical selling creates buying opportunities for HY funds — but the downgrade often precedes further fundamental deterioration. The 'rising stars' index tracks upgrades back to IG. Pandemic-era Fed bond-buying explicitly included fallen angels.",
        ["S&P Dow Jones Indices", "ICE"],
        indications=["Credit"], category="Pricing & Valuation"),

    entry("Rising Star", "",
        "HY bond upgraded to IG — gains pricing premium as IG buyers enter.",
        "Opposite of fallen angel. Companies typically work toward rising-star upgrades through deleveraging, business improvement, or M&A by IG acquirers. Bonds usually trade up before the formal upgrade as the market prices in the expectation. Spreads tighten on the upgrade announcement. Tracked in dedicated indexes by ICE and Bloomberg. Common in post-LBO refinancing stories.",
        ["S&P Dow Jones Indices"],
        indications=["Credit"], category="Pricing & Valuation"),

    entry("Credit Rating", "",
        "Letter grade assigned by a rating agency to a bond issuer or specific debt instrument.",
        "Three majors: S&P, Moody's, Fitch. Scales: AAA to D (S&P/Fitch), Aaa to C (Moody's). Issuer ratings differ from instrument ratings (subordinated debt is rated lower than senior). Ratings drive eligibility for index inclusion, regulatory capital, and pension mandates. The 2008 crisis exposed rating-agency conflicts of interest with structured products; Dodd-Frank tried to reduce regulatory reliance on ratings but the change has been gradual.",
        ["SEC", "ESMA"],
        indications=["Credit"], category="Pricing & Valuation"),

    entry("AAA", "Triple-A",
        "Highest credit rating — minimal default risk.",
        "Sovereign AAAs: US (S&P downgraded 2011), Germany, Netherlands, Switzerland, Singapore. Corporate AAAs are rare — Microsoft and Johnson & Johnson have held it; most companies sit at AA or A. AAA structured products were the cornerstone of pre-2008 securitisation — many turned out to be deeply mispriced. Carries the tightest credit spreads. Downgrades make headlines.",
        ["SEC", "ESMA"],
        indications=["Credit"], category="Pricing & Valuation"),

    entry("Senior Unsecured", "",
        "Standard corporate bond — claim ranks behind secured debt but ahead of subordinated.",
        "Default ladder: secured (collateralised) → senior unsecured → subordinated → preferred → common equity. Most investment-grade corporate issuance is senior unsecured. Recovery rates in default historically average 40 percent for senior unsecured (compared to 60-80 for secured, 10-30 for subordinated). The cushion of subordinated debt below it determines recovery prospects.",
        ["Federal Reserve", "SEC"],
        indications=["Credit"], category="Instruments"),

    entry("Subordinated Debt", "Sub Debt",
        "Bond ranking junior to senior debt — paid after seniors in default.",
        "Banks issue subordinated debt as part of regulatory capital structures (Tier 2 capital). Holders receive higher coupons in exchange for taking deeper-in-the-capital-stack risk. Recovery rates historically 10-30 percent. In bank resolution scenarios under the BRRD (Europe), sub debt is fair game for bail-in before senior debt — confirmed in the March 2023 Credit Suisse rescue where 17 billion of AT1 was wiped out.",
        ["Federal Reserve", "ECB"],
        indications=["Credit"], category="Instruments"),

    entry("Convertible Bond", "Convertible",
        "Bond that can convert into equity at a fixed ratio — debt with embedded call option.",
        "Issuer benefits from lower coupon (the conversion option is part of the compensation); investor benefits from upside participation. Issued primarily by mid-cap growth companies and stressed names. The convert market spiked during 2020-21 SPAC and growth-stock issuance. Pricing decomposes into bond floor plus conversion value plus implied option vol. Convertible arb funds run the dominant pricing edge.",
        ["SEC", "ISDA"],
        indications=["Credit", "Equities"], category="Instruments"),

    entry("AT1", "Additional Tier 1 / CoCo",
        "Bank capital instrument that converts to equity or gets written down if regulatory ratios breach.",
        "Created post-2008 under Basel III to provide loss-absorbing capital that doesn't dilute existing equity in normal times. Counts as Tier 1 capital. The March 2023 Credit Suisse rescue wiped out 17 billion of AT1 to zero while equity holders got partial payment — broke the conventional capital-stack hierarchy and sent shockwaves through the AT1 market. Yields demanded subsequently widened by hundreds of basis points.",
        ["ECB", "Federal Reserve", "FCA"],
        indications=["Credit"], category="Instruments"),

    entry("Contingent Convertible", "CoCo Bond",
        "Bank capital bond that converts to equity (or gets written down) on a regulatory trigger.",
        "Synonym for AT1 in European bank usage. Trigger usually a CET1 ratio falling below 5.125 percent (or 7 percent for higher-trigger CoCos). Mechanism: convert to common equity (dilutes existing shareholders, recapitalises bank) or principal write-down (creditors lose, equity holders preserved). Designed to absorb losses without taxpayer bailout. Performed as intended in some bank rescues, controversially in Credit Suisse.",
        ["ECB", "FCA"],
        indications=["Credit"], category="Instruments"),

    entry("Default", "",
        "Failure to make a contractual debt payment when due.",
        "Triggers acceleration clauses (full principal owed immediately) and cross-default provisions on the issuer's other debt. ISDA determines whether a credit event has occurred for CDS purposes. Three forms: missed payment, bankruptcy filing, distressed exchange (forced restructuring offered at discount). Sovereign defaults: Russia 1998, Argentina 2001, Greece 2012 (debt exchange), Sri Lanka 2022. Corporate default rates spike in recessions.",
        ["ISDA", "Federal Reserve"],
        indications=["Credit"], category="Risk"),

    entry("Recovery Rate", "",
        "Percentage of bond face value recovered by creditors after default.",
        "Senior secured: 60-80 percent average. Senior unsecured: 30-50. Subordinated: 10-30. Determined post-default through bankruptcy court (Chapter 11) or auction (for CDS settlement). Recovery rates fall during recessions when liquidation values shrink and many defaults happen simultaneously. Moody's, S&P, and the Loan Pricing Corporation publish recovery datasets. Crucial input to credit-spread analysis (CDS pricing assumes 40 percent default-recovery convention).",
        ["ISDA"],
        indications=["Credit"], category="Risk"),

    entry("LGD", "Loss Given Default",
        "Percentage of exposure lost when an obligor defaults — equals 100 percent minus recovery rate.",
        "Bank credit-risk models combine three numbers: probability of default (PD), exposure at default (EAD), and LGD. Expected loss equals PD times LGD times EAD. Basel regulatory capital uses these inputs. LGD varies by seniority, collateral, jurisdiction, and economic cycle — recession LGD runs higher than normal. Senior secured LGD typically 30-40 percent; unsecured 50-70 percent.",
        ["BIS", "Federal Reserve"],
        indications=["Credit"], category="Risk"),

    entry("Probability of Default", "PD",
        "Estimated likelihood that a borrower will default over a given horizon.",
        "Drawn from rating agency data, internal bank models, or market-implied (CDS-derived) probabilities. One-year PD for IG averages well under 1 percent; HY runs 3-5 percent in normal times, spiking in stress. Banks use through-the-cycle versus point-in-time PD distinctions for capital adequacy. Critical input to expected loss calculations and IFRS 9 forward-looking provisioning.",
        ["BIS"],
        indications=["Credit"], category="Risk"),

    entry("EAD", "Exposure at Default",
        "Expected outstanding exposure at the moment of default.",
        "For amortising loans, EAD is straightforward — it's the remaining balance. For revolving credit facilities, EAD models the expected drawdown at default time (typically higher than current outstandings as defaulting companies often draw down before bankruptcy). For derivatives, EAD accounts for potential future exposure. Used in Basel regulatory capital calculations with PD and LGD.",
        ["BIS", "Federal Reserve"],
        indications=["Credit"], category="Risk"),

    entry("Credit Migration", "",
        "Movement of an obligor's credit rating up or down — drives bond price changes outside of yield curve moves.",
        "Standard rating-agency transition matrices show one-year probabilities: an A-rated obligor has roughly a 1 percent chance of upgrade to AA, 2 percent of downgrade to BBB, 96 percent of staying A. Long-horizon transitions compound through migration matrices. Bank IFRS 9 provisioning explicitly uses migration to project expected losses. Migration risk is the credit equivalent of duration risk for fixed-income portfolios.",
        ["BIS"],
        indications=["Credit"], category="Risk"),

    entry("CDX", "CDS Index",
        "Basket of 125 North American CDS contracts — the most-traded credit derivatives benchmark.",
        "Two main sub-indexes: CDX IG (investment grade) and CDX HY (high yield). Roll every six months as composition refreshes. Replaced single-name CDS as the primary credit-risk-transfer venue post-2009 — daily volumes in the tens of billions. Used to hedge corporate bond portfolios, express macro credit views, and arbitrage against single-name CDS. Cleared at ICE Clear Credit.",
        ["ICE", "ISDA"],
        indications=["Credit"], category="Indexes & Benchmarks"),

    entry("iTraxx", "",
        "European/Asian equivalent of CDX — Markit-administered CDS index family.",
        "iTraxx Europe (125 European IG names), iTraxx Crossover (75 European HY names), iTraxx Asia ex-Japan, iTraxx SovX (sovereign CDS). Composition rolls semiannually. Most-traded European credit benchmarks. iTraxx Crossover spreads are the European equivalent of CDX HY — gap dramatically in stress. Operated by Markit under LSEG since the 2014 IHS Markit (then LSEG) acquisition.",
        ["LSEG", "ICE"],
        indications=["Credit"], category="Indexes & Benchmarks"),

    entry("Credit Curve", "",
        "Term structure of an issuer's credit spread across maturities — like a yield curve but for credit.",
        "Normally upward-sloping: longer-dated bonds carry larger credit spreads to compensate for default-probability accumulation over time. Inverted credit curves (short spreads above long) signal acute distress — Lehman's curve inverted before bankruptcy. Single-name CDS quotes by tenor (1y, 3y, 5y, 7y, 10y) build the curve. The 5y CDS is the benchmark liquidity point.",
        ["ISDA", "ICE"],
        indications=["Credit"], category="Pricing & Valuation"),

    entry("Z-Spread", "Zero-Volatility Spread",
        "Constant spread added to the Treasury zero curve that prices a bond at market.",
        "More precise than nominal yield spread (which compares to a single Treasury point) — Z-spread accounts for the timing of every cash flow. The 'zero-volatility' qualifier means no embedded option value assumed. For non-callable bonds, Z-spread equals OAS. For callable bonds, OAS subtracts the option value from Z-spread. Standard quote in IG bond markets.",
        ["CFA Institute", "ICE"],
        indications=["Credit"], category="Pricing & Valuation"),

    entry("OAS", "Option-Adjusted Spread",
        "Z-spread minus the embedded option value — true credit spread for callable bonds.",
        "Critical for MBS and callable corporates where prepayment or call options shift cash flows. Calculated via Monte Carlo simulation over interest-rate paths. MBS OAS is the standard credit measure for mortgage portfolios — wide OAS in 2007-08 and again 2022 signalled MBS stress. Lower OAS means richer pricing relative to underlying optionality.",
        ["Federal Reserve", "ICE"],
        indications=["Credit"], category="Pricing & Valuation"),

    entry("Asset Swap Spread", "ASW",
        "Spread over the swap curve that prices a bond at par when its coupon is converted to floating.",
        "Mechanics: investor buys the bond and enters a fixed-to-floating swap, converting the bond's fixed coupon into SOFR-plus-spread. ASW measures the spread on the floating leg that makes the package zero-cost at inception. Used by bank treasuries to compare across instruments on a uniform floating-rate basis. Differs from Z-spread by the convexity correction and bond price effects.",
        ["ISDA", "ICMA"],
        indications=["Credit"], category="Pricing & Valuation"),

    entry("Spread Duration", "",
        "Bond price sensitivity to a one-basis-point change in credit spread.",
        "Credit equivalent of interest-rate duration. A bond with 7-year spread duration loses 0.07 percent per bp of spread widening. Long-duration HY bonds get hammered when spreads widen in stress. Portfolio managers manage spread duration separately from rate duration — IG bond funds tend to be high spread duration and high rate duration; HY funds high spread duration, lower rate duration.",
        ["CFA Institute"],
        indications=["Credit"], category="Risk"),
]


# ============================================================================
# BATCH 9 — Credit derivatives & structured (25 terms — CDS, CLOs, MBS, ABS)
# ============================================================================

BATCH_CREDIT_DERIVS = [
    entry("CDS", "Credit Default Swap",
        "Insurance contract on a bond's default — buyer pays premium, seller pays out on credit event.",
        "Buyer pays the seller a quarterly premium (the spread) over the contract's term; if the reference name suffers a credit event, the seller pays out the face value minus recovery. Standardised 2009 reforms moved most CDS to central clearing at LCH and ICE. The single-name CDS market shrank dramatically post-Dodd-Frank as flows moved to index CDS (CDX, iTraxx). ISDA defines credit events and runs auctions.",
        ["ISDA", "LCH", "ICE"],
        indications=["Credit"], category="Instruments"),

    entry("CDS Auction", "",
        "ISDA-administered auction that determines the recovery rate after a CDS credit event.",
        "Triggered when a Credit Determinations Committee rules a credit event occurred. Two-stage auction: initial bidding sets a midpoint price, then a final 'open interest' phase where dealers transact bonds at the determined recovery. Roughly 100 auctions have been held since 2005. Famous cases: Lehman (8.625 cents on the dollar), Greek 2012 restructuring (21.5 cents), Sears 2018 (16 cents).",
        ["ISDA"],
        indications=["Credit"], category="Settlement & Operations"),

    entry("Credit Event", "",
        "ISDA-defined trigger for CDS payout — bankruptcy, failure to pay, or restructuring.",
        "Bankruptcy: court filing or analogous proceeding. Failure to Pay: missed payment over a grace period. Restructuring: terms changed to creditors' disadvantage (debt exchange, maturity extension, coupon reduction, principal write-down). Restructuring as a credit event is less common in US contracts post-2009; standard in Europe. Determination by ISDA's Credit Determinations Committee, made of major dealer and buy-side firms.",
        ["ISDA"],
        indications=["Credit"], category="Risk"),

    entry("CLO", "Collateralised Loan Obligation",
        "Securitisation of leveraged loans — bonds backed by a pool of bank loans, tranched by seniority.",
        "Market grew to roughly 1.2 trillion in 2024. Pool of 100-300 senior secured loans from LBOs and corporate borrowers. Tranches from AAA down to equity, paying different yields. CLOs are the largest buyer of leveraged loans globally — bank loan markets effectively depend on CLO demand. Tested in 2008 (held up better than CDOs), again in March 2020 (volatile but resilient). Managers actively rotate the pool.",
        ["SEC", "ICE"],
        indications=["Credit"], category="Instruments"),

    entry("CDO", "Collateralised Debt Obligation",
        "Securitisation of bonds (corporate, MBS, ABS) — infamous for its role in the 2008 crisis.",
        "Pool of debt securities tranched by seniority — investors got the spread differential and ratings benefits. Synthetic CDOs used CDS to gain exposure without owning bonds. The 2008 crisis exposed massive mispricing in mortgage-backed CDOs and CDOs-squared (CDOs of CDOs). Post-crisis the CDO market shrank dramatically; CLOs (CDOs of leveraged loans) survived and grew, but mortgage CDOs largely disappeared.",
        ["SEC"],
        indications=["Credit"], category="Instruments"),

    entry("MBS", "Mortgage-Backed Security",
        "Bond backed by a pool of residential or commercial mortgages.",
        "Holders receive monthly principal and interest from the underlying mortgages. Three sources of cash flow uncertainty: prepayments (homeowners refinancing or moving), defaults, and curtailments. The US MBS market is roughly 12 trillion outstanding — second only to Treasuries in size. Agency MBS (guaranteed by Fannie Mae, Freddie Mac, Ginnie Mae) is most of it; private-label MBS shrank dramatically post-2008.",
        ["Federal Reserve", "SEC"],
        indications=["Credit"], category="Instruments"),

    entry("Agency MBS", "",
        "MBS guaranteed against credit loss by a government-sponsored enterprise (GSE).",
        "Issued by Fannie Mae, Freddie Mac, and Ginnie Mae. The GSE guarantees principal and interest, removing credit risk for the investor — but leaving prepayment and rate risk. Treated as 'Treasury-like' for regulatory capital and pension mandates. The Fed bought trillions of agency MBS during QE programs; runoff post-2022 has put pressure on mortgage spreads. Roughly 9 trillion outstanding.",
        ["Federal Reserve"],
        indications=["Credit"], category="Instruments"),

    entry("Non-Agency MBS", "Private-Label MBS",
        "MBS without a government guarantee — credit risk priced separately.",
        "Underlying loans typically don't meet conforming-loan criteria (jumbo mortgages, alt-A, subprime). Investors take both rate/prepayment and credit risk. The 2008 crisis was largely a private-label MBS event — issuance went from 1.2 trillion in 2006 to near-zero in 2008. Slowly recovering since but a fraction of pre-crisis size. Modern non-agency deals include detailed loan-level disclosure.",
        ["SEC"],
        indications=["Credit"], category="Instruments"),

    entry("CMBS", "Commercial Mortgage-Backed Security",
        "MBS backed by commercial mortgages — office, retail, hotel, multi-family.",
        "Pool of 50-100 large commercial loans, tranched by seniority and rating. Distinct from RMBS because commercial mortgages don't prepay freely (yield-maintenance clauses lock in lender economics). The 2020-22 office crisis hammered CMBS valuations: vacancy rates spiked, refinancing dried up, several major office loans defaulted. Roughly 700 billion outstanding. SEC oversight; ratings from Moody's, S&P, KBRA.",
        ["SEC", "Federal Reserve"],
        indications=["Credit"], category="Instruments"),

    entry("RMBS", "Residential Mortgage-Backed Security",
        "MBS backed by residential mortgages — the bulk of the global MBS market.",
        "Cash flows come from millions of individual homeowner payments. Agency RMBS (Fannie, Freddie, Ginnie) dominates US issuance; non-agency RMBS issuance remains a fraction of pre-2008 levels. Prepayment risk is the central modelling challenge — homeowners refinance freely when rates fall, hurting MBS holders. RMBS deals tranched into pass-throughs, CMOs, and IO/PO strips for different risk appetites.",
        ["Federal Reserve", "SEC"],
        indications=["Credit"], category="Instruments"),

    entry("ABS", "Asset-Backed Security",
        "Bond backed by non-mortgage consumer or commercial receivables.",
        "Auto loans, credit cards, student loans, equipment leases, and more. Tranched into rated bond classes similar to MBS structures. The 2 trillion US ABS market is dominated by auto and credit card issuance from banks and captive finance companies. ABS held up better than RMBS in 2008 because underwriting was tighter and the underlying assets shorter-dated and easier to repossess.",
        ["SEC", "Federal Reserve"],
        indications=["Credit"], category="Instruments"),

    entry("Auto ABS", "",
        "ABS backed by auto loans or leases — the largest non-mortgage ABS sector.",
        "Roughly 250 billion outstanding in the US. Pool of 30,000-100,000 auto loans, weighted-average life of 1-3 years. Prepayments come from car sales, refinancing, and total losses. Default and loss rates correlate with employment and used-car prices. Performed remarkably well in 2008 (better than MBS) but stressed in 2020 before COVID-era stimulus and supply-chain car-price spikes flipped used-car values upward.",
        ["SEC"],
        indications=["Credit"], category="Instruments"),

    entry("Credit Card ABS", "",
        "ABS backed by revolving credit-card receivables — short-dated, high-yielding.",
        "Pool of credit-card balances from a single issuer (Capital One, Citi, Amex). Master trust structures let issuers add and remove receivables over time. Weighted-average life of 2-5 years. Charge-off rates run 2-4 percent in calm times, spiking in recessions. Post-2008 issuance recovered; modern deals carry low spreads reflecting strong collateral performance and frequent issuer stress tests.",
        ["SEC", "Federal Reserve"],
        indications=["Credit"], category="Instruments"),

    entry("Tranche", "",
        "Slice of a structured product with specific priority of payment and risk.",
        "Senior tranche gets paid first, takes losses last; equity tranche gets paid last, absorbs first losses. Mezzanine sits between. Each tranche carries a separate credit rating (senior often AAA, mezzanine BBB, equity unrated). Investors choose tranches matched to their mandate: pension funds buy senior, hedge funds buy equity for higher yield. The 'waterfall' specifies the cash-flow order.",
        ["SEC", "ICE"],
        indications=["Credit"], category="Instruments"),

    entry("Senior Tranche", "",
        "Highest-priority slice of a structured product — paid first from cash flows.",
        "Usually AAA-rated, lowest yield. In a typical CLO, the senior tranche makes up 60-70 percent of the capital stack and absorbs losses only after all subordinated tranches are wiped out. Senior CLO tranches survived even the 2008 crisis with full principal recovery. Banks, insurance companies, and money funds are the typical buyers. Sized so that the rating-agency stress scenario doesn't penetrate it.",
        ["SEC"],
        indications=["Credit"], category="Instruments"),

    entry("Mezzanine Tranche", "Mezz",
        "Middle-of-the-stack slice — pays after senior, before equity.",
        "Typically rated BBB to single-B depending on subordination. Yields the spread differential between AAA senior and equity. Hedge funds, insurance companies, and dedicated mezz funds buy it. The 2008 crisis taught that mezz tranches in mortgage CDOs could go from BBB to zero within months — credit ratings dramatically understated the tail risk. Modern CLO mezz holds up better due to tighter underwriting and less correlated underlying loans.",
        ["SEC"],
        indications=["Credit"], category="Instruments"),

    entry("Equity Tranche", "First-Loss Piece",
        "Lowest-priority slice of a structured product — absorbs first losses, gets residual cash flow.",
        "Unrated, highest yield. In a CLO, the equity tranche is typically 8-12 percent of the deal and pays cash flow after all senior tranches are serviced. Equity-tranche IRRs of 15-25 percent in normal markets, deeply negative in stress. Held by hedge funds, family offices, CLO managers themselves (alignment), and structured-credit funds. Often retained by issuer in regulatory 'skin in the game' contexts.",
        ["SEC"],
        indications=["Credit"], category="Instruments"),

    entry("Subprime Mortgage", "",
        "Mortgage to a borrower with poor credit history or other adverse underwriting features.",
        "FICO scores below 620, no income verification, high loan-to-value ratios, or option-ARM payment features. Subprime origination peaked around 600 billion annually in 2005-06, then collapsed. The wave of subprime defaults in 2007 triggered the 2008 financial crisis. Modern definitions and underwriting standards have tightened; what's called 'non-prime' or 'non-QM' today is far better-underwritten than pre-crisis subprime.",
        ["Federal Reserve", "SEC"],
        indications=["Credit"], category="Instruments"),

    entry("Prepayment Risk", "",
        "Risk that MBS holders get their principal back early — usually when rates fall and homeowners refinance.",
        "Forces reinvestment at lower yields. Higher-coupon MBS (originated when rates were high) are most exposed: as soon as rates fall, refinancing surges. MBS modellers estimate Conditional Prepayment Rates (CPR) and Public Securities Association (PSA) speeds. The 2003 refi wave produced extreme prepayment shocks; the 2020 wave was deepest. Negative convexity follows directly from prepayment risk.",
        ["Federal Reserve"],
        indications=["Credit"], category="Risk"),

    entry("Extension Risk", "",
        "Risk that MBS principal returns slower than expected — typically when rates rise.",
        "The flip side of prepayment risk. As rates rise, fewer homeowners refinance (or move), so MBS principal returns are extended. Holders are locked into below-market coupons longer than modelled. Extension risk hammered MBS portfolios in 2022 as rates rose 400 bps in a year. Negative convexity captures both prepayment and extension dynamics — MBS holders lose either way.",
        ["Federal Reserve"],
        indications=["Credit"], category="Risk"),

    entry("WAL", "Weighted Average Life",
        "Expected average time until principal is returned — like duration but for amortising securities.",
        "Most relevant for MBS and ABS where principal returns over time, not in a lump sum. WAL depends heavily on prepayment assumptions — a 30-year MBS might have a WAL of 6 years if prepayments are heavy, 20 years if slow. Quoted in years. Used to size positions in amortising securities and compare them to bullet bonds of similar duration.",
        ["CFA Institute", "SEC"],
        indications=["Credit"], category="Pricing & Valuation"),

    entry("Subordination", "Credit Enhancement",
        "Junior tranches absorbing losses below a senior tranche — creates the senior's credit cushion.",
        "If a CLO senior tranche is 70 percent of the deal, it has 30 percent subordination — losses can hit 30 percent of the pool before the senior tranche takes any loss. Rating agencies set subordination levels to achieve target ratings: AAA seniors typically require 30-40 percent subordination in CLOs. Other forms of credit enhancement: overcollateralisation, reserve accounts, and excess spread.",
        ["SEC", "ICE"],
        indications=["Credit"], category="Instruments"),

    entry("Waterfall", "Payment Waterfall",
        "Pre-defined order in which a structured product's cash flows are distributed across tranches.",
        "Interest waterfall: senior interest first, then mezz, then equity. Principal waterfall: usually starts with senior amortisation in a 'turbo' structure. Tests embedded in the waterfall (overcollateralisation, interest-coverage tests) redirect cash flow to seniors if performance deteriorates. The 2007-08 mortgage crisis exposed how failure of waterfall tests cascaded through CDOs. Modern deals have triggers tuned from that experience.",
        ["SEC"],
        indications=["Credit"], category="Instruments"),

    entry("SPV", "Special Purpose Vehicle",
        "Bankruptcy-remote legal entity created solely to hold assets and issue securities.",
        "The legal shell behind every CLO, CDO, MBS, and ABS. Structured to be isolated from the originator's bankruptcy — if the bank or originator fails, the SPV's assets remain available to its bondholders. SPVs are typically Delaware or Cayman entities with limited purposes set in the trust agreement. The 'orphan' SPV variant (owned by a charity, not the originator) provides extra bankruptcy isolation.",
        ["SEC"],
        indications=["Credit"], category="Instruments"),

    entry("Synthetic CLO", "",
        "CLO using CDS rather than physical loans for credit exposure.",
        "References a basket of loans via CDS contracts rather than owning the loans outright. Issuer (typically a bank) buys protection on its loan portfolio; investors sell protection and earn premiums. Lets banks transfer credit risk off-balance-sheet without selling the loans. Synthetic CLO issuance has grown post-2018 as banks face higher regulatory capital requirements on retained credit risk. SRT (Significant Risk Transfer) trades fall in this space.",
        ["ISDA", "Federal Reserve"],
        indications=["Credit"], category="Instruments"),
]


# ============================================================================
# BATCH 10 — Commodities energy (25 terms — crude, gas, refined products, carbon)
# ============================================================================

BATCH_COMMODITIES_ENERGY = [
    entry("WTI", "West Texas Intermediate",
        "US benchmark crude oil grade — light, sweet, deliverable to Cushing, Oklahoma.",
        "Quoted in dollars per barrel. NYMEX-listed WTI futures (/CL) are the most-traded energy contract globally. Light (API gravity 39.6) and sweet (low sulphur) make it easier to refine into gasoline. The April 2020 negative WTI episode — front-month settled at minus 37 dollars — was a contango storage-overflow event. Delivery at Cushing creates landlocked pricing dynamics different from waterborne Brent.",
        ["CME Group", "Federal Reserve FRED"],
        indications=["Commodities"], category="Instruments"),

    entry("Brent", "Brent Crude",
        "North Sea crude benchmark — global pricing reference, especially for non-US trade.",
        "Quoted in dollars per barrel. ICE-listed Brent futures are the global benchmark, used in pricing roughly two-thirds of internationally traded crude. Lighter and sweeter than many EM grades but heavier than WTI. Brent-WTI spread reflects North Sea supply, US pipeline constraints, and global vs continental dynamics. Historically WTI traded above Brent by a few dollars; flipped in 2011 with the US shale boom.",
        ["ICE", "BIS"],
        indications=["Commodities"], category="Instruments"),

    entry("NYMEX", "New York Mercantile Exchange",
        "CME-owned exchange listing the world's most-traded energy futures — crude, gas, gasoline, heating oil.",
        "Acquired by CME Group in 2008. Listed contracts (codes in parentheses): WTI Crude (/CL), Henry Hub Natural Gas (/NG), RBOB Gasoline (/RB), NY Harbor ULSD heating oil (/HO). All physically deliverable in principle, mostly financially settled or rolled before expiry. Floor trading ended in 2016; all electronic via CME Globex. Margin requirements managed via CME Clearing.",
        ["CME Group"],
        indications=["Commodities"], category="Market Structure"),

    entry("Natural Gas", "Nat Gas",
        "Hydrocarbon fuel used for power generation, heating, industry, and as petrochemical feedstock.",
        "Priced in dollars per million BTU (MMBtu). US natural gas peaked around 13 dollars per MMBtu in 2008, crashed below 2 dollars in 2020, surged above 9 in 2022, sat around 2 in 2024. Heavily seasonal demand drives winter price spikes. The US shale boom turned the US from net importer to net exporter (via LNG). Storage levels reported weekly by EIA.",
        ["CME Group", "Federal Reserve FRED"],
        indications=["Commodities"], category="Instruments"),

    entry("Henry Hub", "",
        "Pipeline interconnect in Erath, Louisiana — pricing reference for North American natural gas.",
        "NYMEX natural gas futures settle to Henry Hub delivery. Connects to a dozen pipelines crossing the Gulf Coast — the most-connected pricing point in the US gas system. Henry Hub prices diverge from regional prices (Permian, Marcellus, AECO in Alberta) when pipeline constraints bite. The 2022 European gas crisis pulled US LNG export demand, lifting Henry Hub prices via the international arbitrage.",
        ["CME Group"],
        indications=["Commodities"], category="Indexes & Benchmarks"),

    entry("LNG", "Liquefied Natural Gas",
        "Natural gas chilled to liquid form for transport by sea — turned global the gas market.",
        "Cooled to minus 162 degrees Celsius, volume shrinks 600x for shipping. US went from net LNG importer in 2010 to largest LNG exporter by 2023. Cheniere's Sabine Pass led the US LNG export boom; QatarEnergy and Australia are major peers. Spot pricing benchmarks: JKM (Asia), TTF (Europe), Henry Hub (US). The 2022 European gas crisis drove TTF to 350 EUR/MWh, roughly 10x normal.",
        ["BIS", "World Bank"],
        indications=["Commodities"], category="Instruments"),

    entry("Heating Oil", "ULSD",
        "Diesel-grade fuel used for residential and commercial heating, mostly in the US Northeast.",
        "NYMEX-listed heating oil futures (/HO) are now ULSD (ultra-low sulphur diesel) post-2012, same as on-road diesel fuel. Quoted in dollars per gallon. Demand is heavily seasonal. The crack spread between WTI crude and heating oil futures is a refining margin indicator. Heating oil consumption has declined as households switch to natural gas and electric heat.",
        ["CME Group"],
        indications=["Commodities"], category="Instruments"),

    entry("RBOB Gasoline", "Reformulated Blendstock for Oxygenate Blending",
        "Specification gasoline traded on NYMEX — proxy for US wholesale gasoline price.",
        "Quoted in dollars per gallon. Standard contract is 42,000 gallons. RBOB is the unfinished gasoline before retail-grade ethanol blending. Crack spreads (RBOB minus WTI) measure refining profitability; widened sharply post-2022 amid global refining capacity tightness. Retail gasoline prices typically lag RBOB futures by 1-2 weeks. The EIA publishes weekly inventory and demand data.",
        ["CME Group"],
        indications=["Commodities"], category="Instruments"),

    entry("Crack Spread", "",
        "Difference between refined product prices (gasoline, distillates) and crude oil — refining margin.",
        "Classic 3-2-1 crack: three barrels of crude in, two of gasoline plus one of distillate out — refining margin per crude barrel. Widened to record levels in summer 2022 as global refining capacity shortages collided with sanctions on Russian product exports. Refiners use crack-spread futures to lock in margins; speculators trade them as direct macro views on global product balances.",
        ["CME Group", "ICE"],
        indications=["Commodities"], category="Pricing & Valuation"),

    entry("Refinery Margin", "",
        "Profit per barrel a refiner earns turning crude into products — broader than the crack spread.",
        "Includes the cost of operating, financing, and maintaining the refinery — beyond just the crude-versus-product spread. Refineries with complex configurations (cokers, hydrocrackers) earn higher margins on heavier crude grades. The 2022 European refining margins on diesel exceeded 60 dollars per barrel, historically unheard-of, before settling to 15-25 in 2024. Captured in EIA's gross product margin data.",
        ["BIS"],
        indications=["Commodities"], category="Pricing & Valuation"),

    entry("OPEC", "Organisation of Petroleum Exporting Countries",
        "13-member oil cartel coordinating production to support prices.",
        "Founded 1960 in Baghdad. Members: Saudi Arabia, Iran, Iraq, UAE, Kuwait, Venezuela, Nigeria, Algeria, Libya, Angola (exited 2023), Equatorial Guinea, Gabon, Republic of Congo. Holds roughly 40 percent of global production and 80 percent of proven reserves. Quarterly meetings set production quotas. Saudi Arabia, with the largest spare capacity, plays swing-producer role. OPEC discipline has wavered over decades.",
        ["IMF", "World Bank"],
        indications=["Commodities", "Macro"], category="Market Structure"),

    entry("OPEC+", "OPEC Plus",
        "OPEC plus 10 non-OPEC producers (notably Russia) coordinating supply — formed 2016.",
        "Saudi Arabia and Russia anchor OPEC+, with combined production around 20 million barrels per day. Production-cut deal triggered by the 2014-16 oil price crash. The April 2020 OPEC+ price war (Saudi-Russia disagreement) triggered the WTI negative-price event; resolved with the largest-ever production cut. OPEC+ post-2022 has cut production several times to defend prices around 80 dollars per barrel.",
        ["IMF"],
        indications=["Commodities", "Macro"], category="Market Structure"),

    entry("Strategic Petroleum Reserve", "SPR",
        "US government's emergency oil stockpile — held in salt caverns in Texas and Louisiana.",
        "Established 1975 post-Arab embargo. Capacity 714 million barrels; held roughly 350 million as of late 2024 after massive 2022 releases (180 million barrels) aimed at cushioning post-Ukraine prices. SPR releases require presidential authorisation; the 2022 release was the largest in history. Refilling the SPR at lower prices is a Biden-administration objective. Other countries maintain analogous reserves.",
        ["Federal Reserve FRED", "IMF"],
        indications=["Commodities", "Macro"], category="Instruments"),

    entry("EIA Inventory Report", "Weekly Petroleum Status Report",
        "US weekly snapshot of crude oil, gasoline, and distillate stocks — moves oil prices.",
        "Published Wednesdays at 10:30 AM Eastern by the Energy Information Administration. Surprise builds or draws move WTI 1-3 dollars per barrel on release. Includes inventories, production, imports, exports, and refinery utilisation. The American Petroleum Institute (API) publishes a competing report Tuesday evenings, watched as a preview. Distilled into weekly traders' notes globally.",
        ["Federal Reserve FRED"],
        indications=["Commodities"], category="Indexes & Benchmarks"),

    entry("Coal", "Thermal Coal",
        "Carbon-rich solid fuel used primarily for electricity generation.",
        "Major pricing references: Newcastle thermal (Asia), Rotterdam (Europe), Central Appalachian (US). Demand peaked globally around 2014; in retreat from gas and renewables in OECD economies, but China and India still expanding. 2022 European energy crisis briefly revived coal demand as gas supplies were squeezed. Carbon-pricing schemes (EU ETS) penalise coal generation. Futures traded on ICE and CME.",
        ["ICE", "World Bank"],
        indications=["Commodities"], category="Instruments"),

    entry("EU ETS", "European Union Emissions Trading System",
        "World's largest cap-and-trade scheme — covers EU power, industry, aviation.",
        "Launched 2005. Companies must surrender allowances (EUAs) matching their CO2 emissions; shortfalls require buying allowances. The cap shrinks annually toward 2030/2050 targets. EUA prices: roughly 5 euros per tonne in 2017, 80-90 in 2024, briefly above 100 in early 2023. Industries on the system: power, steel, cement, aluminium, refining, aviation (intra-EU). Phase 4 runs 2021-2030.",
        ["ESMA"],
        indications=["Commodities"], category="Instruments"),

    entry("Carbon Credit", "Carbon Allowance",
        "Tradable permit to emit one tonne of CO2 — issued under cap-and-trade schemes.",
        "EU ETS EUAs are the largest credit market. Voluntary markets (REDD+ forest conservation, renewable-energy credits) operate separately at lower prices and with weaker integrity controls. Cap-and-trade schemes shrink credit supply over time, lifting prices. Critics argue carbon markets allow polluters to outsource action; supporters cite EU ETS achieving real emission reductions cost-effectively.",
        ["ESMA", "World Bank"],
        indications=["Commodities"], category="Instruments"),

    entry("Electricity Market", "Power Market",
        "Wholesale market where electricity is bought and sold — settles in real time across grids.",
        "Major hubs: PJM, ERCOT (Texas), CAISO (California), MISO (Midwest), Nord Pool (Europe). Day-ahead markets fix prices for the next 24 hours; real-time balancing markets clear last-minute imbalances. Texas ERCOT February 2021 winter storm produced 9,000-dollar-per-MWh prices for days; Australia's 2022 NEM crisis saw similar extremes. Renewable penetration drives more negative-price episodes.",
        ["ICE"],
        indications=["Commodities"], category="Market Structure"),

    entry("Diesel", "Gasoil",
        "Middle distillate fuel — used for trucks, trains, ships, and as heating oil.",
        "Global benchmarks: ICE Gas Oil (European), NYMEX ULSD (US). Diesel demand correlates with industrial activity — manufacturing, freight, agriculture. Diesel crack spreads (vs Brent) hit record highs in 2022 amid sanctions on Russian product exports and refining capacity tightness. Marine fuel transitioned post-2020 to IMO-2020 low-sulphur specs, restructuring global diesel/HSFO markets.",
        ["ICE", "CME Group"],
        indications=["Commodities"], category="Instruments"),

    entry("Convenience Yield", "",
        "Implicit benefit of holding physical commodity inventory vs holding a futures contract.",
        "Drives the relationship between spot and futures. Physical holders have flexibility — they can use the commodity, deliver to short sellers, profit from local shortages. The convenience yield equals interest rate plus storage cost minus the futures-spot basis. When convenience yield exceeds storage cost, the curve goes into backwardation. Common in heavily-used commodities (oil, gas) with thin spot inventories.",
        ["CFA Institute"],
        indications=["Commodities"], category="Pricing & Valuation"),

    entry("Open Interest", "OI",
        "Total number of open futures or options contracts at the end of each day.",
        "Differs from volume: volume counts daily trades, open interest counts unsettled contracts. Increases when new positions are opened; decreases when positions are closed. Rising open interest plus rising prices signals new long money entering; rising OI with falling prices signals short build-up. CME and ICE publish OI daily by contract. Crucial gauge of trader positioning.",
        ["CME Group", "ICE", "CFTC"],
        indications=["Commodities", "Derivatives"], category="Market Structure"),

    entry("COT Report", "Commitments of Traders",
        "Weekly CFTC report breaking down futures positions by trader category.",
        "Published Fridays for positions as of the prior Tuesday close. Categories: commercial hedgers (producers/users), managed money (hedge funds and CTAs), other reportables, non-reportables (small specs). Watched closely for signals of extreme positioning — when managed money is at record long, often a contrarian sell signal. Available across crude, gas, gold, currencies, equities, and rates contracts.",
        ["CFTC"],
        indications=["Commodities", "FX"], category="Market Structure"),

    entry("Roll Yield", "",
        "Gain or loss from rolling expiring futures contracts into the next month.",
        "Positive in backwardated markets (selling expiring contract at higher price than rolling into cheaper next month); negative in contango. Long-only commodity ETFs (USO, UNG, DBC) systematically pay roll yield in contango — explains why USO underperforms WTI spot over time. Optimised commodity indexes (Goldman, Bloomberg) try to smartly time rolls or weight curve points to minimise contango drag.",
        ["CME Group"],
        indications=["Commodities"], category="Pricing & Valuation"),

    entry("Producer Hedge", "",
        "Oil, gas, or mining company selling forward production to lock in revenue.",
        "Standard risk management: an oil producer with 100,000 bpd output sells WTI futures or buys put options to lock in prices for the next 1-3 years. Reduces revenue volatility; sacrifices upside if prices rally. Major producers (Pioneer, Devon, Hess) disclose hedge books in 10-Ks. Mexico's sovereign hedge program (Hacienda Hedge) is the largest single oil hedging program — billions in coverage annually.",
        ["CME Group", "ICE"],
        indications=["Commodities"], category="Trading & Execution"),

    entry("Spot vs Futures", "",
        "Spot market is the physical commodity delivered now; futures are contracts for later delivery.",
        "Spot oil prices reflect the cargo available at the delivery point today; futures reflect expected price plus storage, financing, and convenience yield. Spot markets are usually thinner and more locally driven; futures are highly liquid global benchmarks. The basis (spot minus futures) varies with local supply, demand, transport constraints. Refiners and traders arbitrage the basis when it strays from fundamentals.",
        ["CME Group", "ICE"],
        indications=["Commodities"], category="Market Structure"),
]


# ============================================================================
# BATCH 11 — Commodities metals & ags (25 terms — base metals, precious, grains, softs)
# ============================================================================

BATCH_COMMODITIES_METALS_AGS = [
    entry("Gold", "",
        "Yellow precious metal — monetary store of value across millennia, now also industrial.",
        "Priced in dollars per troy ounce. London Bullion Market Association (LBMA) sets the daily gold price fix. Central banks hold roughly 17 percent of all gold ever mined as reserves; private investors hold another 22 percent. Gold rallies in real-rate falls, USD weakness, and risk-off episodes. Crossed 2,000 dollars per ounce in 2020, 2,800 in 2024. Used as inflation hedge, currency hedge, and crisis insurance.",
        ["LSEG", "World Bank"],
        indications=["Commodities", "Macro"], category="Instruments"),

    entry("Silver", "",
        "Precious metal — half monetary store of value, half industrial input.",
        "Roughly 50 percent of demand is industrial (solar panels, electronics, medical), 50 percent investment/jewellery. More volatile than gold because the industrial demand swings with the economy. The 1980 Hunt brothers attempt to corner silver took it from 6 to 50 dollars per ounce before crashing. Gold-silver ratio (gold price / silver price) hovers historically 60-80; spikes to 100+ in stress, collapses in metals bull markets.",
        ["LSEG", "CME Group"],
        indications=["Commodities"], category="Instruments"),

    entry("Platinum", "",
        "Precious metal — catalytic converter feedstock, jewellery, industrial.",
        "Priced in dollars per ounce. Roughly 70 percent of supply comes from South Africa. Diesel-engine catalytic converter demand collapsed post-Dieselgate (2015) as gasoline cars (using palladium instead) took share. Platinum has traded below gold since 2015 — historically rare inversion. Hydrogen-economy demand could revive platinum prices over the next decade as fuel cells scale.",
        ["LSEG"],
        indications=["Commodities"], category="Instruments"),

    entry("Palladium", "",
        "Precious metal heavily used in gasoline-engine catalytic converters.",
        "Roughly 80 percent of demand is auto-catalyst. Russia and South Africa produce most supply. Prices surged to over 3,000 dollars per ounce in 2022 as Russia sanctions hit supply; collapsed to under 1,000 by 2024 as EV adoption reduced demand for ICE catalysts. The 2018-2022 palladium bull market was one of the most dramatic commodity runs of the century.",
        ["LSEG"],
        indications=["Commodities"], category="Instruments"),

    entry("Copper", "Dr Copper",
        "Industrial base metal — wiring, plumbing, construction, electrification.",
        "Nicknamed 'Dr Copper' for its perceived ability to diagnose the global economy — strong copper demand signals industrial expansion. Quoted in dollars per pound (US) or dollars per tonne (LME). China consumes roughly half of global copper. Electrification, EVs, and renewable grids drive structural demand growth. Surged to 5 dollars per pound in 2021-22; supply constraints from declining ore grades and project delays keep prices structurally elevated.",
        ["LSEG"],
        indications=["Commodities", "Macro"], category="Instruments"),

    entry("Aluminum", "Aluminium",
        "Lightweight industrial metal — packaging, aerospace, construction, transport.",
        "LME-listed aluminium is the benchmark. Production is electricity-intensive (4 percent of global power consumption); aluminium prices closely track power costs. China produces 60 percent of global aluminium. The 2022 European energy crisis forced widespread European smelter closures. Demand growth driven by EV lightweighting and electrification. Carbon-intensity differences across producers create premium markets for 'green' aluminium.",
        ["LSEG"],
        indications=["Commodities"], category="Instruments"),

    entry("Nickel", "",
        "Base metal — stainless steel and EV battery cathode demand.",
        "Stainless steel is roughly 70 percent of demand; battery demand is the fast-growing 15 percent. Indonesia dominates production (40 percent). The March 2022 LME nickel short squeeze (price 4x in two days, triggered by a Chinese tycoon's massive short position) forced the LME to halt trading and cancel trades — controversial episode that damaged LME's reputation. Battery-grade nickel sulfate commands premium over LME contract.",
        ["LSEG"],
        indications=["Commodities"], category="Instruments"),

    entry("Lithium", "",
        "Critical battery metal — boomed and busted with EV cycle.",
        "Two main sources: hard-rock spodumene (Australia) and brine evaporation (Chile, Argentina, China). Lithium carbonate prices peaked above 80,000 dollars per tonne in late 2022 as EV demand outran supply; collapsed below 12,000 by 2024 as new supply came online and EV growth slowed. Pricing increasingly transparent via Fastmarkets and Benchmark Mineral Intelligence indexes. Long-term demand outlook depends on EV adoption pace.",
        ["World Bank"],
        indications=["Commodities"], category="Instruments"),

    entry("LME", "London Metal Exchange",
        "Global benchmark exchange for base metals — aluminium, copper, nickel, zinc, lead, tin.",
        "Founded 1877. Owned by Hong Kong Exchanges (HKEX) since 2012. Unique 'date structure' — contracts for every business day out to three months, then monthly out to multi-year tenors. Three-month rolling contracts are the standard benchmark. Physical delivery from LME-registered warehouses globally. Battered reputation post-2022 nickel cancellation; reforms ongoing.",
        ["LSEG"],
        indications=["Commodities"], category="Market Structure"),

    entry("COMEX", "",
        "CME-owned division for precious-metals and copper futures — gold and silver benchmark.",
        "Originally the Commodity Exchange of New York. Merged with NYMEX in 1994; under CME Group since 2008. Lists gold (/GC), silver (/SI), copper (/HG), platinum, palladium. Physically deliverable in principle, mostly financially settled. Gold and silver delivery warrants from COMEX-registered warehouses (HSBC, JP Morgan, Brinks) form the physical market backbone. Daily settlement prices are key benchmarks.",
        ["CME Group"],
        indications=["Commodities"], category="Market Structure"),

    entry("Gold-Silver Ratio", "",
        "Gold price divided by silver price — relative-value gauge between the two metals.",
        "Historically averages around 60. Above 80 typically marks silver as cheap relative to gold (silver underperforms in early metals bull markets, outperforms in late stages). Above 100 (2020) signals extreme dislocation. Below 50 signals silver-heavy bull market (1980s). Used by precious-metals traders for relative-value rotation between the two metals. Both gold and silver futures listed on COMEX.",
        ["CME Group", "LSEG"],
        indications=["Commodities"], category="Pricing & Valuation"),

    entry("Iron Ore", "",
        "Steel-making raw material — China-dominated demand drives global prices.",
        "Priced in dollars per dry tonne of 62 percent iron content (Platts IODEX). China imports roughly two-thirds of global seaborne supply. Top exporters: Australia (Rio Tinto, BHP) and Brazil (Vale). The 2019 Vale tailings dam collapse triggered a price spike above 200 dollars per tonne; collapsed below 100 in 2022 as Chinese property slowdown crushed steel demand. SGX-listed iron ore futures are the benchmark.",
        ["LSEG", "World Bank"],
        indications=["Commodities", "Macro"], category="Instruments"),

    entry("Corn", "Maize",
        "Globally largest crop by volume — feed, food, ethanol, industrial uses.",
        "CME-listed corn futures (/ZC) are the benchmark. US is the largest producer (Iowa, Illinois, Nebraska). Roughly 40 percent of US corn goes to ethanol production. Brazil's second corn crop (safrinha) increasingly significant. USDA WASDE monthly report drives prices. Drought, heat stress, and planting-progress reports move corn 2-5 percent on release.",
        ["CME Group", "Federal Reserve FRED"],
        indications=["Commodities"], category="Instruments"),

    entry("Wheat", "",
        "Global staple grain — food, feed, industrial.",
        "Three major futures contracts: CBOT SRW (soft red winter, Chicago), KC HRW (hard red winter, Kansas City), Minneapolis HRS (hard red spring). Different protein and gluten properties suit different end uses (bread, pastry, pasta). The 2022 Russia-Ukraine invasion spiked wheat to record prices — Black Sea region produces roughly a quarter of global exports. Volatility eased as Black Sea grain initiative restored some flows.",
        ["CME Group"],
        indications=["Commodities"], category="Instruments"),

    entry("Soybeans", "",
        "High-protein oilseed — meal for animal feed, oil for food and biodiesel.",
        "CME-listed soybean futures (/ZS) are the benchmark. US and Brazil dominate global production. Soybean complex: bean, meal (animal feed), oil (cooking oil, biodiesel). Crush spread (bean price minus meal and oil prices) measures processor margins. Chinese hog herd cycle drives global soybean demand. Trade-war dynamics around the 2018 US-China tariffs reshaped global soybean trade flows.",
        ["CME Group", "Federal Reserve FRED"],
        indications=["Commodities"], category="Instruments"),

    entry("Sugar", "",
        "Sweetener and ethanol feedstock — concentrated production in Brazil and India.",
        "Two ICE-listed contracts: Sugar No 11 (raw, world price) and No 16 (refined, US domestic). Brazil produces roughly 40 percent of global supply. Brazilian sugar/ethanol mills swap between products based on price ratios — drives sugar supply elasticity. India is the second-largest producer; government policy and monsoon weather drive Indian sugar dynamics. EU sugar reform in 2017 removed quotas and shifted European pricing.",
        ["ICE"],
        indications=["Commodities"], category="Instruments"),

    entry("Coffee", "",
        "Tropical bean — Arabica (premium) and Robusta (mass-market) varieties.",
        "ICE-listed Arabica (Coffee C) is the premium benchmark; Robusta on London ICE. Brazil produces roughly 40 percent of global Arabica; Vietnam dominates Robusta. Arabica prices spiked to record highs in 2024 on Brazilian drought and frost concerns. Specialty coffee market (premium grades) developing alongside the commodity market with separate pricing dynamics. Climate change is a real long-term threat — Arabica's growing range is shrinking.",
        ["ICE", "World Bank"],
        indications=["Commodities"], category="Instruments"),

    entry("Cocoa", "Cocoa Beans",
        "Chocolate raw material — concentrated supply in West Africa.",
        "Ivory Coast and Ghana produce roughly 60 percent of global supply. ICE-listed cocoa futures (London for European delivery, NYC for US). Prices surged to record 10,000+ dollars per tonne in early 2024 — quadruple historical averages — as West African disease and weather damaged crops. Climate change and aging tree stocks create structural supply concerns. Cocoa demand grows roughly 2-3 percent annually; supply struggles to keep pace.",
        ["ICE"],
        indications=["Commodities"], category="Instruments"),

    entry("Cotton", "",
        "Natural fibre for textiles — competes with synthetic fibres (polyester).",
        "ICE-listed cotton futures (/CT) are the benchmark. US, China, India, Brazil are top producers. Cotton prices closely correlate with global GDP — apparel demand reflects discretionary spending. Synthetic fibres now dominate global fibre consumption; cotton holds roughly 25 percent share. ESG concerns around water-intensive cultivation (Aral Sea desiccation by Soviet cotton growing) drive sustainability initiatives.",
        ["ICE"],
        indications=["Commodities"], category="Instruments"),

    entry("Live Cattle", "",
        "Beef-cattle futures — feedlot animals ready for slaughter.",
        "CME-listed live cattle futures (/LE). Companion contract: feeder cattle (younger animals headed to feedlots). US beef supply chain: cow-calf operations, feedlots, packers (JBS, Tyson, Cargill, National Beef control roughly 85 percent of US packing). Cyclical multi-year herd-rebuilding patterns. Lean Hogs (/HE) is the pork counterpart. African Swine Fever epidemic in China (2018-19) wiped out roughly half of Chinese hog herd, reshaping global protein trade.",
        ["CME Group", "Federal Reserve FRED"],
        indications=["Commodities"], category="Instruments"),

    entry("WASDE Report", "World Agricultural Supply and Demand Estimates",
        "USDA's monthly snapshot of global crop supply, demand, and stocks — moves ag markets.",
        "Released mid-month at noon Eastern. Updates production estimates, ending stocks, demand forecasts for major crops. Bigger-than-expected revisions move corn, soybeans, wheat 2-5 percent on release. Quarterly Grain Stocks reports also significant. International equivalent: FAO Food Price Index, less market-moving but watched for macro food-price commentary.",
        ["Federal Reserve FRED"],
        indications=["Commodities"], category="Indexes & Benchmarks"),

    entry("CBOT", "Chicago Board of Trade",
        "CME-owned exchange listing grain and bond futures — home of corn, wheat, soybeans.",
        "Founded 1848 as the first US futures exchange. Merged with CME in 2007. Lists CBOT corn (/ZC), wheat (/ZW), soybeans (/ZS), and also 30-year US Treasury bond futures (/ZB) and 10-year T-Note (/ZN). Trading hours extended overnight for global access. Historic Chicago grain-trading floor closed in 2015; trading now electronic via Globex.",
        ["CME Group"],
        indications=["Commodities", "Rates"], category="Market Structure"),

    entry("Soybean Crush Spread", "",
        "Spread between soybean futures and the value of resulting soybean meal and oil.",
        "Processor margin: buy beans, crush into meal and oil, sell the products. Standard crush ratio: one bushel of soybeans yields roughly 44 pounds of meal and 11 pounds of oil. CBOT-traded crush spread futures simplify hedging for processors (ADM, Bunge, Cargill). Wider crush spreads incentivise more processing; narrower spreads slow processing and tighten product markets.",
        ["CME Group"],
        indications=["Commodities"], category="Trading & Execution"),

    entry("Weather Risk", "Crop Weather Risk",
        "Agricultural commodity price risk driven by weather — drought, frost, heatwaves, flooding.",
        "El Niño and La Niña cycles affect global crop patterns predictably. The 2012 US Midwest drought spiked corn and soybean prices over 50 percent in months. Australian wheat crops sensitive to rainfall during winter. Brazilian frost has driven coffee price spikes. Weather derivatives (CME-listed) hedge specific climate-data outcomes (temperature, rainfall). Climate change intensifies tail-risk events.",
        ["CME Group", "World Bank"],
        indications=["Commodities", "Macro"], category="Risk"),

    entry("Spot Gold ETF", "Bullion ETF",
        "ETF holding physical gold — gives investors gold exposure without bars.",
        "SPDR Gold Shares (GLD), launched 2004, was the first major spot gold ETF — now holds roughly 27 million ounces (worth 80 billion dollars). iShares Gold Trust (IAU) is the largest competitor. The shares represent a fractional ownership stake in actual gold held in vaults (HSBC London for GLD). The 2024 launch of US spot Bitcoin ETFs explicitly modelled the GLD structure.",
        ["SEC", "LSEG"],
        indications=["Commodities"], category="Instruments"),
]


# ============================================================================
# BATCH 12 — Derivatives fundamentals (25 terms — option mechanics, ISDA, margin)
# ============================================================================

BATCH_DERIV_FUNDAMENTALS = [
    entry("Forward Contract", "Forward",
        "OTC agreement to buy or sell an asset at a future date for a price agreed today.",
        "Distinct from futures (exchange-traded, standardised, mark-to-market) — forwards are bilateral and customised. Settle on delivery date with cash or physical delivery. No daily margining unless governed by ISDA CSA. Used heavily in FX (corporate hedging), commodities (producer/consumer hedging), and rates (forward rate agreements). The 2008 crisis prompted regulators to push standardisation toward exchange-traded futures.",
        ["ISDA", "BIS"],
        indications=["Derivatives"], category="Instruments"),

    entry("Notional Amount", "Notional",
        "Reference quantity in a derivatives contract — not money that changes hands.",
        "A 100-million IRS doesn't involve 100 million dollars moving; the notional just determines coupon and payment sizes. Total notional outstanding in global derivatives is approximately 600 trillion dollars (BIS data) — far larger than actual market value (roughly 20 trillion). Headline notional figures can dramatically overstate counterparty risk. Net market value and credit exposure are the meaningful risk metrics.",
        ["BIS", "ISDA"],
        indications=["Derivatives"], category="Instruments"),

    entry("Underlying", "Underlying Asset",
        "Asset or reference rate a derivative is based on — drives the derivative's price.",
        "Could be a single stock (Apple), an index (S&P 500), a currency pair (EUR/USD), a commodity (WTI), a rate (SOFR), or even another derivative (option on a future). Defines the contract's economics and Greeks. Derivatives draw their name from being 'derived' from underlying prices. Crypto derivatives use cryptocurrencies as underlyings; weather derivatives reference temperature or rainfall indices.",
        ["ISDA", "CME Group"],
        indications=["Derivatives"], category="Instruments"),

    entry("Strike Price", "Exercise Price",
        "Price at which an option holder can buy (call) or sell (put) the underlying.",
        "Set at trade inception. Determines moneyness: a call with strike below current price is in-the-money; above is out-of-the-money. Listed options trade at standardised strikes — typically integer dollar increments for cheap stocks, larger gaps for expensive ones. Index options strike in 5- or 25-point increments. OTC options can use any strike negotiated between counterparties.",
        ["CBOE", "ISDA"],
        indications=["Derivatives"], category="Pricing & Valuation"),

    entry("Expiration", "Expiry",
        "Date an option or futures contract ends — last day to trade or exercise.",
        "Standard monthly options expire third Friday of expiration month. Weeklies expire every Friday; SPX has daily expirations now. Futures expire at varying dates (third Friday for many indexes, mid-month for commodities). 'Triple witching' is the quarterly Friday when index options, index futures, and single-stock options all expire together — produces unusual hedging flows and intraday volatility.",
        ["CBOE", "CME Group"],
        indications=["Derivatives"], category="Instruments"),

    entry("American Option", "",
        "Option exercisable any time up to and including expiration.",
        "Standard for single-stock equity options (most listed options on US stocks). Early exercise rarely optimal — typically only justified by dividends (for calls) or deep in-the-money status (for puts on illiquid names). American options can be valued via binomial trees or finite-difference methods; closed-form solutions don't exist. The name has nothing to do with geography.",
        ["CBOE", "CFA Institute"],
        indications=["Derivatives"], category="Instruments"),

    entry("European Option", "",
        "Option exercisable only at expiration — no early exercise.",
        "Standard for index options (SPX, RUT, etc.) and most OTC FX options. Simpler to value than American options — Black-Scholes assumes European exercise. Avoids the assignment risk that complicates American option positions. Most exotic options (barriers, digitals, Asians) are European-style. The 'European' label is convention, not geographic.",
        ["CBOE", "CFA Institute"],
        indications=["Derivatives"], category="Instruments"),

    entry("Bermudan Option", "",
        "Option exercisable on a set of pre-specified dates — between European and American.",
        "Common for OTC swaptions (the right to enter a swap) and callable bonds (issuer's embedded option). 'Bermudan' because it sits between European (one date) and American (every date). Pricing uses backwards-induction through the exercise dates. Issuer-callable corporate bonds and mortgage callability are economically Bermudan options.",
        ["ISDA"],
        indications=["Derivatives"], category="Instruments"),

    entry("Intrinsic Value", "",
        "Amount an option would be worth if exercised immediately — current price minus strike (for calls).",
        "A call with strike 100 when the stock is at 110 has intrinsic value of 10 dollars per share, regardless of time to expiry. Puts: strike minus stock price (if positive). Out-of-money options have zero intrinsic value. Option premium equals intrinsic plus time value. As expiry approaches, time value decays to zero, leaving only intrinsic.",
        ["CBOE", "CFA Institute"],
        indications=["Derivatives"], category="Pricing & Valuation"),

    entry("Time Value", "Extrinsic Value",
        "Option premium beyond intrinsic value — captures uncertainty and remaining time to expiry.",
        "An ATM option has zero intrinsic value; all its premium is time value. Decays through theta as expiry approaches. Time value is largest for at-the-money options (highest uncertainty about whether they'll end in-money). Time value depends on implied volatility, time to expiry, interest rates, and dividend expectations. Falls to zero precisely at expiry.",
        ["CBOE", "CFA Institute"],
        indications=["Derivatives"], category="Pricing & Valuation"),

    entry("In-The-Money", "ITM",
        "Option that would have intrinsic value if exercised now.",
        "Call with strike below current price; put with strike above current price. Deep ITM options have high delta (close to 1.0 for calls, -1.0 for puts) and behave nearly like the underlying. Most option exercise activity concentrates on ITM options near expiry. Distinguished from ATM (near current price) and OTM (out-of-money).",
        ["CBOE"],
        indications=["Derivatives"], category="Pricing & Valuation"),

    entry("Out-Of-The-Money", "OTM",
        "Option with no intrinsic value — all premium is time value.",
        "Call with strike above current price; put with strike below. Cheapest options but low probability of profit. Lottery-ticket appeal drives heavy retail trading of OTM options, especially short-dated calls in meme stocks. Far OTM options are sometimes called 'tail-risk hedges' — small premium for large payoff in extreme moves. Probability-weighted expected value of OTM options is typically negative.",
        ["CBOE"],
        indications=["Derivatives"], category="Pricing & Valuation"),

    entry("At-The-Money", "ATM",
        "Option struck close to the current price of the underlying.",
        "Strictly: strike equals spot. Loosely: strike within a small range of spot. ATM options have the highest time value, highest gamma, and roughly 0.5 delta (or -0.5 for puts). Most option volume concentrates in at-the-money and just-out-of-money strikes. ATM volatility is the headline implied-vol number quoted for any expiry.",
        ["CBOE"],
        indications=["Derivatives"], category="Pricing & Valuation"),

    entry("Moneyness", "",
        "Relationship between an option's strike and the underlying's current price.",
        "Categories: deep ITM, ITM, ATM, OTM, deep OTM. Quantitative moneyness: K/S (strike over spot) or ln(K/S). Vol surfaces are quoted by moneyness — at fixed-strike points (25-delta, 50-delta, etc.) rather than fixed prices, so the smile shape persists as the underlying moves. Important concept for any option-pricing or strategy discussion.",
        ["CBOE", "ISDA"],
        indications=["Derivatives"], category="Pricing & Valuation"),

    entry("Black-Scholes", "Black-Scholes-Merton",
        "Foundational option-pricing model — risk-neutral valuation via Brownian-motion underlying.",
        "Published 1973 by Fischer Black and Myron Scholes; extended by Robert Merton. Scholes and Merton won the 1997 Nobel Prize (Black died in 1995). Assumes log-normal returns, constant volatility, no dividends, continuous trading, risk-free rate hedging. Real markets violate every assumption — but the framework persists as the canonical reference. Implied volatility is the 'fudge factor' that lets traders use the model despite its flaws.",
        ["CFA Institute", "CME Group"],
        indications=["Derivatives"], category="Quantitative"),

    entry("Greeks", "Option Greeks",
        "Risk sensitivities of an option's price — delta, gamma, vega, theta, rho.",
        "Greek letters used (not all are actually Greek): Delta, Gamma, Theta, Vega (not Greek — letter resembling V), Rho. Higher-order Greeks: Charm, Vanna, Volga, Zomma. Traders manage option books by Greeks rather than individual position P&Ls. Dealers hedge delta continuously (delta-neutral books), then manage gamma and vega exposures within risk limits. The Greeks aggregate across positions in a portfolio.",
        ["CFA Institute", "ISDA"],
        indications=["Derivatives"], category="Risk"),

    entry("Hedge Ratio", "",
        "Number of hedging instruments needed to offset a position's risk.",
        "For a single option: delta tells you how many units of underlying to hold to offset price risk. For a portfolio: gamma-vega ratios determine cross-hedges. Pension funds running LDI use duration-matching hedge ratios; commodity producers calculate barrels-hedged ratios. Imperfect hedging — basis risk between hedge instrument and underlying exposure — limits how much risk can be neutralised.",
        ["CFA Institute"],
        indications=["Derivatives"], category="Risk"),

    entry("Initial Margin", "IM",
        "Collateral posted at trade inception — covers potential future exposure.",
        "Required by clearing houses (CME, LCH, ICE) and bilateral counterparties (under post-2008 IM rules). Calculated using historical-simulation VaR or SIMM (the ISDA standard initial-margin model). Typically 5-10 percent of notional for swaps, higher for volatile or longer-dated trades. Held in the counterparty's name in segregated accounts. Returned at trade termination minus variation margin movements.",
        ["ISDA", "LCH", "CME Group"],
        indications=["Derivatives"], category="Settlement & Operations"),

    entry("Variation Margin", "VM",
        "Daily cash flows that settle the change in derivative mark-to-market.",
        "If a swap's value falls 100,000 dollars on a given day, the counterparty owes 100,000 in variation margin. Settled in cash or eligible collateral (Treasuries, often) every business day. Eliminates counterparty risk on existing P&L. Cleared swaps post VM through clearing houses; bilateral swaps via CSA. The 2008 AIG failure was triggered by VM calls AIG couldn't meet.",
        ["ISDA", "LCH"],
        indications=["Derivatives"], category="Settlement & Operations"),

    entry("Mark-to-Market", "MTM",
        "Daily revaluation of a position at current market prices — produces unrealised P&L.",
        "Standard for futures, cleared swaps, and most bilateral derivatives under CSAs. Daily MTM moves drive variation margin calls. Held-for-trading accounting (FAS 157, IFRS 13) requires MTM for derivative positions on balance sheets. Banks and broker-dealers MTM all trading-book derivatives daily. Distinct from mark-to-model, where complex products use modelled prices when market quotes don't exist.",
        ["SEC", "BIS"],
        indications=["Derivatives"], category="Settlement & Operations"),

    entry("Novation", "",
        "Transfer of a derivative trade to a new counterparty — replaces the original contract.",
        "Used in bilateral derivative compression cycles to reduce gross exposures, and to migrate trades to central clearing post-Dodd-Frank. Original counterparty needs consent to novate. The new counterparty steps fully into the trade's economics. ISDA published novation protocols to standardise the process. Each clearing-eligible OTC swap that came on after 2014 was effectively novated to a clearing house.",
        ["ISDA", "LCH"],
        indications=["Derivatives"], category="Settlement & Operations"),

    entry("ISDA Master Agreement", "",
        "Industry-standard bilateral contract governing OTC derivatives between two parties.",
        "Includes the main agreement, schedule (with party-specific elections), CSA (collateral), and confirmations (for each trade). First version 1992; current 2002 form. Provides netting (close-out under default), events of default, and termination provisions. Without an ISDA, OTC derivatives would face vast counterparty risk and operational chaos. Roughly 250,000 active ISDA Master Agreements globally.",
        ["ISDA"],
        indications=["Derivatives"], category="Settlement & Operations"),

    entry("CSA", "Credit Support Annex",
        "ISDA annex governing collateral posting — eligible types, thresholds, and timing.",
        "Specifies eligible collateral (typically cash plus Treasuries), thresholds below which no collateral is posted, minimum transfer amounts, and dispute resolution. Daily MTM produces collateral movements under CSA terms. Sophisticated CSAs differentiate between currency, tenor, and asset class. The post-2016 'IM Big Bang' rolled out two-way initial margin requirements for non-cleared derivatives across major asset managers, banks, and corporates.",
        ["ISDA"],
        indications=["Derivatives"], category="Settlement & Operations"),

    entry("Cleared vs Bilateral", "Cleared OTC",
        "Cleared derivatives settle through a central counterparty; bilateral settle directly between parties.",
        "Dodd-Frank and EMIR mandated clearing for most standardised IRS and CDS post-2012. Clearing concentrates counterparty risk in clearing houses (LCH, CME, ICE), backed by member default-funds and initial margin. Bilateral trades use ISDA Master Agreement plus CSA collateral. Cleared trades benefit from netting across all clearing-house members. Most new OTC swap volume is cleared; exotic and non-standardised trades remain bilateral.",
        ["LCH", "CME Group", "ISDA"],
        indications=["Derivatives"], category="Settlement & Operations"),

    entry("Compression", "Trade Compression",
        "Process that nets offsetting derivative trades — reduces gross notional without changing net risk.",
        "Run by TriOptima and other providers in cycles across cleared and bilateral books. Pre-2008 derivatives notional outstanding compressed dramatically post-crisis — global IRS notional fell from over 500 trillion peak to roughly 400 trillion as duplicate trades got terminated. Reduces leverage ratio drag, operational risk, and balance-sheet usage. Routine for banks active in cleared swap markets.",
        ["ISDA", "LCH"],
        indications=["Derivatives"], category="Settlement & Operations"),
]


# ============================================================================
# BATCH 13 — Derivatives exotics & quant (25 terms — barriers, autocallables, vol models)
# ============================================================================

BATCH_DERIV_EXOTICS = [
    entry("Barrier Option", "",
        "Option that activates or extinguishes if the underlying crosses a barrier level.",
        "Four flavours: knock-in (activates on touch), knock-out (extinguishes on touch), up-and-in, down-and-out. Cheaper than vanilla options because part of the time the holder doesn't own anything. Heavily used in structured products and FX hedging. Pricing handles path-dependence — analytical solutions for some types, Monte Carlo for others. Barrier breaches in stressed markets create discontinuous payoff jumps that hedgers fear.",
        ["ISDA", "CFA Institute"],
        indications=["Derivatives"], category="Instruments"),

    entry("Knock-In", "KI",
        "Barrier feature — option only activates if the underlying touches a specified level.",
        "A down-and-in put activates only if the stock falls to a trigger level. Buyer pays less upfront because there's a chance the barrier is never hit and the option expires worthless. Common in retail structured notes ('memory autocallable with KI') — investor sells a knock-in put implicitly. The 2008 collapse triggered massive KI activations as equities plunged through barriers en masse.",
        ["ISDA"],
        indications=["Derivatives"], category="Instruments"),

    entry("Knock-Out", "KO",
        "Barrier feature — option terminates if the underlying touches a specified level.",
        "An up-and-out call extinguishes if the stock rallies above a ceiling. Holder gets normal call payoff up to the KO level, nothing if breached. Cheaper than vanilla calls because the upside is capped. Used in cost-reducing hedges and structured notes. The barrier creates pin risk and gap-risk near the level — dealers struggle to hedge KO options as the underlying approaches the trigger.",
        ["ISDA"],
        indications=["Derivatives"], category="Instruments"),

    entry("Asian Option", "Average-Rate Option",
        "Option whose payoff depends on the average price of the underlying over a period — not the final price.",
        "Common in commodity hedging (averages match physical exposure over a delivery period), FX hedging (smooths out month-end rate spikes), and structured products. Average can be arithmetic or geometric, fixed-strike or floating-strike. Lower premiums than vanilla options because averaging dampens volatility. Asian options got their name because they were popularised in Tokyo trading in the 1980s.",
        ["ISDA"],
        indications=["Derivatives"], category="Instruments"),

    entry("Digital Option", "Binary Option",
        "Option that pays a fixed amount if the underlying finishes above (or below) the strike — zero otherwise.",
        "All-or-nothing payoff. A digital call on AAPL with 200 strike pays 1 dollar if AAPL ends above 200, zero otherwise. Cheap to buy, easy to understand, popular in structured products. The retail 'binary option' craze (2010s) saw widespread fraud — regulators (FCA, ASIC) banned retail binaries. Institutional digital options remain legitimate but cleared through OTC channels with regulated counterparties.",
        ["FCA", "ESMA"],
        indications=["Derivatives"], category="Instruments"),

    entry("Lookback Option", "",
        "Option whose payoff depends on the most favourable price reached over the contract life.",
        "Fixed-strike lookback call pays the maximum stock price minus strike. Floating-strike lookback pays the final price minus the minimum observed. Eliminates regret — holder buys at the lowest and sells at the highest. Expensive premiums reflect that desirable feature. Rare in vanilla markets; common in structured notes targeting retail or wealth-management investors who like the 'no regret' narrative.",
        ["ISDA"],
        indications=["Derivatives"], category="Instruments"),

    entry("Quanto", "Quanto Option",
        "Option on a foreign-currency asset that pays in a different currency at a fixed exchange rate.",
        "A USD-paying option on the Nikkei 225 is a quanto — Japanese-yen index, dollar payoff. Investor gets index exposure without yen exposure. Pricing accounts for the correlation between the underlying and the FX rate — a parameter that's harder to estimate than vol alone. Common in structured notes sold to retail investors wanting foreign-equity exposure without FX risk.",
        ["ISDA", "BIS"],
        indications=["Derivatives", "FX"], category="Instruments"),

    entry("Auto-callable", "Autocall",
        "Structured note that gets early-redeemed if the underlying is at or above an observation level on coupon dates.",
        "Pays a fixed coupon if the underlying is above the call barrier on observation dates; otherwise rolls forward, potentially with memory of unpaid coupons. If the underlying falls below a knock-in barrier, the investor takes equity-like downside at maturity. Massive product class in Europe and Asia — over 500 billion outstanding globally. Investor effectively sells volatility and downside risk for an enhanced coupon.",
        ["ISDA", "SEC"],
        indications=["Derivatives", "Equities"], category="Instruments"),

    entry("Range Accrual", "",
        "Structured product that accrues coupon for each day the underlying stays within a range.",
        "If the reference rate (often LIBOR replacement) stays between a floor and ceiling on a given day, the coupon accrues; otherwise the day's coupon is zero. Embedded short option on volatility — investor profits if the rate stays inside the range. Popular as yield-enhancement during low-rate periods. Risk: rate gaps outside the range during volatility spikes, coupon accrual goes to zero, principal can be at risk.",
        ["ISDA"],
        indications=["Derivatives"], category="Instruments"),

    entry("Heston Model", "",
        "Stochastic-volatility option-pricing model — vol follows its own random process.",
        "Published 1993 by Steven Heston. Volatility mean-reverts and is correlated with the underlying. Better captures vol smile dynamics than Black-Scholes. Parameters: long-run vol, mean-reversion speed, vol-of-vol, correlation. Heston has a semi-closed-form solution via Fourier transform, making it tractable for calibration. Standard reference in derivatives quant interviews; widely used in production option-pricing engines.",
        ["CFA Institute"],
        indications=["Derivatives"], category="Quantitative"),

    entry("SABR Model", "",
        "Stochastic Alpha-Beta-Rho model — industry standard for interest-rate vol smile fitting.",
        "Published 2002 by Hagan, Kumar, Lesniewski, Woodward. Four parameters (alpha, beta, rho, nu) fit the smile shape. Beta controls the underlying dynamics (between normal and lognormal); rho is correlation between underlying and vol; nu is vol-of-vol. Approximate closed-form solution makes calibration fast. The de facto standard for interest-rate-derivative vol modelling, especially swaptions and caps/floors.",
        ["CFA Institute"],
        indications=["Derivatives", "Rates"], category="Quantitative"),

    entry("Local Volatility", "Dupire Model",
        "Vol model where instantaneous volatility is a deterministic function of underlying price and time.",
        "Published 1994 by Bruno Dupire. Calibrates exactly to any observed vol surface by construction — solves the inverse problem from market option prices. Used widely for pricing path-dependent derivatives (barriers, lookbacks) where exact vol-surface fit matters. Criticised for unrealistic forward vol dynamics — local vol typically forecasts the smile to flatten over time, which doesn't match real-world behaviour.",
        ["CFA Institute"],
        indications=["Derivatives"], category="Quantitative"),

    entry("Stochastic Volatility", "",
        "Class of models where volatility follows its own random process, separate from the underlying.",
        "Heston, SABR, and others are stochastic-vol models. Capture vol smile and term-structure dynamics that local-vol models miss. Trade-off: more parameters to calibrate, more computational cost. Hybrid local-stochastic vol (LSV) models combine the calibration-fit of local vol with the realistic dynamics of stochastic vol. Standard in modern exotic-options desks.",
        ["CFA Institute"],
        indications=["Derivatives"], category="Quantitative"),

    entry("Jump Diffusion", "Merton Jump Model",
        "Model adding sudden price jumps to standard diffusion — captures fat-tail returns.",
        "Robert Merton's 1976 model. Stock price follows geometric Brownian motion plus a Poisson jump process. Captures crash risk that Black-Scholes misses. Out-of-money option prices in jump-diffusion models are higher than Black-Scholes, matching observed market smiles. Popular in credit modelling (sudden defaults) and FX (currency-crisis jumps). Calibration is harder than pure diffusion.",
        ["CFA Institute"],
        indications=["Derivatives"], category="Quantitative"),

    entry("Monte Carlo Simulation", "",
        "Numerical method that prices derivatives by simulating thousands of possible underlying paths.",
        "Generate many random paths consistent with the model dynamics, calculate the derivative's payoff on each, average to get the price. Indispensable for path-dependent options (Asians, barriers, lookbacks) where no closed form exists. Variance-reduction techniques (antithetic variates, control variates, importance sampling) speed up convergence. GPUs and quasi-random sequences (Sobol) make Monte Carlo tractable for production pricing.",
        ["CFA Institute"],
        indications=["Derivatives"], category="Quantitative"),

    entry("Binomial Tree", "Cox-Ross-Rubinstein",
        "Discrete option-pricing model — underlying moves up or down each timestep with assigned probabilities.",
        "Published 1979. Build the tree of possible price paths backward from expiry, computing option value at each node. Handles American exercise naturally (compare hold vs exercise at each node). Converges to Black-Scholes as timesteps approach infinity. Used heavily for teaching and for callable-bond pricing. Trinomial trees (three branches per step) converge faster and handle some path-dependent products better.",
        ["CFA Institute"],
        indications=["Derivatives"], category="Quantitative"),

    entry("Risk-Neutral Probability", "",
        "Adjusted probability under which all assets earn the risk-free rate — used for option pricing.",
        "Not the actual probability of events — it's the probability that makes derivative prices consistent with no-arbitrage. The risk-neutral expected discounted payoff equals today's option price. Implied probabilities can be back-solved from option market prices to get the 'risk-neutral density' of future prices. Used in event-trading (binary outcomes) and as a market-implied probability gauge.",
        ["CFA Institute"],
        indications=["Derivatives"], category="Quantitative"),

    entry("Martingale", "",
        "Stochastic process whose expected future value equals its current value.",
        "Foundational concept in derivative pricing. Under the right probability measure (risk-neutral measure), discounted asset prices are martingales — no arbitrage exists. Pricing a derivative reduces to computing the expected discounted payoff under the martingale measure. Martingale theory underpins the entire mathematical framework of modern finance, from Black-Scholes to forward measures used in interest-rate modelling.",
        ["CFA Institute"],
        indications=["Derivatives"], category="Quantitative"),

    entry("Numeraire", "",
        "Reference asset against which other assets are priced — usually a risk-free bond or money-market account.",
        "Change-of-numeraire technique lets quants switch the reference asset to simplify pricing problems. Forward-measure pricing uses a zero-coupon bond as numeraire — handy for interest-rate options. Risk-neutral pricing uses the money-market account. Choosing the right numeraire can turn a hard pricing problem into a manageable one. Standard tool in advanced derivatives quant work.",
        ["CFA Institute"],
        indications=["Derivatives"], category="Quantitative"),

    entry("Calibration", "Model Calibration",
        "Process of fitting model parameters to observed market prices.",
        "Daily for option-pricing desks: load market quotes for vanilla options across strikes and tenors, solve for the model parameters that minimise pricing errors. Calibration accuracy determines exotic-option pricing quality. Local-vol models calibrate exactly to vanillas; stochastic-vol models trade exact fit for better dynamics. Volatility-surface arbitrage exploits calibration errors between desks.",
        ["CFA Institute"],
        indications=["Derivatives"], category="Quantitative"),

    entry("Vanna", "",
        "Second-order Greek — sensitivity of delta to changes in implied volatility.",
        "Captures the interaction between delta and vega. Important for options near the wings (far OTM) where vol moves dramatically shift the delta. Quants manage vanna exposure when running large vol books. Vanna-Volga adjustment is a common FX option-pricing add-on that corrects Black-Scholes for smile effects using vanna and volga.",
        ["CFA Institute", "ISDA"],
        indications=["Derivatives"], category="Risk"),

    entry("Volga", "Vomma",
        "Second-order Greek — sensitivity of vega to changes in implied volatility.",
        "Measures the curvature of option price in implied vol. Long-volga positions benefit from vol-of-vol moves (vol spiking from 10 to 30 more than offsets vol grinding back from 30 to 10). Important for ATM options far from expiry and for vol books. Vanna and volga are the two main 'second-order vol Greeks' that vol traders track alongside vega.",
        ["CFA Institute"],
        indications=["Derivatives"], category="Risk"),

    entry("Cliquet", "Ratchet Option",
        "Series of forward-starting options — locks in periodic gains.",
        "Each leg resets the strike at the beginning of its period. Used in structured products as 'ratcheted' return profiles — investor locks in gains period-by-period without giving them back. The 1999 LTCM-era cliquet craze created huge vol-surface exposures that surfaced losses for dealers during the 2000 vol spike. Now standard in equity structured products and exotic FX hedges.",
        ["ISDA"],
        indications=["Derivatives"], category="Instruments"),

    entry("Path Dependence", "",
        "Derivative whose payoff depends on the underlying's price history, not just the final value.",
        "Asian options (averaging), lookbacks (extreme values), barriers (touching levels), autocallables (intermediate observations) all path-dependent. Cannot be priced with simple Black-Scholes; needs Monte Carlo, finite-difference, or tree methods. Path-dependent payoffs are central to structured-product engineering — they let issuers create payoff profiles that can't be replicated with vanilla options.",
        ["ISDA", "CFA Institute"],
        indications=["Derivatives"], category="Quantitative"),

    entry("Variance Risk Premium", "VRP",
        "Difference between implied volatility and subsequently realised volatility.",
        "Usually positive: implied vol trades above realised vol on average. Volatility sellers (selling options or variance swaps) capture this premium over time, with occasional crash losses. VRP collapses or inverts during stress — 2008, 2020, 2022 all saw realised vol exceed prior implied vol by wide margins. CBOE's VIX index versus subsequent S&P realised vol is the canonical VRP series.",
        ["CBOE", "CFA Institute"],
        indications=["Derivatives"], category="Pricing & Valuation"),
]


# ============================================================================
# BATCH 14 — Market microstructure (25 terms — order types, venues, HFT, market abuse)
# ============================================================================

BATCH_MICROSTRUCTURE = [
    entry("Order Book", "Limit Order Book",
        "Real-time list of all outstanding buy and sell orders at each price level.",
        "Continuous double auction: limit orders rest at their prices, market orders cross immediately. Top of book is the best bid and best offer (NBBO in US equities). Depth measures resting orders at and behind the top — thinner book means more impact for large trades. Order-book data is the raw material for HFT, market-making, and execution algos. Most exchanges publish via direct feeds and consolidated feeds.",
        ["SEC", "NYSE", "Nasdaq"],
        indications=["Cross-asset"], category="Market Structure"),

    entry("Limit Order", "",
        "Order to buy at or below a specified price, or sell at or above — won't fill at worse prices.",
        "Adds liquidity to the order book. Won't execute if the limit price isn't reached. Used by patient traders, market-makers (passive quotes), and execution algos. Day-trader-popular for entry/exit at specific levels. The complement to market orders (which take liquidity). Most retail order types behind the scenes are limit orders, even when entered as 'market' (broker adds protective limits).",
        ["SEC", "NYSE"],
        indications=["Cross-asset"], category="Trading & Execution"),

    entry("Market Order", "",
        "Order to buy or sell immediately at the best available price.",
        "Crosses the spread, takes liquidity. Fills at NBBO (or worse if the order is large enough to walk the book). Fast and certain execution but can produce surprising fills in thin markets — Knight Capital's 2012 algo bug placed billions in market orders, draining the book and bankrupting the firm. Modern brokers convert market orders into protected limit orders to prevent egregious fills.",
        ["SEC", "FINRA"],
        indications=["Cross-asset"], category="Trading & Execution"),

    entry("Stop Order", "",
        "Order that becomes a market order once a trigger price is touched.",
        "Stop-buy triggers above the current price; stop-sell (stop-loss) triggers below. Used to enter on breakouts or exit losing positions automatically. Stop orders aren't visible in the order book — they convert to market orders only on trigger. The May 2010 Flash Crash was amplified by stop-loss cascades — once prices started falling, stops triggered into thin liquidity, accelerating the rout.",
        ["SEC", "FINRA"],
        indications=["Cross-asset"], category="Trading & Execution"),

    entry("Iceberg Order", "Hidden Quantity",
        "Large order that displays only a small portion of its size at any time — the rest is hidden.",
        "Common in equity and futures markets. Visible 'tip' replenishes when filled. Disguises large orders from front-runners and information leakage. Time priority is sometimes preserved at the same price for the hidden portion; varies by venue. Used by institutional investors and algos to work large orders without alarming the market.",
        ["SEC"],
        indications=["Cross-asset"], category="Trading & Execution"),

    entry("Time-in-Force", "TIF",
        "Order parameter specifying how long an order stays active.",
        "GTC (Good-Till-Cancelled), DAY (cancel at session close), IOC (Immediate-or-Cancel — fill what you can, cancel rest), FOK (Fill-or-Kill — all or nothing). Different markets and broker platforms offer varying TIF options. Algos use IOC heavily to probe for liquidity at multiple venues. Retail traders mostly use DAY orders implicitly.",
        ["NYSE", "Nasdaq"],
        indications=["Cross-asset"], category="Trading & Execution"),

    entry("NBBO", "National Best Bid and Offer",
        "Highest bid and lowest offer across all US equity venues — the consolidated 'top of book'.",
        "Established under Reg NMS. SIPs (Securities Information Processors) consolidate quotes from all venues into the NBBO. Broker-dealers must execute customer orders at NBBO or better — the trade-through rule. Direct exchange data feeds are faster than SIPs, giving HFT firms a milliseconds-level edge that retail traders don't see. The 2010 Flash Crash exposed weaknesses in NBBO during stress.",
        ["SEC", "FINRA"],
        indications=["Equities"], category="Market Structure"),

    entry("Reg NMS", "Regulation National Market System",
        "SEC framework that ties together US equity venues into a single national market.",
        "Adopted 2005, implemented 2007. Core rules: Order Protection Rule (trade-throughs banned at protected prices), Access Rule (fair access to quotes), Sub-Penny Rule, Market Data Rules. Created the patchwork of competing exchanges (NYSE, Nasdaq, BATS, IEX, etc.) connected by SIPs. Now under SEC review — proposals to update market-data infrastructure and tick sizes for 2024-25.",
        ["SEC"],
        indications=["Equities"], category="Regulation"),

    entry("Tick Size", "",
        "Minimum price increment a security can trade at.",
        "Most US stocks above 1 dollar trade in penny ticks (0.01 dollar). Sub-penny tick proposals (0.005, 0.001) periodically debated. Smaller ticks tighten spreads but reduce displayed liquidity (incentive to post resting orders shrinks). Futures and options have venue-specific tick sizes — SPX options in 0.05 dollar, ES in 0.25 index points. SEC's 2024 tick-size reforms reduce some pilot stocks to half-penny ticks.",
        ["SEC", "FINRA"],
        indications=["Equities"], category="Market Structure"),

    entry("Price Discovery", "",
        "Process by which markets determine fair prices through order flow.",
        "Driven by the aggregate of buying and selling decisions reflecting traders' information and expectations. Lit venues (exchanges) contribute more to price discovery than dark pools (which don't display quotes). Periods of stressed price discovery — when prices move on thin volume — produce wider spreads and bigger price gaps. The 2020 March pandemic week saw extreme price-discovery stress across asset classes.",
        ["SEC", "NYSE"],
        indications=["Cross-asset"], category="Market Structure"),

    entry("Best Execution", "",
        "Broker's duty to seek the most favourable terms reasonably available for customer orders.",
        "Codified in FINRA Rule 5310 and MiFID II (Europe). Factors: price, speed, likelihood of execution, settlement, total transaction cost. Broker reports (Rule 605/606 in US, RTS 27/28 in Europe) disclose execution quality publicly. Best-execution standards have intensified with retail commission compression and order-flow-payment scrutiny. Robinhood and others have faced regulatory action over PFOF-induced execution-quality concerns.",
        ["FINRA", "SEC", "FCA"],
        indications=["Cross-asset"], category="Regulation"),

    entry("Dark Pool", "",
        "Trading venue where orders are not publicly displayed — large blocks cross without market impact.",
        "Operated by banks (Credit Suisse Crossfinder, Morgan Stanley MS Pool), exchanges (NYSE Block, Nasdaq), and independent operators (Liquidnet, Investment Technology Group). Dark pools represent roughly 12-15 percent of US equity volume. Trade prints to consolidated tape with a delay; quotes don't show on order books. Critics argue dark pools fragment price discovery; supporters cite reduced market impact for institutional orders.",
        ["SEC", "FINRA"],
        indications=["Equities"], category="Market Structure"),

    entry("Lit Market", "Lit Venue",
        "Trading venue with publicly displayed quotes — opposite of dark pool.",
        "NYSE, Nasdaq, NYSE Arca, BATS, IEX, CHX are the major US lit exchanges. Contribute to price discovery via visible order book. Required to publish quotes in real-time to SIPs. Make money from trading fees and market-data fees. Reg NMS protects displayed quotes at lit venues from trade-throughs by routing orders to the best price.",
        ["SEC", "NYSE", "Nasdaq"],
        indications=["Equities"], category="Market Structure"),

    entry("Latency", "",
        "Time delay between an event (price tick, news release) and a system's response.",
        "Measured in microseconds and nanoseconds in HFT. Sources of latency: physical distance (light-speed limit), network hops, processing time, exchange matching engines. Co-location facilities reduce latency by placing trader servers next to exchange match engines. Microwave radio links between major financial centres (NYC-Chicago, London-Frankfurt) are faster than fibre — significant infrastructure investment for HFT firms.",
        ["NYSE", "Nasdaq"],
        indications=["Cross-asset"], category="Market Structure"),

    entry("Co-location", "",
        "Placing trading servers in the same data centre as the exchange matching engine.",
        "Reduces network latency from milliseconds to microseconds. NYSE Mahwah, Nasdaq Carteret, CME Aurora are the major co-location sites. Costs tens of thousands of dollars per month per cabinet. HFT firms invest heavily in co-location plus FPGA hardware to minimise tick-to-trade latency. Regulators have raised fairness concerns but allow co-location as standard practice.",
        ["NYSE", "Nasdaq", "CME Group"],
        indications=["Cross-asset"], category="Market Structure"),

    entry("HFT", "High-Frequency Trading",
        "Algorithmic trading strategies relying on speed — typically holding positions for milliseconds to minutes.",
        "Roughly half of US equity volume. Strategies: market-making (Citadel Securities, Virtu), latency arbitrage (Hudson River Trading), statistical arbitrage (Two Sigma, Renaissance). Profitability has compressed as competition has scaled — HFT industry revenues fell from peaks of 7 billion in 2009 to roughly 1.5 billion in recent years. Maker-taker fee rebates and exchange data fees are substantial cost components.",
        ["SEC", "FINRA"],
        indications=["Cross-asset"], category="Market Structure"),

    entry("Spoofing", "",
        "Illegal practice of placing orders with no intent to execute — to mislead other traders about supply or demand.",
        "Banned under Dodd-Frank. The 2010 Flash Crash trader Navinder Sarao was convicted of spoofing E-mini S&P futures. JPMorgan paid 920 million in 2020 to settle CFTC and SEC spoofing charges related to its precious metals desk. Detection algorithms (cancelled orders relative to executed orders, patterns of one-sided pressure followed by reversal) identify suspicious behaviour for regulators.",
        ["CFTC", "SEC"],
        indications=["Cross-asset"], category="Regulation"),

    entry("Layering", "",
        "Form of spoofing — placing multiple orders on one side of the book to create false depth.",
        "Trader places visible orders to make a stock look heavily bid (or offered), inducing other traders to react, then cancels and trades the opposite direction. The 2014 Coscia case was the first US criminal conviction for layering. Major banks have settled layering cases across spot FX, precious metals, Treasuries. Surveillance algorithms now detect layering patterns automatically across asset classes.",
        ["CFTC", "FINRA"],
        indications=["Cross-asset"], category="Regulation"),

    entry("Front-Running", "",
        "Illegally trading ahead of a client order with knowledge of the client's intent.",
        "Banned under SEC rules and FINRA conduct rules. Modern HFT firms are often accused of latency-based front-running — detecting incoming retail orders from broker order-flow payments and trading ahead. Distinct from anticipating market direction based on public information. Several settlements (Citadel Securities, Robinhood) involved disputed front-running allegations around payment for order flow.",
        ["SEC", "FINRA"],
        indications=["Cross-asset"], category="Regulation"),

    entry("Wash Trade", "",
        "Trade where the same party is both buyer and seller — artificially inflates volume without economic substance.",
        "Banned under exchange rules. Sometimes attempted to game volume-based metrics (tape painting), or to create misleading impressions of liquidity in thin markets. Crypto exchanges have been particularly criticised for wash trading prior to regulation. Detection: cross-trades between affiliated accounts, near-simultaneous opposing orders. Exchanges run surveillance algorithms to flag wash trades for compliance review.",
        ["CFTC", "SEC"],
        indications=["Cross-asset"], category="Regulation"),

    entry("Market Maker", "",
        "Firm continuously quoting two-way prices in a security — provides liquidity for a small spread.",
        "Citadel Securities, Virtu, Susquehanna, Jane Street are major equity market-makers. Bank desks make markets in fixed-income, FX, and OTC derivatives. Profitability: capture half-spread on trades, plus exchange rebates (maker rebates in maker-taker fee schedules). Risk: inventory accumulation, adverse selection (informed traders consistently pick off market-makers). Required liquidity providers in many designated-market-maker arrangements.",
        ["NYSE", "Nasdaq", "SEC"],
        indications=["Cross-asset"], category="Market Structure"),

    entry("Designated Market Maker", "DMM",
        "NYSE-listed firm formally responsible for facilitating trading in specific stocks.",
        "Replaced the legacy NYSE specialist role in 2008. DMMs provide opening and closing auction prices, supply liquidity during stress, and step in when buy-sell imbalances arise. Major DMMs: GTS, Citadel Securities, Virtu, IMC. Earn rebates and modest privileged access in exchange for liquidity obligations. The Nasdaq equivalent is the Market Maker firm assigned to each Nasdaq stock.",
        ["NYSE"],
        indications=["Equities"], category="Market Structure"),

    entry("PFOF", "Payment for Order Flow",
        "Broker receives compensation from market-makers for routing retail orders to them.",
        "Standard practice in US retail equity and options trading. Robinhood made it famous (and controversial). Critics argue it conflicts with best-execution duties; supporters note it enables zero-commission trading. UK's FCA banned PFOF in 2012; EU restrictions tightened in 2024. SEC adopted Reg NMS updates in 2023 to improve disclosure but didn't ban PFOF. Annual PFOF revenue across US brokers approached 4 billion dollars in peak years.",
        ["SEC", "FCA", "FINRA"],
        indications=["Cross-asset"], category="Regulation"),

    entry("Flash Crash", "",
        "Sudden, brief, severe market plunge followed by rapid recovery.",
        "Most famous: May 6, 2010 — Dow Jones fell 1,000 points (9 percent) in minutes, recovered most losses within 30 minutes. Triggered by an algo selling E-mini futures into thin liquidity, amplified by HFT liquidity withdrawal and stop-loss cascades. Subsequent flash crashes hit Treasury yields (October 2014), Swiss franc (January 2015), British pound (October 2016), and gold. Limit Up Limit Down rules and circuit breakers reduce but don't eliminate.",
        ["SEC", "CFTC"],
        indications=["Cross-asset"], category="Risk"),

    entry("Circuit Breaker", "Trading Halt",
        "Pre-set rule that halts trading when prices move beyond a threshold.",
        "Three-tier S&P 500 circuit breakers: Level 1 (7 percent decline, 15-minute halt), Level 2 (13 percent, 15-minute halt), Level 3 (20 percent, halt for the day). Single-stock LULD (Limit Up Limit Down) bands tighter still. Triggered multiple times during March 2020 pandemic selloff. Designed to give participants time to assess information during disorderly moves. Critics argue they can amplify volatility by pulling liquidity around triggers.",
        ["SEC", "NYSE", "Nasdaq"],
        indications=["Cross-asset"], category="Regulation"),
]


# ============================================================================
# BATCH 15 — Execution algos (25 terms — algo families, RFQ, market impact)
# ============================================================================

BATCH_EXECUTION_ALGOS = [
    entry("Implementation Shortfall", "IS",
        "Difference between the price when the trade was decided and the average execution price.",
        "Captures total execution cost: market impact, opportunity cost from delayed fills, and spread paid. Coined by Andre Perold in 1988. The 'arrival price' benchmark for execution algos. IS algos try to minimise this gap by balancing impact (fill faster) against urgency (wait for liquidity). Distinct from VWAP/TWAP benchmarks which compare to participation-weighted prices, ignoring timing.",
        ["CFA Institute"],
        indications=["Cross-asset"], category="Trading & Execution"),

    entry("POV", "Percent of Volume",
        "Algo that targets a percentage of market volume — adapts to changing trading activity.",
        "Trader specifies, say, 10 percent participation. Algo trades 10 percent of each minute's volume — accelerates when others trade, slows when they don't. Different to VWAP (volume profile assumed in advance) and TWAP (constant pace). Used by traders confident in their direction but unwilling to drive prices. POV-targeting algos can hit excessive impact if market volume surges and the algo can't keep up.",
        ["NYSE"],
        indications=["Cross-asset"], category="Trading & Execution"),

    entry("Smart Order Router", "SOR",
        "System that decides where to route each child order across available venues to optimise execution.",
        "Considers visible quotes (NBBO), hidden liquidity at dark pools, exchange fees, latency, and routing logic from broker preferences. Routes parent orders to the venue most likely to fill at the best price. Smart routers represent decades of evolution from simple 'route to NYSE' systems to multi-venue optimisation. Quality varies by broker; sophisticated buy-side institutions evaluate SOR performance via TCA.",
        ["SEC", "FINRA"],
        indications=["Cross-asset"], category="Trading & Execution"),

    entry("RFQ", "Request for Quote",
        "Buyer requests prices from multiple dealers; dealers respond competitively.",
        "Standard execution protocol in fixed-income, FX, and OTC derivatives. Dealer-to-customer (D2C) RFQ platforms: MarketAxess (bonds), Tradeweb (rates, bonds), Bloomberg (multi-asset). Quotes are firm for a brief window (often 30-60 seconds). RFQ-IS (RFQ Implementation Shortfall) execution lets traders compare quoted prices to internal valuations. EU MiFID II requires RFQ disclosure for transparency.",
        ["MSCI", "ESMA"],
        indications=["Cross-asset"], category="Trading & Execution"),

    entry("Block Trade", "Block",
        "Large transaction negotiated off the public order book — minimises market impact.",
        "Equity block thresholds: NYSE 10,000+ shares, Nasdaq similar. Block trades cross between institutional buyers and sellers via block-trading desks, dark pools, or RFQ networks. Treasury block trades go via interdealer brokers (Cantor Fitzgerald, BGC). Block flow is critical for pension funds and asset managers handling million-share orders. Detection: trade prints at sizes far above typical retail orders.",
        ["NYSE", "SEC"],
        indications=["Cross-asset"], category="Trading & Execution"),

    entry("Crossing Network", "",
        "Anonymous matching engine — buyers and sellers cross at a reference price (usually midpoint).",
        "Examples: Liquidnet, Posit, Bloomberg POSIT, MS Pool. Periodic auctions or continuous crossing. Reference price typically NBBO midpoint, removing the half-spread cost. No public quote display — institutions match large orders without leaking information. Crossing networks are technically a form of dark pool, often distinguished by their continuous-auction crossing mechanism rather than continuous matching.",
        ["SEC", "FINRA"],
        indications=["Equities"], category="Market Structure"),

    entry("Last Look", "",
        "FX dealer's right to reject a quoted trade in the milliseconds before execution.",
        "Standard practice in OTC FX. Dealer commits to a quote, sees the incoming order, has milliseconds to decide whether to execute or reject (typically rejecting if market has moved against the quote). Controversial because it asymmetrically benefits dealers. Buy-side traders watch reject rates as an execution-quality metric. The FX Global Code (2017) imposed transparency rules but didn't ban last-look.",
        ["BIS", "FCA"],
        indications=["FX"], category="Trading & Execution"),

    entry("Slippage", "",
        "Difference between expected execution price and actual fill price.",
        "Positive slippage = better than expected; negative = worse. Causes: bid-ask spread, market impact from large orders, latency between decision and execution. Quantified in basis points or cents per share. Implementation Shortfall captures total slippage versus the decision-time price. Algo execution aims to minimise expected slippage; risk management caps maximum acceptable slippage on individual orders.",
        ["CFA Institute"],
        indications=["Cross-asset"], category="Trading & Execution"),

    entry("Market Impact", "Price Impact",
        "Adverse price movement caused by a large trade's own activity.",
        "Empirically, impact scales roughly with the square root of order size relative to daily volume. Temporary impact reverses (price snaps back after the trade); permanent impact reflects information leakage. Pre-trade impact estimates inform algo selection and order sizing. Buy-side TCA (transaction cost analysis) measures realised impact versus pre-trade forecasts to evaluate algo and broker performance.",
        ["CFA Institute", "FINRA"],
        indications=["Cross-asset"], category="Trading & Execution"),

    entry("Toxic Flow", "",
        "Order flow that consistently trades against market-makers because it has informational advantage.",
        "Market-makers lose money to toxic flow on a per-trade basis. HFT firms classify counterparties (retail, institutional, other HFT) and adjust their quotes accordingly. PFOF brokers route retail flow to market-makers specifically because it's non-toxic — retail trades aren't reliably informed. Buy-side flow from sophisticated quant funds is often the most toxic. Dark pools struggle with toxic-flow filtering.",
        ["SEC", "FINRA"],
        indications=["Cross-asset"], category="Market Structure"),

    entry("Adverse Selection", "",
        "Market-maker risk that the counterparty has better information.",
        "Core risk in market-making: you quote a two-way price, informed traders pick off the side that's mispriced. Adverse-selection costs grow with bid-ask spread (compensation) and shrink with quote-update speed. Dark pools that don't filter informed flow can suffer extreme adverse selection. Information asymmetry economics underpin most market-making profit/loss dynamics.",
        ["CFA Institute"],
        indications=["Cross-asset"], category="Risk"),

    entry("Maker-Taker", "",
        "Exchange fee structure where liquidity providers (makers) get rebates and takers pay fees.",
        "Standard in US equity, futures, and options. Typical: maker rebate 20-30 cents per 100 shares; taker fee 30 cents. Inverted-pricing venues (BATS Y, NYSE National) reverse this. The economics drive HFT market-making strategies. Critics argue maker-taker creates conflicts in broker order-routing decisions. SEC pilot programs have studied effects of fee changes on liquidity provision.",
        ["SEC", "FINRA"],
        indications=["Cross-asset"], category="Market Structure"),

    entry("MTF", "Multilateral Trading Facility",
        "European equivalent of US Alternative Trading Systems — non-exchange trading venues.",
        "Cboe Europe, Aquis Exchange, Turquoise are major MTFs. Same regulatory category as RM (regulated market, i.e. exchange) under MiFID II but with lighter listing requirements. MTFs handle roughly 35 percent of European equity trading volume. The post-Brexit split between EU MTFs and UK MTFs fragmented liquidity further — many securities now trade in multiple jurisdictions.",
        ["ESMA", "FCA"],
        indications=["Equities"], category="Market Structure"),

    entry("ATS", "Alternative Trading System",
        "Non-exchange trading venue registered with the SEC under Reg ATS.",
        "Includes dark pools, ECNs, and crossing networks. Roughly 50 ATSs operate in US equities. Form ATS-N requires public disclosure of operations. Subject to SEC rule changes proposed in 2022-2024 that would tighten oversight. ATSs allow flexibility in market structure without full exchange status — lower regulatory burden but no listing role and limited quote-display privileges.",
        ["SEC", "FINRA"],
        indications=["Equities"], category="Market Structure"),

    entry("ECN", "Electronic Communication Network",
        "Electronic system matching buy and sell orders from multiple participants.",
        "Pioneered by Instinet in the 1970s; Island, Archipelago, BATS dominated the 2000s. Reg ATS regulates ECNs as Alternative Trading Systems. ECN inventors (Joshua Levine, William Lupien) reshaped US equity markets by undercutting exchange-floor middlemen. Many original ECNs merged into today's exchanges: Archipelago became NYSE Arca, BATS became Cboe BZX. Distinct from dark pools by displaying quotes.",
        ["SEC", "FINRA"],
        indications=["Equities"], category="Market Structure"),

    entry("Volume Curve", "",
        "Historical pattern of intraday volume distribution across a trading day.",
        "US equity volume is U-shaped: heavy in the first and last hours, light in the middle. Index rebalances spike closing-auction volume. VWAP algos slice orders to match the volume curve. Different securities have idiosyncratic curves — illiquid stocks may concentrate volume at the open. Modern algos use machine-learned curves that adapt to recent days and intraday surprises.",
        ["NYSE", "Nasdaq"],
        indications=["Cross-asset"], category="Trading & Execution"),

    entry("Aggressor Side", "Initiator",
        "Side of a trade that took liquidity — opposite of the resting (passive) side.",
        "If a buy order lifts a resting offer, the buy is the aggressor. Trade reporting includes aggressor flags. Aggressor data is critical for inferring order-flow toxicity, sentiment, and price-impact patterns. HFT firms quote aggressively only when their models indicate favourable expected value. Buy-side TCA scrutinises aggressor versus passive fill mix as an execution-quality dimension.",
        ["NYSE", "Nasdaq"],
        indications=["Cross-asset"], category="Trading & Execution"),

    entry("Liquidity-Seeking Algo", "Sniper",
        "Algo that aggressively hunts for hidden liquidity across venues.",
        "Probes dark pools and reserve orders with small IOC orders to find blocks of latent demand. Used by traders confident in their direction who want to fill quickly with minimal market signalling. Less price-sensitive than VWAP/POV algos. Critics call them 'sniper algos' for their predatory feel toward unsuspecting passive liquidity. Standard in modern algo toolkits — most major brokers offer some flavour.",
        ["SEC"],
        indications=["Cross-asset"], category="Trading & Execution"),

    entry("Schedule-Based Algo", "",
        "Algo executing a pre-defined trading schedule — VWAP, TWAP, POV.",
        "Trader specifies parameters (start/end time, target rate, etc.) and the algo executes according to schedule without real-time decisioning. Predictable behaviour; easy to model. Critics note schedule-based algos can be gamed by predatory traders detecting the regular slicing pattern. Most institutional flow uses adaptive algos that adjust to real-time market conditions rather than fixed schedules.",
        ["NYSE"],
        indications=["Cross-asset"], category="Trading & Execution"),

    entry("Algo Wheel", "",
        "Buy-side framework that allocates orders across multiple brokers' algos and measures performance.",
        "Each order randomly (or systematically) routed to one of several broker algos; performance compared via TCA. Removes broker selection bias and isolates execution quality. Standardised by buy-side traders to extract better execution from competing brokers. Goldman Sachs, Morgan Stanley, JPM, and others compete for algo-wheel allocations. Common in modern institutional equity execution.",
        ["CFA Institute"],
        indications=["Cross-asset"], category="Trading & Execution"),

    entry("TCA", "Transaction Cost Analysis",
        "Post-trade analysis measuring execution quality against benchmarks.",
        "Standard benchmarks: arrival price (IS), VWAP, TWAP, opening/closing prices, reverse-VWAP. Buy-side institutions use TCA to evaluate brokers, algos, and traders. Pre-trade TCA forecasts expected costs to guide execution choices. Regulatory frameworks (MiFID II, Reg BI) increasingly require TCA disclosure to investors. Vendors: Abel Noser, ITG, IHS Markit (LSEG), Trade Informatics.",
        ["CFA Institute", "ESMA"],
        indications=["Cross-asset"], category="Trading & Execution"),

    entry("Internalisation", "",
        "Broker matches client orders internally rather than routing to public venues.",
        "Large brokers (Citadel Securities for retail flow, banks for institutional flow) internalise extensively. Saves exchange fees and avoids leaking client intent. Critics argue internalisation reduces transparency and price discovery; supporters note many trades happen at NBBO midpoint or better. SEC's Best Execution rules and FINRA Rule 5310 require brokers to demonstrate internalisation produces favourable customer outcomes.",
        ["SEC", "FINRA"],
        indications=["Cross-asset"], category="Trading & Execution"),

    entry("Iceberg Algo", "",
        "Algo that uses iceberg orders to gradually work a large order — only the tip visible.",
        "Reveals just a small slice of total intended quantity; replenishes as the visible tip fills. Conceals true order size to avoid market signalling. Used in equities (where iceberg orders are explicit order types) and adapted via algos in markets without native iceberg support. Distinct from broader liquidity-seeking algos that pull from multiple sources.",
        ["NYSE"],
        indications=["Cross-asset"], category="Trading & Execution"),

    entry("Inverted Pricing", "",
        "Maker-taker fee model with the signs flipped — takers get rebates, makers pay fees.",
        "Used by smaller exchanges (BATS BY, NYSE National) to attract aggressive order flow. Counterintuitive: liquidity-providers pay to post, liquidity-takers earn to lift quotes. Works when the venue can attract enough aggressive order flow to offset the rebates. Strategic role in capturing 'taker-heavy' segments of the market. Operates alongside standard maker-taker venues.",
        ["SEC", "FINRA"],
        indications=["Cross-asset"], category="Market Structure"),

    entry("Latency Arbitrage", "Lat Arb",
        "Profit strategy exploiting microsecond price differences across venues.",
        "Example: SPY ETF on NYSE Arca shows new price; the AMEX-listed alternative still has old price for 100 microseconds. Latency arbitrageurs trade the slow side at the obsolete price. IEX's 350-microsecond speedbump explicitly aims to neutralise latency-arb. Critics argue lat arb tax retail traders; defenders argue it tightens prices across venues. The Michael Lewis 'Flash Boys' book centred on lat-arb practices.",
        ["SEC", "FINRA"],
        indications=["Cross-asset"], category="Trading & Execution"),
]


# ============================================================================
# BATCH 16 — Settlement, clearing, custody (25 terms — CCPs, custodians, payment rails)
# ============================================================================

BATCH_SETTLEMENT = [
    entry("T+1", "T-Plus-One",
        "Settlement one business day after trade — US equities adopted T+1 in May 2024.",
        "Replaced the long-running T+2 cycle. Shorter settlement reduces counterparty risk between trade and final ownership transfer but compresses post-trade processing time. India was the first major market on T+1; Canada and Mexico moved simultaneously with the US. UK and EU equities remain on T+2 as of late 2024. T+0 (same-day) settlement studies ongoing.",
        ["SEC", "DTCC"],
        indications=["Cross-asset"], category="Settlement & Operations"),

    entry("T+2", "T-Plus-Two",
        "Standard equity settlement cycle in most markets outside the US — two business days post-trade.",
        "EU and UK equities, Asian markets, most government bonds outside the US. Long-standing standard before the US T+1 transition. Most international FX spot also settles T+2 (except USD/CAD and USD/MXN at T+1). The transition costs of shortening settlement cycles are significant — affects collateral pipelines, fail rates, and cross-border timing. EU consulting on potential T+1 move 2027+.",
        ["DTCC", "ESMA"],
        indications=["Cross-asset"], category="Settlement & Operations"),

    entry("CCP", "Central Counterparty",
        "Clearing house standing between buyer and seller — guarantees each trade's settlement.",
        "Major CCPs: LCH (interest-rate swaps, equity, FX), ICE Clear Credit (CDS), CME Clearing (futures, swaps), Eurex Clearing (European derivatives), DTCC NSCC (US equities). Counterparty risk concentrated at the CCP, mitigated by initial margin, default fund, and skin-in-the-game. Designated SIFMU (Systemically Important Financial Market Utility) status by FSB.",
        ["LCH", "CME Group", "ICE"],
        indications=["Cross-asset"], category="Settlement & Operations"),

    entry("Clearing Member", "",
        "Bank or broker authorised to clear trades through a specific CCP — their customers' trades pass through them.",
        "Major clearing members: JPMorgan, Morgan Stanley, Goldman Sachs, Citi, Barclays, BNP Paribas. Customers must use a clearing member to access central clearing. Clearing members post initial margin to the CCP, fund their share of the default fund, and assume liability for their customers' obligations. CCP eligibility requires significant capital and operational sophistication.",
        ["LCH", "CME Group"],
        indications=["Cross-asset"], category="Settlement & Operations"),

    entry("Default Fund", "Guarantee Fund",
        "Pool of clearing-member contributions standing behind a CCP's defaulter losses.",
        "Sized to cover losses from the simultaneous default of the two largest clearing members under extreme stress. Funded by clearing members proportional to their cleared volume and risk. The 'mutualisation' layer of the default waterfall — losses spread across surviving members after defaulter's initial margin is exhausted. Major CCPs hold default funds in the low single-digit billions.",
        ["LCH", "CME Group"],
        indications=["Cross-asset"], category="Settlement & Operations"),

    entry("Default Waterfall", "",
        "Order in which a CCP applies financial resources to cover a defaulting member's losses.",
        "Standard sequence: defaulting member's initial margin → defaulting member's default fund contribution → CCP's own 'skin in the game' → surviving members' default fund contributions → assessment rights (force surviving members to top up). Designed so non-defaulting members aren't immediately on the hook. Real-world tests rare and limited — Lehman's bankruptcy was successfully resolved within the LCH waterfall.",
        ["LCH", "BIS"],
        indications=["Cross-asset"], category="Settlement & Operations"),

    entry("Skin in the Game", "CCP Capital",
        "CCP's own equity capital that absorbs losses before tapping the default fund.",
        "Typically 5-25 percent of the smallest tier of the default fund — modest relative to total mutualised resources. Designed to align CCP incentives with risk management. Critics argue it's too small to materially incentivise CCPs to manage risk prudently; supporters note it sits in the right position in the waterfall. EMIR 3.0 in Europe is increasing skin-in-the-game requirements 2024-25.",
        ["ESMA", "LCH"],
        indications=["Cross-asset"], category="Settlement & Operations"),

    entry("Custodian", "",
        "Bank that holds securities on behalf of investors — separate from trading and clearing.",
        "Major custodians: State Street, BNY Mellon, Citi, JPMorgan, Northern Trust, BNP Paribas, HSBC. Combined trillions in assets under custody. Service includes: safekeeping, trade settlement, corporate-action processing, income collection, securities lending, fund administration. The 1995 Barings Bank collapse partly stemmed from inadequate custody segregation. Post-Madoff (2008), regulators tightened custodian-investor segregation rules.",
        ["SEC", "FINRA"],
        indications=["Cross-asset"], category="Settlement & Operations"),

    entry("Sub-Custodian", "Local Custodian",
        "Local custodian appointed by a global custodian to hold securities in a specific jurisdiction.",
        "Global custodian (State Street) appoints local sub-custodians (a local bank in each market) to access the local CSD. The 2008 Madoff fraud highlighted sub-custody risks; subsequent rules tightened due-diligence requirements. Cross-border investing depends on robust sub-custody networks. Sub-custodian risk includes country risk, operational risk, and legal/regulatory risk.",
        ["SEC", "ESMA"],
        indications=["Cross-asset"], category="Settlement & Operations"),

    entry("DvP", "Delivery versus Payment",
        "Settlement mechanism where securities and cash change hands simultaneously.",
        "Eliminates principal risk: neither party can deliver without receiving. Standard for most securities settlement worldwide via CSDs. Three DvP models (BIS classification): Model 1 (gross trade-by-trade simultaneous), Model 2 (gross securities, net cash), Model 3 (net both). Most modern systems (DTC, Euroclear, Clearstream) use Model 2 or 3 for efficiency.",
        ["BIS", "DTCC"],
        indications=["Cross-asset"], category="Settlement & Operations"),

    entry("PvP", "Payment versus Payment",
        "FX settlement mechanism where both currency legs settle simultaneously.",
        "Implemented globally via CLS (Continuous Linked Settlement). Eliminates Herstatt risk where one party pays out before receiving. Roughly two-thirds of global FX settlement now goes via CLS or equivalent PvP arrangements. Remaining settlement (mostly EM currencies outside CLS) still bears principal risk. Continuous push to expand PvP coverage to additional currencies and counterparties.",
        ["BIS"],
        indications=["FX"], category="Settlement & Operations"),

    entry("CSD", "Central Securities Depository",
        "Institution holding securities in electronic form — the registry and settlement layer.",
        "DTC for US equities. Euroclear (Belgium) for international bonds. Clearstream (Luxembourg) for European bonds and equities. Each jurisdiction has its own CSD for local securities. CSDs handle ownership records, dividend payments, and settlement. Settlement happens by book entry — physical certificates rare. CSDs are designated SIFMUs by global regulators.",
        ["DTCC", "ESMA"],
        indications=["Cross-asset"], category="Settlement & Operations"),

    entry("Euroclear", "",
        "Largest international CSD — clears trillions in bonds and equities, mostly EU-related.",
        "Based in Brussels. Settles roughly 1 quadrillion euros in transactions annually. Holds custody of nearly 40 trillion euros in securities. Russian sanctions in 2022 immobilised approximately 200 billion euros of Russian central bank assets at Euroclear — politically and legally complex. Sister institution Euroclear Bank handles cross-border eurobond settlement.",
        ["ESMA", "ECB"],
        indications=["Cross-asset"], category="Settlement & Operations"),

    entry("Clearstream", "",
        "International CSD based in Luxembourg — competitor to Euroclear.",
        "Subsidiary of Deutsche Börse. Handles roughly 8 trillion euros in custody. Stronger in German and Asian fixed-income markets than Euroclear. Provides international settlement for sovereign bonds, corporate bonds, equities, and increasingly investment funds. Has been expanding T2S participation in EU CSD harmonisation.",
        ["ECB", "ESMA"],
        indications=["Cross-asset"], category="Settlement & Operations"),

    entry("DTC", "Depository Trust Company",
        "US CSD subsidiary of DTCC — holds and settles US equities and corporate bonds.",
        "Founded 1973. Holds nearly all US-listed securities in book-entry form (95-plus percent). Daily settlement value approximately 5 trillion dollars across DTC, NSCC, and FICC subsidiaries. Survived 2008 stress with minimal disruption. Currently transitioning systems to support T+1 settlement and explore T+0 capabilities.",
        ["DTCC", "SEC"],
        indications=["Cross-asset"], category="Settlement & Operations"),

    entry("SWIFT", "Society for Worldwide Interbank Financial Telecommunication",
        "Global banking messaging network — handles payment, securities, FX messages.",
        "Belgium-based cooperative owned by member banks. Roughly 11,000 institutions across 200-plus countries. Sends 50 million-plus messages daily. Cut off Russian banks in 2022 in response to Ukraine invasion — significantly limited Russian cross-border banking. Replaced by competing systems (SPFS in Russia, CIPS in China) as geopolitical sanctions concerns grow.",
        ["BIS"],
        indications=["Cross-asset"], category="Settlement & Operations"),

    entry("Fedwire", "Fedwire Funds Service",
        "Federal Reserve's real-time gross settlement system — large-value US dollar payments.",
        "Handles roughly 1 trillion dollars daily in 750,000+ payments. Used for interbank transfers, securities settlement, treasury operations. Open 21.5 hours daily. RTGS architecture means each payment settles immediately and finally — no netting. Compare with CHIPS (private-sector competitor) which uses netting. Fed-operated; payment system risk monitored closely.",
        ["Federal Reserve"],
        indications=["Cross-asset"], category="Settlement & Operations"),

    entry("CHIPS", "Clearing House Interbank Payments System",
        "Private-sector USD large-value payment system — operated by The Clearing House.",
        "Handles roughly 1.8 trillion dollars daily. Uses real-time multilateral netting rather than gross settlement — more efficient than Fedwire. Final settlement at end of day via Fedwire. Operated by major US banks. Together with Fedwire, handles vast majority of US dollar wholesale payments. Foundation of US financial plumbing.",
        ["Federal Reserve"],
        indications=["Cross-asset"], category="Settlement & Operations"),

    entry("RTGS", "Real-Time Gross Settlement",
        "Payment system where transfers settle individually and immediately — no netting.",
        "Used for high-value wholesale payments to eliminate settlement risk. Fedwire (USD), TARGET2 (EUR, ECB-operated), CHAPS (GBP, BoE-operated), BOJ-NET (JPY). Differs from net settlement (FedNet, CHIPS, Bacs) where payments are batched and netted. RTGS prevents systemic risk from a payment-system participant failure but requires participants to fund every gross outflow with liquidity.",
        ["BIS", "Federal Reserve"],
        indications=["Cross-asset"], category="Settlement & Operations"),

    entry("Failure to Deliver", "FTD",
        "Trade where the seller fails to deliver securities at settlement.",
        "Causes: counterparty default, short-selling without locating shares to borrow, operational error. Triggers buy-in procedures — the buyer can purchase shares in the market and bill the failed seller. SEC Reg SHO governs short-sale fails. Persistent FTDs in a security can flag manipulation or extreme short interest. Reported and tracked by SEC and FINRA.",
        ["SEC", "FINRA"],
        indications=["Equities"], category="Settlement & Operations"),

    entry("ETD", "Exchange-Traded Derivatives",
        "Standardised derivatives traded on regulated exchanges with central clearing.",
        "Includes futures (CME, ICE, Eurex), listed options (CBOE, ISE), and exchange-traded swaps. Standardised contracts, daily margining, central clearing reduce counterparty risk. Distinct from OTC derivatives (bilateral, customised). The shift from OTC to ETD has been a regulatory priority post-2008 — Dodd-Frank pushed many cleared OTC trades into futures-like cleared structures, blurring lines.",
        ["CME Group", "ICE", "Eurex"],
        indications=["Derivatives"], category="Instruments"),

    entry("Netting", "",
        "Combining multiple offsetting payment obligations into a single net settlement.",
        "Bilateral netting: two parties net amounts they owe each other. Multilateral netting (via a CCP) consolidates across all members. Hugely reduces gross settlement volumes and required liquidity. The 'novation' to a CCP enables multilateral netting. ISDA Master Agreement provides netting upon default for bilateral derivatives. Netting reduces credit risk and operational burden.",
        ["ISDA", "BIS"],
        indications=["Cross-asset"], category="Settlement & Operations"),

    entry("Close-Out Netting", "",
        "ISDA Master Agreement provision triggering immediate termination and netting of all trades upon default.",
        "Critical legal protection for derivatives counterparties. On default, all outstanding trades terminate, net market value is calculated, and a single payment determines the final claim. Enforceable in major jurisdictions through specific legal opinions. Without close-out netting, gross derivative exposures would create massive counterparty risks. Crisis-tested through Lehman 2008 — close-out worked as designed.",
        ["ISDA"],
        indications=["Derivatives"], category="Settlement & Operations"),

    entry("Position Limits", "",
        "Maximum number of futures or options contracts an entity may hold in a single security.",
        "Set by CFTC for US commodity futures, by exchanges for equity and rate futures. Designed to prevent market manipulation and excessive speculation. Spot-month limits typically tighter than aggregate limits. The 2011 Dodd-Frank position-limits rule went through extensive revisions and litigation; finalised 2021. Exemptions exist for hedging by commercial users.",
        ["CFTC", "CME Group"],
        indications=["Cross-asset"], category="Regulation"),

    entry("Buy-In", "",
        "Settlement enforcement — buyer purchases failed-to-deliver securities in the market, bills the seller.",
        "Triggered when a seller fails to deliver securities by settlement deadline. The buyer purchases shares from any seller in the market, and the original seller must reimburse the cost difference. SEC Reg SHO mandates close-out within specific timeframes. CSDR (EU equivalent) imposes similar buy-in regime. Discourages chronic failure to deliver and protects buyers.",
        ["SEC", "ESMA"],
        indications=["Cross-asset"], category="Settlement & Operations"),

    entry("Fails Charge", "Penalty Charge",
        "Daily charge imposed on a counterparty that fails to settle a trade on time.",
        "Designed to incentivise timely settlement. US Treasury fails charge introduced 2008 — 3 percent annualised on fail amount. CSDR in Europe imposes cash penalties for settlement fails. Repo and securities-lending fails carry market-rate penalties. Aggregate fails data published by Treasury and Fed; spikes in fails signal operational stress or extreme short interest in the affected security.",
        ["Federal Reserve", "ESMA"],
        indications=["Cross-asset"], category="Settlement & Operations"),
]


# ============================================================================
# BATCH 17 — Regulation US/EU (25 terms — Dodd-Frank, MiFID II, EMIR, insider trading)
# ============================================================================

BATCH_REGULATION_US_EU = [
    entry("Dodd-Frank", "Dodd-Frank Wall Street Reform and Consumer Protection Act",
        "2010 US legislation overhauling financial regulation in response to the 2008 crisis.",
        "Signed July 2010. Established CFPB, Financial Stability Oversight Council, Volcker Rule restrictions on bank prop trading, Title VII mandatory clearing for standardised OTC derivatives, swap-dealer registration, position limits, and SEF trading mandates. Repealed parts of Glass-Steagall hadn't already been gone. Partial rollback under the 2018 Trump administration EGRRCPA Act loosened rules for smaller banks.",
        ["SEC", "CFTC", "Federal Reserve"],
        indications=["Cross-asset"], category="Regulation"),

    entry("EMIR", "European Market Infrastructure Regulation",
        "EU's post-2008 derivatives regulation — mandates clearing, reporting, and risk mitigation.",
        "Enacted 2012, in force 2013. Counterpart to Dodd-Frank Title VII in the US. Three core mandates: clearing eligible OTC derivatives at authorised CCPs, reporting all derivative trades to trade repositories, and risk mitigation requirements (collateral, dispute resolution) for non-cleared derivatives. EMIR REFIT (2019) simplified reporting; EMIR 3.0 (2024) increased EU CCP requirements.",
        ["ESMA", "ECB"],
        indications=["Derivatives"], category="Regulation"),

    entry("MiFID II", "Markets in Financial Instruments Directive II",
        "EU's sweeping 2018 markets regulation — investor protection, transparency, market structure.",
        "Together with sister regulation MiFIR. Key provisions: research-payment unbundling, broader best-execution rules, pre/post-trade transparency, trade reporting, OTF and SI trading-venue categories, position-limits regime, product-governance rules, inducement disclosures. Heavily reshaped European market structure. UK retained MiFID II after Brexit but is diverging on some details.",
        ["ESMA", "FCA"],
        indications=["Cross-asset"], category="Regulation"),

    entry("MiFIR", "Markets in Financial Instruments Regulation",
        "Sister regulation to MiFID II — directly applicable across EU without national transposition.",
        "Covers transaction-reporting requirements, trading-venue rules, post-trade transparency. Implemented same date as MiFID II (January 2018). The MiFIR Review proposed in 2021 aims to simplify the consolidated tape, transparency provisions, and pre-trade rules. Currently in legislative finalisation. UK MiFIR diverges post-Brexit on some details, including small-cap exemptions and bond-transparency rules.",
        ["ESMA"],
        indications=["Cross-asset"], category="Regulation"),

    entry("Volcker Rule", "",
        "Dodd-Frank provision banning banks from proprietary trading for their own profit.",
        "Section 619 of Dodd-Frank, finalised 2013, effective 2014. Banned banks from prop trading and most hedge-fund/private-equity sponsorship. Required banks to demonstrate market-making was customer-driven, not prop. 2019 'Volcker 2.0' simplifications reduced compliance burden. Sometimes credited with reducing US bank trading-revenue volatility post-2014. Named after former Fed Chair Paul Volcker, its principal advocate.",
        ["Federal Reserve", "SEC"],
        indications=["Cross-asset"], category="Regulation"),

    entry("Reg BI", "Regulation Best Interest",
        "SEC rule requiring broker-dealers to act in retail customers' best interest when recommending securities.",
        "Adopted 2019, effective June 2020. Imposes Care, Disclosure, Conflict of Interest, and Compliance obligations. Doesn't require pure fiduciary duty — explicitly preserves the broker-dealer/IA distinction. Critics argue Reg BI is weaker than DOL's earlier proposed fiduciary rule (vacated by court). Influences broker compensation, product recommendations, and disclosure forms (Form CRS).",
        ["SEC", "FINRA"],
        indications=["Cross-asset"], category="Regulation"),

    entry("Reg SHO", "",
        "SEC rule governing short selling — locate requirement, close-out, mark-and-hold.",
        "Adopted 2005. Short-sellers must 'locate' shares available to borrow before selling. Threshold securities (chronic FTDs) face stricter close-out requirements. The 2008 emergency SEC short-selling restrictions and the 2021 GameStop-era discussions reignited Reg SHO scrutiny. Naked short selling (selling without proper locate) is prohibited but persists in some forms. SEC modernised some provisions in 2023.",
        ["SEC"],
        indications=["Equities"], category="Regulation"),

    entry("Reg M", "",
        "SEC anti-manipulation rules governing securities offerings.",
        "Adopted 1997. Prohibits issuers, distribution participants, and affiliates from engaging in market activities that could artificially influence the price during a 'restricted period' around an offering. Three components: Rules 100 (definitions), 101-102 (distribution participants), 103 (Nasdaq market-makers), 104 (stabilising bids), 105 (short sales). Tightens during IPOs and secondary offerings.",
        ["SEC"],
        indications=["Equities"], category="Regulation"),

    entry("Reg SCI", "Systems Compliance and Integrity",
        "SEC rule requiring critical market infrastructure entities to maintain technology resilience.",
        "Adopted 2014 in response to flash crashes and exchange technology failures. Applies to SCI entities: exchanges, SIPs, clearing agencies, large ATSs. Requires policies for systems, business continuity, disaster recovery, cyber resilience. Annual senior-management reviews and 24-hour outage reporting. Several high-profile SCI events (Nasdaq 2013 outage, BATS 2012 IPO failure) drove its creation.",
        ["SEC"],
        indications=["Cross-asset"], category="Regulation"),

    entry("SEF", "Swap Execution Facility",
        "Dodd-Frank trading-venue category for standardised swaps — alternative to RFQ on platforms.",
        "Required for clearable swaps after 2013. Two execution methods: order book (auction-style) and RFQ (request for quote to multiple dealers). Bloomberg's SEF and Tradeweb's are the largest. EU equivalent is MTF/OTF under MiFID II. Roughly half of US cleared swap volume goes through SEFs. CFTC adopted significant updates in 2024 to modernise SEF rules.",
        ["CFTC"],
        indications=["Derivatives"], category="Regulation"),

    entry("PRIIPs", "Packaged Retail and Insurance-based Investment Products",
        "EU rule requiring standardised disclosure documents for retail investment products.",
        "Effective 2018. Issuers must produce a Key Information Document (KID) for any complex retail product — structured notes, ETFs (under contested interpretation), insurance products, mutual funds (post-UCITS-to-PRIIPs transition completed 2023). Standardised format includes performance scenarios, risk indicator, costs. UK-specific PRIIPs amendments diverge post-Brexit.",
        ["ESMA", "FCA"],
        indications=["Cross-asset"], category="Regulation"),

    entry("UCITS", "Undertakings for Collective Investment in Transferable Securities",
        "EU regulatory framework for retail-eligible investment funds.",
        "First adopted 1985, currently UCITS V (in force 2016). Cross-border distribution within EU on a passport basis — a UCITS authorised in Luxembourg can be sold to retail in Spain or Germany. Limits on portfolio concentration, leverage, derivatives. 11 trillion euros in UCITS funds — the dominant European retail fund vehicle. Distinct from AIFMD which covers alternative funds.",
        ["ESMA"],
        indications=["Cross-asset"], category="Regulation"),

    entry("AIFMD", "Alternative Investment Fund Managers Directive",
        "EU regulation for alternative investment funds — hedge funds, private equity, real estate funds.",
        "Effective 2013. Manager registration, capital requirements, leverage limits, transparency obligations. Allows EU and non-EU AIFM to market across the EU via passport (subject to conditions). Stricter than US Form ADV/Form PF in some respects, lighter in others. Brexit forced UK managers into national private-placement regimes for EU marketing. AIFMD II amendments in 2024 add delegation and loan-fund rules.",
        ["ESMA"],
        indications=["Cross-asset"], category="Regulation"),

    entry("SMCR", "Senior Managers and Certification Regime",
        "UK individual-accountability framework for financial-services firms.",
        "Effective 2016 for banks, 2018 for insurers, 2019 for solo-regulated firms. Senior managers face explicit responsibilities and personal liability for misconduct. Annual certifications for staff in significant roles. Replaced the discredited Approved Persons Regime post-LIBOR. EU's Senior Managers requirements under CRD have similar effect. Has reshaped UK bank governance culture.",
        ["FCA"],
        indications=["Cross-asset"], category="Regulation"),

    entry("MNPI", "Material Non-Public Information",
        "Information not yet public that a reasonable investor would consider important — basis of insider-trading rules.",
        "Trading on MNPI is insider trading under SEC Rule 10b-5. The 'mosaic theory' allows synthesis of public information into proprietary analysis without crossing the MNPI line. SEC and DOJ enforce aggressively — Galleon's Raj Rajaratnam (2011, convicted), Steven Cohen's SAC Capital (2013 settlement), and many smaller cases. Compliance walls, restricted lists, and trading-supervision systems are core MNPI controls at investment firms.",
        ["SEC"],
        indications=["Equities"], category="Regulation"),

    entry("Regulation FD", "Fair Disclosure",
        "SEC rule requiring public companies to disclose material information broadly, not selectively.",
        "Adopted 2000. Banned the practice of companies feeding earnings tips or guidance to select analysts. Material disclosures must be simultaneous and public (via 8-K, press release, or webcast). Modernised in 2008 to include social media disclosure. Reshaped sell-side analyst access to management — analyst-day events, broad investor calls, conference appearances are now the standard channel.",
        ["SEC"],
        indications=["Equities"], category="Regulation"),

    entry("Sarbanes-Oxley", "SOX",
        "2002 US legislation enhancing corporate governance and financial-reporting accountability.",
        "Enacted post-Enron, WorldCom, Tyco accounting scandals. Required CEO/CFO certification of financial reports (Section 302), independent audit committees, internal-controls reporting (Section 404), and CEO/CFO clawbacks for misstatements. Created PCAOB to oversee auditing. Section 404 compliance is famously costly. Whistleblower protections embedded. Reshaped public-company financial-reporting culture.",
        ["SEC"],
        indications=["Equities"], category="Regulation"),

    entry("Glass-Steagall", "Banking Act of 1933",
        "Depression-era US law separating commercial and investment banking — substantially repealed 1999.",
        "Forbade Federal Reserve member banks from underwriting securities or affiliating with securities firms. Repealed by Gramm-Leach-Bliley Act 1999, enabling commercial-investment banking mergers (Citi-Travelers/Salomon, JPMorgan-Chase). Sometimes blamed for setting the stage for 2008 crisis; counter-argument is that several pure investment banks (Bear, Lehman) and pure commercial banks (Washington Mutual) also failed. Periodic calls for revival.",
        ["Federal Reserve", "SEC"],
        indications=["Cross-asset"], category="Regulation"),

    entry("Insider Trading", "",
        "Trading securities while in possession of material non-public information (MNPI).",
        "Banned under SEC Rule 10b-5. Covers corporate insiders (officers, directors, employees), tippers and tippees who knowingly received MNPI. Section 16 of '34 Act requires disclosure of officer/director trades and bans short-swing profits. Federal prosecutions include Ivan Boesky (1986), Martha Stewart (2004), Raj Rajaratnam (2011). Recent SEC focus on cherry-picking, expert-network leaks, and political-intelligence trading.",
        ["SEC"],
        indications=["Cross-asset"], category="Regulation"),

    entry("Quiet Period", "",
        "Pre-IPO and pre-offering window during which company communications are restricted.",
        "From IPO filing through effectiveness, companies and underwriters can't engage in marketing speech outside the prospectus. Reg M extends quiet-period-like restrictions on share repurchases and analyst recommendations. Google's 2004 Playboy interview violated quiet period; Salesforce and others have had similar issues. Has been modernised to allow certain communications (testing-the-waters) under JOBS Act 2012.",
        ["SEC"],
        indications=["Equities"], category="Regulation"),

    entry("Reg AC", "Analyst Certification",
        "SEC rule requiring research analysts to certify their reports reflect personal views.",
        "Adopted 2003 post-Wall Street research scandals. Analysts must certify (in each report) that views accurately reflect personal opinions and disclose any compensation tied to specific recommendations. Together with the 2002 Global Research Settlement, reshaped sell-side research independence from investment banking. MiFID II's research-unbundling rules in Europe achieve similar separation through different mechanism.",
        ["SEC", "FINRA"],
        indications=["Equities"], category="Regulation"),

    entry("Title VII", "Dodd-Frank Title VII",
        "Dodd-Frank's derivatives provisions — central clearing, SEF trading, swap-dealer registration.",
        "Required mandatory clearing for standardised swaps, real-time public reporting, position limits, and capital and margin requirements for non-cleared derivatives. Created SD (Swap Dealer) and MSP (Major Swap Participant) registration categories. SBSD (Security-Based Swap Dealer) under SEC versus SD under CFTC by product type. Reshaped derivatives industry from 2013 onward. CFTC and SEC continue to issue clarifying guidance.",
        ["CFTC", "SEC"],
        indications=["Derivatives"], category="Regulation"),

    entry("Securitisation Regulation", "EU Securitisation Reg",
        "EU framework for securitisation issuance — STS label, transparency, retention.",
        "Effective 2019. Established the 'Simple, Transparent, Standardised' (STS) label for high-quality securitisations qualifying for preferential capital treatment. Mandatory risk retention (5 percent skin-in-the-game) for originators. Investor due-diligence rules. Aimed at reviving European securitisation post-2008 (which has lagged US recovery). Currently under review for further loosening to support EU capital-markets union.",
        ["ESMA"],
        indications=["Credit"], category="Regulation"),

    entry("Form PF", "",
        "SEC quarterly/annual filing required of large private fund advisers.",
        "Adopted 2011 under Dodd-Frank. Covers hedge funds, private equity, real-estate funds, securitised-asset funds. Detailed disclosures on AUM, portfolio composition, leverage, counterparty exposure, financing. Used by FSOC for systemic-risk monitoring. Confidential to the public. 2024 amendments expanded reporting requirements substantially. Form ADV (publicly available) supplements with manager-level disclosures.",
        ["SEC"],
        indications=["Cross-asset"], category="Regulation"),

    entry("CFPB", "Consumer Financial Protection Bureau",
        "Dodd-Frank-created US agency enforcing consumer-financial-products rules.",
        "Established 2011. Oversees mortgages, credit cards, payday loans, debt collection, student loans. Independent funding through Fed (constitutional challenges to that funding model unsuccessful at Supreme Court 2024). Returned billions in restitution to consumers for predatory lending, illegal fees, deceptive marketing. Frequently in political crosshairs — Republican administrations push for restructuring; Democrats expand authority.",
        ["Federal Reserve"],
        indications=["Cross-asset"], category="Regulation"),
]


# ============================================================================
# BATCH 18 — Regulation Basel/capital (25 terms — capital ratios, stress tests, resolution)
# ============================================================================

BATCH_REGULATION_BASEL = [
    entry("Basel III", "",
        "Post-2008 global bank capital and liquidity rules from the Basel Committee.",
        "Finalised 2010-2017, implementation extending through 2028 in some jurisdictions. Key additions over Basel II: higher and better-quality capital (CET1 minimum 4.5 percent), capital conservation and countercyclical buffers, liquidity ratios (LCR, NSFR), leverage ratio. Final 'Basel III Endgame' (Basel 3.1) standardises risk-weights with internal-models constraints. US implementation finalised 2024 for major banks.",
        ["BIS", "Federal Reserve", "ECB"],
        indications=["Cross-asset"], category="Regulation"),

    entry("CET1", "Common Equity Tier 1",
        "Highest-quality bank capital — common stock plus retained earnings.",
        "Minimum 4.5 percent of risk-weighted assets under Basel III, plus conservation buffer (2.5 percent), countercyclical buffer (variable), G-SIB surcharge (1-3.5 percent). Total CET1 requirement for largest banks: roughly 10-13 percent. Absorbs losses first; protects depositors and senior creditors. Tracked by every bank earnings release.",
        ["BIS", "Federal Reserve"],
        indications=["Cross-asset"], category="Regulation"),

    entry("Tier 1 Capital", "",
        "CET1 plus Additional Tier 1 — going-concern capital that absorbs losses while bank operates.",
        "Includes CET1 (highest-quality) plus AT1 instruments (CoCo bonds with conversion triggers). Basel III minimum 6 percent of RWA. Distinct from Tier 2 (gone-concern, subordinated debt) which absorbs losses only at resolution. Heightened AT1 scrutiny post-Credit Suisse 2023 wipe-out — Tier 1 instruments now command higher yields than pre-2023.",
        ["BIS"],
        indications=["Cross-asset"], category="Regulation"),

    entry("Tier 2 Capital", "",
        "Subordinated bank debt — absorbs losses in resolution but not as going concern.",
        "Includes subordinated bonds with at least five-year maturities and other 'gone-concern' instruments. Basel III minimum (combined with Tier 1) 8 percent of RWA. Less expensive than Tier 1 capital. Banks issue Tier 2 as a cost-effective layer above subordinated debt eligibility. Tier 2 holders sit above equity and AT1 in the resolution hierarchy.",
        ["BIS"],
        indications=["Cross-asset"], category="Regulation"),

    entry("RWA", "Risk-Weighted Assets",
        "Bank assets adjusted for their credit, market, and operational risk profiles.",
        "Foundation of regulatory capital ratios — capital divided by RWA gives the headline ratios. Different asset types get different risk weights: sovereign bonds 0 percent, retail mortgages 35 percent, unsecured corporate loans 100 percent, junk bonds 150 percent. Banks can use Standardised approach (regulator-set weights) or Internal Models approach (their own estimates). Basel III Endgame restricts internal-model use.",
        ["BIS"],
        indications=["Cross-asset"], category="Regulation"),

    entry("Leverage Ratio", "",
        "Tier 1 capital divided by total bank assets (unrisk-weighted) — backstop to RWA-based ratios.",
        "Basel III minimum 3 percent. US Supplementary Leverage Ratio (SLR) 5 percent for G-SIBs. Captures off-balance-sheet exposures (derivatives, lending commitments) at notional. Designed as a non-risk-sensitive backstop in case banks game RWA calculations. The 2021 SLR Treasury exemption expired, pressuring bank balance sheets and Treasury market intermediation capacity.",
        ["BIS", "Federal Reserve"],
        indications=["Cross-asset"], category="Regulation"),

    entry("LCR", "Liquidity Coverage Ratio",
        "Bank must hold high-quality liquid assets covering 30 days of net cash outflows in stress.",
        "Basel III minimum 100 percent. HQLA includes Treasuries, central-bank reserves, and other government bonds. Stressed outflow assumptions: retail deposit run-offs (5-10 percent), wholesale funding rollovers, derivatives margin calls, contingent liabilities. Daily monitoring at most banks. Designed to prevent the 30-day liquidity crisis that contributed to 2008 failures (Lehman, Bear Stearns, Northern Rock).",
        ["BIS"],
        indications=["Cross-asset"], category="Regulation"),

    entry("NSFR", "Net Stable Funding Ratio",
        "Bank must have stable funding sources covering at least 100 percent of its required stable funding.",
        "Basel III long-run liquidity ratio — complement to LCR's 30-day focus. Stable funding sources: long-term debt, retail deposits, Tier 1 capital. Required stable funding: long-term loans, illiquid assets, derivatives positions. Implemented later than LCR (2018-21 in major jurisdictions). Forces banks toward longer-tenor funding mixes.",
        ["BIS"],
        indications=["Cross-asset"], category="Regulation"),

    entry("TLAC", "Total Loss-Absorbing Capacity",
        "G-SIB requirement to hold enough capital plus eligible debt to absorb losses without taxpayer bailout.",
        "Financial Stability Board standard (2015). G-SIBs must hold TLAC of 18 percent of RWA plus the leverage-ratio component. Eligible: capital instruments plus senior subordinated debt structurally subordinated to operating-company liabilities (US holdco senior debt; EU MREL-eligible instruments). Enables resolution via bail-in rather than bailout. EU's MREL is similar but applies to all banks.",
        ["BIS", "Federal Reserve"],
        indications=["Cross-asset"], category="Regulation"),

    entry("MREL", "Minimum Requirement for own funds and Eligible Liabilities",
        "EU resolution-funding requirement — equivalent of TLAC but extends beyond G-SIBs.",
        "Single Resolution Board sets MREL targets bank-by-bank. Loss-absorbing layer above operating-company senior debt. Substantial issuance forecast across EU banks 2025-2030. Combined with EU bail-in tool, designed to make resolution credible without state aid. Notable test in 2023 Credit Suisse case — though Switzerland used a state-supported merger rather than full MREL resolution.",
        ["ESMA", "ECB"],
        indications=["Cross-asset"], category="Regulation"),

    entry("SIFI", "Systemically Important Financial Institution",
        "Bank or non-bank whose failure would threaten financial stability.",
        "FSOC designates US SIFIs; FSB designates G-SIFIs internationally. Subject to enhanced supervision, higher capital requirements, recovery and resolution planning. Non-bank SIFI designation contentious: AIG (2014), MetLife (2014, vacated 2018 by court), Prudential (2013, de-designated 2018). FSOC under Biden re-tightened SIFI designation procedures in 2024.",
        ["Federal Reserve", "BIS"],
        indications=["Cross-asset"], category="Regulation"),

    entry("G-SIB", "Global Systemically Important Bank",
        "Bank designated by FSB and BCBS as critical to global financial stability.",
        "Current G-SIB list: 29 banks across 13 jurisdictions. Five categories of surcharge from 1 percent (lowest) to 3.5 percent (highest, currently unoccupied). JPMorgan, HSBC, Citigroup, BNP Paribas in higher tiers. Annual reassessment based on size, interconnectedness, complexity, cross-jurisdictional activity, substitutability. G-SIB surcharge sits on top of regular capital requirements.",
        ["BIS", "Federal Reserve"],
        indications=["Cross-asset"], category="Regulation"),

    entry("D-SIB", "Domestic Systemically Important Bank",
        "Bank important to its home country's financial system but not at global G-SIB level.",
        "Domestic regulators designate D-SIBs. US D-SIB regime gives Category II-IV banks specific capital surcharges and stress-test treatment. EU D-SIB framework similar. Smaller banks below the D-SIB threshold get lighter regulation. The threshold matters: when SVB grew above the Category IV threshold in 2021, additional supervisory expectations would have applied — its 2023 failure prompted EGRRCPA-rollback critiques.",
        ["Federal Reserve", "BIS"],
        indications=["Cross-asset"], category="Regulation"),

    entry("CCAR", "Comprehensive Capital Analysis and Review",
        "Fed annual stress test for largest US banks — assesses capital adequacy under stress scenarios.",
        "Introduced 2011. Banks submit capital plans (dividend, buyback proposals) for Fed review. Fed runs banks' balance sheets through severely adverse scenarios. Quantitative pass/fail (now replaced by Stress Capital Buffer in 2020). Forces banks to maintain capital adequate for prescribed stress scenarios. Now integrated with the annual Dodd-Frank Stress Test (DFAST).",
        ["Federal Reserve"],
        indications=["Cross-asset"], category="Regulation"),

    entry("DFAST", "Dodd-Frank Annual Stress Test",
        "Statutory stress-test framework — overlaps with CCAR.",
        "Required by Dodd-Frank Section 165. Run annually by Fed for largest banks. Tests bank capital adequacy under macroeconomic stress scenarios. Mid-sized banks tested every two years post-EGRRCPA. Public disclosure of results. Effectively merged with CCAR since 2020. Stress scenarios include severely adverse, adverse, and baseline economic projections.",
        ["Federal Reserve"],
        indications=["Cross-asset"], category="Regulation"),

    entry("SCB", "Stress Capital Buffer",
        "Bank-specific capital buffer derived from CCAR stress-test results.",
        "Replaced the fixed 2.5 percent conservation buffer for largest US banks in 2020. Calculated from peak-to-trough capital decline in CCAR adverse scenario plus four quarters of planned dividends. Buffer floor 2.5 percent. Banks must maintain capital above the buffer; constraint on dividends and buybacks if it dips. Personalises capital requirements to each bank's risk profile.",
        ["Federal Reserve"],
        indications=["Cross-asset"], category="Regulation"),

    entry("SREP", "Supervisory Review and Evaluation Process",
        "ECB's annual review setting bank-specific capital and qualitative requirements.",
        "Single Supervisory Mechanism conducts SREP for major euro-area banks. Outputs: Pillar 2 Requirement (binding capital surcharge), Pillar 2 Guidance (non-binding capital guidance), qualitative supervisory measures. Bank-by-bank assessment of business model, governance, capital adequacy, liquidity. Results not fully public — but ratings categories disclosed.",
        ["ECB"],
        indications=["Cross-asset"], category="Regulation"),

    entry("ICAAP", "Internal Capital Adequacy Assessment Process",
        "Banks' internal process for assessing risks and capital — fed into SREP/CCAR.",
        "Required under Basel II Pillar 2. Banks document risks not captured by Pillar 1 capital requirements (concentration risk, interest-rate-risk-in-banking-book, reputation risk). Annual submission to supervisors. Forms basis of supervisory dialogue. ILAAP (Internal Liquidity Adequacy Assessment Process) is the liquidity counterpart. Together, central to modern bank-supervisory framework.",
        ["BIS", "ECB"],
        indications=["Cross-asset"], category="Regulation"),

    entry("SLR", "Supplementary Leverage Ratio",
        "US-specific leverage ratio for G-SIBs — 5 percent of total exposure.",
        "More stringent than Basel III's 3 percent. The 2020-2021 Fed Treasury exemption (temporarily excluded Treasuries and reserves from the denominator) helped banks support Treasury markets during COVID stress. Expired April 2021. Critics argue SLR constraint limits bank capacity to intermediate Treasury markets, contributing to volatility episodes. Ongoing debate about adjustment.",
        ["Federal Reserve"],
        indications=["Cross-asset"], category="Regulation"),

    entry("CCyB", "Countercyclical Capital Buffer",
        "Variable capital buffer that regulators raise in boom times and release in stress.",
        "Basel III tool. Set by national regulators between 0 and 2.5 percent of RWA. US Fed has kept CCyB at zero throughout. UK PRA raised UK CCyB to 2 percent in mid-2023, signalling concerns about leverage. Released in stress to give banks capital headroom to keep lending. Designed to lean against the credit cycle.",
        ["BIS", "Federal Reserve"],
        indications=["Cross-asset"], category="Regulation"),

    entry("Capital Conservation Buffer", "",
        "2.5 percent CET1 buffer above minimum — constrains distributions when breached.",
        "Mandatory under Basel III. If a bank's CET1 falls into the buffer zone (below 7 percent total), restrictions on dividends, buybacks, and bonus payments kick in proportional to the breach depth. Designed to ensure banks rebuild capital naturally through retained earnings rather than forced capital raises during stress. Sits above the 4.5 percent CET1 minimum.",
        ["BIS"],
        indications=["Cross-asset"], category="Regulation"),

    entry("Bail-in", "",
        "Post-crisis resolution tool — bank's bondholders and shareholders absorb losses rather than taxpayers.",
        "Triggered when a bank is failing or likely to fail. Resolution authority writes down equity, AT1, Tier 2, then potentially senior debt in a specified order. The 2017 Banco Popular resolution in Spain wiped out 2 billion euros of equity and AT1; the 2023 Credit Suisse wipe-out of AT1 was a partial bail-in. Designed to make resolution credible without state aid.",
        ["ECB", "FCA"],
        indications=["Cross-asset"], category="Regulation"),

    entry("Living Will", "Resolution Plan",
        "Bank's plan for how it could be resolved without disrupting financial stability or requiring bailout.",
        "Required by Dodd-Frank for largest US banks; EU equivalent under BRRD. Annual or biennial submission to regulators. Details: organisational structure, critical functions, resolution strategy (single-point-of-entry vs multi-point), contingency funding. Confidential to regulators but disclosed summaries public. Several US bank submissions deemed deficient by Fed and FDIC in recent years.",
        ["Federal Reserve"],
        indications=["Cross-asset"], category="Regulation"),

    entry("Resolution Authority", "",
        "Government agency with power to resolve failing banks — restructure or wind down without bankruptcy.",
        "US: FDIC plus Fed under Title II of Dodd-Frank (orderly liquidation authority). EU: Single Resolution Board for euro-area banks. UK: Bank of England. Powers include bail-in, asset transfers to bridge banks, sale to acquirers. The 2023 SVB and Signature resolutions used FDIC's regular receivership powers; First Republic was sold to JPMorgan in a similar mechanism.",
        ["Federal Reserve", "ECB", "FCA"],
        indications=["Cross-asset"], category="Regulation"),

    entry("Basel IV", "Basel 3.1 / Endgame",
        "Final Basel III revisions — restricts internal-model use, introduces output floors.",
        "Finalised by BCBS in 2017. Caps internal-model RWA benefits to 72.5 percent of standardised RWA (output floor). Restricts internal models for low-default portfolios. Implementation began 2023 in EU, 2025-2028 in UK. US 'Basel III Endgame' proposal 2023, finalised mid-2024 with significant pushback from large banks claiming it would constrain lending. Phase-in through 2028.",
        ["BIS", "Federal Reserve"],
        indications=["Cross-asset"], category="Regulation"),
]


# ============================================================================
# BATCH 19 — Indexes & benchmarks (25 terms — equity, bond, commodity indexes)
# ============================================================================

BATCH_INDEXES = [
    entry("S&P 500", "S&P 500 Index",
        "Top 500 US large-cap stocks weighted by market cap — the dominant US equity benchmark.",
        "Maintained by S&P Dow Jones Indices. Selection criteria: market cap, liquidity, sector representation. Constituents reviewed quarterly; rebalances drive significant trading volume. Total market value approaches 50 trillion dollars (2024). Tracked by 7+ trillion in indexed assets (SPY, VOO, IVV ETFs). Total return version (with dividends reinvested) is the standard benchmark for US equity performance comparisons.",
        ["S&P Dow Jones Indices", "SEC"],
        indications=["Equities"], category="Indexes & Benchmarks"),

    entry("Nasdaq Composite", "",
        "Market-cap-weighted index of all 3,000+ Nasdaq-listed stocks.",
        "Heavy tech tilt — Apple, Microsoft, Amazon, Alphabet, Meta, Nvidia together comprise over 30 percent. Launched 1971. Survived massive 78 percent decline in 2000-2002 dot-com crash. Crossed 20,000 for the first time December 2024. Tracked by Invesco QQQ Trust (QQQ ETF, technically tracks Nasdaq-100, not Composite). Distinct from Nasdaq stock exchange itself.",
        ["Nasdaq"],
        indications=["Equities"], category="Indexes & Benchmarks"),

    entry("Nasdaq-100", "NDX",
        "Largest 100 non-financial Nasdaq-listed stocks by market cap.",
        "Subset of Nasdaq Composite excluding financials. Highly tech-heavy: top six tech names approach 40 percent weight. Tracked by Invesco QQQ Trust (QQQ ETF), one of the most-traded ETFs globally. Quarterly rebalances; annual reconstitution. Underlies Nasdaq-100 futures (/NQ) on CME and Nasdaq-100 options. The S&P 500's tech-heavy alternative.",
        ["Nasdaq", "CME Group"],
        indications=["Equities"], category="Indexes & Benchmarks"),

    entry("Dow Jones Industrial Average", "Dow / DJIA",
        "30 large US companies, price-weighted — the oldest US stock index.",
        "Launched 1896 by Charles Dow. Price-weighted (not market-cap-weighted) — a 1-dollar move in any stock contributes equally to the index. UnitedHealth, Goldman, Microsoft, Apple are heavy weights despite different market caps. Less representative than S&P 500 but more recognised by retail and media. Crossed 40,000 in 2024. Tracked by SPDR DIA ETF.",
        ["S&P Dow Jones Indices"],
        indications=["Equities"], category="Indexes & Benchmarks"),

    entry("Russell 2000", "RTY",
        "Small-cap US stock index — 2,000 smallest of the Russell 3000.",
        "Benchmark for US small-cap performance. Total market cap around 3 trillion dollars. Heavy regional-bank, biotech, and consumer-cyclical exposure. iShares Russell 2000 ETF (IWM) is the largest tracker. Annual reconstitution in late June causes significant index trading. Distinct from S&P 600 (S&P's competing small-cap index). Underperformed large-caps significantly 2014-2023.",
        ["FTSE Russell"],
        indications=["Equities"], category="Indexes & Benchmarks"),

    entry("MSCI World", "",
        "23 developed-market countries, large- and mid-cap stocks — the global DM equity benchmark.",
        "1,500-plus constituents. US makes up over 70 percent (its share has grown over the decade). Japan, UK, France, Germany next largest. Methodology: free-float-adjusted market-cap weighting. Underlies trillions in passive and benchmark-linked assets. MSCI ACWI adds EM countries; MSCI EAFE excludes US/Canada (heavy in pension benchmarks).",
        ["MSCI"],
        indications=["Equities"], category="Indexes & Benchmarks"),

    entry("MSCI EAFE", "",
        "Developed markets ex-US and Canada — Europe, Australasia, Far East.",
        "21 developed countries. Japan, UK, France, Germany top weights. Heavily used as international-equity benchmark for US pension funds and asset managers. Tracked by iShares MSCI EAFE ETF (EFA). Persistent EAFE-US performance gap since 2010 reflects US tech dominance — EAFE returns roughly half those of US equities over the past decade.",
        ["MSCI"],
        indications=["Equities"], category="Indexes & Benchmarks"),

    entry("MSCI Emerging Markets", "MSCI EM",
        "24 emerging-market countries — the global EM equity benchmark.",
        "1,400-plus constituents. China, India, Taiwan, Korea, Brazil top weights — China's weight has grown then shrunk in recent years. South Korea and Taiwan technically developed by World Bank standards but classed as EM by MSCI for years (relatively unique classification). Tracked by iShares MSCI EM ETF (EEM), Vanguard FTSE Emerging Markets (VWO). Multi-trillion in indexed flows.",
        ["MSCI"],
        indications=["Equities", "Macro"], category="Indexes & Benchmarks"),

    entry("FTSE 100", "Footsie",
        "100 largest UK-listed companies by market cap — the UK equity benchmark.",
        "Established 1984. Heavy in financials, energy, mining, pharma — global businesses with London listings. Many constituents derive most revenue overseas (Shell, AstraZeneca, HSBC). Total market cap around 2 trillion pounds. Tracked by iShares Core FTSE 100 ETF (ISF). FTSE 250 covers mid-caps; FTSE All-Share is the broader UK benchmark. Operated by FTSE Russell, part of LSEG.",
        ["FTSE Russell"],
        indications=["Equities"], category="Indexes & Benchmarks"),

    entry("DAX", "Deutscher Aktien Index",
        "40 largest German-listed stocks — German equity benchmark.",
        "Total-return index by default (dividends reinvested) — unusual among major indexes. Expanded from 30 to 40 constituents in 2021 to broaden representation. SAP, Siemens, Mercedes, Volkswagen, Allianz are major weights. Auto, chemicals, industrials heavy. Operated by Deutsche Börse. The 2020 inclusion of Wirecard, just before its fraud collapse, embarrassed Deutsche Börse and triggered methodology reforms.",
        ["Eurex"],
        indications=["Equities"], category="Indexes & Benchmarks"),

    entry("Nikkei 225", "",
        "225 large Japanese stocks, price-weighted — the headline Japanese equity index.",
        "Launched 1950, the post-war Japanese benchmark. Price-weighted methodology (like DJIA) gives Fast Retailing (Uniqlo) and SoftBank outsized weights. Hit historic 38,915 in December 1989 — wasn't surpassed until 2024. Tracked by Nikkei 225 futures (/NK), Nikkei ETFs. TOPIX (broader market-cap-weighted index of TSE Prime stocks) is the alternative Japanese benchmark.",
        ["BIS"],
        indications=["Equities"], category="Indexes & Benchmarks"),

    entry("Hang Seng Index", "HSI",
        "Hong Kong's main equity index — large companies listed in Hong Kong.",
        "Approximately 80 constituents. Tencent, Alibaba, HSBC, AIA, China Construction Bank are heavy weights. Expanded recently to include more mainland Chinese tech companies via secondary listings. Operated by Hang Seng Indexes. Highly correlated with mainland Chinese equity sentiment. The 2021 Beijing tech crackdown caused dramatic underperformance versus global benchmarks.",
        ["LSEG"],
        indications=["Equities"], category="Indexes & Benchmarks"),

    entry("CAC 40", "",
        "40 largest French-listed companies — France's main equity index.",
        "LVMH, TotalEnergies, L'Oréal, Sanofi, Hermès are major weights. Heavy luxury-goods, energy, and pharma exposure. Operated by Euronext. The French headline equity index for political and economic commentary. CAC 40 ETFs and futures support trading. Higher correlation with European peers (DAX, Eurostoxx 50) than with US equity benchmarks.",
        ["LSEG", "Eurex"],
        indications=["Equities"], category="Indexes & Benchmarks"),

    entry("STOXX Europe 600", "",
        "600 large- and mid-cap stocks across 17 European countries — the broad European equity benchmark.",
        "More comprehensive than the headline national indexes (FTSE 100, DAX, CAC 40, IBEX). Heavy in financials, consumer staples, healthcare. Operated by STOXX (Deutsche Börse subsidiary). Tracked by iShares STOXX Europe 600 (EXSA), large European ETFs. Eurostoxx 50 (50 large euro-area stocks) is the narrower derivatives-focused alternative.",
        ["Eurex"],
        indications=["Equities"], category="Indexes & Benchmarks"),

    entry("Bloomberg US Aggregate", "Bloomberg Agg / Lehman Agg",
        "Broad US investment-grade taxable bond benchmark — the bond Agg.",
        "Roughly 13,000 securities: US Treasuries, agency MBS, IG corporate bonds, ABS, CMBS. Market-value weighted. Originally Lehman Brothers Aggregate; renamed Bloomberg Barclays after acquisitions, now simply Bloomberg US Aggregate. Tracked by iShares Core US Aggregate Bond ETF (AGG), Vanguard Total Bond Market (BND). Multi-trillion indexed against. Duration around 6 years; yield reflects mixed Treasury and credit composition.",
        ["Federal Reserve FRED"],
        indications=["Credit", "Rates"], category="Indexes & Benchmarks"),

    entry("Bloomberg Global Aggregate", "Global Agg",
        "Multi-currency investment-grade bond benchmark spanning developed markets.",
        "Combines US Aggregate, Pan-European, and Asia-Pacific aggregates. Total market value approaches 70 trillion dollars (notional). Provides global IG fixed-income exposure for institutional benchmarks. Hedged-USD versions strip FX risk. Various sub-indexes for specific exposures (Bloomberg Global Aggregate ex-Treasury, ex-Government, etc.). Operated by Bloomberg Index Services.",
        ["Federal Reserve FRED"],
        indications=["Credit", "Rates"], category="Indexes & Benchmarks"),

    entry("JPM EMBI", "Emerging Market Bond Index",
        "USD-denominated emerging-market sovereign bond benchmark.",
        "Operated by JPMorgan. EMBI Global Diversified (with country weight caps) is the most-followed version. Roughly 70 countries. Heavy weights: Mexico, Indonesia, Turkey, Brazil, Argentina. Tracked by iShares JPM EMB ETF, multiple EM debt funds. Long-running multi-trillion benchmark. Country additions and removals on issuance and credit-rating thresholds.",
        ["IMF"],
        indications=["Credit", "FX"], category="Indexes & Benchmarks"),

    entry("JPM GBI-EM", "Global Bond Index – Emerging Markets",
        "Local-currency emerging-market sovereign bond benchmark.",
        "Tracks local-currency sovereign debt (BRL, MXN, IDR, etc.). Different risk profile than hard-currency EMBI: FX exposure dominates, lower credit risk. GBI-EM Global Diversified has country weight caps. Roughly 20 countries. Tracked by VanEck JPM Local Currency EM (EMLC). Local-currency EM has grown substantially as EM governments build domestic capital markets.",
        ["IMF"],
        indications=["Credit", "FX"], category="Indexes & Benchmarks"),

    entry("ICE BofA US Treasury Index", "",
        "Comprehensive US Treasury bond benchmark — alternative to Bloomberg Treasury Index.",
        "Operated by ICE. Multiple sub-indexes by maturity bucket (1-3y, 3-7y, 7-10y, 10-20y, 20+y). Used as benchmark for US Treasury portfolios. Total return versions include coupon reinvestment. Compete with Bloomberg US Treasury Index variants. Each fund chooses its preferred index based on construction methodology nuances.",
        ["ICE", "Federal Reserve FRED"],
        indications=["Rates"], category="Indexes & Benchmarks"),

    entry("CRB Index", "Commodity Research Bureau Index",
        "Historical commodity index — first published 1957, the dean of commodity benchmarks.",
        "Currently the Refinitiv/CoreCommodity CRB Index (RJ-CRB). 19 commodities with fixed component weights: energy 39 percent, agriculture 41 percent, base metals 13 percent, precious metals 7 percent. Rebalanced periodically. Tracked by iPath series and other commodity products. Less actively traded than GSCI or BCOM but the longest-running commodity benchmark.",
        ["LSEG"],
        indications=["Commodities"], category="Indexes & Benchmarks"),

    entry("Bloomberg Commodity Index", "BCOM",
        "Diversified commodity benchmark — 24 commodities with capping rules.",
        "Operated by Bloomberg. Roll methodology: third Friday before each month's contract expiry. Caps single-commodity weights at 15 percent and sector weights at 33 percent — limits oil dominance. Used as benchmark by many commodity funds and ETFs. Total return version includes collateral return on cash backing the futures positions. Long-running multi-billion benchmark for diversified commodity exposure.",
        ["LSEG"],
        indications=["Commodities"], category="Indexes & Benchmarks"),

    entry("GSCI", "S&P GSCI",
        "Production-weighted commodity index — heavy in energy due to oil production scale.",
        "Originally Goldman Sachs Commodity Index. Energy is roughly 55 percent of the index — much higher than BCOM. Roll methodology can produce significant contango drag. Pioneered the era of commodity-index investing in the 2000s. Total return version critical to passive commodity investment strategies. Multiple sub-indexes available for sector-specific exposure.",
        ["S&P Dow Jones Indices"],
        indications=["Commodities"], category="Indexes & Benchmarks"),

    entry("ICE BofA High Yield Index", "BofA HY Index",
        "Broad US high-yield bond benchmark — formerly Merrill Lynch HY Master II.",
        "Includes most USD-denominated junk bonds. Total market value approximately 1.5 trillion dollars. Tracked by SPDR Bloomberg HY (JNK) and iShares Broad USD HY (USHY) ETFs. Effective yield, option-adjusted spread (OAS), and modified duration published daily. The standard reference for HY market commentary.",
        ["ICE"],
        indications=["Credit"], category="Indexes & Benchmarks"),

    entry("LSTA Leveraged Loan Index", "S&P/LSTA",
        "US institutional leveraged-loan benchmark — covers most syndicated bank loans.",
        "Operated by Morningstar/PitchBook in partnership with the Loan Syndications and Trading Association. Roughly 1.4 trillion dollar market. Tracks performance, default rates, recovery rates. Distinct from HY bonds: loans are senior-secured (higher recovery), floating-rate (lower duration). CLO universe references the LSTA index. Default rates spiked to 6 percent in 2020, recovered to under 2 percent post-pandemic.",
        ["S&P Dow Jones Indices"],
        indications=["Credit"], category="Indexes & Benchmarks"),

    entry("VIX", "Cboe Volatility Index",
        "30-day implied volatility of S&P 500 index options — the 'fear gauge'.",
        "Calculated by CBOE from SPX options across strikes and tenors. Quoted as annualised vol in percent. Long-run average around 19; spikes above 80 during extreme stress (2008 Lehman crisis, 2020 March pandemic crash). VIX futures (/VX) and VIX options trade on CFE. Volatility ETFs (VXX, UVXY) provide retail VIX exposure with significant contango drag. The volatility benchmark for risk sentiment globally.",
        ["CBOE"],
        indications=["Equities", "Derivatives"], category="Indexes & Benchmarks"),
]


# ============================================================================
# BATCH 20 — Corporate actions (25 terms — M&A, IPOs, splits, buybacks, SPACs)
# ============================================================================

BATCH_CORP_ACTIONS = [
    entry("IPO", "Initial Public Offering",
        "Company's first sale of stock to public investors — moves from private to public ownership.",
        "Underwriters (typically a syndicate of investment banks) price the offering, distribute to clients, and support trading post-listing. Standard 'IPO discount' 5-15 percent to first-day trading price. Issuer pays gross spread (typically 7 percent) and faces lock-up restrictions (6-month sales prohibition for insiders). The 2020-21 IPO boom (over 1,000 US IPOs raising hundreds of billions) collapsed to a multi-year low by 2023.",
        ["SEC", "FINRA"],
        indications=["Equities"], category="Corporate Actions"),

    entry("Direct Listing", "DPO",
        "Company lists existing shares on an exchange without raising new capital.",
        "No underwriters, no new share issuance, no traditional roadshow. Existing shareholders simply sell into the public market starting day one. Spotify (2018), Slack (2019), Coinbase (2021), Roblox (2021) used direct listings. Recently extended to allow new share issuance simultaneously. Saves underwriter fees but provides less price stability than traditional IPOs.",
        ["SEC", "NYSE"],
        indications=["Equities"], category="Corporate Actions"),

    entry("Secondary Offering", "Follow-on Offering",
        "Sale of additional shares by an already-public company.",
        "Two flavours: primary (new shares issued, dilutes existing holders) and secondary (insiders sell existing shares, no dilution). Often announced after-hours with overnight bookbuild — pricing the next morning. Hurts short-term stock price (1-5 percent typical drop) due to dilution and signalling. Required for capital needs, deleveraging, insider liquidity events.",
        ["SEC"],
        indications=["Equities"], category="Corporate Actions"),

    entry("Stock Split", "Forward Split",
        "Company increases shares outstanding while proportionally reducing per-share price.",
        "Two-for-one split halves the price, doubles the share count — total market cap unchanged. Often used by companies whose share prices have grown to levels (1,000+ dollars) that limit retail accessibility. Tesla's 5:1 split (2020), Apple's 4:1 split (2020), Nvidia's 10:1 split (2024). Mechanical effect on price; theoretical equivalence to a stock dividend with similar reverse-purpose effect.",
        ["SEC", "NYSE"],
        indications=["Equities"], category="Corporate Actions"),

    entry("Reverse Stock Split", "Reverse Split",
        "Company reduces shares outstanding while proportionally increasing per-share price.",
        "Used to lift a low stock price above exchange listing minima (1 dollar typical NYSE threshold) or to remove penny-stock stigma. One-for-ten reverse split: 10 dollars stock at 1 dollar becomes 1 share at 10 dollars. Often signals weakness. AIG (2009), Citigroup (2011), and many SPACs in 2023-24 used reverse splits to maintain listings.",
        ["SEC"],
        indications=["Equities"], category="Corporate Actions"),

    entry("Spin-off", "",
        "Company separates a subsidiary into a standalone public entity — existing shareholders receive new shares.",
        "Standard tax-free reorganisation in the US. Notable spin-offs: GE's healthcare (GE HealthCare, 2023), GE Vernova (energy, 2024), Kellanova/WK Kellogg, ADT split. Often creates value when the spin-off has different growth or capital-allocation characteristics than the parent. Spin-off shares typically underperform initially as forced selling from index-tracking funds (the spin isn't yet in indexes).",
        ["SEC"],
        indications=["Equities"], category="Corporate Actions"),

    entry("Carve-out", "Equity Carve-out",
        "Company sells a minority stake in a subsidiary via IPO, retaining majority control.",
        "Distinct from spin-off (which separates entirely). Parent receives cash from IPO proceeds; carved-out entity gets a public market valuation. Notable examples: AT&T's Vrio, Lambda's IPO in 2023. Sometimes precursor to full spin-off — parent crystallises valuation, then later distributes remaining stake. Tax treatment more complex than tax-free spin-offs.",
        ["SEC"],
        indications=["Equities"], category="Corporate Actions"),

    entry("Tender Offer", "",
        "Direct offer to buy shares from existing shareholders at a stated price.",
        "Used in hostile takeovers (bypass target's board), going-private transactions, and accelerated share repurchases. Standard premium 20-40 percent over market price. Subject to SEC Reg 14D-9. Famous tender offers: Microsoft's failed 2008 Yahoo bid, Cooper Tire's 2014 tender, frequent activist-investor tenders. Distinct from open-market purchases which don't require formal offer documentation.",
        ["SEC"],
        indications=["Equities"], category="Corporate Actions"),

    entry("M&A", "Mergers and Acquisitions",
        "Corporate transactions combining or acquiring companies.",
        "Strategic acquisitions (buyer absorbs target into operations), financial acquisitions (LBOs, private equity buyouts), mergers of equals. Global M&A volume varies dramatically with interest-rate and macro conditions: 2021 record 5 trillion, 2023 sub-3 trillion. Heavily regulated for antitrust (DOJ, FTC, European Commission) and securities laws. Activist investors increasingly drive M&A activity.",
        ["SEC", "FCA"],
        indications=["Equities"], category="Corporate Actions"),

    entry("Merger", "",
        "Combination of two companies into one — both entities cease to exist, new entity emerges.",
        "Distinguished from acquisitions where one company absorbs the other. Stock-for-stock mergers exchange shares; cash mergers buy out the target. Significant 21st-century mergers: ExxonMobil (1999), DaimlerChrysler (1998, failed), United-Continental Airlines (2010), Vodafone-Mannesmann (2000). Antitrust scrutiny intense — Microsoft-Activision deal took 18 months to close (2022-23).",
        ["SEC", "FCA"],
        indications=["Equities"], category="Corporate Actions"),

    entry("Hostile Takeover", "",
        "Acquisition pursued against the target board's wishes — bypasses board via shareholder appeal.",
        "Tactics: tender offer (direct to shareholders), proxy fight (replace the board), public campaign. Carl Icahn (TWA 1985, Texaco 1988), KKR (RJR Nabisco 1988), Microsoft-Yahoo (2008, failed). Target defenses: poison pills, white knights, staggered boards. Increasingly rare since 2000s — most takeovers now negotiated. Activist investors use takeover threats as leverage for governance changes.",
        ["SEC"],
        indications=["Equities"], category="Corporate Actions"),

    entry("Poison Pill", "Shareholder Rights Plan",
        "Anti-takeover defence allowing existing shareholders to buy discounted stock if acquirer crosses ownership threshold.",
        "Standard threshold 10-15 percent. When triggered, existing shareholders (except the acquirer) can buy new shares at half price, severely diluting the acquirer's stake. Twitter adopted poison pill in 2022 in response to Elon Musk's initial stake — later withdrawn when Musk agreed to acquire the company. Delaware law generally upholds poison pills if independently approved.",
        ["SEC"],
        indications=["Equities"], category="Corporate Actions"),

    entry("White Knight", "",
        "Friendly counter-acquirer that target seeks to replace a hostile bidder.",
        "Target board prefers being bought by a white knight (often paying a higher price or offering better employment continuity) than by a hostile acquirer. The 2013 Dell going-private deal had Carl Icahn pressing for higher prices; Michael Dell partnered with Silver Lake as the white-knight option. White-knight protections include reciprocal break-up fees and lock-up arrangements.",
        ["SEC"],
        indications=["Equities"], category="Corporate Actions"),

    entry("SPAC", "Special Purpose Acquisition Company",
        "Shell company that IPOs with the intent to merge with a private target — backdoor public listing.",
        "Investors hold cash in trust until a deal closes; can redeem if they don't like the chosen target. Massive 2020-21 boom: 600+ SPACs raising 160 billion in 2021. Most underperformed dramatically post-merger. SEC tightened SPAC rules 2024 — required underwriter liability, enhanced disclosures, hindering future deal flow. Most 2021-vintage SPACs that completed mergers (de-SPACs) traded well below 10-dollar redemption.",
        ["SEC"],
        indications=["Equities"], category="Corporate Actions"),

    entry("PIPE", "Private Investment in Public Equity",
        "Private placement of public-company stock — typically to institutional investors at a discount.",
        "Used by companies needing capital without going through a full secondary offering — faster, less regulatory friction. Common in SPAC deals: PIPEs anchor the merger by committing capital alongside SPAC trust. Standard 10-20 percent discount to market. Often comes with anti-dilution protections, registration rights, and lock-up provisions. PIPE volume tracks broader risk-on cycles.",
        ["SEC"],
        indications=["Equities"], category="Corporate Actions"),

    entry("Buyback", "Share Repurchase",
        "Company buys back its own shares — reduces share count, returns cash to shareholders.",
        "Two forms: open-market repurchase (gradual purchases over time) and tender offers (one-time large buys). S&P 500 buybacks routinely exceed 900 billion annually. 2022 Inflation Reduction Act imposed 1 percent excise tax on net buybacks. Compared to dividends as a method of returning capital — buybacks are more tax-efficient and flexible. Often boost EPS mechanically by reducing share count denominator.",
        ["SEC"],
        indications=["Equities"], category="Corporate Actions"),

    entry("ASR", "Accelerated Share Repurchase",
        "Company buys back a large chunk of shares from an investment bank immediately — bank covers via market.",
        "Investment bank delivers shares immediately, then buys them in market over weeks or months. Locks in capital return faster than open-market repurchase. Common when companies want to retire shares quickly (rebalancing leverage post-spin, accelerated EPS impact). Typically 3-9 month execution windows. The investment bank takes execution risk; pricing usually tied to VWAP over the buying period.",
        ["SEC"],
        indications=["Equities"], category="Corporate Actions"),

    entry("Rights Issue", "Rights Offering",
        "Existing shareholders given priority to buy new shares — usually at a discount.",
        "Common in Europe and Asia for capital raises. Each rights holder can subscribe pro-rata for new shares; non-subscribers can sell their rights in the market. UK banking sector used massive rights issues post-2008 (RBS's 12 billion pound rights issue famously failed). Less common in the US, where secondary offerings to institutional investors dominate capital-raising. Heavily discounted (20-50 percent to market) to ensure full subscription.",
        ["FCA", "SEC"],
        indications=["Equities"], category="Corporate Actions"),

    entry("Warrant", "",
        "Long-dated option issued by a company on its own stock.",
        "Distinct from listed equity options: warrants are issuer-created securities with multi-year tenors (5-10 typical). Used in capital raises (often attached to debt to sweeten terms), SPAC deals (warrants sweetened the early SPAC structures), and crisis-era restructurings (TARP warrants for major bank bailouts). Settles in newly-issued shares when exercised — dilutive to existing holders.",
        ["SEC"],
        indications=["Equities"], category="Corporate Actions"),

    entry("Record Date", "",
        "Date on which a shareholder must own shares to be eligible for a dividend or corporate action.",
        "Distinct from ex-date (typically two business days before record date) when the stock starts trading without the dividend. Settlement-cycle change to T+1 in 2024 shortened the gap — ex-date is now one business day before record date. Payable date is when the dividend hits accounts. Sequence: declaration date → ex-date → record date → payable date.",
        ["SEC", "DTCC"],
        indications=["Equities"], category="Corporate Actions"),

    entry("Ex-Date", "Ex-Dividend Date",
        "First day a stock trades without its declared dividend — buyers don't receive the upcoming payout.",
        "Stock price typically drops by the dividend amount on the ex-date as the future right to the dividend disappears. Set by the exchange one business day before the record date under T+1 settlement. Dividend capture strategies attempt to buy just before ex-date, capture the dividend, sell after — usually unprofitable after transaction costs and tax implications.",
        ["NYSE", "Nasdaq"],
        indications=["Equities"], category="Corporate Actions"),

    entry("DRIP", "Dividend Reinvestment Plan",
        "Company-sponsored plan letting shareholders reinvest dividends into additional shares automatically.",
        "Often offered without commissions and sometimes at modest discounts to market price. Major dividend payers (Coca-Cola, J&J, Procter & Gamble) operate DRIPs that have built long-term wealth for patient shareholders. Tax treatment: dividends still taxable when received, even if reinvested. Useful for compounding long-term but creates tax-lot tracking complexity. Most modern brokers offer broker-administered reinvestment with similar economics.",
        ["SEC"],
        indications=["Equities"], category="Corporate Actions"),

    entry("Special Dividend", "",
        "One-off dividend payment outside the company's regular dividend schedule.",
        "Used when companies have excess cash but don't want to commit to a higher regular dividend (which would imply ongoing capability). Microsoft's 3-dollar special dividend in 2004 (32 billion total) was one of the largest. Costco regularly pays special dividends. Tax treatment generally same as regular dividends in the US. Sometimes used to return capital without buyback excise tax implications.",
        ["SEC"],
        indications=["Equities"], category="Corporate Actions"),

    entry("Going Private", "Take-Private",
        "Public company is acquired by an investor group and delisted from public markets.",
        "Typical structure: private-equity-led LBO. Notable take-privates: Dell (2013, returned public 2018), Hilton Worldwide (2007), Thomson Reuters' Refinitiv (2018), Sirius XM (under discussion 2024). Average premium 25-35 percent to undisturbed share price. Goes-private deals dropped sharply 2022-23 with higher financing costs; recovering in 2024 as rate expectations stabilised.",
        ["SEC"],
        indications=["Equities"], category="Corporate Actions"),

    entry("Going Concern", "",
        "Auditor's assessment that a company can continue operations for at least 12 months.",
        "Going-concern qualifications in audit reports signal financial distress. Trigger covenant breaches, accelerate debt, accelerate creditor enforcement. Major historical going-concern flags: Bear Stearns (March 2008), Lehman (September 2008), Hertz (2020 — eventually exited bankruptcy), Bed Bath & Beyond (2023). Modern accounting standards require management to assess and disclose substantial doubt about going-concern status.",
        ["SEC"],
        indications=["Equities", "Credit"], category="Risk"),
]


# ============================================================================
# BATCH 21 — Macro central banks & rates (25 terms — Fed plumbing, QE, forward guidance)
# ============================================================================

BATCH_MACRO_CB = [
    entry("FOMC", "Federal Open Market Committee",
        "Fed's policy-setting body — 7 governors plus 5 regional Fed presidents.",
        "Eight scheduled meetings per year. Sets the federal funds target range and chooses balance-sheet operations (QE, QT). Chair (currently Jay Powell) and Vice Chair lead. Five voting regional presidents rotate (NY Fed always votes; other 11 rotate in groups). Statements, press conferences, and Summary of Economic Projections (SEP) drive market reactions. Minutes released three weeks post-meeting.",
        ["Federal Reserve"],
        indications=["Rates", "Macro"], category="Market Structure"),

    entry("Dot Plot", "FOMC Dot Plot",
        "Chart of individual FOMC members' rate projections — released quarterly with the SEP.",
        "Each member places a dot at their projected fed funds target rate at year-end for the current year, next two years, and longer run. Markets infer the FOMC's collective median view from the dot distribution. The longer-run dot is the median estimate of r-star (neutral rate). Famous market-moving dot shifts: December 2018 (rate-cut signals), September 2021 (hike-bringing-forward signals), September 2024 (steeper rate-cut path).",
        ["Federal Reserve"],
        indications=["Rates", "Macro"], category="Indexes & Benchmarks"),

    entry("Forward Guidance", "",
        "Central bank communication about likely future policy paths — used to influence market expectations.",
        "Two flavours: time-based (rates low until 2024), state-based (rates low until unemployment falls below X percent). The Bank of England and Fed pioneered modern forward guidance post-2008. Forward guidance creates self-fulfilling expectations — if markets price in the path, financial conditions adjust as if the policy were already implemented. Credibility-dependent: gradual phasing-out signals must be carefully managed.",
        ["Federal Reserve", "ECB", "Bank of England"],
        indications=["Rates", "Macro"], category="Regulation"),

    entry("Quantitative Easing", "QE",
        "Central bank buys government bonds and other assets — expands balance sheet, lowers long rates.",
        "Used when policy rates are near zero (the ZLB). Fed bought trillions in Treasuries and agency MBS through QE1 (2008-10), QE2 (2010-11), QE3 (2012-14), and pandemic QE (2020-22). Peak Fed balance sheet 9 trillion dollars (April 2022). ECB, BoE, BoJ ran parallel programs. Mechanism: increases reserves, lowers long-term yields, eases financial conditions. Now winding down via QT.",
        ["Federal Reserve", "ECB"],
        indications=["Rates", "Macro"], category="Regulation"),

    entry("Quantitative Tightening", "QT",
        "Central bank shrinks balance sheet — typically by letting bonds mature without reinvesting.",
        "Reverse of QE. Fed's current QT runs at roughly 60 billion dollars per month of Treasury runoff and 35 billion in agency MBS runoff (slowed from peak pace in 2024). Drains reserves from the banking system. Different from rate hikes — affects different parts of the yield curve. Banks of England and Canada are also reducing balance sheets. ECB QT progressing slower. Long-term effects still being studied.",
        ["Federal Reserve", "ECB", "Bank of England"],
        indications=["Rates", "Macro"], category="Regulation"),

    entry("Open Market Operations", "OMO",
        "Day-to-day Fed activity buying or selling Treasuries to manage reserves and short rates.",
        "Distinct from large-scale QE/QT. Permanent OMOs (POMO) for outright purchases; temporary OMOs (TOMO) via repo and reverse repo. Conducted by the New York Fed's Open Market Desk. Pre-2008, OMOs were the primary tool — Fed kept reserves scarce and moved short rates by adjusting supply. Post-2008 abundant-reserves regime, OMOs play smaller role; IORB and ON RRP are the primary tools.",
        ["Federal Reserve"],
        indications=["Rates"], category="Settlement & Operations"),

    entry("Inflation Targeting", "",
        "Monetary-policy framework where central bank explicitly commits to a numerical inflation target.",
        "New Zealand was the first (1990). Now standard across major central banks: Fed 2 percent (since 2012), ECB 2 percent (since 2003), Bank of England 2 percent (1997). The target anchors expectations and provides accountability. Hard targets (BoE — 'symmetric') versus 'within a band' (other approaches). Empirical evidence supports inflation targeting's success at anchoring expectations during the 2000s; tested by 2021-22 inflation surge.",
        ["Federal Reserve", "ECB", "Bank of England"],
        indications=["Rates", "Macro"], category="Regulation"),

    entry("AIT", "Average Inflation Targeting",
        "Fed framework adopted 2020 — tolerates above-target inflation to make up for below-target periods.",
        "Replaced the previous symmetric 2 percent target with an averaging approach. Aimed at preventing prolonged ZLB risk by letting actual inflation run above 2 percent after extended periods of undershooting (most of post-2008 era). Adopted Aug 2020. Criticised in retrospect as contributing to the 2021-22 inflation overshoot — by signalling tolerance for higher inflation, gave the Fed less urgency in tightening when prices started rising. Currently being internally reviewed.",
        ["Federal Reserve"],
        indications=["Rates", "Macro"], category="Regulation"),

    entry("Dual Mandate", "",
        "Federal Reserve's legal mandate — maximum employment plus stable prices.",
        "Established by 1977 Federal Reserve Reform Act. Most other major central banks (ECB, Bank of England) have price stability as primary mandate; employment is secondary. The dual mandate occasionally creates tension — high inflation with low unemployment (2022) requires policy choices weighing both objectives. Fed Chairs publicly emphasise both in press conferences and Congressional testimony.",
        ["Federal Reserve"],
        indications=["Rates", "Macro"], category="Regulation"),

    entry("Output Gap", "",
        "Difference between actual economic output and the economy's potential output.",
        "Positive gap (output above potential) signals overheating and inflation pressure; negative gap (slack) suggests room for non-inflationary growth. Estimated by CBO, IMF, OECD with significant uncertainty — potential output is unobservable. Negative output gap reached -5 percent during 2008-10 (large slack); recently closed and slightly positive (overheating). Used in Taylor Rule and central-bank reaction functions to assess policy stance.",
        ["IMF", "Federal Reserve FRED"],
        indications=["Macro"], category="Pricing & Valuation"),

    entry("Phillips Curve", "",
        "Empirical relationship between unemployment and inflation — typically inverse.",
        "Documented 1958 by A.W. Phillips. Forms basis of much central-bank thinking. Has shown remarkable instability over decades: appeared flat during 2010s (low unemployment without inflation), then sharply steep in 2021-22 (inflation surge). Augmented Phillips curve includes inflation expectations. Death of the Phillips curve has been repeatedly proclaimed; some version of it always seems to come back.",
        ["Federal Reserve FRED"],
        indications=["Macro"], category="Pricing & Valuation"),

    entry("NAIRU", "Non-Accelerating Inflation Rate of Unemployment",
        "Theoretical unemployment rate below which inflation accelerates.",
        "Pre-2010 estimates put US NAIRU around 5-6 percent. The 2014-2019 period of falling unemployment to 3.5 percent without inflation pressure forced economists to revise NAIRU downward dramatically — to 4 percent or lower. The 2021-22 inflation episode revived debates about how reliable NAIRU estimates are. Central banks use NAIRU implicitly in reaction functions; estimates are policy-dependent.",
        ["Federal Reserve FRED", "IMF"],
        indications=["Macro"], category="Pricing & Valuation"),

    entry("R-star", "Natural Rate of Interest",
        "Real interest rate consistent with stable inflation and full employment in the long run.",
        "Unobservable; estimated via macroeconomic models (Laubach-Williams, Holston-Laubach-Williams). Pre-2008 estimates around 2-2.5 percent real; collapsed to roughly 0.5 percent by 2010s. Most recent FOMC longer-run rate dots imply a nominal r-star around 2.9 percent (2-percent inflation plus 0.9 real). Critical input to monetary-policy stance — current rates above r-star imply restrictive policy.",
        ["Federal Reserve", "BIS"],
        indications=["Rates", "Macro"], category="Pricing & Valuation"),

    entry("Taylor Rule", "",
        "Monetary-policy rule prescribing the fed funds rate based on inflation gap and output gap.",
        "Published 1993 by John Taylor. Rule: rate equals r-star plus inflation plus 0.5 times (inflation minus target) plus 0.5 times output gap. Used as benchmark for evaluating Fed policy — Taylor Rule estimates often deviate from actual Fed policy in interesting ways. Numerous variants and modifications (inertial Taylor, balanced approach). Fed itself doesn't follow any specific rule but considers Taylor-Rule prescriptions in policy discussions.",
        ["Federal Reserve"],
        indications=["Rates", "Macro"], category="Quantitative"),

    entry("Lender of Last Resort", "LLR",
        "Central bank's role providing emergency liquidity to solvent but illiquid institutions.",
        "Walter Bagehot's classic 1873 principle: lend freely at high rate against good collateral. Fed used LLR during 2008 (Bear Stearns rescue, Lehman didn't qualify), 2020 (PMCCF, MMLF), 2023 (Bank Term Funding Program). Includes Discount Window for routine emergencies. ECB's various refinancing operations serve similar role. The fundamental backstop preventing solvent-bank runs from collapsing the system.",
        ["Federal Reserve", "ECB"],
        indications=["Rates"], category="Settlement & Operations"),

    entry("Central Bank Independence", "",
        "Operational autonomy of central banks from political interference.",
        "Empirical evidence supports independent central banks delivering lower inflation. Fed enjoyed strong independence through Volcker (anti-inflation push) and Greenspan-Bernanke eras. Trump administration verbally pressured Powell (2018-2020). BoE has full operational independence (since 1997). ECB has very high independence (constitutionally enshrined). Turkey's central bank independence eroded under Erdoğan, contributing to lira crisis. Indispensable for credible inflation targeting.",
        ["IMF", "BIS"],
        indications=["Macro"], category="Regulation"),

    entry("Helicopter Money", "",
        "Direct central-bank transfer to citizens or government — money-financed fiscal stimulus.",
        "Coined by Milton Friedman (1969 essay). Hypothetical extreme policy — never actually deployed in pure form. Closest analogues: 2020 US stimulus checks (Fed-funded fiscally, not direct), Japan's deficit-funded stimulus financed by BoJ bond purchases. Distinct from QE (which buys assets, lends, doesn't gift). Permanently expands base money — irreversible. Theoretical guard against deflationary trap and ZLB-bound monetary policy.",
        ["BIS", "Federal Reserve"],
        indications=["Macro"], category="Regulation"),

    entry("Reserve Requirement", "",
        "Fraction of customer deposits banks must hold as reserves at the central bank.",
        "Traditional monetary-policy tool. Fed eliminated reserve requirements in March 2020 (set to zero), reflecting the abundant-reserves regime where reserves are no longer the binding constraint. ECB still has a 1 percent reserve requirement. China's PBOC actively uses reserve requirements as a policy tool (10-15 percent range in recent years). The Fed's elimination signals fundamental shift in monetary plumbing.",
        ["Federal Reserve", "ECB"],
        indications=["Rates"], category="Regulation"),

    entry("ZLB", "Zero Lower Bound",
        "Hypothetical floor on nominal interest rates around zero — limits conventional monetary policy.",
        "Fed hit the ZLB Dec 2008 - Dec 2015 and Mar 2020 - Mar 2022. ECB went below the ZLB to negative rates (-0.5 percent at deepest). The presumed ZLB at zero turned out to be slightly negative as central banks discovered they could push below zero. Once at the ZLB, central banks rely on QE, forward guidance, and credit-easing tools. Discussion of higher inflation targets (3-4 percent) partly aims to reduce ZLB frequency.",
        ["Federal Reserve", "ECB"],
        indications=["Rates", "Macro"], category="Pricing & Valuation"),

    entry("Yield Curve Control", "YCC",
        "Central bank caps yields at specific maturities by committing to unlimited buying at those points.",
        "Bank of Japan implemented YCC 2016-2024, pegging the 10-year JGB yield around zero (with bands widened over time). Reserve Bank of Australia attempted YCC during COVID, abandoned painfully in 2021 when markets broke through the cap. Fed considered YCC in 2020 but didn't implement. YCC controls the price of bonds; QE controls the quantity. The BoJ exited YCC March 2024 as inflation finally returned.",
        ["BIS", "Federal Reserve"],
        indications=["Rates"], category="Regulation"),

    entry("FOMC Minutes", "",
        "Detailed record of FOMC meeting discussions — released three weeks after each meeting.",
        "More detailed than the post-meeting statement. Captures range of views, internal debates, staff economic projections. Watched closely for hawk-dove signals beyond the headline statement. Sometimes shifts market expectations meaningfully when minutes reveal more hawkish or dovish internal discussion than the statement language conveyed. Heavily lawyered to avoid market-moving leaks.",
        ["Federal Reserve"],
        indications=["Rates", "Macro"], category="Market Structure"),

    entry("Beige Book", "",
        "Anecdotal economic survey from the twelve Federal Reserve districts — published eight times yearly.",
        "Each Federal Reserve Bank surveys local business contacts, lenders, and industry experts. Released two weeks before each FOMC meeting. Captures qualitative regional economic trends not in headline statistics. Often early indicator of changes in consumer behaviour, labour markets, real-estate conditions. Watched by macro analysts for ground-level signal complementing top-down data. Less market-moving than minutes but useful for nowcasting.",
        ["Federal Reserve"],
        indications=["Macro"], category="Indexes & Benchmarks"),

    entry("BoJ", "Bank of Japan",
        "Japan's central bank — global pioneer of unconventional monetary policy.",
        "Implemented QE first in 2001 (years before other major banks). Maintained zero or negative rates for nearly all of 2000-2024. Owns roughly half of all outstanding JGBs and significant ETF holdings (around 7 percent of TOPIX market cap). Exited negative-rate policy and YCC March 2024 after inflation finally returned to target. Now slowly normalising — first major central bank to hike after the pandemic-era easing.",
        ["BIS"],
        indications=["Rates", "Macro"], category="Market Structure"),

    entry("PBoC", "People's Bank of China",
        "China's central bank — manages renminbi exchange rate and key domestic financial conditions.",
        "Less independent than developed-market peers; coordinates closely with State Council. Active reserve-requirement adjustments, multiple policy rates (LPR, MLF), targeted lending tools. Manages CNY against trade-weighted basket with significant intervention. PBoC reforms reflect China's evolving monetary framework — gradual marketisation alongside continued state guidance. CNY-CNH spread reflects offshore-onshore dynamics.",
        ["IMF", "BIS"],
        indications=["Rates", "Macro", "FX"], category="Market Structure"),

    entry("Currency Pair Carry Premium", "Cross-Currency Basis",
        "Pricing deviation from covered interest parity in FX swap markets — reflects funding stress.",
        "Persistent negative cross-currency basis for USD funding since 2008 (despite CIP arbitrage incentives). EUR-USD basis hit -100 bps in March 2020 stress. Reflects post-crisis bank balance-sheet constraints and limits to arbitrage. Watched by macro traders as a stress indicator. The 'basis' here is the cross-currency basis spread, distinct from the basis-point unit.",
        ["BIS", "Federal Reserve"],
        indications=["FX", "Rates"], category="Pricing & Valuation"),
]


# ============================================================================
# BATCH 22 — Macro FX & EM (25 terms — inflation gauges, GDP, soft/hard landing)
# ============================================================================

BATCH_MACRO_FX_EM = [
    entry("CPI", "Consumer Price Index",
        "Measure of inflation based on a basket of consumer goods and services.",
        "BLS-published monthly in the US. Components: housing (shelter is largest at over 30 percent), food, energy, medical care, transportation. Headline CPI includes everything; core CPI excludes food and energy (more stable signal). Year-over-year and month-over-month changes both watched. UK uses RPI alongside CPI. Inflation surge 2021-22 took US headline CPI to 9 percent peak; back near 3 percent by 2024.",
        ["Federal Reserve FRED", "World Bank"],
        indications=["Macro"], category="Indexes & Benchmarks"),

    entry("PCE", "Personal Consumption Expenditures",
        "BEA's measure of consumer prices — the Fed's preferred inflation gauge.",
        "Calculated from BEA's national income accounts data. Differs from CPI in scope (includes employer-paid healthcare), weights (chain-weighted), and methodology. Core PCE (ex food and energy) is the FOMC's explicit 2 percent target. Typically runs 0.3-0.5 percentage points below CPI. Released after CPI with a 2-week delay, so CPI captures more immediate market attention even though PCE is the policy target.",
        ["Federal Reserve FRED"],
        indications=["Macro"], category="Indexes & Benchmarks"),

    entry("PPI", "Producer Price Index",
        "Inflation measure from the producer's perspective — wholesale prices of goods and services.",
        "BLS-published. Captures pricing pressure upstream — manufacturers, processors, wholesalers. Often a leading indicator of CPI: rising input costs eventually feed through to consumer prices. PPI surged in 2021-22 as supply-chain disruptions pushed up commodity and goods prices. Core PPI (ex food and energy) more stable. Less retail-visible than CPI but watched by economists and the Fed.",
        ["Federal Reserve FRED"],
        indications=["Macro"], category="Indexes & Benchmarks"),

    entry("Core Inflation", "",
        "Inflation excluding volatile food and energy prices — proxy for underlying inflation trend.",
        "More stable signal of price pressures because food and energy are highly volatile. Most central banks focus on core (or 'underlying') inflation for policy decisions. Critics note core can underestimate inflation when food and energy rise persistently. Variants: trimmed-mean inflation (exclude top and bottom outliers), median CPI, sticky-price CPI. Cleveland Fed publishes multiple alternative measures.",
        ["Federal Reserve FRED"],
        indications=["Macro"], category="Pricing & Valuation"),

    entry("Headline Inflation", "",
        "Total inflation including all components — food, energy, and everything else.",
        "The number most often quoted in news headlines. Captures the cost-of-living impact most relevant to consumers. Subject to large fluctuations from food and energy price moves. The 9 percent US headline CPI peak in 2022 was driven heavily by post-Ukraine-invasion energy spikes. Central banks ultimately care about headline (it's what consumers experience) but focus on core for policy because core is the controllable underlying trend.",
        ["Federal Reserve FRED"],
        indications=["Macro"], category="Pricing & Valuation"),

    entry("Hyperinflation", "",
        "Extreme inflation, typically defined as 50 percent or more per month.",
        "Historical examples: Weimar Germany 1923, Hungary 1945-46 (highest recorded — prices doubled every 15 hours), Zimbabwe 2007-08, Venezuela 2017-19, Argentina recurring. Always rooted in massive monetary financing of fiscal deficits. Destroys savings, breaks contracts, ends in currency reform or dollarisation. Distinct from very high inflation (50-200 percent annual). Modern advanced economies don't experience it; remains an EM crisis-state phenomenon.",
        ["IMF", "World Bank"],
        indications=["Macro"], category="Risk"),

    entry("Stagflation", "",
        "High inflation combined with high unemployment and stagnant growth.",
        "Classic 1970s phenomenon: 1973-1981 saw the US suffer through repeated stagflation episodes triggered by oil shocks. Confounds standard Phillips Curve thinking — both inflation and unemployment rising. Volcker's tight monetary policy 1979-82 broke it at huge employment cost. 2022's surge of inflation amid solid employment was widely feared to be a stagflation precursor but the US navigated to disinflation without major job losses. UK 2022-24 came closer to mild stagflation.",
        ["Federal Reserve FRED"],
        indications=["Macro"], category="Risk"),

    entry("Disinflation", "",
        "Decline in the rate of inflation — inflation still positive but slowing.",
        "Distinct from deflation (negative inflation). The 2022-2024 process where US CPI dropped from 9 percent to 3 percent was disinflation. Soft-landing disinflation (without recession) is the policy goal — historically rare but achieved 2022-2024 in the US. Sticky-price components (services, shelter) typically lag goods disinflation, so the last mile to 2 percent is hardest.",
        ["Federal Reserve FRED"],
        indications=["Macro"], category="Pricing & Valuation"),

    entry("Deflation", "",
        "Sustained decline in the general price level — opposite of inflation.",
        "Japan experienced mild deflation/zero inflation through most of 1995-2024. The 1930s Great Depression saw severe deflation in advanced economies. Dangerous because it raises real debt burdens, encourages spending delays, and pushes economies into self-reinforcing slumps. Central banks fear deflation more than mild inflation. The 2008-09 brief deflationary scare drove the Fed to QE; pandemic-era stimulus aimed in part at preventing renewed deflation.",
        ["Federal Reserve FRED"],
        indications=["Macro"], category="Risk"),

    entry("Real GDP", "",
        "Gross Domestic Product adjusted for inflation — measures real economic output growth.",
        "Reported as annualised quarterly growth in the US (BEA), quarter-on-quarter in Europe (Eurostat). Real GDP growth roughly equals labour-force growth plus productivity growth in steady state. US trend growth around 1.8-2 percent post-2010; emerging economies higher. Quarter-to-quarter swings dominated by inventory changes, trade, and government spending. The output gap measures real GDP versus potential.",
        ["Federal Reserve FRED", "IMF"],
        indications=["Macro"], category="Indexes & Benchmarks"),

    entry("Nominal GDP", "",
        "GDP in current-dollar terms — without inflation adjustment.",
        "Difference between nominal and real GDP is the GDP deflator. Nominal GDP is what's used for debt-to-GDP ratios, fiscal-policy comparisons, currency-area size rankings. China and India have higher real GDP growth than the US; on nominal-dollar terms (with FX effects) the rankings shift. Nominal GDP growth roughly equals real GDP plus inflation in the simple identity.",
        ["IMF", "World Bank"],
        indications=["Macro"], category="Indexes & Benchmarks"),

    entry("GDP Deflator", "",
        "Broadest inflation measure — covers all goods and services in GDP.",
        "Calculated implicitly: nominal GDP divided by real GDP. Covers all output in the economy, not just consumption (like CPI). Differs from CPI in basket scope and weighting methodology. Typically closer to PCE than CPI in level. Used in academic and IMF cross-country inflation comparisons. Less timely than CPI/PCE (released quarterly with GDP, not monthly).",
        ["Federal Reserve FRED"],
        indications=["Macro"], category="Indexes & Benchmarks"),

    entry("Recession", "",
        "Significant decline in economic activity spread across the economy, lasting more than a few months.",
        "Officially dated by the NBER Business Cycle Dating Committee in the US (typically with a lag). Commonly defined as two consecutive quarters of negative real GDP growth (informal rule of thumb). The pandemic recession (Feb-Apr 2020) was the shortest ever — two months. The 2007-09 'Great Recession' was the longest post-WWII at 18 months. NBER uses broader factors: employment, real income, sales, industrial production.",
        ["Federal Reserve FRED", "IMF"],
        indications=["Macro"], category="Risk"),

    entry("Soft Landing", "",
        "Central bank successfully reduces inflation without triggering a recession.",
        "Historically rare — only the 1994-95 Greenspan tightening cycle is the textbook US example. The 2022-2024 US disinflation from 9 to 3 percent without recession is the second clearest case. Requires policy precision: tight enough to slow demand and break inflation but not so tight as to crash labour markets. Often debated whether achieved — 2024 narratives shifted from soft-landing skepticism to acceptance.",
        ["Federal Reserve FRED"],
        indications=["Macro"], category="Pricing & Valuation"),

    entry("Hard Landing", "",
        "Central bank tightening triggers a significant recession.",
        "Volcker's 1979-82 hard landing crushed inflation but cost massive unemployment (10.8 percent peak). The 1990-91 US recession after late-1980s tightening was milder. 2024 fears of a hard landing eased as employment held up despite Fed hikes. Hard landings can be unavoidable if inflation expectations are deeply embedded. Term is contested — defining when an outcome counts as hard versus soft involves judgment.",
        ["Federal Reserve FRED"],
        indications=["Macro"], category="Risk"),

    entry("Sovereign Default", "",
        "Government failing to meet its debt obligations on time and in full.",
        "Russia 1998 (rouble bonds), Argentina 2001 (USD bonds), Greece 2012 (private creditor exchange, technically default), Lebanon 2020, Sri Lanka 2022, Ghana 2022, Zambia 2020. Hard-currency defaults more common than local-currency (the government can print local currency). Resolution: IMF programs, Paris Club restructurings for official creditors, London Club / private negotiations for bonds. Long market-access exclusion typically follows.",
        ["IMF"],
        indications=["FX", "Macro", "Credit"], category="Risk"),

    entry("IMF", "International Monetary Fund",
        "Multilateral institution providing balance-of-payments crisis financing — 191 members.",
        "Founded at Bretton Woods 1944. Originally to support fixed-exchange-rate system; now serves as global lender of last resort to countries in payments crises. Major facilities: Stand-By Arrangements, Extended Fund Facility, RFI (Rapid Financing). Loans come with conditionality (policy reforms). Recent large programs: Argentina 2018 (57 billion), Egypt 2020-24, Pakistan repeated, Ukraine post-2022. World Bank focuses on long-term development.",
        ["IMF"],
        indications=["Macro", "FX"], category="Market Structure"),

    entry("World Bank", "World Bank Group",
        "Multilateral development bank funding poverty-reduction and infrastructure projects.",
        "Founded with IMF at Bretton Woods 1944. Five institutions: IBRD (loans to middle-income), IDA (concessional finance for poorest), IFC (private-sector lending), MIGA (guarantees), ICSID (dispute settlement). Total commitments roughly 100 billion annually. Distinct from IMF: World Bank funds projects, IMF stabilises balance of payments. Recent priorities: climate adaptation, pandemic response, conflict states.",
        ["World Bank"],
        indications=["Macro"], category="Market Structure"),

    entry("Wage-Price Spiral", "",
        "Self-reinforcing dynamic where rising wages drive prices up, which drives further wage demands.",
        "1970s textbook stagflation pattern: oil shock raises prices, unions demand cost-of-living adjustments, businesses raise prices to cover wage costs, repeat. Modern labour markets less unionised; spirals less automatic. 2021-22 inflation surge prompted wage-price-spiral concerns but didn't fully materialise — real wages mostly stayed below price growth, breaking the feedback. Central banks watch real-wage trends to assess spiral risk.",
        ["Federal Reserve FRED", "IMF"],
        indications=["Macro"], category="Risk"),

    entry("Current Account", "",
        "Net international trade in goods, services, income, and transfers — broad measure of external balance.",
        "Surplus: country saves more than invests, accumulates foreign assets. Deficit: country invests more than saves, accumulates foreign liabilities. US has run persistent current-account deficit since 1990 (around 3-4 percent of GDP). China, Germany, Japan have run surpluses. Persistent imbalances build up to financial-system pressure and currency adjustment. The 2008-09 crisis partly reflected unsustainable US-China imbalance unwinding.",
        ["IMF", "World Bank"],
        indications=["FX", "Macro"], category="Pricing & Valuation"),

    entry("Capital Account", "",
        "Net cross-border capital flows — direct investment, portfolio investment, banking flows.",
        "By accounting identity, capital account mirrors current account (with errors and omissions). Capital flows into US — Chinese, Japanese, Saudi reserves into Treasuries; foreign equity into US tech — fund US current-account deficit. Reversals can be sharp: 1998 Asian crisis, 2020 March COVID flight. Capital controls aim to limit volatility but distort allocation.",
        ["IMF"],
        indications=["FX", "Macro"], category="Pricing & Valuation"),

    entry("Balance of Payments", "BoP",
        "Comprehensive accounting of a country's international economic transactions.",
        "Three components: current account (trade, services, income, transfers), capital account (capital flows), and the financial account (changes in reserves). Always balances by accounting identity; persistent imbalances reflect underlying economic dynamics. BoP crises occur when capital inflows reverse abruptly — Asian 1997, Russia 1998, Argentina 2001. IMF programs typically address BoP crises.",
        ["IMF"],
        indications=["FX", "Macro"], category="Pricing & Valuation"),

    entry("Hard Landing Trade", "Recession Trade",
        "Investment strategy positioning for an economic downturn.",
        "Typical components: long long-duration Treasuries (rally on rate cuts), long defensive equities (utilities, staples, healthcare), short cyclicals (consumer discretionary, banks), short oil, long USD or JPY (safe-haven). 2024 hard-landing-trade unwinds were sharp as US data kept beating recession expectations. Macro funds rotate between hard-landing and soft-landing trades as data flows.",
        ["Federal Reserve FRED"],
        indications=["Macro"], category="Trading & Execution"),

    entry("Reflation", "",
        "Period of rising prices and economic activity — often after deflation or disinflation.",
        "1933-35 New Deal reflation under FDR. Post-2020 pandemic reflation drove the historic 2021-2022 inflation surge as monetary and fiscal stimulus collided with supply constraints. 'Reflation trade' typically: long cyclicals, commodities, value over growth, short bonds. The 2016-2017 reflation expectation following Trump's election produced a major rally in cyclical assets.",
        ["Federal Reserve FRED"],
        indications=["Macro"], category="Pricing & Valuation"),

    entry("Volcker Shock", "",
        "1979-1982 Fed tightening that crushed inflation but caused severe recession.",
        "Fed Chair Paul Volcker took over August 1979. Federal funds rate hit 20 percent in 1981. US fell into the longest post-WWII recession (1980, 1981-82); unemployment hit 10.8 percent. CPI fell from 14 percent (1980) to 3 percent (1983). Established Fed credibility on inflation. Volcker shock remains the benchmark for understanding what extreme monetary tightening costs and achieves.",
        ["Federal Reserve FRED", "Federal Reserve"],
        indications=["Macro"], category="Risk"),
]


# ============================================================================
# BATCH 23 — Risk management (25 terms — VaR, stress, XVA, tail risk)
# ============================================================================

BATCH_RISK = [
    entry("VaR", "Value at Risk",
        "Maximum loss expected at a given confidence level over a given horizon.",
        "A 95-percent 1-day VaR of 10 million means there's a 5-percent chance of losing more than 10 million tomorrow. Basel framework requires banks to hold capital against VaR. Three calculation methods: historical simulation (use past returns), parametric (assume normal distribution), Monte Carlo (simulate paths). Tail-risk events repeatedly exceed VaR (2008 banks losing far more than VaR suggested) — hence the shift toward Expected Shortfall.",
        ["BIS", "CFA Institute"],
        indications=["Cross-asset"], category="Risk"),

    entry("Expected Shortfall", "ES / CVaR / Conditional VaR",
        "Average loss in the worst-case scenarios beyond VaR.",
        "A 95-percent ES is the average loss given you're in the bottom 5 percent. Captures tail risk better than VaR (which is silent about how bad bad gets). Basel III FRTB switched market-risk capital from VaR to ES specifically because of VaR's tail-risk blindness. Heavier tails in actual market returns make ES significantly larger than VaR for the same confidence level.",
        ["BIS", "CFA Institute"],
        indications=["Cross-asset"], category="Risk"),

    entry("Historical VaR", "",
        "VaR calculated by directly applying historical returns to current positions.",
        "Take the past 252 trading days of returns, apply to today's portfolio, find the 5th percentile. Captures actual market behaviour including non-normal distributions. Limitations: assumes the past is representative of the future. Crisis periods (2008, 2020) sit in or out of the rolling window depending on calculation date — sliding the window can produce dramatic VaR changes. Common in trading-book risk models.",
        ["CFA Institute"],
        indications=["Cross-asset"], category="Risk"),

    entry("Parametric VaR", "Variance-Covariance VaR",
        "VaR calculated by assuming returns follow a normal (or other parametric) distribution.",
        "Uses current portfolio sensitivities (delta, gamma) and historical volatility/correlation estimates. Fast to compute, good for large portfolios. Major flaw: assumes normal distribution while financial returns have fat tails. Underestimates tail risk. The 1998 LTCM blow-up and 2008 bank losses repeatedly exceeded parametric VaR. Useful as baseline calculation, not as sole risk measure.",
        ["CFA Institute"],
        indications=["Cross-asset"], category="Risk"),

    entry("Stress Test", "Internal Stress Test",
        "Risk calculation applying hypothetical or historical extreme scenarios to current portfolios.",
        "Standard scenarios: 1987 crash repeat, 2008 financial crisis, 1998 LTCM crisis, 2020 COVID crash. Forward-looking scenarios: 25 percent equity drop, 200 bp rate move, 30 percent FX move. Banks and asset managers run stress tests routinely. Regulatory stress tests (CCAR, EBA tests) prescribe specific scenarios. The 2023 SVB collapse highlighted gaps between internal stress tests and actual rate-rise scenarios.",
        ["Federal Reserve", "BIS"],
        indications=["Cross-asset"], category="Risk"),

    entry("Scenario Analysis", "",
        "Evaluating portfolio performance under specific hypothetical conditions.",
        "Distinct from stress testing (which focuses on extreme conditions). Scenario analysis examines moderate to severe but plausible scenarios. Macro scenarios: 'soft landing', 'hard landing', 'no landing', 'reaccelerating inflation'. Geopolitical: 'Russia-Ukraine resolution', 'Taiwan crisis'. Used in portfolio construction, capital allocation, business planning. Multi-scenario discounting in DCF models is similar approach.",
        ["CFA Institute"],
        indications=["Cross-asset"], category="Risk"),

    entry("Reverse Stress Test", "",
        "Identifies scenarios that would cause a specific level of loss — works backward from outcome to inputs.",
        "Required by Basel III. Question: 'What scenario would cost us 10 percent of capital?' rather than 'What loss in the standard scenario?'. Useful for tail-risk identification — surfaces scenarios that internal models might not naturally generate. Difficult to operationalise; results sensitive to model assumptions. Increasingly required in regulatory capital plans.",
        ["BIS", "Federal Reserve"],
        indications=["Cross-asset"], category="Risk"),

    entry("PFE", "Potential Future Exposure",
        "Maximum expected counterparty credit exposure over a future horizon, at a confidence level.",
        "Critical input for derivatives counterparty risk and Basel regulatory capital. Calculated by simulating portfolio evolution and taking the high-quantile (typically 97.5 percent) at each future time. PFE profile grows with derivative tenor — peaks somewhere in the middle for swap-like products. Used in setting trading-line credit limits and as the basis for SA-CCR regulatory capital calculations.",
        ["BIS", "ISDA"],
        indications=["Derivatives"], category="Risk"),

    entry("CVA", "Credit Valuation Adjustment",
        "Adjustment to derivative fair value reflecting counterparty default risk.",
        "Banks deduct CVA from gross derivative values — what you'd get if no counterparty default minus what you actually expect. CVA reflects expected loss = PD x LGD x exposure. Largest dealers have dedicated CVA desks managing aggregate counterparty exposure with CDS, equity, and FX hedges. CVA gain/loss volatility was a major P&L source 2008-2015. Basel III specifically charges capital against CVA volatility.",
        ["BIS", "ISDA"],
        indications=["Derivatives"], category="Risk"),

    entry("DVA", "Debit Valuation Adjustment",
        "Adjustment for the bank's own default risk — gains if own credit deteriorates.",
        "Counterintuitive: if a bank's own CDS spread widens, its derivative liabilities are worth less in fair-value terms, producing accounting gains. Headed banks book DVA gains/losses in income statement under fair-value accounting. The 2011 European sovereign crisis saw major banks book multi-billion DVA gains on their own widening credit spreads — controversially. Excluded from regulatory capital calculations.",
        ["ISDA"],
        indications=["Derivatives"], category="Risk"),

    entry("FVA", "Funding Valuation Adjustment",
        "Adjustment for the funding cost of uncollateralised derivative positions.",
        "Banks fund derivative collateral and unsecured positions at their own (above-Treasury) funding cost — FVA captures the gap. Less established than CVA — different banks calculate differently. Major OTC derivative valuation differences across dealers partly reflect FVA-methodology differences. FVA and CVA together can offset (a bank's FVA gain offsets the counterparty's FVA charge in mirror form).",
        ["ISDA"],
        indications=["Derivatives"], category="Risk"),

    entry("XVA", "Valuation Adjustments",
        "Collective term for CVA, DVA, FVA, KVA, MVA — adjustments to derivative fair value.",
        "Modern derivative pricing requires multiple adjustments: CVA (counterparty risk), DVA (own credit), FVA (funding), KVA (regulatory capital), MVA (initial margin funding). Dealers have dedicated XVA desks managing aggregate adjustment exposure. XVA P&L can swing dramatically with market conditions. The 'pure mid' price (Black-Scholes-perfect, no adjustments) is increasingly an academic concept — XVAs are the price.",
        ["ISDA"],
        indications=["Derivatives"], category="Risk"),

    entry("Wrong-Way Risk", "WWR",
        "Counterparty credit exposure rises just when the counterparty's credit deteriorates.",
        "Classic example: bank sells CDS protection on a sovereign back to that sovereign's bank — both default trigger together. AIG's 2008 collapse: huge CDS protection sold on mortgages, hammered when housing tanked, exactly when AIG itself was failing. Basel III imposes specific WWR capital charges. Hard to model; recognition is qualitative and judgment-based.",
        ["BIS", "ISDA"],
        indications=["Credit"], category="Risk"),

    entry("Right-Way Risk", "",
        "Counterparty credit exposure declines just when their credit deteriorates — favourable case.",
        "Opposite of wrong-way risk. Example: bank lends to oil producer collateralised by oil reserves — if oil prices crash (hurting producer credit), collateral value falls together but bank's claim becomes less valuable when most needed. Less common than WWR in practice. Some collateralised lending structures inherently produce right-way risk (loans collateralised by counterparty-correlated assets).",
        ["BIS"],
        indications=["Credit"], category="Risk"),

    entry("Concentration Risk", "",
        "Risk from large exposure to a single name, sector, geography, or risk factor.",
        "Pension funds limit single-name equity exposure to 5-10 percent typically. Bank lending concentrated in single industries (commercial real estate, energy) historically caused failures. The 2023 SVB collapse: concentrated tech-VC client base, long-duration asset book — twin concentration risks. Basel large-exposure regime limits single-counterparty bank exposure to 25 percent of Tier 1 capital. Diversification is the main mitigation.",
        ["BIS"],
        indications=["Cross-asset"], category="Risk"),

    entry("Liquidity Risk", "",
        "Risk that an institution cannot meet payment obligations as they fall due.",
        "Distinct from solvency risk (insufficient assets to cover liabilities). Liquidity risk caused multiple 2008 failures (Bear Stearns, Lehman) and 2023 SVB — institutions had assets but couldn't convert them to cash fast enough. Mitigations: LCR requirement, NSFR requirement, contingent funding plans. Market liquidity risk versus funding liquidity risk are related but distinct concepts. Treasury market liquidity stress periodic.",
        ["BIS"],
        indications=["Cross-asset"], category="Risk"),

    entry("Operational Risk", "",
        "Risk of loss from inadequate or failed internal processes, people, systems, or external events.",
        "Examples: rogue traders (Barings 1995, SocGen 2008 Kerviel), settlement failures, IT outages, cyber attacks, fraud, natural disasters. Basel II/III imposes operational-risk capital — banks can use Standardised approach (income-based) or AMA (modelled). Multi-billion losses from operational risk are sadly routine: BNP Paribas 9-billion sanctions penalty 2014, JPMorgan whale 6-billion loss 2012. Hard to model.",
        ["BIS"],
        indications=["Cross-asset"], category="Risk"),

    entry("Model Risk", "",
        "Risk of loss from using inaccurate or inappropriate financial models.",
        "Models are simplifications. Black-Scholes assumes constant volatility — markets show vol smile. Copula models for mortgage CDOs missed correlation breakdowns. The 1998 LTCM crisis and 2008 mortgage debacle were partly model risk. Fed SR 11-7 letter (2011) mandates US bank model risk management: independent validation, ongoing performance monitoring, governance. CRO functions take model risk seriously post-crisis.",
        ["Federal Reserve", "BIS"],
        indications=["Cross-asset"], category="Risk"),

    entry("Tail Risk", "",
        "Risk of extreme outcomes — events in the tails of return distributions.",
        "Financial markets have fatter tails than Gaussian models suggest. Examples: 1987 crash (22 percent in one day, a 20-sigma event under Gaussian assumptions), 2008 Lehman week, March 2020 COVID crash, 2022 Russia-Ukraine equity vol. Standard portfolios underestimate tail risk; portfolios benefit from explicit tail hedges (long-vol, long Treasuries, gold). Nassim Taleb's 'Black Swan' framework popularised tail-risk thinking.",
        ["CFA Institute"],
        indications=["Cross-asset"], category="Risk"),

    entry("Black Swan", "",
        "Rare, high-impact event that is hard to predict and rationalised in hindsight.",
        "Coined by Nassim Taleb (2007 book). The 2008 financial crisis, 2020 pandemic, 2022 Ukraine invasion arguably fit. Reframes risk management: focus less on predicting probability of extreme events (impossible), more on building robustness to surprises. Critics argue 'black swan' has become overused — some events labelled black swans were predictable in advance.",
        ["CFA Institute"],
        indications=["Cross-asset"], category="Risk"),

    entry("Risk Parity", "",
        "Portfolio allocation method that equalises risk contributions across asset classes.",
        "Pioneered by Bridgewater's All Weather Fund (Ray Dalio). Traditional 60/40 portfolios have most risk from equities; risk parity adds significant fixed-income exposure scaled up via leverage to equalise risk contributions. Performed well 2008-2020 (rates falling, equity/bond negative correlation). Hit hard in 2022 as both equities and bonds fell together. AQR's risk-parity strategies have been industry leaders alongside Bridgewater.",
        ["CFA Institute"],
        indications=["Cross-asset"], category="Quantitative"),

    entry("Drawdown", "",
        "Peak-to-trough decline in portfolio value during a specific period.",
        "Measured from each high-water mark forward. A portfolio at 100 drops to 80 then recovers — 20 percent drawdown. Maximum drawdown is the largest peak-to-trough fall over the entire history. Used as a risk measure alongside volatility — drawdown captures investor experience better than annualised volatility. Behavioural impact: investors panic on big drawdowns regardless of long-term return.",
        ["CFA Institute"],
        indications=["Cross-asset"], category="Risk"),

    entry("Maximum Drawdown", "Max DD",
        "Worst peak-to-trough loss observed over a portfolio's history.",
        "Common headline risk metric for hedge funds and asset managers. S&P 500 maximum drawdown: 86 percent (Great Depression), 57 percent (2007-09), 34 percent (March 2020). Recovery time after maximum drawdown often longer than the drawdown itself. Used in performance evaluation: high Sharpe with low max DD is the holy grail. Calmar ratio = annualised return divided by max DD.",
        ["CFA Institute"],
        indications=["Cross-asset"], category="Risk"),

    entry("Sortino Ratio", "",
        "Risk-adjusted return measure using downside deviation rather than total volatility.",
        "Sharpe ratio penalises both upside and downside volatility equally; Sortino only counts downside. Calculation: excess return over downside standard deviation. Favoured by alternative-asset managers who argue upside vol is good. Higher Sortino values better. Limitations: less data robust than Sharpe (only counts negative returns), more sensitive to sample size. Tracked alongside Sharpe in modern performance reporting.",
        ["CFA Institute"],
        indications=["Cross-asset"], category="Pricing & Valuation"),

    entry("Information Ratio", "",
        "Excess return over benchmark divided by tracking error — active-management skill metric.",
        "Tells you how much active risk a manager takes per unit of active return. High IR (1.0+) signals genuine alpha; low IR (below 0.3) suggests luck or expensive tracking. Compared with Sharpe (uses risk-free rate as benchmark). Active equity managers' IRs have been declining secularly as markets become more efficient. The 0.5 IR threshold separates institutional-grade active managers from average.",
        ["CFA Institute"],
        indications=["Cross-asset"], category="Pricing & Valuation"),
]


# ============================================================================
# BATCH 24 — Quantitative methods (25 terms — CAPM, factors, pairs, GARCH, backtest)
# ============================================================================

BATCH_QUANT = [
    entry("CAPM", "Capital Asset Pricing Model",
        "Theoretical model relating expected return to beta — the foundational asset-pricing equation.",
        "Expected return equals risk-free rate plus beta times market risk premium. Published 1964-66 by Sharpe, Lintner, Mossin. Single-factor model — every asset's expected return depends only on market beta. Empirical evidence shows CAPM systematically under-prices low-beta stocks and over-prices high-beta — leading to multi-factor extensions. Still the cornerstone of academic finance and undergraduate textbooks. Sharpe won 1990 Nobel.",
        ["CFA Institute"],
        indications=["Equities"], category="Quantitative"),

    entry("Beta", "",
        "Stock's sensitivity to market moves — slope of regression against market return.",
        "Market index beta = 1.0 by definition. High-beta stocks (tech 1.3+) amplify market moves; low-beta stocks (utilities 0.5) dampen them. Negative beta is rare (gold mining stocks occasionally). Historic beta uses past returns; forward beta predicts. Used in CAPM, factor models, portfolio risk decomposition. The 'low-beta anomaly' — low-beta stocks outperforming risk-adjusted — is one of the persistent findings in empirical finance.",
        ["CFA Institute"],
        indications=["Equities"], category="Pricing & Valuation"),

    entry("Alpha", "Active Return",
        "Excess return over a benchmark, adjusted for risk — measure of investment skill.",
        "Jensen's alpha (1968): observed return minus CAPM-predicted return. Positive alpha signals stock-picking or timing skill. Persistent alpha is rare and contested. After fees, most active mutual funds underperform benchmarks (SPIVA reports). Hedge fund alpha typically small after fees and survivorship bias corrections. Modern factor models often reattribute 'alpha' to factor exposures, suggesting much active outperformance is factor beta in disguise.",
        ["CFA Institute"],
        indications=["Equities"], category="Pricing & Valuation"),

    entry("Sharpe Ratio", "",
        "Risk-adjusted return — excess return over risk-free rate divided by return volatility.",
        "Bill Sharpe's 1966 ratio: (return minus risk-free rate) divided by standard deviation. Higher is better. S&P 500 long-run Sharpe roughly 0.4. Hedge funds claim 1.0+ Sharpe — often inflated by smoothed returns, selection bias. The 0.5-1.0 Sharpe range covers legitimate institutional managers. Doesn't distinguish upside from downside vol (see Sortino). Asymmetric returns and non-normality limit interpretability for many strategies.",
        ["CFA Institute"],
        indications=["Cross-asset"], category="Pricing & Valuation"),

    entry("APT", "Arbitrage Pricing Theory",
        "Multi-factor extension of CAPM — expected return depends on multiple risk factor exposures.",
        "Stephen Ross's 1976 framework. Foundation for modern factor models. APT itself doesn't specify which factors matter — empirical work fills that in. Fama-French and successors built on APT logic. The 'no-arbitrage' principle: if two portfolios have the same factor exposures, they must have the same expected return. Underpins modern asset-pricing research and factor-investing practice.",
        ["CFA Institute"],
        indications=["Equities"], category="Quantitative"),

    entry("Fama-French Three-Factor", "FF3",
        "Asset-pricing model adding size and value factors to CAPM market beta.",
        "Eugene Fama and Kenneth French (1992-93): excess return depends on market beta, size (small minus big), and value (high minus low book-to-market). Better fits historical returns than CAPM. Established that small-cap and value stocks earned premium historical returns. Spawned the 'factor zoo' of subsequent multi-factor models. Fama won 2013 Nobel partly for this work.",
        ["CFA Institute"],
        indications=["Equities"], category="Quantitative"),

    entry("Fama-French Five-Factor", "FF5",
        "Extension adding profitability and investment factors to FF3.",
        "Fama-French (2015) added robust-minus-weak (RMW) profitability factor and conservative-minus-aggressive (CMA) investment factor. Better fit than FF3 in modern data. Profitability and investment factors largely subsume the value factor's explanatory power. Adding momentum (Carhart 1997) and quality factors expands further. Modern factor investing (smart beta) typically uses five to ten factors.",
        ["CFA Institute"],
        indications=["Equities"], category="Quantitative"),

    entry("Correlation", "Pearson Correlation",
        "Statistical measure of how two variables move together — ranges from -1 to +1.",
        "Critical input to portfolio construction, factor models, hedging. Equity correlation rises in stress (the 'correlation goes to 1' phenomenon) — exactly when diversification is most needed. Spurious correlations common with short samples. Correlation doesn't imply causation (famous statistical caveat). Rolling correlations capture time variation; copulas extend beyond simple correlation. The 2008 mortgage CDO debacle exposed catastrophic correlation-model failures.",
        ["CFA Institute"],
        indications=["Cross-asset"], category="Quantitative"),

    entry("Cointegration", "",
        "Two non-stationary time series whose linear combination is stationary — they share a long-run equilibrium.",
        "Engle-Granger test (1987 Nobel) is the standard cointegration test. Used in pairs trading: identify stocks/instruments that tend to revert to a long-run ratio. The pairs trade buys the underpriced side and shorts the overpriced side, profiting from convergence. Statistical arbitrage shops run hundreds of cointegrated pairs simultaneously. Famous example: gold versus gold miners; Coca-Cola versus Pepsi.",
        ["CFA Institute"],
        indications=["Cross-asset"], category="Quantitative"),

    entry("Statistical Arbitrage", "Stat Arb",
        "Quantitative strategy exploiting short-term price deviations from statistical patterns.",
        "Pioneered by Morgan Stanley's APT desk (1980s) and David Shaw's DE Shaw (1988). Two main flavours: pairs trading (mean reversion between related instruments) and broader equity stat arb (industry-neutral factor exposures). Modern stat arb is dominated by Two Sigma, Renaissance, AQR, Citadel. Annual returns have compressed as the field has grown but still significant for top performers.",
        ["CFA Institute"],
        indications=["Equities"], category="Trading & Execution"),

    entry("Pairs Trading", "",
        "Long one security, short a correlated one — profit from mean reversion of the spread.",
        "Classic stat arb strategy. Identify pairs that historically move together (Coke-Pepsi, Ford-GM, gold-gold miners). When the ratio diverges from historical mean, bet on convergence. Equity neutral by construction. Modern algos systematically scan thousands of potential pairs. Variants: index pairs (long index, short component basket), commodity pairs (corn-soybeans, Brent-WTI). Drawdowns when historical relationships break.",
        ["CFA Institute"],
        indications=["Equities"], category="Trading & Execution"),

    entry("Mean Reversion", "",
        "Tendency of prices to return to a long-run average — opposite of trend following.",
        "Persistent in short-term equity returns and FX. Long-term valuation metrics (P/E, P/B) mean revert over decades. Used in pairs trading, low-volatility strategies, contrarian investing. The 1990s convergence trades (LTCM, Salomon) bet on mean reversion of credit spreads — devastatingly when reversion took too long. Asymmetric: mean reversion in calm markets, momentum in stress.",
        ["CFA Institute"],
        indications=["Cross-asset"], category="Quantitative"),

    entry("Momentum", "Trend Following",
        "Strategy buying past winners and selling past losers — exploits persistent return patterns.",
        "Jegadeesh-Titman (1993) found momentum factor robust in equity markets. CTAs systematically trend-follow across futures markets. Long-run momentum returns: 8-10 percent annualised, low correlation to stocks/bonds. Spectacular drawdowns when trends reverse: 2009 momentum crash, 2020 March pandemic flip. Counterintuitive to value investors — but documented in 200+ academic papers across asset classes.",
        ["CFA Institute"],
        indications=["Cross-asset"], category="Quantitative"),

    entry("Factor Investing", "",
        "Systematic strategy targeting specific risk factors (value, momentum, quality, size, low-vol).",
        "Pioneered by Dimensional (1981) and now mainstream via iShares, Vanguard factor ETFs. Smart Beta is the marketing label. Trillions invested globally. The 2018-2022 'value drawdown' was painful for value-tilted factor funds; the 2024 recovery partially offset. Critics argue factor premiums have shrunk with capital flows; supporters note long-run statistical evidence remains. Multi-factor blends popular over single-factor exposures.",
        ["MSCI", "CFA Institute"],
        indications=["Equities"], category="Quantitative"),

    entry("Smart Beta", "",
        "ETFs and indexes weighting by factors rather than market cap.",
        "Equal-weighted, fundamentally weighted (revenue, earnings), low-vol, dividend-weighted, multi-factor. Roughly 1.5 trillion in US smart-beta ETFs. Largest sponsors: BlackRock iShares, Invesco, Vanguard, WisdomTree. Performance depends on factor exposure — value-tilted smart beta underperformed cap-weighted 2014-2022, then partially recovered. Cheaper than active funds but more expensive than vanilla cap-weighted.",
        ["MSCI", "FTSE Russell"],
        indications=["Equities"], category="Quantitative"),

    entry("Tracking Error", "",
        "Standard deviation of return differences between a portfolio and its benchmark.",
        "Measure of active risk. Pure index funds: 0-0.2 percent tracking error. Active equity managers: 2-6 percent typical. Hedge funds and concentrated portfolios: higher still. Information Ratio = alpha divided by tracking error — measures skill per unit of active risk. Excessive tracking error in benchmark-aware portfolios attracts client scrutiny. Optimisation algorithms aim to minimise tracking error subject to other constraints.",
        ["CFA Institute"],
        indications=["Cross-asset"], category="Pricing & Valuation"),

    entry("Beta-Neutral", "Market-Neutral",
        "Portfolio constructed to have zero net beta to the market — equal long and short market exposure.",
        "Standard hedge-fund category. Long-short equity, market-neutral pairs, equity stat arb. Aims for absolute returns independent of market direction. Generally lower returns and lower volatility than long-only equity. The 2007 Quant Quake (August 2007) hit market-neutral hedge funds particularly hard as positions unwound simultaneously. Industry has matured; volatility lower than 2008-09 extremes.",
        ["CFA Institute"],
        indications=["Equities"], category="Quantitative"),

    entry("PCA", "Principal Component Analysis",
        "Statistical technique decomposing data into uncorrelated factors ranked by explained variance.",
        "In fixed income: first three PCs of yield-curve moves capture level (parallel shift), slope (steepening/flattening), curvature (butterfly) — explain ~99 percent of curve variance. In equity: PCs identify dominant industry or factor exposures. Used in factor model construction, dimensionality reduction for ML models, scenario design. The mathematical foundation for many risk-modelling and stat-arb approaches.",
        ["CFA Institute"],
        indications=["Cross-asset"], category="Quantitative"),

    entry("Regime Switching", "",
        "Statistical model where the data-generating process changes between distinct states.",
        "Markov regime switching models (Hamilton 1989) capture market state transitions: low-vol versus high-vol regimes, bull versus bear regimes. Useful for capturing structural breaks (1990s low-vol period, 2008-09 stress, 2020 COVID). Forecasting regime changes ex ante is hard; identifying current regime usually easier. Used in dynamic asset allocation, volatility forecasting, signal generation.",
        ["CFA Institute"],
        indications=["Cross-asset"], category="Quantitative"),

    entry("GARCH", "Generalised Autoregressive Conditional Heteroskedasticity",
        "Time-series model for volatility — captures volatility clustering and persistence.",
        "Engle (1982) introduced ARCH; Bollerslev (1986) generalised to GARCH. Captures the fact that volatility comes in clusters (high-vol periods follow high-vol days). GARCH(1,1) is the workhorse model in finance. Used in VaR, option pricing, risk forecasting. Recent extensions: HEAVY-GARCH (with high-frequency data), realised-GARCH, multivariate GARCH. Engle won 2003 Nobel partly for ARCH.",
        ["CFA Institute"],
        indications=["Cross-asset"], category="Quantitative"),

    entry("EWMA", "Exponentially Weighted Moving Average",
        "Volatility estimator giving more weight to recent observations — common in trading.",
        "Variants: RiskMetrics (JP Morgan 1996) uses lambda = 0.94 for daily data. Simple, fast, transparent. Doesn't capture vol clustering as fully as GARCH but easier to implement and maintain. Used in much of bank risk-system infrastructure. Equivalent to a special case of GARCH model with constrained parameters. The standard pre-GARCH volatility model used by trading desks for decades.",
        ["CFA Institute", "BIS"],
        indications=["Cross-asset"], category="Quantitative"),

    entry("Bootstrap", "Statistical Bootstrap",
        "Resampling technique generating statistical estimates without parametric assumptions.",
        "Bradley Efron (1979). Resample with replacement from observed data to create alternative samples; compute statistics on each; build empirical distribution. Used for confidence intervals, hypothesis tests, model validation without distributional assumptions. Block bootstrap preserves time-series dependence. Common in modern empirical finance and quant strategy validation.",
        ["CFA Institute"],
        indications=["Cross-asset"], category="Quantitative"),

    entry("Backtesting", "",
        "Testing a strategy on historical data to evaluate its performance.",
        "Essential for systematic strategy development. Pitfalls: data-mining bias (testing too many strategies), look-ahead bias (using future information), survivorship bias (using only surviving stocks), transaction-cost neglect. Walk-forward analysis: split data into training and out-of-sample test sets. Cross-validation. Most backtests overestimate live trading performance — a 2x reduction is rule of thumb. Standard in quant research.",
        ["CFA Institute"],
        indications=["Cross-asset"], category="Quantitative"),

    entry("Stochastic Process", "",
        "Mathematical model for systems evolving randomly over time.",
        "Foundational to derivative pricing and quant modelling. Common examples: Brownian motion (continuous random walk — Black-Scholes), Ornstein-Uhlenbeck process (mean-reverting), Poisson process (jumps), Levy processes (broader fat-tailed class). The choice of stochastic process shapes pricing models. Calibration to historical data and option prices selects the process and parameters that fit best.",
        ["CFA Institute"],
        indications=["Derivatives"], category="Quantitative"),

    entry("Quant Quake", "",
        "August 2007 systematic strategy crash — many market-neutral funds lost 10-20 percent in a week.",
        "Crowded positions in similar quant signals unwound simultaneously. Likely triggered by initial subprime-related fund liquidations forcing wider deleveraging. Affected stat arb, market-neutral, factor strategies. Recovered by year-end but many funds had taken structural losses. Highlighted concentration risk in seemingly diversified quant strategies — many models had similar inputs and similar trades.",
        ["CFA Institute"],
        indications=["Equities"], category="Risk"),
]


# ============================================================================
# BATCH 25 — Basics gap-fill + Q/X/Z letter coverage (25 terms)
# ============================================================================

BATCH_GAP_FILL = [
    entry("Asset", "",
        "Anything of value owned by a person or company — generates future economic benefit.",
        "Three broad categories: financial (cash, bonds, stocks), real (property, equipment), intangible (patents, brand value). Total US household financial assets approach 100 trillion dollars (2024). Bank balance sheets distinguish between trading-book and banking-book assets, each with different accounting and regulatory treatment. Foundation of every financial statement and balance-sheet analysis.",
        ["SEC", "CFA Institute"],
        indications=["Cross-asset"], category="Instruments"),

    entry("Liability", "",
        "Obligation a person or company owes to another party.",
        "Categories: current liabilities (due within 12 months), long-term liabilities (mortgages, multi-year debt). Bank liabilities are mostly deposits (customer money owed back). For corporates: accounts payable, accrued expenses, long-term debt, deferred tax liabilities. The balance-sheet identity: Assets = Liabilities + Equity. Pension obligations are a major hidden liability for many corporates and governments.",
        ["SEC", "CFA Institute"],
        indications=["Cross-asset"], category="Instruments"),

    entry("Interest Rate", "",
        "Cost of borrowing money, expressed as a percentage of principal per year.",
        "Different rates for different purposes and risks: federal funds rate (overnight bank lending), Treasury yields (risk-free for various maturities), mortgage rates (consumer borrowing), corporate bond yields (corporate borrowing). The 'risk-free rate' anchors all other rates plus credit spreads. Real rates strip out inflation expectations; nominal rates are what's quoted publicly. Drive valuations across asset classes.",
        ["Federal Reserve", "Federal Reserve FRED"],
        indications=["Rates", "Macro"], category="Pricing & Valuation"),

    entry("Inflation", "",
        "Sustained rise in the general price level of goods and services.",
        "Measured by various indexes: CPI (consumer prices, US BLS), PCE (Fed's preferred, US BEA), HICP (EU), RPI (UK). Drivers: demand pull (too much money chasing too few goods), cost push (rising input costs), expectations (self-fulfilling). The 2021-2022 US inflation surge took CPI to 9 percent; back near 3 percent by 2024. Hyperinflation is the extreme version; deflation is the negative version.",
        ["Federal Reserve FRED", "World Bank"],
        indications=["Macro"], category="Pricing & Valuation"),

    entry("Bull Market", "",
        "Rising market — typically 20-plus percent above a recent low.",
        "Often used for equity markets but applies broadly. Average post-WWII US bull market: 60 months, 175 percent S&P gain. Recent bulls: March 2009 to February 2020 (132 percent gain), 2020 lows to current. Sentiment shifts during bull markets: skepticism, hope, optimism, euphoria. Famous bull-market peaks: 1929 (Depression), 2000 (dot-com), 2007 (financial crisis). Each ends differently.",
        ["Federal Reserve FRED"],
        indications=["Equities"], category="Pricing & Valuation"),

    entry("Bear Market", "",
        "Falling market — typically 20-plus percent below a recent high.",
        "Average post-WWII US bear market: 13 months, 35 percent S&P decline. Notable bears: 1929-32 (89 percent decline), 1973-74 (48 percent), 2000-02 (49 percent), 2007-09 (57 percent), 2020 (34 percent), 2022 (25 percent). Bear-market psychology: denial, anger, fear, capitulation. Sometimes followed by bear-market rallies that retest lows.",
        ["Federal Reserve FRED"],
        indications=["Equities"], category="Pricing & Valuation"),

    entry("Volatility", "Vol",
        "Statistical measure of price variability — typically annualised standard deviation of returns.",
        "Higher volatility means bigger price swings. Equity vol typically 15-20 percent annual; safe-haven currencies (CHF, JPY) lower; emerging-market FX higher. Implied vol (from options) versus realised vol (from historical prices) the basic distinction. Volatility clusters — high-vol periods follow high-vol days (the GARCH effect). Mean-reverts to long-run averages, but slowly.",
        ["CBOE", "CFA Institute"],
        indications=["Cross-asset", "Derivatives"], category="Risk"),

    entry("Liquidity", "",
        "Ease with which an asset can be bought or sold without affecting its price.",
        "Highly liquid: cash, Treasuries, large-cap stocks. Less liquid: corporate bonds, emerging-market equities, real estate, private equity stakes. Two flavours: market liquidity (can you trade now?) and funding liquidity (can you borrow against the asset?). Liquidity disappears in crises — 2008 commercial paper markets, March 2020 Treasury markets briefly. Bank Liquidity Coverage Ratio aims to ensure short-term funding resilience.",
        ["BIS", "Federal Reserve"],
        indications=["Cross-asset"], category="Market Structure"),

    entry("Bid", "Bid Price",
        "Highest price a buyer is currently willing to pay for an asset.",
        "Half of the bid-ask spread. The 'best bid' is the highest among multiple buyers; sub-best bids stack behind in the order book. Market orders to sell execute at the bid. Lifting the offer means buying at the offer; hitting the bid means selling at the bid. NBBO (National Best Bid and Offer) is the consolidated bid across US equity venues.",
        ["NYSE", "Nasdaq"],
        indications=["Cross-asset"], category="Market Structure"),

    entry("Ask", "Offer / Ask Price",
        "Lowest price at which a seller is currently willing to sell an asset.",
        "Other half of bid-ask spread. The 'best offer' is the lowest among multiple sellers. Market orders to buy execute at the offer. Often called 'offer' interchangeably. The spread between bid and offer is the dealer's compensation for providing liquidity. Wider spreads in illiquid securities; pennies in major equities. EU/UK markets sometimes use 'offer' instead of 'ask' as the convention.",
        ["NYSE", "Nasdaq"],
        indications=["Cross-asset"], category="Market Structure"),

    entry("Hedge", "",
        "Position taken to reduce exposure to a specific risk.",
        "Examples: oil company buying crude futures to lock in revenue; airline buying jet fuel futures; corporate borrower swapping floating-rate debt to fixed; portfolio manager buying VIX to hedge equity tail risk. Hedge effectiveness measured by reduction in P&L volatility. Imperfect hedges (basis risk) common — perfect hedges are rare. Distinct from speculation which seeks to profit from market moves.",
        ["CFA Institute"],
        indications=["Cross-asset"], category="Trading & Execution"),

    entry("Arbitrage", "Arb",
        "Risk-free profit from simultaneous buying and selling of related instruments.",
        "Pure arbitrage: same security trading at different prices on different exchanges (rare in modern markets). Statistical arbitrage: short-term pricing relationships expected to revert. Convertible arbitrage: long convertible bonds, short the stock and bond components. Capital structure arbitrage: long one debt class, short another. Modern markets have shrunk most pure arb opportunities to milliseconds via HFT.",
        ["CFA Institute"],
        indications=["Cross-asset"], category="Trading & Execution"),

    entry("Leverage", "",
        "Borrowed money used to amplify investment returns or business returns.",
        "Financial leverage (corporate debt to equity), operational leverage (fixed costs as percentage of total). 2x leverage doubles returns but also doubles losses. Banks operate at 10x leverage typical (Tier 1 ratio inverse). Hedge funds at 3-5x. The 2008 crisis exposed dangers of high financial leverage — Lehman ran at 30x. Modern Basel rules cap bank leverage explicitly.",
        ["BIS", "CFA Institute"],
        indications=["Cross-asset"], category="Risk"),

    entry("Margin", "",
        "Borrowed money used to buy securities; collateral posted against trading positions.",
        "Two contexts: margin loans (broker lends, security as collateral) and derivative margin (collateral posted with clearing house). Margin lending: Fed's Regulation T limits initial margin to 50 percent for equity. Variation margin: daily settlement of P&L on derivatives. Initial margin: prudential buffer at trade inception. Margin calls force position liquidation if collateral runs short.",
        ["Federal Reserve", "SEC"],
        indications=["Cross-asset"], category="Risk"),

    entry("Short Selling", "Shorting",
        "Selling borrowed shares with intent to buy back later at a lower price.",
        "Borrower pays a fee to the share lender; profits if the stock falls. Open-ended risk on the upside (no cap on how high a stock can go). Used for speculation, hedging long positions, statistical arbitrage. Famous short squeezes: Volkswagen (2008), GameStop (2021). Regulators have temporarily banned shorting in specific stocks during crises (banking sector 2008). Reg SHO mandates locate before shorting in the US.",
        ["SEC", "FINRA"],
        indications=["Equities"], category="Trading & Execution"),

    entry("Long Position", "",
        "Holding an asset with expectation of price appreciation.",
        "The opposite of short. 'Going long' means buying. Long-only funds (most mutual funds, pension funds) only take long positions. Long-short funds combine both. Long exposure determines economic interest — even via derivatives or synthetic positions. Net long exposure is total long minus total short across a portfolio.",
        ["SEC", "CFA Institute"],
        indications=["Cross-asset"], category="Trading & Execution"),

    entry("Derivative", "",
        "Financial instrument whose value derives from an underlying asset, rate, or index.",
        "Categories: futures (exchange-traded), forwards (OTC), options (call/put), swaps (rate, currency, credit). Notional outstanding globally: roughly 600 trillion dollars. Used for hedging, speculation, and synthetic exposure. Post-2008 Dodd-Frank reforms forced standardised derivatives onto central clearing. The 2008 crisis was partly an opaque-derivatives crisis (mortgage CDOs, AIG's CDS book).",
        ["ISDA", "BIS"],
        indications=["Derivatives"], category="Instruments"),

    entry("Call Option", "Call",
        "Option giving the right to buy the underlying at a strike price by expiry.",
        "Long call: holder buys, pays premium, profits if underlying rallies above strike plus premium. Short call (naked): writer collects premium, unlimited loss potential if underlying rallies — covered calls offset by owning the underlying. Common in hedging and speculation. American calls on dividend-paying stocks can be optimal to exercise early just before ex-dividend dates; European calls cannot be early-exercised.",
        ["CBOE", "SEC"],
        indications=["Derivatives", "Equities"], category="Instruments"),

    entry("Put Option", "Put",
        "Option giving the right to sell the underlying at a strike price by expiry.",
        "Long put: holder profits if underlying falls below strike minus premium. Protective puts hedge long positions (limit downside while keeping upside). Naked short puts: writer collects premium, takes downside risk (limited to strike minus premium). Cash-secured puts: collateralised by cash, common in income strategies. Tail-risk hedging often uses far out-of-money puts. The 1987 crash drove the persistent equity skew toward put premium.",
        ["CBOE", "SEC"],
        indications=["Derivatives", "Equities"], category="Instruments"),

    entry("ETF", "Exchange-Traded Fund",
        "Investment fund traded on an exchange like a stock.",
        "Tracks an index, sector, theme, or actively managed strategy. Major issuers: BlackRock iShares, Vanguard, State Street SPDR, Invesco. Tax-efficient structure via in-kind creation/redemption avoids capital-gains distributions. Global ETF AUM exceeds 12 trillion dollars (2024). The 2024 launch of US spot Bitcoin ETFs (IBIT, FBTC, others) attracted tens of billions in months.",
        ["SEC", "NYSE"],
        indications=["Equities"], category="Instruments"),

    entry("Mutual Fund", "",
        "Pooled investment vehicle collecting money from many investors to buy a diversified portfolio.",
        "Two main types: open-end (issue/redeem shares at NAV daily) and closed-end (fixed share count, trades on exchange). US mutual fund industry: 25-plus trillion in assets. Vanguard, Fidelity, BlackRock are largest managers. Subject to Investment Company Act of 1940 disclosure and conduct rules. ETFs (1990s onward) have stolen market share from mutual funds for cost and tax-efficiency reasons.",
        ["SEC"],
        indications=["Equities"], category="Instruments"),

    entry("Hedge Fund", "",
        "Lightly regulated investment fund — often uses leverage, derivatives, short selling.",
        "Limited to accredited investors. Charges performance fees (typically 20 percent of gains) plus management fees (1-2 percent). Strategies: long-short equity, global macro, event-driven, fixed-income arbitrage, multi-strategy. Industry AUM around 4 trillion dollars. Top funds: Citadel, Millennium, DE Shaw, Renaissance, Bridgewater. Performance varies enormously; average post-fee returns hardly beat S&P 500 in recent decades.",
        ["SEC"],
        indications=["Cross-asset"], category="Instruments"),

    entry("Private Equity", "PE",
        "Investment in private companies, often via leveraged buyouts.",
        "Major firms: Blackstone, KKR, Carlyle, Apollo, Bain Capital. Charge 2-and-20 fee structure (2 percent management, 20 percent carry). 10-year fund vehicles typical. AUM industry-wide approaches 8 trillion globally. Returns: roughly 11-12 percent net annualised long-run, with significant dispersion. Currently focused on continuation vehicles, secondaries, and special situations as exits have slowed since 2022.",
        ["SEC"],
        indications=["Equities"], category="Instruments"),

    entry("Diversification", "",
        "Spreading investments across uncorrelated assets to reduce portfolio risk.",
        "Modern portfolio theory (Markowitz 1952): optimal portfolios maximise return per unit of risk via diversification. International stocks, bonds, real estate, commodities offer different return drivers. Correlation matters — assets that move together don't diversify each other. Stress periods often see correlations rise toward 1 — 'diversification disappearing when you need it most'. The classic 60/40 portfolio (60 percent stocks, 40 percent bonds) is the canonical diversified portfolio.",
        ["CFA Institute"],
        indications=["Cross-asset"], category="Risk"),

    entry("Portfolio", "",
        "Collection of investments owned by a person or institution.",
        "Sized by total market value, characterised by asset allocation, risk metrics, and benchmark. Institutional portfolios: pension funds (15-30 trillion globally), sovereign wealth funds (10-trillion), endowments, foundations. Retail portfolios: brokerage accounts, retirement accounts, real estate. Portfolio construction balances return objectives, risk tolerance, liquidity needs, and time horizon. Rebalancing maintains target weights as markets move.",
        ["CFA Institute"],
        indications=["Cross-asset"], category="Trading & Execution"),

    entry("Counterparty", "",
        "Party on the other side of a financial transaction.",
        "Critical concept for derivatives, repo, securities lending. Counterparty risk: the other party may default before settlement. Mitigations: central clearing (interposes a CCP), netting agreements (ISDA), collateral (CSA), credit limits, monitoring. Pre-2008, OTC derivatives counterparty risk was largely unmonitored. Dodd-Frank and EMIR forced standardisation and clearing. Lehman 2008 demonstrated cascading counterparty failures.",
        ["ISDA", "BIS"],
        indications=["Cross-asset"], category="Market Structure"),

    entry("OTC", "Over-the-Counter",
        "Trading directly between two parties, off-exchange.",
        "Most fixed-income, FX, and complex derivatives trade OTC. Negotiated bilaterally rather than via centralised order book. Pricing varies by counterparty creditworthiness, size, market conditions. Less transparent than exchange trading. Post-2008 regulatory push moved standardised OTC derivatives onto central clearing and electronic trading platforms (SEFs, MTFs). Bespoke and complex products remain OTC.",
        ["SEC", "ISDA"],
        indications=["Cross-asset"], category="Market Structure"),

    entry("Quote", "",
        "Stated price at which a security is bid or offered.",
        "Two-sided quote: bid and offer. One-sided quote: bid only or offer only. Firm quote: commitment to trade at that price. Indicative quote: suggestion subject to confirmation. Quote currency: the currency expressing the price (USD in EUR/USD). Quote-driven markets (FX, OTC bonds): dealers quote prices. Order-driven markets (equities): order book aggregates limit orders into quotes.",
        ["NYSE", "Nasdaq"],
        indications=["Cross-asset"], category="Market Structure"),

    entry("Z-Score", "",
        "Number of standard deviations a value is from the mean.",
        "Statistical measure: (observation minus mean) divided by standard deviation. Z-score above 2 (or below -2) often used as 'unusual' threshold. Altman Z-score (1968) is the classic corporate-credit version: combines profitability, leverage, liquidity, solvency, asset-turnover ratios to predict bankruptcy. Z-score below 1.8 historically signals high distress risk. Many other Z-scores used in market regimes, sentiment, statistical anomaly detection.",
        ["CFA Institute"],
        indications=["Cross-asset"], category="Quantitative"),

    entry("Eurozone", "Euro Area",
        "19 EU countries (now 20 with Croatia 2023) using the euro as common currency.",
        "Created 1999 with 11 founding members. ECB sets common monetary policy. Common currency but separate fiscal policies — chronic tension during sovereign-debt crisis 2010-12 (Greece, Portugal, Ireland, Italy, Spain). 'Single currency, multiple sovereigns' design flaw partially addressed by ESM (2012) and OMT (Mario Draghi's whatever-it-takes). Banking union with Single Supervisory Mechanism (2014) further integrated.",
        ["ECB", "ESMA"],
        indications=["FX", "Macro"], category="Market Structure"),
]


BATCHES = {
    1: BATCH_SMOKE_TEST,
    2: BATCH_RATES_BASICS,
    3: BATCH_RATES_DEEP,
    4: BATCH_FX_SPOT,
    5: BATCH_FX_OPTIONS_EM,
    6: BATCH_EQUITIES_CASH,
    7: BATCH_EQUITY_DERIVS,
    8: BATCH_CREDIT_BONDS,
    9: BATCH_CREDIT_DERIVS,
    10: BATCH_COMMODITIES_ENERGY,
    11: BATCH_COMMODITIES_METALS_AGS,
    12: BATCH_DERIV_FUNDAMENTALS,
    13: BATCH_DERIV_EXOTICS,
    14: BATCH_MICROSTRUCTURE,
    15: BATCH_EXECUTION_ALGOS,
    16: BATCH_SETTLEMENT,
    17: BATCH_REGULATION_US_EU,
    18: BATCH_REGULATION_BASEL,
    19: BATCH_INDEXES,
    20: BATCH_CORP_ACTIONS,
    21: BATCH_MACRO_CB,
    22: BATCH_MACRO_FX_EM,
    23: BATCH_RISK,
    24: BATCH_QUANT,
    25: BATCH_GAP_FILL,
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
