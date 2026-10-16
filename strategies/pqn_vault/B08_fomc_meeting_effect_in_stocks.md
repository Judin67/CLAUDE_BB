---
id: B8
name: FOMC Meeting Effect in Stocks
tier: B — Calendar timing
strength: Moderate
difficulty: Beginner
source: FOMC calendar-effect study (S&P 500, 1960–2000)
doc: https://docs.google.com/document/d/11-bvVVTK2mwZZPnObZ9N2t23GOtiAe_8MRUMS2LjawI
data_status: buildable
build_status: not started
verdict: 
---
# B8 · FOMC Meeting Effect in Stocks

## At a glance
- **Tier:** B — Calendar timing
- **Strength (PQN):** Moderate · **Difficulty (PQN):** Beginner
- **Source:** FOMC calendar-effect study (S&P 500, 1960–2000)
- **PQN doc:** [B8 on Drive](https://docs.google.com/document/d/11-bvVVTK2mwZZPnObZ9N2t23GOtiAe_8MRUMS2LjawI)
- **Data status:** buildable · **Build status:** not started · **Verdict:** —

## Thesis
—

## Rules as written
- **Universe:** SPY
- **Entry:** buy at the close the day before each FOMC meeting
- **Exit:** sell at the close the day after the meeting
- **Position:** 100% long in the window (~8 per year), cash otherwise; doc notes it is a leverage candidate

## Data map
- **Data:** daily closes → Massive aggs; **FOMC dates are not in Massive** (no economic calendar) → static list from federalreserve.gov

## Open questions
- **⚠ Resolve before build:** most meetings span two days — define "meeting date" (decision / statement day).

**Decisions:** none yet. (Resolve each line with Judin before building — never pick a definition silently.)

## Risk
- **Risk:** no hedge

## Backtest
Not run. When it is, results live in `results/B8/` (returns.csv · trades.csv · eda.png · report.md), ending in `tools/backtest_eda.py`.

## Notes
—
