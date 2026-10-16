---
id: A7
name: Momentum Factor Effect in Country Equity Indexes
tier: A — ETFs, price only
strength: High
difficulty: Beginner
source: MSCI country-index momentum study (1970–2009); Andreu, Swinkels & Tjong-A-Tjoe; Bhojraj & Swaminathan
doc: https://docs.google.com/document/d/1piimfk9FbbbethjO9JRWtxzow3wHsWgCKzXrlzO3rEE
data_status: buildable
build_status: not started
verdict: 
---
# A7 · Momentum Factor Effect in Country Equity Indexes

## At a glance
- **Tier:** A — ETFs, price only
- **Strength (PQN):** High · **Difficulty (PQN):** Beginner
- **Source:** MSCI country-index momentum study (1970–2009); Andreu, Swinkels & Tjong-A-Tjoe; Bhojraj & Swaminathan
- **PQN doc:** [A7 on Drive](https://docs.google.com/document/d/1piimfk9FbbbethjO9JRWtxzow3wHsWgCKzXrlzO3rEE)
- **Data status:** buildable · **Build status:** not started · **Verdict:** —

## Thesis
—

## Rules as written
- **Universe:** EWA, EWO, EWK, EWZ, EWC, FXI, EWQ, EWG, EWH, EWI, EWJ, EWM, EWW, EWN, EWS, EZA, EWY, EWP, EWD, EWL, EWT, THD, EWU, SPY
- **Signal:** trailing return. The doc's implementation uses 6 months (126 days); the doc says studies favor 10–12 months.
- **Selection:** top 5, equal weight (1/5)
- **Rebalance:** monthly

## Data map
- **Data:** daily closes → Massive aggs

## Open questions
- **⚠ Resolve before build:** lookback — 6 months (implementation) or 10–12 months (studies).

**Decisions:** none yet. (Resolve each line with Judin before building — never pick a definition silently.)

## Risk
- **Risk:** no hedge; tends to load late-cycle emerging markets

## Backtest
Not run. When it is, results live in `results/A7/` (returns.csv · trades.csv · eda.png · report.md), ending in `tools/backtest_eda.py`.

## Notes
—
