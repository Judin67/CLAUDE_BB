---
id: A5
name: Momentum Factor and Style Rotation Effect
tier: A — ETFs, price only
strength: High
difficulty: Beginner
source: style-momentum literature
doc: https://docs.google.com/document/d/1uTaBrM1b8uBAlTCfA03J52atKW4l4WXD8yZnCbn4-GM
data_status: buildable
build_status: not started
verdict: 
---
# A5 · Momentum Factor and Style Rotation Effect

## At a glance
- **Tier:** A — ETFs, price only
- **Strength (PQN):** High · **Difficulty (PQN):** Beginner
- **Source:** style-momentum literature
- **PQN doc:** [A5 on Drive](https://docs.google.com/document/d/1uTaBrM1b8uBAlTCfA03J52atKW4l4WXD8yZnCbn4-GM)
- **Data status:** buildable · **Build status:** not started · **Verdict:** —

## Thesis
—

## Rules as written
- **Universe:** IWS, IWP, IWN, IWO, IVE, IVW (mid/small/large × value/growth)
- **Signal:** 12-month momentum (252 trading days)
- **Positions:** 100% long the top style, 100% short the bottom style; flat the rest
- **Rebalance:** monthly

## Data map
- **Data:** daily closes → Massive aggs

## Open questions
None flagged in the triage.

**Decisions:** none yet. (Resolve each line with Judin before building — never pick a definition silently.)

## Risk
- **Risk:** long-short has low market correlation; hedge value not established

## Backtest
Not run. When it is, results live in `results/A5/` (returns.csv · trades.csv · eda.png · report.md), ending in `tools/backtest_eda.py`.

## Notes
—
