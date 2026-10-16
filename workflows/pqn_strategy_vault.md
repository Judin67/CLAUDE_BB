# PQN Strategy Vault — build catalog

> **Source:** PyQuant News "Alpha Strategy Vault" (pro.pyquantnews.com), 66 strategy write-ups saved to Google Drive
> folder **`PQN strategy vault`** (folder id `1Fm8yz5CU-pXE9F3OgR_MmOqr4qOhbrpM`). Each Drive doc has the full
> write-up + pseudo-code; this file is the index, the rules as written, and the data-feasibility triage.
> **Triaged:** 2026-09-14, against Massive (Polygon) + free SEC EDGAR.
> **Status: PARKED** — potential future project, not on the build queue. WIP = 1: to build one, put that ONE
> strategy on `PROJECT_QUEUE.md` first.
> **Standalone:** these are PQN's rules as written. Do not blend them into Cascade / Dr. S / the low-float stack.

---

## Scoreboard

| Tier | Count | Meaning |
|---|---|---|
| ✅ A — ETFs, price only | 11 | Massive daily bars only |
| ✅ B — Calendar timing | 8 | One or two ETFs + a date calendar |
| ✅ C — Single stocks, price + market cap | 12 | Cross-sectional, no fundamentals |
| ✅ D — Single stocks + fundamentals | 12 | Massive financials / EDGAR XBRL |
| ✅ E — Short interest | 2 | Massive short-interest endpoint |
| ✅ F — Earnings-date event studies | 4 | Dates from EDGAR 8-K Item 2.02 |
| ✅ G — EDGAR filings (13F / text) | 2 | EDGAR only |
| ✅ H — Options | 1 | Conditional on options entitlement |
| 🟡 P — Partial / heavy lift | 3 | A required input has no clean source |
| ❌ X — Blocked | 11 | Required data not available |
| **Total** | **66** | **52 buildable** |

---

## Data map (what feeds what)

| Need | Source | Existing code to reuse |
|---|---|---|
| Daily OHLCV, stocks + ETFs | Massive `/v2/aggs/ticker/...`; whole market per day via `/v2/aggs/grouped/locale/us/market/stocks/{date}` | `tools/fetch_polygon.py` |
| Market cap / shares / SIC / type / delisted | Massive ticker reference | `tools/polygon_ref.py` |
| Fundamentals (assets, equity, EPS, R&D, cash flow) | Massive `/vX/reference/financials` + EDGAR XBRL `companyfacts` | `tools/edgar_client.py` (`latest_asof` = point-in-time), `tools/accel_decel.py`, `tools/fetch_earnings_trend.py` |
| Short interest | Massive `/stocks/v1/short-interest` (FINRA settlements) | `tools/short_float.py`, `tools/polygon_ref.py` |
| Float | Massive `/stocks/vX/float` (snapshot only) | `tools/short_float.py` |
| Earnings announcement dates | EDGAR 8-K Item 2.02 filing dates (Benzinga is 403) | `tools/revenue_backfill.py` already locates the earnings 8-K per quarter |
| 13F holdings | EDGAR 13F-HR information tables | `tools/edgar_client.py` |
| Filing text (10-K / 10-Q) | EDGAR `document_text` | `tools/edgar_client.py` |
| Treasury yields (risk-free, 10Y) | Massive `/fed/v1/*` | — |
| FX spot | Massive `C:EURUSD` style tickers | — |
| Options history | Massive options (**entitlement unverified**) | `tools/test_polygon_options.py` |
| **Blocked** | Indices asset class (no VIX / SPX), Benzinga (no estimates, no earnings calendar), ETF constituents, TMX calendar | see `reference_massive_entitlement_map` memory |

### Known traps that apply here
- `sic_code` **filter** on `/v3/reference/tickers` is silently ignored — read SIC per ticker instead (matters for industry grouping, REIT and financials exclusions).
- `/vX/reference/financials` **drops quarters** (documented in `tools/revenue_backfill.py`) — use EDGAR companyfacts as primary or backfill.
- Massive aggs `adjusted=true` adjusts for **splits only**, not dividends. Total-return comparisons (bond ETFs IEF/AGG/SHY, SPY-vs-SHY switches, pairs spreads) need dividends added.
- Short-interest settlement date ≠ publication date. Signal must use the date the number became public, or the backtest has look-ahead.

---

## ⚠ Open checks — run before the FIRST build (not yet verified)

1. **Price history depth** on the plan (earliest daily bar) — sets the backtest start for everything.
2. **Delisted-ticker coverage + point-in-time market cap / shares** — survivorship for every cross-sectional stock strategy (tiers C, D, E, F).
3. **Financials history depth** — how many years `/vX/reference/financials` and EDGAR XBRL give (tier D; R&D needs 5 years per firm).
4. **Short-interest history depth** (tier E).
5. **Options history entitlement** (H1; also the "active options market" filter in F3/F4).
6. **Futures entitlement** — if Massive futures are available, X9 and X10 move up, and A11 can use crude futures instead of USO.
7. **Treasury tenors** on `/fed/v1` — 3-month and 10-year (A11, P2).

---

## ✅ A — ETFs, price only (11)

