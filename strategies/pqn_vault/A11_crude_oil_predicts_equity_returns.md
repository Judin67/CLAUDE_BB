---
id: A11
name: Crude Oil Predicts Equity Returns
tier: A — ETFs, price only
strength: Moderate
difficulty: Intermediate
source: Driesprong, Jacobsen & Maat, "Striking Oil: Another Puzzle?"
doc: https://docs.google.com/document/d/1vWZeA2aGAAhQ1-zru-zN91Jf86pRFcyxbGsAjSB9X9U
data_status: buildable
build_status: not started
verdict: 
---
# A11 · Crude Oil Predicts Equity Returns

## At a glance
- **Tier:** A — ETFs, price only
- **Strength (PQN):** Moderate · **Difficulty (PQN):** Intermediate
- **Source:** Driesprong, Jacobsen & Maat, "Striking Oil: Another Puzzle?"
- **PQN doc:** [A11 on Drive](https://docs.google.com/document/d/1vWZeA2aGAAhQ1-zru-zN91Jf86pRFcyxbGsAjSB9X9U)
- **Data status:** buildable · **Build status:** not started · **Verdict:** —

## Thesis
—

## Rules as written
- **Doc universe:** E-mini S&P 500 continuous future (risky), crude oil continuous future (predictor), SHY (cash); risk-free = 3-month Treasury
- **Signal:** each month, OLS of equity return(t) on oil return(t−1) over all history (expanding window); minimum 13 months
- **Forecast:** intercept + slope × latest oil return
- **Position:** forecast > risk-free → 100% equity; otherwise 100% SHY
- **Rebalance:** monthly

## Data map
- **Substitution (no futures in stack):** SPY for the S&P future, USO for crude. USO carries roll costs, so it is not identical to the crude future.
- **Data:** SPY / USO / SHY → Massive aggs; 3-month yield → Massive `/fed/v1` (open check #7)

## Open questions
None flagged in the triage.

**Decisions:** none yet. (Resolve each line with Judin before building — never pick a definition silently.)

## Risk
- **Risk:** partial hedge (market timing)

## Backtest
Not run. When it is, results live in `results/A11/` (returns.csv · trades.csv · eda.png · report.md), ending in `tools/backtest_eda.py`.

## Notes
—
