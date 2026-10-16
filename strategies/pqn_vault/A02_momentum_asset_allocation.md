---
id: A2
name: Momentum Asset Allocation
tier: A — ETFs, price only
strength: High
difficulty: Beginner
source: Faber (relative-strength variant); Kessler & Scherer, "Macro Momentum and the Economy"
doc: https://docs.google.com/document/d/1kN8RzAnnSj-pB-DfM5CgHTunXulrX-mpeg7j_ZyBRaI
data_status: buildable
build_status: not started
verdict: 
---
# A2 · Momentum Asset Allocation

## At a glance
- **Tier:** A — ETFs, price only
- **Strength (PQN):** High · **Difficulty (PQN):** Beginner
- **Source:** Faber (relative-strength variant); Kessler & Scherer, "Macro Momentum and the Economy"
- **PQN doc:** [A2 on Drive](https://docs.google.com/document/d/1kN8RzAnnSj-pB-DfM5CgHTunXulrX-mpeg7j_ZyBRaI)
- **Data status:** buildable · **Build status:** not started · **Verdict:** —

## Thesis
- **Thesis:** rank asset classes by 12-month return, always hold the top three.

## Rules as written
- **Universe:** SPY, EFA, IEF, VNQ, GSG
- **Signal:** trailing 12-month return (252 trading days)
- **Selection:** top 3; drop any that fall out of the top 3
- **Weighting:** 1/3 each; always fully invested
- **Rebalance:** monthly, first trading session

## Data map
- **Data:** daily closes → Massive aggs

## Open questions
None flagged in the triage.

**Decisions:** none yet. (Resolve each line with Judin before building — never pick a definition silently.)

## Risk
- **Risk:** partial hedge (overlay)

## Backtest
Not run. When it is, results live in `results/A2/` (returns.csv · trades.csv · eda.png · report.md), ending in `tools/backtest_eda.py`.

## Notes
—
