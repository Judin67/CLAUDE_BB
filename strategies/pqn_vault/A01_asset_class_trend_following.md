---
id: A1
name: Asset Class Trend-Following
tier: A — ETFs, price only
strength: High
difficulty: Beginner
source: Faber, "A Quantitative Approach to Tactical Asset Allocation"
doc: https://docs.google.com/document/d/1JglHYFlMP9VWnPT7uHqczP59x5Nft6evbbvw_FhOHMo
data_status: buildable
build_status: not started
verdict: 
---
# A1 · Asset Class Trend-Following

## At a glance
- **Tier:** A — ETFs, price only
- **Strength (PQN):** High · **Difficulty (PQN):** Beginner
- **Source:** Faber, "A Quantitative Approach to Tactical Asset Allocation"
- **PQN doc:** [A1 on Drive](https://docs.google.com/document/d/1JglHYFlMP9VWnPT7uHqczP59x5Nft6evbbvw_FhOHMo)
- **Data status:** buildable · **Build status:** not started · **Verdict:** —

## Thesis
- **Thesis:** hold each asset-class ETF only while it trades above its 10-month SMA; otherwise that sleeve sits in cash.

## Rules as written
- **Universe:** SPY, EFA, IEF, VNQ, GSG
- **Signal:** price vs 210-trading-day SMA (10 months × ~21)
- **Entry / exit:** hold when price > SMA; liquidate at ≤ SMA → cash
- **Weighting:** 1/N across ETFs passing the filter; 100% cash if none
- **Rebalance:** monthly, first trading session

## Data map
- **Data:** daily closes → Massive aggs

## Open questions
None flagged in the triage.

**Decisions:** none yet. (Resolve each line with Judin before building — never pick a definition silently.)

## Risk
- **Risk (per doc):** partial hedge — an exposure overlay, not a direct hedge

## Backtest
Not run. When it is, results live in `results/A1/` (returns.csv · trades.csv · eda.png · report.md), ending in `tools/backtest_eda.py`.

## Notes
—
