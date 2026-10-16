---
id: B5
name: January Effect in Stocks
tier: B — Calendar timing
strength: Low
difficulty: Beginner
source: Haug & Hirschey, "The January Effect"
doc: https://docs.google.com/document/d/1emd4lCGTKUzwLO6eaBAF9KXuf__KwveLJ-ZVQPEnsg0
data_status: buildable
build_status: not started
verdict: 
---
# B5 · January Effect in Stocks

## At a glance
- **Tier:** B — Calendar timing
- **Strength (PQN):** Low · **Difficulty (PQN):** Beginner
- **Source:** Haug & Hirschey, "The January Effect"
- **PQN doc:** [B5 on Drive](https://docs.google.com/document/d/1emd4lCGTKUzwLO6eaBAF9KXuf__KwveLJ-ZVQPEnsg0)
- **Data status:** buildable · **Build status:** not started · **Verdict:** —

## Thesis
—

## Rules as written
- **Universe:** IWM (small-cap), SPY (large-cap)
- **Position:** 100% IWM in January; 100% SPY February–December
- **Rebalance:** first session of each month

## Data map
- **Data:** daily closes → Massive aggs

## Open questions
None flagged in the triage.

**Decisions:** none yet. (Resolve each line with Judin before building — never pick a definition silently.)

## Risk
- **Doc's own caveat:** effect decaying, may not survive costs

## Backtest
Not run. When it is, results live in `results/B5/` (returns.csv · trades.csv · eda.png · report.md), ending in `tools/backtest_eda.py`.

## Notes
—
