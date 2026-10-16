---
id: B6
name: January Barometer
tier: B — Calendar timing
strength: Low
difficulty: Beginner
source: Cooper, McConnell & Ovtchinnikov, "The Other January Effect"
doc: https://docs.google.com/document/d/1ssGNLSlF8xhMI01JS_y532ilXBt7yL2yVzVamAfpr40
data_status: buildable
build_status: not started
verdict: 
---
# B6 · January Barometer

## At a glance
- **Tier:** B — Calendar timing
- **Strength (PQN):** Low · **Difficulty (PQN):** Beginner
- **Source:** Cooper, McConnell & Ovtchinnikov, "The Other January Effect"
- **PQN doc:** [B6 on Drive](https://docs.google.com/document/d/1ssGNLSlF8xhMI01JS_y532ilXBt7yL2yVzVamAfpr40)
- **Data status:** buildable · **Build status:** not started · **Verdict:** —

## Thesis
—

## Rules as written
- **Universe:** SPY, SHY
- **Rule:** 100% SPY in January. At the start of February: January return > 0 → stay SPY through year-end; otherwise 100% SHY through year-end.

## Data map
- **Data:** daily closes → Massive aggs

## Open questions
None flagged in the triage.

**Decisions:** none yet. (Resolve each line with Judin before building — never pick a definition silently.)

## Risk
- **Doc's own caveat:** weak rationale, likely data-mined, contested out of sample

## Backtest
Not run. When it is, results live in `results/B6/` (returns.csv · trades.csv · eda.png · report.md), ending in `tools/backtest_eda.py`.

## Notes
—
