---
id: A6
name: Paired Switching
tier: A — ETFs, price only
strength: Moderate
difficulty: Beginner
source: paired-switching research (original used VFINX / VUSTX)
doc: https://docs.google.com/document/d/1_6rfZ8GuIf3KTHkPWz69aBWxZ6FHZZDdUHb3NSLBess
data_status: buildable
build_status: not started
verdict: 
---
# A6 · Paired Switching

## At a glance
- **Tier:** A — ETFs, price only
- **Strength (PQN):** Moderate · **Difficulty (PQN):** Beginner
- **Source:** paired-switching research (original used VFINX / VUSTX)
- **PQN doc:** [A6 on Drive](https://docs.google.com/document/d/1_6rfZ8GuIf3KTHkPWz69aBWxZ6FHZZDdUHb3NSLBess)
- **Data status:** buildable · **Build status:** not started · **Verdict:** —

## Thesis
—

## Rules as written
- **Universe:** SPY and AGG
- **Signal:** trailing-quarter return (~90 calendar days ≈ 63 trading days)
- **Position:** 100% in whichever had the higher trailing-quarter return; never both
- **Rebalance:** quarterly, first trading day of the quarter

## Data map
- **Data:** daily closes → Massive aggs (dividend-adjust AGG — split-only adjustment understates a bond fund)

## Open questions
None flagged in the triage.

**Decisions:** none yet. (Resolve each line with Judin before building — never pick a definition silently.)

## Risk
- **Risk:** partial hedge (overlay)

## Backtest
Not run. When it is, results live in `results/A6/` (returns.csv · trades.csv · eda.png · report.md), ending in `tools/backtest_eda.py`.

## Notes
—
