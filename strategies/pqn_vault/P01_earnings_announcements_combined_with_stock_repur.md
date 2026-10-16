---
id: P1
name: Earnings Announcements Combined with Stock Repurchases
tier: P — Partial / heavy lift
strength: Moderate
difficulty: Intermediate
source: market-timing / earnings-predictability study (repurchases vs secondary offerings)
doc: https://docs.google.com/document/d/10Fa9Fj1588ArDTrlir2pu6QGfEOxUcg_MOCh8kjhacM
data_status: partial
build_status: not started
verdict: 
---
# P1 · Earnings Announcements Combined with Stock Repurchases

## At a glance
- **Tier:** P — Partial / heavy lift
- **Strength (PQN):** Moderate · **Difficulty (PQN):** Intermediate
- **Source:** market-timing / earnings-predictability study (repurchases vs secondary offerings)
- **PQN doc:** [P1 on Drive](https://docs.google.com/document/d/10Fa9Fj1588ArDTrlir2pu6QGfEOxUcg_MOCh8kjhacM)
- **Data status:** partial · **Build status:** not started · **Verdict:** —

## Thesis
—

## Rules as written
- **Universe:** NYSE / AMEX / NASDAQ excluding ADRs, closed-end funds, REITs; drop smallest 25% by market cap
- **Signal:** repurchase program for ≥ 5% of shares outstanding announced 30 to 15 days before the earnings date
- **Holding:** long from 10 days before to 15 days after the announcement; equal weight; cap 40 positions
- **Rebalance:** selection quarterly; trades daily

## Data map
- **Blocker:** no buyback-announcement feed. Date and program size must be parsed from 8-K / press-release text (EDGAR full-text search), and dollar authorizations converted to % of shares. Live use also needs forward earnings dates.

## Open questions
None flagged in the triage.

**Decisions:** none yet. (Resolve each line with Judin before building — never pick a definition silently.)

## Risk
—

## Backtest
Not run. When it is, results live in `results/P1/` (returns.csv · trades.csv · eda.png · report.md), ending in `tools/backtest_eda.py`.

## Notes
—
