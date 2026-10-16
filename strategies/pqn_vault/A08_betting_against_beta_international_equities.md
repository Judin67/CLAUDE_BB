---
id: A8
name: Betting Against Beta – International Equities
tier: A — ETFs, price only
strength: High
difficulty: Intermediate
source: Frazzini & Pedersen, "Betting Against Beta"
doc: https://docs.google.com/document/d/1EJxooz0QLoHpCUED8ZFV1G5avR0PcUtoGuJxVPrIzqQ
data_status: buildable
build_status: not started
verdict: 
---
# A8 · Betting Against Beta – International Equities

## At a glance
- **Tier:** A — ETFs, price only
- **Strength (PQN):** High · **Difficulty (PQN):** Intermediate
- **Source:** Frazzini & Pedersen, "Betting Against Beta"
- **PQN doc:** [A8 on Drive](https://docs.google.com/document/d/1EJxooz0QLoHpCUED8ZFV1G5avR0PcUtoGuJxVPrIzqQ)
- **Data status:** buildable · **Build status:** not started · **Verdict:** —

## Thesis
—

## Rules as written
- **Universe:** EWA, EWO, EWK, EWZ, EWC, FXI, EWQ, EWG, EWH, EWI, EWJ, EWM, EWW, EWN, EWS, EZA, EWY, EWP, EWD, EWL, EWT, THD, EWU; SPY = beta reference
- **Signal:** 252-day rolling beta of daily returns vs SPY
- **Construction:** split at median beta; within each side weight by distance from the median; lever the low-beta (long) leg and the high-beta (short) leg each to beta = 1; cap 5× per side
- **Rebalance:** monthly

## Data map
- **Data:** daily closes → Massive aggs
- **Needs:** leverage + ETF shorting

## Open questions
None flagged in the triage.

**Decisions:** none yet. (Resolve each line with Judin before building — never pick a definition silently.)

## Risk
- **Risk:** partial hedge; crowding can stretch low-beta valuations

## Backtest
Not run. When it is, results live in `results/A8/` (returns.csv · trades.csv · eda.png · report.md), ending in `tools/backtest_eda.py`.

## Notes
—
