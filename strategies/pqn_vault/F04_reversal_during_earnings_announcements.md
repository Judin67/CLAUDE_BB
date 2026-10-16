---
id: F4
name: Reversal During Earnings Announcements
tier: F — Earnings-date event studies
strength: Moderate
difficulty: Advanced
source: study of six-fold reversal around earnings (market-maker inventory risk)
doc: https://docs.google.com/document/d/1j65KQMekLBbpBDwo9pj2pWJctWU631g2Oj4SLdUdXSk
data_status: buildable
build_status: not started
verdict: 
---
# F4 · Reversal During Earnings Announcements

## At a glance
- **Tier:** F — Earnings-date event studies
- **Strength (PQN):** Moderate · **Difficulty (PQN):** Advanced
- **Source:** study of six-fold reversal around earnings (market-maker inventory risk)
- **PQN doc:** [F4 on Drive](https://docs.google.com/document/d/1j65KQMekLBbpBDwo9pj2pWJctWU631g2Oj4SLdUdXSk)
- **Data status:** buildable · **Build status:** not started · **Verdict:** —

## Thesis
—

## Rules as written
- **Universe:** NYSE / AMEX / NASDAQ with active options; keep top market-cap quintile
- **Signal:** return over t−4 to t−2 before the announcement
- **Positions:** versus previous quarter's distribution — long ≤ 20th percentile (losers), short ≥ 80th (winners)
- **Holding:** 3 days (t−1, t, t+1); equal weight; cap 20 long / 20 short

## Data map
- **Live gap:** needs forward earnings dates (see tier note)

> **Tier note:** Common data: announcement dates from EDGAR 8-K Item 2.02 filing dates (`tools/revenue_backfill.py` already finds the earnings 8-K per quarter). A filing date does not say before-open vs after-close — event windows must tolerate a one-day ambiguity. **Live-trading gap:** F3 and F4 enter *before* the announcement, so live use needs a **forward** earnings calendar — you have none (Benzinga 403, TMX 403). Backtests are fine (historical dates are known); live signals are not.

## Open questions
- **⚠ Resolve before build:** the doc says "average return" over the window but its code computes a cumulative return.

**Decisions:** none yet. (Resolve each line with Judin before building — never pick a definition silently.)

## Risk
—

## Backtest
Not run. When it is, results live in `results/F4/` (returns.csv · trades.csv · eda.png · report.md), ending in `tools/backtest_eda.py`.

## Notes
—
