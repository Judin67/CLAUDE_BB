---
id: F3
name: Reversal in Post-Earnings Announcement Drift
tier: F — Earnings-date event studies
strength: Moderate
difficulty: Advanced
source: Milian (reversal in PEAD)
doc: https://docs.google.com/document/d/11DwRW_rZJQaxk_4_pjYZU5difFX-zjMrWI2B0-8QYKA
data_status: buildable
build_status: not started
verdict: 
---
# F3 · Reversal in Post-Earnings Announcement Drift

## At a glance
- **Tier:** F — Earnings-date event studies
- **Strength (PQN):** Moderate · **Difficulty (PQN):** Advanced
- **Source:** Milian (reversal in PEAD)
- **PQN doc:** [F3 on Drive](https://docs.google.com/document/d/11DwRW_rZJQaxk_4_pjYZU5difFX-zjMrWI2B0-8QYKA)
- **Data status:** buildable · **Build status:** not started · **Verdict:** —

## Thesis
—

## Rules as written
- **Universe:** NYSE / AMEX / NASDAQ with an active options market (effectively large caps), reporting the next trading day
- **Signal:** previous announcement's EAR = stock return − market return from t−2 to t+1 business days
- **Positions:** versus the previous quarter's EAR distribution — long ≤ 10th percentile, short ≥ 90th percentile
- **Holding:** 2 days spanning the upcoming announcement; equal weight; cap 10 long / 10 short
- **Evaluation:** daily

## Data map
- **Data:** "active options market" filter needs options reference data (open check #5) or a large-cap proxy
- **Live gap:** needs forward earnings dates (see tier note)

> **Tier note:** Common data: announcement dates from EDGAR 8-K Item 2.02 filing dates (`tools/revenue_backfill.py` already finds the earnings 8-K per quarter). A filing date does not say before-open vs after-close — event windows must tolerate a one-day ambiguity. **Live-trading gap:** F3 and F4 enter *before* the announcement, so live use needs a **forward** earnings calendar — you have none (Benzinga 403, TMX 403). Backtests are fine (historical dates are known); live signals are not.

## Open questions
None flagged in the triage.

**Decisions:** none yet. (Resolve each line with Judin before building — never pick a definition silently.)

## Risk
—

## Backtest
Not run. When it is, results live in `results/F3/` (returns.csv · trades.csv · eda.png · report.md), ending in `tools/backtest_eda.py`.

## Notes
—
