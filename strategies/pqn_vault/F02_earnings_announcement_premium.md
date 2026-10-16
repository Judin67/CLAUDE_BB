---
id: F2
name: Earnings Announcement Premium
tier: F — Earnings-date event studies
strength: Moderate
difficulty: Advanced
source: Frazzini & Lamont, "The Earnings Announcement Premium and Trading Volume"
doc: https://docs.google.com/document/d/1EKf9S4WSsLaUU2chH2upgp24jAEMB8_w-THi_0s5otM
data_status: buildable
build_status: not started
verdict: 
---
# F2 · Earnings Announcement Premium

## At a glance
- **Tier:** F — Earnings-date event studies
- **Strength (PQN):** Moderate · **Difficulty (PQN):** Advanced
- **Source:** Frazzini & Lamont, "The Earnings Announcement Premium and Trading Volume"
- **PQN doc:** [F2 on Drive](https://docs.google.com/document/d/1EKf9S4WSsLaUU2chH2upgp24jAEMB8_w-THi_0s5otM)
- **Data status:** buildable · **Build status:** not started · **Verdict:** —

## Thesis
—

## Rules as written
- **Universe:** top ~1,000 by dollar volume
- **Signal:** volume concentration = volume in the previous 16 announcement months ÷ total volume over the previous 48 months
- **Selection:** top quintile by concentration
- **Split:** announced in this calendar month last year → long; otherwise → short
- **Weighting:** market-cap weighted per leg
- **Rebalance:** monthly, month start

## Data map
- **Data:** 48 months of monthly volume (Massive aggs) + 4 years of announcement months (8-K 2.02)

> **Tier note:** Common data: announcement dates from EDGAR 8-K Item 2.02 filing dates (`tools/revenue_backfill.py` already finds the earnings 8-K per quarter). A filing date does not say before-open vs after-close — event windows must tolerate a one-day ambiguity. **Live-trading gap:** F3 and F4 enter *before* the announcement, so live use needs a **forward** earnings calendar — you have none (Benzinga 403, TMX 403). Backtests are fine (historical dates are known); live signals are not.

## Open questions
None flagged in the triage.

**Decisions:** none yet. (Resolve each line with Judin before building — never pick a definition silently.)

## Risk
—

## Backtest
Not run. When it is, results live in `results/F2/` (returns.csv · trades.csv · eda.png · report.md), ending in `tools/backtest_eda.py`.

## Notes
- **Note:** uses last year's calendar as the forecast, so it does not need a forward calendar live.