### A1. Asset Class Trend-Following
[doc](https://docs.google.com/document/d/1JglHYFlMP9VWnPT7uHqczP59x5Nft6evbbvw_FhOHMo) · Strength: High · Difficulty: Beginner · Source: Faber, "A Quantitative Approach to Tactical Asset Allocation"
- **Thesis:** hold each asset-class ETF only while it trades above its 10-month SMA; otherwise that sleeve sits in cash.
- **Universe:** SPY, EFA, IEF, VNQ, GSG
- **Signal:** price vs 210-trading-day SMA (10 months × ~21)
- **Entry / exit:** hold when price > SMA; liquidate at ≤ SMA → cash
- **Weighting:** 1/N across ETFs passing the filter; 100% cash if none
- **Rebalance:** monthly, first trading session
- **Data:** daily closes → Massive aggs
- **Risk (per doc):** partial hedge — an exposure overlay, not a direct hedge

### A2. Momentum Asset Allocation
[doc](https://docs.google.com/document/d/1kN8RzAnnSj-pB-DfM5CgHTunXulrX-mpeg7j_ZyBRaI) · High · Beginner · Source: Faber (relative-strength variant); Kessler & Scherer, "Macro Momentum and the Economy"
- **Thesis:** rank asset classes by 12-month return, always hold the top three.
- **Universe:** SPY, EFA, IEF, VNQ, GSG
- **Signal:** trailing 12-month return (252 trading days)
- **Selection:** top 3; drop any that fall out of the top 3
- **Weighting:** 1/3 each; always fully invested
- **Rebalance:** monthly, first trading session
- **Data:** daily closes → Massive aggs
- **Risk:** partial hedge (overlay)

### A3. Sector Momentum – Rotational System
[doc](https://docs.google.com/document/d/1a_TrkiN1ZFNWx6D9ZpEQkwNGlza5pYnREeKvSsvVDa0) · High · Beginner · Source: Faber; Moskowitz & Grinblatt, "Do Industries Explain Momentum?"
- **Universe:** VNQ, XLK, XLE, XLV, XLF, XLI, XLB, XLY, XLP, XLU
- **Signal:** trailing 12-month return (252 trading days)
- **Selection:** top 3, equal weight (1/3)
- **Rebalance:** monthly
- **Data:** daily closes → Massive aggs
- **Risk:** long-only does not hedge. Doc mentions a variant: long top sectors / short the index.

### A4. Industry Momentum – Riding Industry Bubbles
[doc](https://docs.google.com/document/d/1wbZoB7rb2gKncGuYCkAsWooHJMdE2-EtBoMdhg1WxDU) · Moderate · Advanced · Source: research on riding asset-price bubbles (CAPM structural-break detection)
- **Thesis:** a statistically significant CAPM alpha = a bubble; ride it, exit mechanically when significance fades.
- **Universe:** XLF, XLV, XLP, XLY, XLI, XLE, XLB, XLK, XLU; SPY = market
- **Signal:** CAPM regression of sector monthly returns on SPY monthly returns over 120 months; bubble if alpha t-stat ≥ ~2.0
- **Entry / exit:** long every sector in a bubble; drop when no longer significant
- **Weighting:** 1/N across bubbled sectors; hold nothing if none
- **Rebalance:** monthly
- **Data:** daily closes → monthly returns → Massive aggs
- **Data note:** needs 120 monthly observations before the first signal.
- **Risk:** does not hedge

### A5. Momentum Factor and Style Rotation Effect
[doc](https://docs.google.com/document/d/1uTaBrM1b8uBAlTCfA03J52atKW4l4WXD8yZnCbn4-GM) · High · Beginner · Source: style-momentum literature
- **Universe:** IWS, IWP, IWN, IWO, IVE, IVW (mid/small/large × value/growth)
- **Signal:** 12-month momentum (252 trading days)
- **Positions:** 100% long the top style, 100% short the bottom style; flat the rest
- **Rebalance:** monthly
- **Data:** daily closes → Massive aggs
- **Risk:** long-short has low market correlation; hedge value not established

### A6. Paired Switching
[doc](https://docs.google.com/document/d/1_6rfZ8GuIf3KTHkPWz69aBWxZ6FHZZDdUHb3NSLBess) · Moderate · Beginner · Source: paired-switching research (original used VFINX / VUSTX)
- **Universe:** SPY and AGG
- **Signal:** trailing-quarter return (~90 calendar days ≈ 63 trading days)
- **Position:** 100% in whichever had the higher trailing-quarter return; never both
- **Rebalance:** quarterly, first trading day of the quarter
- **Data:** daily closes → Massive aggs (dividend-adjust AGG — split-only adjustment understates a bond fund)
- **Risk:** partial hedge (overlay)

### A7. Momentum Factor Effect in Country Equity Indexes
[doc](https://docs.google.com/document/d/1piimfk9FbbbethjO9JRWtxzow3wHsWgCKzXrlzO3rEE) · High · Beginner · Source: MSCI country-index momentum study (1970–2009); Andreu, Swinkels & Tjong-A-Tjoe; Bhojraj & Swaminathan
- **Universe:** EWA, EWO, EWK, EWZ, EWC, FXI, EWQ, EWG, EWH, EWI, EWJ, EWM, EWW, EWN, EWS, EZA, EWY, EWP, EWD, EWL, EWT, THD, EWU, SPY
- **Signal:** trailing return. The doc's implementation uses 6 months (126 days); the doc says studies favor 10–12 months.
- **Selection:** top 5, equal weight (1/5)
- **Rebalance:** monthly
- **Data:** daily closes → Massive aggs
- **⚠ Resolve before build:** lookback — 6 months (implementation) or 10–12 months (studies).
- **Risk:** no hedge; tends to load late-cycle emerging markets

### A8. Betting Against Beta – International Equities
[doc](https://docs.google.com/document/d/1EJxooz0QLoHpCUED8ZFV1G5avR0PcUtoGuJxVPrIzqQ) · High · Intermediate · Source: Frazzini & Pedersen, "Betting Against Beta"
- **Universe:** EWA, EWO, EWK, EWZ, EWC, FXI, EWQ, EWG, EWH, EWI, EWJ, EWM, EWW, EWN, EWS, EZA, EWY, EWP, EWD, EWL, EWT, THD, EWU; SPY = beta reference
- **Signal:** 252-day rolling beta of daily returns vs SPY
- **Construction:** split at median beta; within each side weight by distance from the median; lever the low-beta (long) leg and the high-beta (short) leg each to beta = 1; cap 5× per side
- **Rebalance:** monthly
- **Data:** daily closes → Massive aggs
- **Needs:** leverage + ETF shorting
- **Risk:** partial hedge; crowding can stretch low-beta valuations

### A9. Pairs Trading with Country ETFs
[doc](https://docs.google.com/document/d/1NaTrxGmqhb1mKFErgoIhLktCcVVARVlyDz11okL3Hxg) · Moderate · Advanced · Source: distance-method pairs trading applied to country ETFs
- **Universe:** 22 country ETFs (EWA … EWU list above) + SPY reference
- **Formation:** 120 trading days; normalize each series to $1; distance = sum of squared deviations between normalized series
- **Selection:** 5 tightest pairs; re-select each 20-day trading period
- **Entry:** spread > 0.5 SD from its mean → long the cheap leg, short the rich leg
- **Exit:** reconvergence, or force-close after 20 trading days
- **Weighting:** equal across the 5 pairs; monitor daily
- **Data:** daily closes → Massive aggs. The doc prefers total-return prices, so add dividends.
- **Risk:** small positive equity correlation per source — not a hedge

### A10. Reversal Effect in International Equity ETFs
[doc](https://docs.google.com/document/d/1vJc7mrxIWouW92oZpB-chb8FvuRdL-TG-KJZt2jLeko) · Moderate · Intermediate · Source: winner-loser reversal in 16 national indices; Balvers, Wu & Gilliland; Spierdijk, Bikker & Van den Hoek
- **Universe:** the country ETF list above + SPY
- **Signal:** trailing 36-month return (756 trading days)
- **Positions:** long the 4 worst, short the 4 best; ±1/4 each
- **Rebalance:** every three years
- **Data:** daily closes → Massive aggs
- **Data note:** rebalances are three years apart, so a backtest has very few independent periods.
- **Risk:** no hedge; losers can keep falling in a crisis

### A11. Crude Oil Predicts Equity Returns
[doc](https://docs.google.com/document/d/1vWZeA2aGAAhQ1-zru-zN91Jf86pRFcyxbGsAjSB9X9U) · Moderate · Intermediate · Source: Driesprong, Jacobsen & Maat, "Striking Oil: Another Puzzle?"
- **Doc universe:** E-mini S&P 500 continuous future (risky), crude oil continuous future (predictor), SHY (cash); risk-free = 3-month Treasury
- **Signal:** each month, OLS of equity return(t) on oil return(t−1) over all history (expanding window); minimum 13 months
- **Forecast:** intercept + slope × latest oil return
- **Position:** forecast > risk-free → 100% equity; otherwise 100% SHY
- **Rebalance:** monthly
- **Substitution (no futures in stack):** SPY for the S&P future, USO for crude. USO carries roll costs, so it is not identical to the crude future.
- **Data:** SPY / USO / SHY → Massive aggs; 3-month yield → Massive `/fed/v1` (open check #7)
- **Risk:** partial hedge (market timing)

---

## ✅ B — Calendar timing (8)

### B1. Turn of the Month in Equity Indexes
[doc](https://docs.google.com/document/d/155xMH35zOooazrZtnWIv_lOYaCAbUcNvEfPUN6s5cUM) · Moderate · Beginner · Source: McConnell & Xu, "Equity Returns at the Turn of the Month"; Lakonishok & Smidt (1988)
- **Universe:** SPY
- **Entry:** buy at the open one day before month end (some studies use four days before)
- **Exit:** sell at the close of the 3rd trading day of the new month
- **Position:** 100% in window, cash otherwise
- **Data:** daily OHLC → Massive aggs; trading-day calendar
- **Risk:** no hedge; calendar effects can drift

### B2. Payday Anomaly
[doc](https://docs.google.com/document/d/11iKmTCPy2mpSm3Qq7O-HPkHOABwNSSWmceOaTHZnrj4) · Moderate · Beginner · Source: payday / turn-of-month research (the 16th calendar day)
- **Universe:** SPY
- **Signal:** mid-month payday — semi-monthly pay on the 15th reaches the market on the 16th
- **Position:** 100% SPY for one session; cash otherwise
- **Data:** daily closes → Massive aggs
- **⚠ Resolve before build:** the doc's rule text and code disagree. Rules say "the 16th, rolled back to prior Friday if a weekend; buy into the close of that session, exit next day". Code computes the **15th** rolled to Friday and enters on that date. Decide which session's return is being captured (target = the 16th's session).
- **Risk:** no hedge; decaying as bi-weekly pay spreads

### B3. Pre-Holiday Effect
[doc](https://docs.google.com/document/d/14zmrK7AL44Jaui7IGrOa0G0YrY7NwQLqpkrLxbeqM2A) · Moderate · Beginner · Source: Zhang & Jacobsen, "Are Monthly Seasonals Real? A Three Century Perspective"
- **Universe:** SPY
- **Holidays (doc list):** New Year's, MLK, Presidents', Good Friday, Memorial, Independence, Labor, Election Day, Thanksgiving, Christmas
- **Entry:** 100% long on the trading day immediately before a market holiday (code: a holiday within the next 1–2 calendar days, weekends removed)
- **Exit:** back to cash after the pre-holiday session
- **Data:** daily closes → Massive aggs; historical exchange-holiday calendar from an exchange-calendar library (Massive's holiday endpoint is upcoming-only)
- **Data note:** NYSE has not closed for Election Day since 1980, so an exchange calendar will not trigger it.
- **Risk:** no hedge; effect diminished since late 1980s except small caps (per source)

### B4. Market Seasonality Effect ("Sell in May")
[doc](https://docs.google.com/document/d/1QyvrMw68hQbO6zLMTT0Z3A2Yrh2w8Snubm1MuHzVlI8) · Moderate · Beginner · Source: Bouman & Jacobsen, "The Halloween Indicator"
- **Universe:** SPY (SHY optional as defensive sleeve)
- **Entry:** start of November → 100% SPY
- **Exit:** start of May → cash
- **Rebalance:** two trades per year, checked on the first trading session of each month
- **Data:** daily closes → Massive aggs
- **Risk:** partial (overlay)

### B5. January Effect in Stocks
[doc](https://docs.google.com/document/d/1emd4lCGTKUzwLO6eaBAF9KXuf__KwveLJ-ZVQPEnsg0) · **Low** · Beginner · Source: Haug & Hirschey, "The January Effect"
- **Universe:** IWM (small-cap), SPY (large-cap)
- **Position:** 100% IWM in January; 100% SPY February–December
- **Rebalance:** first session of each month
- **Data:** daily closes → Massive aggs
- **Doc's own caveat:** effect decaying, may not survive costs

### B6. January Barometer
[doc](https://docs.google.com/document/d/1ssGNLSlF8xhMI01JS_y532ilXBt7yL2yVzVamAfpr40) · **Low** · Beginner · Source: Cooper, McConnell & Ovtchinnikov, "The Other January Effect"
- **Universe:** SPY, SHY
- **Rule:** 100% SPY in January. At the start of February: January return > 0 → stay SPY through year-end; otherwise 100% SHY through year-end.
- **Data:** daily closes → Massive aggs
- **Doc's own caveat:** weak rationale, likely data-mined, contested out of sample

### B7. Option-Expiration Week Effect
[doc](https://docs.google.com/document/d/1BNgEtbfsQ7PxprkF6t9_bIAGfiqhqXdVVI03IZcqh_4) · Moderate · Beginner · Source: option-expiration-week effect research (market-maker hedge rebalancing)
- **Universe:** OEF (S&P 100 ETF)
- **Signal:** monthly expiration = Friday before the third Saturday
- **Entry:** each Monday, if expiration is ≤ 5 days away → 100% OEF
- **Exit:** liquidate on expiration day
- **Data:** daily closes → Massive aggs; expiration dates computed from the calendar
- **Data note:** when that Friday is a market holiday, expiration moves to Thursday — the calendar must handle it.
- **Risk:** no hedge

### B8. FOMC Meeting Effect in Stocks
[doc](https://docs.google.com/document/d/11-bvVVTK2mwZZPnObZ9N2t23GOtiAe_8MRUMS2LjawI) · Moderate · Beginner · Source: FOMC calendar-effect study (S&P 500, 1960–2000)
- **Universe:** SPY
- **Entry:** buy at the close the day before each FOMC meeting
- **Exit:** sell at the close the day after the meeting
- **Position:** 100% long in the window (~8 per year), cash otherwise; doc notes it is a leverage candidate
- **Data:** daily closes → Massive aggs; **FOMC dates are not in Massive** (no economic calendar) → static list from federalreserve.gov
- **⚠ Resolve before build:** most meetings span two days — define "meeting date" (decision / statement day).
- **Risk:** no hedge

---

## ✅ C — Single stocks, price + market cap (12)

> Common data for this tier: daily bars for the whole cross-section (grouped daily is one call per date), dollar volume for liquidity ranks, market cap for size ranks, delisted tickers for survivorship (open check #2).

### C1. Momentum Factor Effect in Stocks
[doc](https://docs.google.com/document/d/1WAFaqL8mcwO6NX0gzM3KSgGXXoo1t9JpoU2P3_UZkcE) · High · Intermediate · Source: momentum "fact and fiction" article; Griffin, Ji & Martin; Barroso & Santa-Clara, "Managing the Risk of Momentum"
- **Universe:** top 500 by dollar volume on NYSE / NASDAQ / AMEX
- **Signal:** 12-1 momentum — return from 252 days ago to ~21 days ago (skip the latest month)
- **Positions:** long top quintile, short bottom quintile; equal weight (±1/N)
- **Rebalance:** monthly, month start
- **Risk:** momentum crashes after bear-market rebounds; doc points to volatility-scaled variants

### C2. Momentum Effect in Stocks in Small Portfolios
[doc](https://docs.google.com/document/d/1k3H-LCs2Ivh397m9ymtzdYa9vdMnapqaX1C-h7nlZrU) · Moderate · Intermediate · Source: Siganos (UK data); Ammann, Moellenbeck & Schmid
- **Source rules:** UK listings excluding smallest 25% by market cap; 10 most extreme names each side
- **Implementation:** top 500 US stocks; trailing 12-month return (252 days, no skip); long top decile, short bottom decile; equal weight
- **Rebalance:** yearly
- **Risk:** concentrated; momentum-crash prone

### C3. Consistent Momentum Strategy
[doc](https://docs.google.com/document/d/1ituRqBq-sZ8ufV2S2cKHSrAvoeeDGbMRWI_ZXJ6aXBc) · High · Intermediate · Source: firm-level momentum-consistency study
- **Universe:** top 500 by dollar volume, ≥ 7 months of history
- **Windows:** return t−7→t−1 months and return t−6→t months
- **Long:** top decile in **both** windows; **Short:** bottom decile in both
- **Timing:** one-month skip between formation and holding; hold 6 months, no rebalancing during the hold
- **Weighting:** equal
- **⚠ Resolve before build:** the doc's code indexes price windows newest-first (`w[0] / w[-1]`); confirm the window slicing matches the stated t−7→t−1 / t−6→t definitions.

### C4. Momentum and Reversal Combined with Volatility Effect
[doc](https://docs.google.com/document/d/17Futo0lXZWY8N1rv8_MF4Z6ctzwc3n9H2D9NAgRFbjw) · Moderate · Advanced · Source: momentum/reversal-by-volatility study (1964–2009); Chan, Jegadeesh & Lakonishok; Hong, Lim & Stein
- **Universe:** NYSE / AMEX / NASDAQ, price > $5, larger half by market cap (implementation: 1,000 most liquid, then larger half)
- **Signals:** 6-month return and annualized 6-month realized volatility, both skipping the most recent week (5 trading days)
- **Long:** top return quintile ∩ top volatility quintile; **Short:** bottom return quintile ∩ top volatility quintile
- **Weighting:** equal
- **Holding:** 6 months, overlapping tranches (1/6 of book per month)

### C5. 12 Month Cycle in Cross-Section of Stock Returns
[doc](https://docs.google.com/document/d/1caLFzVMFjjWbJ-1Kv5JPnH6yGXoMFxcibTA_kXzGteY) · Moderate · Advanced · Source: Heston & Sadka
- **Source universe:** top 30% by market cap, NYSE + AMEX. **Implementation:** top US stocks by market cap on NYSE / AMEX / NASDAQ (up to 500), REITs excluded.
- **Signal:** the stock's return in the same calendar month one year ago
- **Positions:** deciles; long winners, short losers
- **Weighting:** source = equal; implementation = market-cap weighted per leg
- **Rebalance:** monthly
- **Data:** REIT exclusion via SIC code, read per ticker

### C6. 52-Weeks High Effect (industry version)
[doc](https://docs.google.com/document/d/1wFWGfx_m4bkebNVzYgpNiXhMs2gDCrkjPcRBz_MsjGg) · Moderate · Advanced · Source: George & Hwang, "The 52-Week High and Momentum Investing" + industry extension
- **Universe:** top ~500 by dollar volume on NYSE / AMEX / NASDAQ, grouped by industry
- **Signal:** PRILAG = price ÷ 252-day high; industry score = market-cap-weighted average PRILAG
- **Positions:** long stocks in the 6 highest-scoring industries, short the 6 lowest
- **Weighting:** equal weight within selected industries
- **Holding:** 3 months, tranched (1/3 of book rebalanced each month); month-end evaluation
- **Data:** industry from SIC code per ticker (the list-endpoint SIC filter is silently ignored)
- **⚠ Resolve before build:** industry granularity — the doc does not say which SIC level defines an "industry".

### C7. Low Volatility Factor Effect in Stocks
[doc](https://docs.google.com/document/d/1dKtSYcmOGPTT17oaQhM4sB1ZboFT0jHL3wwN76CMA-U) · High · Intermediate · Source: global low-volatility study (1986–2006); Clarke, de Silva & Thorley; Baker, Bradley & Wurgler
- **Universe:** US large caps with fundamentals (implementation: top 3,000 by market cap)
- **Signal:** standard deviation of weekly returns
- **Selection:** lowest-volatility quartile (original study: lowest decile); equal weight; long-only
- **Rebalance:** monthly, month end
- **⚠ Resolve before build:** lookback — the doc says "past three years" but its code comment says "roughly 252 trading days".
- **Risk:** long-only softens drawdowns; long-short (lowest decile vs highest) is the hedge version

### C8. Betting Against Beta Factor in Stocks
[doc](https://docs.google.com/document/d/1L01M0INDTtNl8qy81L9VLr74vzpOIz_Nkxw2G1hKgiE) · High · Advanced · Source: Frazzini & Pedersen, "Betting Against Beta"
- **Universe:** 1,000 most liquid US stocks, price > $5; SPY = market
- **Signal:** 252-day beta vs SPY
- **Positions:** long bottom-beta decile, short top-beta decile
- **Leverage:** long leg × min(cap, 1 / mean beta); short leg × min(cap, 1 / mean beta); doc code caps at 2×
- **Weighting:** classic = weighted by ranked beta; doc's simplification = equal weight within deciles
- **Rebalance:** monthly
- **Risk:** partial hedge; crowded low-beta valuations

### C9. Short Term Reversal Effect in Stocks
[doc](https://docs.google.com/document/d/1ppuNA000L-wRst1Jx_kTStU6ybL_OUJabVQNLxW9KcI) · Moderate · Advanced · Source: large-cap reversal-net-of-costs study; Nagel, "Evaporating Liquidity"; de Groot, Huij & Zhou
- **Universe:** 500 most liquid US (price > $1) → top 100 by market cap
- **Long:** 10 lowest 1-week (5-day) returns; **Short:** 10 highest 1-month (21-day) returns
- **Weighting:** ±1/10 each
- **Rebalance:** weekly
- **Risk:** liquidity-providing but short-volatility — strict risk control in crises

### C10. Trend-following Effect in Stocks
[doc](https://docs.google.com/document/d/1JiPCN6xHibzCSvx_W21AtXDOXEF84XWKrwZk6pOGUyA) · Moderate · Advanced · Source: Wilcox & Crittenden, "Does Trend Following Work on Stocks?"
- **Universe:** 100 most liquid US stocks, price > $5
- **Entry:** close ≥ highest close in the stock's entire available history
- **Exit:** 10-period ATR trailing stop; stop = price − 1 ATR, only ratchets up
- **Holdings:** every entered, not-stopped name; equal weight
- **Rebalance:** daily; doc assumes ~0.5% round-turn costs
- **Data:** daily OHLC (for ATR)
- **Data note:** "all-time high" = highest close since the first bar on the plan (open check #1).
- **Risk:** long-only, no hedge

### C11. Pairs Trading with Stocks
[doc](https://docs.google.com/document/d/1QBZVjCiggvYe3DAKN2x3Tl2j43cv0K-ozC354Sabs5Q) · Moderate · Advanced · Source: distance-method pairs study (US 1962–2002); Lucey & Walshe; Chen, Chen & Li; Do & Faff
- **Universe:** top 500 by dollar volume, price > $5
- **Formation:** 12 months; normalize prices to $1; distance = sum of squared deviations
- **Selection:** smallest-distance pairs (original top 20; implementation caps 5 concurrent open pairs)
- **Entry:** spread > 2 SD → short rich leg, long cheap leg, dollar-neutral
- **Exit:** spread reverts inside the band
- **Re-form:** every 6 months; monitor daily
- **Risk:** historically positive in crises (1987, 2008 per Bowen & Hutchinson); edge has decayed

### C12. Size Factor – Small Capitalization Premium
[doc](https://docs.google.com/document/d/1NpfkhRi_DLDPAoOmIqEaJIfrHahc-A3VgX3ApCe0x5g) · Moderate · Intermediate · Source: Fama & French, "The Cross-Section of Expected Stock Returns"; Alquist, Israel & Moskowitz, "Fact, Fiction, and the Size Effect"
- **Universe:** NYSE / AMEX / NASDAQ, implementation top 3,000 by market cap
- **Positions:** quintiles by market cap (canonical = deciles); long smallest, short largest
- **Weighting:** equal; 100% long / 100% short
- **Rebalance:** yearly
- **Risk:** not a hedge — small caps suffer into downturns

---

## ✅ D — Single stocks + fundamentals (12)

> Common data for this tier: point-in-time fundamentals (use filing date, not period end, to avoid look-ahead) from Massive financials with EDGAR XBRL backfill (`edgar_client.latest_asof`). Check financials history depth first (open check #3).

### D1. Value (Book-to-Market) Factor
[doc](https://docs.google.com/document/d/1rvA0z6KY0twu2K9ZbOdzJ_ScvIXyEJ_vMDp1yQCVwNA) · High · Intermediate · Source: Asness, Frazzini, Israel & Moskowitz, "Fact, Fiction, and Value Investing"; Fama & French
- **Universe:** NYSE / AMEX / NASDAQ with valid P/B; top 3,000 by market cap
- **Signal:** P/B (inverse of book-to-market)
- **Positions:** quintiles; long lowest P/B, short highest P/B; equal weight; 100% long / 100% short
- **Rebalance:** monthly
- **Data:** book equity (stockholders' equity) ÷ market cap
- **Risk:** not a hedge; value tied to liquidity and growth risk

### D2. Asset Growth Effect
[doc](https://docs.google.com/document/d/11RHEq9lQkEimz7fAjgZpt5X3lXGCONi8qQBww35W_jQ) · High · Intermediate · Source: Cooper, Gulen & Schill, "Asset Growth and the Cross-Section of Stock Returns"
- **Universe:** non-financial NYSE / AMEX / NASDAQ; implementation top 3,000 by market cap
- **Signal:** year-over-year % change in total assets
- **Positions:** deciles formed end of June; long lowest growth, short highest; equal weight
- **Rebalance:** annually
- **Data:** annual total assets; financials excluded via SIC per ticker

### D3. Investment Factor (CMA)
[doc](https://docs.google.com/document/d/15DttfkACMYhA4rNcibxfy2qy-Oon-RQXWNlf-LH7J5s) · Moderate · Advanced · Source: Fama & French, "A Five-Factor Asset Pricing Model"
- **Source rules:** investment = growth of total assets for fiscal year ending t−1; independent 5 × 5 size × investment sorts on NYSE breakpoints; long biggest-size / lowest-investment, short biggest-size / highest-investment; value-weighted
- **Implementation:** top 3,000 by market cap; quintiles on investment; long lowest, short highest; equal weight
- **Rebalance:** annually, June
- **⚠ Resolve before build:** the doc's code divides a growth figure by total assets again (`asset_growth_1y / total_assets`) — looks double-scaled. Use the Fama-French definition.
- **Note:** same core signal as D2 (asset growth) — building both is largely redundant.

### D4. Momentum Factor Combined with Asset Growth Effect
[doc](https://docs.google.com/document/d/1_9Be-PKr5juaZXS_8VfMRTGLpYDgkXDkzxxy64DfQaY) · High · Advanced · Source: momentum × asset-growth interaction study
- **Universe:** NYSE / AMEX / NASDAQ excluding names below the 20th NYSE market-cap percentile; implementation 500 most liquid
- **Sort 1:** total-asset growth t−2 → t−1 (July cut-off) → keep top decile (highest growth)
- **Sort 2:** within it, 11-month return skipping the most recent month → quintiles
- **Positions:** long top momentum quintile, short bottom; equal weight
- **Rebalance:** monthly, **flat in January** (hold February–December)
- **Risk:** positive in NBER recession months per source

### D5. ROA Effect within Stocks
[doc](https://docs.google.com/document/d/1JetnwYgOyYanbeZAGcjmgXtojvd2fCWYMz4B6P9Do6Y) · High · Intermediate · Source: Hou, Xue & Zhang (q-factor model)
- **Universe:** top 500 by dollar volume, price > $5
- **Size split:** two halves by market cap
- **Signal:** ROA = quarterly income before extraordinary items ÷ one-quarter-lagged total assets
- **Positions:** deciles within each size half; long top 3 deciles of each half, short bottom 3 deciles of each half; equal weight
- **Rebalance:** monthly
- **⚠ Resolve before build:** "extraordinary items" were removed from US GAAP in 2015, so that income line is not reported in recent filings — pick the replacement income concept.

### D6. Earnings Quality Factor
[doc](https://docs.google.com/document/d/1aJpl6FvBcxZTuHdOA94lFGiyQ64YWlrSOnxIatZnuH0) · High · Intermediate · Source: Kozlov & Petajisto (global earnings-quality study, 1988–2012)
- **Universe:** largest US non-financials, top 3,000 by market cap
- **Four metrics:** accruals (lower better) · ROE (higher) · cash flow ÷ assets (higher) · debt ÷ assets (lower)
- **Accruals (doc):** (ΔCurrent assets − ΔCurrent liabilities − ΔCash + ΔCurrent debt − Depreciation) ÷ prior-year total assets
- **Score:** percentile-rank each metric so higher = better quality; sum the four
- **Positions:** long top 30%, short bottom 30%; equal weight
- **Rebalance:** annually, end of June
- **Risk:** plausible diversifier; negatively correlated with value

### D7. Accrual Anomaly
[doc](https://docs.google.com/document/d/1BLjB3B_Kmr0KOrMBviA-sP8skTmIdkfQtiAvP7aLeC4) · Moderate · Advanced · Source: Sloan (1996) lineage; LaFond, "Is the Accrual Anomaly a Global Anomaly?"; Detzel, Schabel & Strauss
- **Universe:** ~1,000 most liquid, largest with complete fundamentals
- **Signal:** BS_ACC = (ΔCA − ΔCash) − (ΔCL − ΔSTD − ΔITP) − Dep, scaled by average total assets (CA current assets, CL current liabilities, STD current debt, ITP income taxes payable, Dep depreciation & amortization)
- **Positions:** deciles; long lowest accruals, short highest; equal weight
- **Rebalance:** once a year in spring (April / May, after annual reports)
- **Data note:** the doc's filter drops any name with a zero in any required field (e.g. zero taxes payable).

### D8. Net Payout Yield Effect
[doc](https://docs.google.com/document/d/1cQVy6bz5z-QL_TrEo4kWVLG8sPI36udDKF8cy3Zt1Lo) · High · Intermediate · Source: Boudoukh, Michaely, Richardson & Roberts, "On the Importance of Measuring Payout Yield"; Gray & Vogel
- **Universe:** 500 most liquid on NYSE / AMEX / NASDAQ
- **Signal:** net payout yield = (dividends + repurchases − common stock issuance) ÷ year-end market cap (cash-flow repurchase measure)
- **Positions:** deciles; **long-only** top decile; equal weight
- **Rebalance:** formed end of June, hold one year
- **Data:** cash-flow statement dividends paid, repurchases of common stock, proceeds from common stock issuance (XBRL)
- **⚠ Resolve before build:** the doc's code formula (`total_yield × market_cap − issuance ÷ market_cap`) does not match its own rule text. Build from the rule text.
- **Risk:** long-only, high market correlation

### D9. Net Current Asset Value (NCAV) Effect
[doc](https://docs.google.com/document/d/1GXr0uF0mllBBNy-tzk9JAgnRJbRbQ_NUdhW9y2WWfBE) · Moderate · Intermediate · Source: Xiao & Arnold, "Testing Benjamin Graham's Net Current Asset Value Strategy in London"
- **Source universe:** London-listed, excluding multi-share-class, foreign, lightly-regulated-market and financial firms. **Implementation:** top 3,000 US by market cap.
- **Signal:** NCAV ÷ market value, where NCAV = current assets − **all** liabilities
- **Filter:** NCAV/MV > 1.5
- **Weighting:** equal across all qualifiers; cash if none
- **Rebalance:** formed July, hold one year
- **⚠ Resolve before build:** the doc's code proxies NCAV with working capital (current assets − current liabilities), which ignores long-term liabilities. Use the stated definition.

### D10. R&D Expenditures and Stock Returns
[doc](https://docs.google.com/document/d/1vtXza48RFncO9Dbe2kBtj8e6DbR-SSwcxKEZM8FopHQ) · Moderate · Intermediate · Source: Chan, Lakonishok & Sougiannis, "The Stock Market Valuation of Research and Development Expenditures"
- **Universe:** NYSE / NASDAQ / AMEX with reported R&D, price > $5
- **Signal:** weighted 5-year R&D (weights 1.0, 0.8, 0.6, 0.4, 0.2, newest first) ÷ current market cap
- **Positions:** end of April; long top quintile, short bottom; equal weight
- **Rebalance:** yearly
- **Data note:** needs 5 years of R&D per firm before its first score.
- **Risk:** very low beta (~0.006 per doc) but still suffers in bear markets

### D11. Combining Fundamental FSCORE and Short-Term Reversals
[doc](https://docs.google.com/document/d/1w7AsVp92FeMId7eG0-_jGLmEnaCj_9VY6vu8PpXVbRc) · High · Intermediate · Source: FSCORE-anchored reversal study; Piotroski FSCORE
- **Universe:** common US stocks > $5, top 500 by dollar volume → largest 40% by market cap
- **FSCORE (9 points, 1 each):** ROA > 0 · operating cash flow > 0 · ROA rising · cash flow > earnings (low accruals) · leverage falling · current ratio rising · no new shares issued · gross margin rising · asset turnover rising
- **Reversal signal:** past 1-month (21-day) return
- **Long:** 1-month return < 0 AND FSCORE 7–9; **Short:** 1-month return > 0 AND FSCORE 0–3
- **Weighting:** equal
- **Rebalance:** monthly
- **Risk:** liquidity-providing but short-volatility

### D12. Residual Momentum Factor
[doc](https://docs.google.com/document/d/1eFzpWCTXd2TXcmjPFDhdkhLle_ArmG6l_WYL84zwfic) · High · Advanced · Source: Blitz, Huij & Martens, "Residual Momentum"
- **Source universe:** domestic primary NYSE / AMEX / NASDAQ, price > $1, excluding closed-end funds, REITs, unit trusts, ADRs, foreign; largest 10% by market cap. **Implementation:** top 500 by market cap.
- **Factor model:** each month regress each stock's past 36 monthly returns on market, size and value factor returns
- **Signal:** sum of the past 12 monthly residuals (excluding the most recent month) ÷ standard deviation of those residuals
- **Positions:** deciles; long top, short bottom; equal weight
- **Rebalance:** monthly
- **Data:** size and value factors built from the same universe (market cap, book-to-market)
- **Data note:** needs 36 + 12 months of history per stock.
- **⚠ Resolve before build:** the doc's text calls the regression intercept "the residual return", but its code (and the paper) uses the residuals. Use residuals.

---

## ✅ E — Short interest (2)

> Common data: Massive `/stocks/v1/short-interest` (FINRA bi-monthly settlements). Both docs define the ratio on **shares outstanding** — `tools/short_float.py` uses **free float** (different denominator; float feed has known garbage rows). Key the signal to publication date, not settlement date. Check history depth (open check #4).

### E1. Short Interest Effect – Long-Short Version
[doc](https://docs.google.com/document/d/1ixWnVQrQvhdlXDx8IMHPNL2fk3DZjcawb8KHsx0AEVg) · Moderate · Intermediate · Source: Asquith, Pathak & Ritter, "Short Interest, Institutional Ownership, and Stock Returns"
- **Universe:** all NYSE / AMEX / NASDAQ stocks
- **Signal:** short interest ÷ shares outstanding
- **Positions:** deciles; long lowest, short highest; equal weight, symmetric legs
- **Rebalance:** monthly, first trading day
- **Risk:** hedge value unresolved per doc

### E2. Short Interest Effect – Long-Only Version
[doc](https://docs.google.com/document/d/194GKwEsOT-xyir1tbNAhZujQLjN3o0CAhN9s_0fp9TQ) · Moderate · Beginner · Source: Asquith, Pathak & Ritter
- **Universe:** all NYSE / AMEX / NASDAQ stocks
- **Signal:** short interest ÷ shares outstanding
- **Holdings:** the least-shorted **1%** of the universe (doc code `top_pct=0.01`); equal weight
- **Rebalance:** monthly, first trading day
- **Risk:** long-only, high market correlation

---

## ✅ F — Earnings-date event studies (4)

> Common data: announcement dates from EDGAR 8-K Item 2.02 filing dates (`tools/revenue_backfill.py` already finds the earnings 8-K per quarter). A filing date does not say before-open vs after-close — event windows must tolerate a one-day ambiguity.
> **Live-trading gap:** F3 and F4 enter *before* the announcement, so live use needs a **forward** earnings calendar — you have none (Benzinga 403, TMX 403). Backtests are fine (historical dates are known); live signals are not.

### F1. Post-Earnings Announcement Drift (PEAD)
[doc](https://docs.google.com/document/d/1rGfek7rRYiz8DHOnVCebpxRD65s36ypOYYJahrixCnE) · High · Advanced · Source: Ball & Brown (1968) lineage; SUE + EAR combination literature
- **Universe:** NYSE / AMEX / NASDAQ excluding financials and utilities, price ≥ $5
- **SUE:** (actual EPS − expected EPS) ÷ standard deviation of past surprises; expected = last same-quarter EPS + average year-over-year same-quarter change (seasonal random walk with drift); needs ≥ 4 same-quarter observations and ≥ 4 past surprises
- **EAR:** 3-day return centered on the announcement minus the market's return
- **Positions:** quintile cut-offs from the previous quarter's cross-section (no look-ahead); long top-SUE ∩ top-EAR; equal weight; **long-only**
- **Timing:** enter 2nd day after announcement; hold one quarter (~60 trading days); quarterly
- **Data:** quarterly EPS from XBRL (Q4 is usually only in the 10-K annual figure — derive it); dates from 8-K 2.02

### F2. Earnings Announcement Premium
[doc](https://docs.google.com/document/d/1EKf9S4WSsLaUU2chH2upgp24jAEMB8_w-THi_0s5otM) · Moderate · Advanced · Source: Frazzini & Lamont, "The Earnings Announcement Premium and Trading Volume"
- **Universe:** top ~1,000 by dollar volume
- **Signal:** volume concentration = volume in the previous 16 announcement months ÷ total volume over the previous 48 months
- **Selection:** top quintile by concentration
- **Split:** announced in this calendar month last year → long; otherwise → short
- **Weighting:** market-cap weighted per leg
- **Rebalance:** monthly, month start
- **Data:** 48 months of monthly volume (Massive aggs) + 4 years of announcement months (8-K 2.02)
- **Note:** uses last year's calendar as the forecast, so it does not need a forward calendar live.

### F3. Reversal in Post-Earnings Announcement Drift
[doc](https://docs.google.com/document/d/11DwRW_rZJQaxk_4_pjYZU5difFX-zjMrWI2B0-8QYKA) · Moderate · Advanced · Source: Milian (reversal in PEAD)
- **Universe:** NYSE / AMEX / NASDAQ with an active options market (effectively large caps), reporting the next trading day
- **Signal:** previous announcement's EAR = stock return − market return from t−2 to t+1 business days
- **Positions:** versus the previous quarter's EAR distribution — long ≤ 10th percentile, short ≥ 90th percentile
- **Holding:** 2 days spanning the upcoming announcement; equal weight; cap 10 long / 10 short
- **Evaluation:** daily
- **Data:** "active options market" filter needs options reference data (open check #5) or a large-cap proxy
- **Live gap:** needs forward earnings dates (see tier note)

### F4. Reversal During Earnings Announcements
[doc](https://docs.google.com/document/d/1j65KQMekLBbpBDwo9pj2pWJctWU631g2Oj4SLdUdXSk) · Moderate · Advanced · Source: study of six-fold reversal around earnings (market-maker inventory risk)
- **Universe:** NYSE / AMEX / NASDAQ with active options; keep top market-cap quintile
- **Signal:** return over t−4 to t−2 before the announcement
- **Positions:** versus previous quarter's distribution — long ≤ 20th percentile (losers), short ≥ 80th (winners)
- **Holding:** 3 days (t−1, t, t+1); equal weight; cap 20 long / 20 short
- **⚠ Resolve before build:** the doc says "average return" over the window but its code computes a cumulative return.
- **Live gap:** needs forward earnings dates (see tier note)

---

## ✅ G — EDGAR filings (2)

### G1. Alpha Cloning – Following 13F Filings
[doc](https://docs.google.com/document/d/1PF665ifntd6PT8qWqq-LkFr3AVgrEO-krIH3L3ddhUU) · Moderate · Intermediate · Source: Cohen, Polk & Silli, "Best Ideas"
- **Universe:** stocks held by a chosen set of active mutual and hedge fund managers
- **Signal:** vote count = number of tracked managers holding the stock as a "best idea"
- **Weighting:** votes ÷ total votes
- **Lag:** holdings treated as known 2 months after the report
- **Rebalance:** quarterly, aligned to the 13F calendar; long-only
- **Data:** EDGAR 13F-HR information tables
- **⚠ Resolve before build:** (1) which managers to track — not specified; (2) how a "best idea" is defined per manager — not specified in the doc (the Cohen/Polk/Silli paper is the reference); (3) 13F lists CUSIPs, not tickers — a CUSIP → ticker map is needed.

### G2. The Positive Similarity of Company Filings and Stock Returns
[doc](https://docs.google.com/document/d/1ZIkrPRUwlGoKhFRSG8Cz-paJ1SxYBLxQjE_etVAir-w) · Moderate · Intermediate · Source: positive-language similarity study (extends "Lazy Prices")
- **Universe:** ~1,000 largest US stocks by market cap with a score and full price history
- **Signal:** cosine similarity of positive-language word-frequency vectors between the latest 10-K / 10-Q and the prior filing (0 = rewritten, 1 = identical)
- **Positions:** monthly deciles; **long bottom decile** (biggest change), **short top decile**; equal weight; stay flat if < 10 scored names
- **Rebalance:** monthly
- **Data:** the doc uses a vendor score → build it yourself from EDGAR 10-K / 10-Q text with a public positive-word dictionary (e.g. Loughran-McDonald)
- **⚠ Resolve before build:** "the prior one" — compare against the prior filing of the same form type, or the prior filing of any type.

---

## ✅ H — Options (1)

### H1. Volatility Risk Premium Effect
[doc](https://docs.google.com/document/d/1ot9RQrzWiUtuRF4t-9lHmhlm017BXk0Tt_145QmeeyE) · Moderate · Advanced · Source: study of expected option returns (zero-beta ATM straddles lose ~3% / week)
- **Universe:** SPY options + SPY
- **Monthly trade:** sell an ATM straddle (call + put at the strike nearest spot, expiration nearest 30 days); buy a put at the strike nearest 85% of spot, same expiration
- **Cash:** remaining cash + collected premium held in SPY
- **Sizing (doc code):** contracts = margin remaining ÷ (spot × 100)
- **Rebalance:** monthly, open only when flat
- **Data:** historical SPY option contract prices + expired-contract reference (**open check #5**)
- **⚠ Resolve before build:** the doc sizes by margin and also sets SPY to 100% of holdings — total exposure is ambiguous.
- **Risk:** fat-tailed; the 15% OTM put is mandatory, not optional

---

## 🟡 P — Partial / heavy lift (3)

### P1. Earnings Announcements Combined with Stock Repurchases
[doc](https://docs.google.com/document/d/10Fa9Fj1588ArDTrlir2pu6QGfEOxUcg_MOCh8kjhacM) · Moderate · Intermediate · Source: market-timing / earnings-predictability study (repurchases vs secondary offerings)
- **Universe:** NYSE / AMEX / NASDAQ excluding ADRs, closed-end funds, REITs; drop smallest 25% by market cap
- **Signal:** repurchase program for ≥ 5% of shares outstanding announced 30 to 15 days before the earnings date
- **Holding:** long from 10 days before to 15 days after the announcement; equal weight; cap 40 positions
- **Rebalance:** selection quarterly; trades daily
- **Blocker:** no buyback-announcement feed. Date and program size must be parsed from 8-K / press-release text (EDGAR full-text search), and dollar authorizations converted to % of shares. Live use also needs forward earnings dates.

### P2. FED Model
[doc](https://docs.google.com/document/d/1DBOtXeefnB06eCGr2wNXkhKYf8NbahcSJI5vxv3M0I4) · Moderate · Intermediate · Source: stock-bond "yield gap" research
- **Universe:** SPY (risky), SHY (cash)
- **Signal:** yield gap YG = ln(1 + E/P) − ln(1 + Y10)
- **Model:** monthly expanding-window OLS of market excess return on lagged YG; forecast next month
- **Position:** forecast > 0 → 100% SPY, else 100% SHY
- **Rebalance:** monthly
- **Blocker:** S&P 500 earnings yield is not available (indices 403; the constituents DB is a current snapshot with no membership history). A self-built large-cap aggregate E/P is a proxy, not the S&P number. Yields via `/fed/v1` (open check #7).
- **⚠ Resolve before build:** the doc's formula text (`ln(1 + E/P)`) and code (`log(EY) − log(Y)`) differ.

### P3. How to Use Lexical Density of Company Filings
[doc](https://docs.google.com/document/d/1dbTdnrjQXb6zqWFLkr8s1jFYPJBX3cG63ykPox5NuAg) · Moderate · Advanced · Source: filings-language dataset study (~6,000 US stocks)
- **Universe:** top 500 by dollar volume on NYSE / NASDAQ / AMEX
- **Signals (vendor):** lexical density ("share of information-carrying words rather than filler") and specific density ("how many finance-related terms appear")
- **Positions:** per metric, long top decile, short bottom decile; equal weight; the two metric sleeves split the book 50 / 50
- **Rebalance:** monthly; universe reselected quarterly
- **Blocker:** both metrics are vendor-defined. A self-built version from EDGAR text is an approximation, not the paper's score.

---

## ❌ X — Blocked (11)

| # | Strategy | Doc | Missing data | What would unblock it |
|---|---|---|---|---|
| X1 | Dispersion Trading | [doc](https://docs.google.com/document/d/1OHXWMedpBSWXyMlOOOLVllU1g6NA1Tu5jZTRbznaXYo) | Analyst EPS forecast dispersion (no estimates feed; Benzinga 403); S&P 100 index options (indices 403) | An analyst-estimates source + options entitlement |
| X2 | ESG Level Factor Investing | [doc](https://docs.google.com/document/d/1h9SDFv2ESZP-fILAj7K4c2GFB4VtoHAPLV4fLHjoLFI) | Annual E / S / G scores (Asset4) | An ESG ratings source |
| X3 | ESG Factor Momentum | [doc](https://docs.google.com/document/d/12AM9Dk7PlyVgbCg_uztP6iCq2dbymP1EC9k_eBPIFsM) | Monthly MSCI ESG rating history; MSCI World (non-US listings) | ESG history + international equities |
| X4 | ESG, Price Momentum & Stochastic Optimization | [doc](https://docs.google.com/document/d/1Hb2BZWMPZIaaiWQQUchlpkuGXy3GvfkIH9lIUbg0pNs) | Per-stock ESG score (momentum half is buildable) | An ESG ratings source |
| X5 | Momentum in Mutual Fund Returns | [doc](https://docs.google.com/document/d/1u7lc-qkWMmN1XbUSiS0QkgKlWOf3aiByr9Wqt1qpHKw) | No-load mutual fund NAV history (Massive covers ETFs, not mutual funds) | A fund NAV source |
| X6 | Value Factor – CAPE within Countries | [doc](https://docs.google.com/document/d/1U5s_n8lAXoV2PQZkvBckNJ_aPNK1SjHlqzHJBcivpwA) | Country-level CAPE series (the ETFs themselves are available) | A country CAPE dataset |
| X7 | Exploiting Term Structure of VIX Futures | [doc](https://docs.google.com/document/d/1GZYAo7AnKY1GmVO5DVnJ1vc_JPsnOJn3yYZTwaeSRrA) | Spot VIX (indices 403), VIX futures, E-mini futures | Index + futures data |
| X8 | Synthetic Lending Rates Predict Market Return | [doc](https://docs.google.com/document/d/1uZ2XgTa3gv7R58BwKllYH3qgfrTsNbJKzNJLndXtrto) | Cboe Hanweck Borrow Intensity Indicators (~4,877 names, 45-day constant maturity) | That vendor dataset |
| X9 | Time Series Momentum | [doc](https://docs.google.com/document/d/1-LsZC0-CwqC466XA7QWhknyG4RKMThfl7mz0ZEFjcFw) | ~58 back-adjusted continuous futures (commodities, FX, indices, bonds). FX spot pairs exist, covering only the currency sleeve. | Futures entitlement (open check #6) |
| X10 | Short Term Reversal with Futures | [doc](https://docs.google.com/document/d/1sCWqIDX8TA93jdBKhC6K3e2zv4Pwi5srQPqe3Fk2pcI) | 24 US futures with daily volume + open interest | Futures entitlement with open interest (open check #6) |
| X11 | Soccer Clubs' Stocks Arbitrage | [doc](https://docs.google.com/document/d/1LaUBfTeYY_g77Pr0MMdNhHsa7XfEgbOWeLfP9J4FU1E) | European listings (only MANU is US-listed) + important-match calendar | International equities + a match schedule |

---

## Starting a build (checklist)

1. Pick ONE strategy → add it to `PROJECT_QUEUE.md` with a DONE line (WIP = 1).
2. Re-read its Drive doc in full (link above) — this file summarizes; the doc has the complete pseudo-code.
3. Run the open checks that tier depends on.
4. Resolve every ⚠ line for that strategy **with Judin** — don't pick thresholds or definitions silently.
5. Build as a `tools/` script; record anything learned back into this file.
