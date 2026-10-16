---
id: B3
name: Pre-Holiday Effect
tier: B — Calendar timing
strength: Moderate
difficulty: Beginner
source: Zhang & Jacobsen, "Are Monthly Seasonals Real? A Three Century Perspective"
doc: https://docs.google.com/document/d/14zmrK7AL44Jaui7IGrOa0G0YrY7NwQLqpkrLxbeqM2A
data_status: buildable
build_status: not started
verdict: 
---
# B3 · Pre-Holiday Effect

## At a glance
- **Tier:** B — Calendar timing
- **Strength (PQN):** Moderate · **Difficulty (PQN):** Beginner
- **Source:** Zhang & Jacobsen, "Are Monthly Seasonals Real? A Three Century Perspective"
- **PQN doc:** [B3 on Drive](https://docs.google.com/document/d/14zmrK7AL44Jaui7IGrOa0G0YrY7NwQLqpkrLxbeqM2A)
- **Data status:** buildable · **Build status:** not started · **Verdict:** —

## Thesis
—

## Rules as written
- **Universe:** SPY
- **Holidays (doc list):** New Year's, MLK, Presidents', Good Friday, Memorial, Independence, Labor, Election Day, Thanksgiving, Christmas
- **Entry:** 100% long on the trading day immediately before a market holiday (code: a holiday within the next 1–2 calendar days, weekends removed)
- **Exit:** back to cash after the pre-holiday session

## Data map
- **Data:** daily closes → Massive aggs; historical exchange-holiday calendar from an exchange-calendar library (Massive's holiday endpoint is upcoming-only)
- **Data note:** NYSE has not closed for Election Day since 1980, so an exchange calendar will not trigger it.

## Open questions
None flagged in the triage.

**Decisions:** none yet. (Resolve each line with Judin before building — never pick a definition silently.)

## Risk
- **Risk:** no hedge; effect diminished since late 1980s except small caps (per source)

## Backtest
Not run. When it is, results live in `results/B3/` (returns.csv · trades.csv · eda.png · report.md), ending in `tools/backtest_eda.py`.

## Notes
—
