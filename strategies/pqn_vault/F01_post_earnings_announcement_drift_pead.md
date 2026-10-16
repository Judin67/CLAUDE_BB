---
id: F1
name: Post-Earnings Announcement Drift (PEAD)
tier: F — Earnings-date event studies
strength: High
difficulty: Advanced
source: Ball & Brown (1968) lineage; SUE + EAR combination literature
doc: https://docs.google.com/document/d/1rGfek7rRYiz8DHOnVCebpxRD65s36ypOYYJahrixCnE
data_status: buildable
build_status: not started
verdict: 
---
# F1 · Post-Earnings Announcement Drift (PEAD)

## At a glance
- **Tier:** F — Earnings-date event studies
- **Strength (PQN):** High · **Difficulty (PQN):** Advanced
- **Source:** Ball & Brown (1968) lineage; SUE + EAR combination literature
- **PQN doc:** [F1 on Drive](https://docs.google.com/document/d/1rGfek7rRYiz8DHOnVCebpxRD65s36ypOYYJahrixCnE)
- **Data status:** buildable · **Build status:** not started · **Verdict:** —

## Thesis
—

## Rules as written
- **Universe:** NYSE / AMEX / NASDAQ excluding financials and utilities, price ≥ $5
- **SUE:** (actual EPS − expected EPS) ÷ standard deviation of past surprises; expected = last same-quarter EPS + average year-over-year same-quarter change (seasonal random walk with drift); needs ≥ 4 same-quarter observations and ≥ 4 past surprises
- **EAR:** 3-day return centered on the announcement minus the market's return
- **Positions:** quintile cut-offs from the previous quarter's cross-section (no look-ahead); long top-SUE ∩ top-EAR; equal weight; **long-only**
- **Timing:** enter 2nd day after announcement; hold one quarter (~60 trading days); quarterly

## Data map
- **Data:** quarterly EPS from XBRL (Q4 is usually only in the 10-K annual figure — derive it); dates from 8-K 2.02

> **Tier note:** Common data: announcement dates from EDGAR 8-K Item 2.02 filing dates (`tools/revenue_backfill.py` already finds the earnings 8-K per quarter). A filing date does not say before-open vs after-close — event windows must tolerate a one-day ambiguity. **Live-trading gap:** F3 and F4 enter *before* the announcement, so live use needs a **forward** earnings calendar — you have none (Benzinga 403, TMX 403). Backtests are fine (historical dates are known); live signals are not.

## Open questions
None flagged in the triage.

**Decisions:** none yet. (Resolve each line with Judin before building — never pick a definition silently.)

## Risk
—

## Backtest
Not run. When it is, results live in `results/F1/` (returns.csv · trades.csv · eda.png · report.md), ending in `tools/backtest_eda.py`.

## Notes
—
