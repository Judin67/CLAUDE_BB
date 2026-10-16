---
id: B4
name: Market Seasonality Effect ("Sell in May")
tier: B — Calendar timing
strength: Moderate
difficulty: Beginner
source: Bouman & Jacobsen, "The Halloween Indicator"
doc: https://docs.google.com/document/d/1QyvrMw68hQbO6zLMTT0Z3A2Yrh2w8Snubm1MuHzVlI8
data_status: buildable
build_status: not started
verdict: 
---
# B4 · Market Seasonality Effect ("Sell in May")

## At a glance
- **Tier:** B — Calendar timing
- **Strength (PQN):** Moderate · **Difficulty (PQN):** Beginner
- **Source:** Bouman & Jacobsen, "The Halloween Indicator"
- **PQN doc:** [B4 on Drive](https://docs.google.com/document/d/1QyvrMw68hQbO6zLMTT0Z3A2Yrh2w8Snubm1MuHzVlI8)
- **Data status:** buildable · **Build status:** not started · **Verdict:** —

## Thesis
—

## Rules as written
- **Universe:** SPY (SHY optional as defensive sleeve)
- **Entry:** start of November → 100% SPY
- **Exit:** start of May → cash
- **Rebalance:** two trades per year, checked on the first trading session of each month

## Data map
- **Data:** daily closes → Massive aggs

## Open questions
None flagged in the triage.

**Decisions:** none yet. (Resolve each line with Judin before building — never pick a definition silently.)

## Risk
- **Risk:** partial (overlay)

## Backtest
Not run. When it is, results live in `results/B4/` (returns.csv · trades.csv · eda.png · report.md), ending in `tools/backtest_eda.py`.

## Notes
—
