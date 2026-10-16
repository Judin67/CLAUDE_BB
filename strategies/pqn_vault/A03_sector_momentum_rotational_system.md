---
id: A3
name: Sector Momentum – Rotational System
tier: A — ETFs, price only
strength: High
difficulty: Beginner
source: Faber; Moskowitz & Grinblatt, "Do Industries Explain Momentum?"
doc: https://docs.google.com/document/d/1a_TrkiN1ZFNWx6D9ZpEQkwNGlza5pYnREeKvSsvVDa0
data_status: buildable
build_status: not started
verdict: 
---
# A3 · Sector Momentum – Rotational System

## At a glance
- **Tier:** A — ETFs, price only
- **Strength (PQN):** High · **Difficulty (PQN):** Beginner
- **Source:** Faber; Moskowitz & Grinblatt, "Do Industries Explain Momentum?"
- **PQN doc:** [A3 on Drive](https://docs.google.com/document/d/1a_TrkiN1ZFNWx6D9ZpEQkwNGlza5pYnREeKvSsvVDa0)
- **Data status:** buildable · **Build status:** not started · **Verdict:** —

## Thesis
—

## Rules as written
- **Universe:** VNQ, XLK, XLE, XLV, XLF, XLI, XLB, XLY, XLP, XLU
- **Signal:** trailing 12-month return (252 trading days)
- **Selection:** top 3, equal weight (1/3)
- **Rebalance:** monthly

## Data map
- **Data:** daily closes → Massive aggs

## Open questions
None flagged in the triage.

**Decisions:** none yet. (Resolve each line with Judin before building — never pick a definition silently.)

## Risk
- **Risk:** long-only does not hedge. Doc mentions a variant: long top sectors / short the index.

## Backtest
Not run. When it is, results live in `results/A3/` (returns.csv · trades.csv · eda.png · report.md), ending in `tools/backtest_eda.py`.

## Notes
—
