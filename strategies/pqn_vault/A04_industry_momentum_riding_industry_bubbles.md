---
id: A4
name: Industry Momentum – Riding Industry Bubbles
tier: A — ETFs, price only
strength: Moderate
difficulty: Advanced
source: research on riding asset-price bubbles (CAPM structural-break detection)
doc: https://docs.google.com/document/d/1wbZoB7rb2gKncGuYCkAsWooHJMdE2-EtBoMdhg1WxDU
data_status: buildable
build_status: not started
verdict: 
---
# A4 · Industry Momentum – Riding Industry Bubbles

## At a glance
- **Tier:** A — ETFs, price only
- **Strength (PQN):** Moderate · **Difficulty (PQN):** Advanced
- **Source:** research on riding asset-price bubbles (CAPM structural-break detection)
- **PQN doc:** [A4 on Drive](https://docs.google.com/document/d/1wbZoB7rb2gKncGuYCkAsWooHJMdE2-EtBoMdhg1WxDU)
- **Data status:** buildable · **Build status:** not started · **Verdict:** —

## Thesis
- **Thesis:** a statistically significant CAPM alpha = a bubble; ride it, exit mechanically when significance fades.

## Rules as written
- **Universe:** XLF, XLV, XLP, XLY, XLI, XLE, XLB, XLK, XLU; SPY = market
- **Signal:** CAPM regression of sector monthly returns on SPY monthly returns over 120 months; bubble if alpha t-stat ≥ ~2.0
- **Entry / exit:** long every sector in a bubble; drop when no longer significant
- **Weighting:** 1/N across bubbled sectors; hold nothing if none
- **Rebalance:** monthly

## Data map
- **Data:** daily closes → monthly returns → Massive aggs
- **Data note:** needs 120 monthly observations before the first signal.

## Open questions
None flagged in the triage.

**Decisions:** none yet. (Resolve each line with Judin before building — never pick a definition silently.)

## Risk
- **Risk:** does not hedge

## Backtest
Not run. When it is, results live in `results/A4/` (returns.csv · trades.csv · eda.png · report.md), ending in `tools/backtest_eda.py`.

## Notes
—
