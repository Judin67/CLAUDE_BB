---
id: D6
name: Earnings Quality Factor
tier: D — Single stocks + fundamentals
strength: High
difficulty: Intermediate
source: Kozlov & Petajisto (global earnings-quality study, 1988–2012)
doc: https://docs.google.com/document/d/1aJpl6FvBcxZTuHdOA94lFGiyQ64YWlrSOnxIatZnuH0
data_status: buildable
build_status: not started
verdict: 
---
# D6 · Earnings Quality Factor

## At a glance
- **Tier:** D — Single stocks + fundamentals
- **Strength (PQN):** High · **Difficulty (PQN):** Intermediate
- **Source:** Kozlov & Petajisto (global earnings-quality study, 1988–2012)
- **PQN doc:** [D6 on Drive](https://docs.google.com/document/d/1aJpl6FvBcxZTuHdOA94lFGiyQ64YWlrSOnxIatZnuH0)
- **Data status:** buildable · **Build status:** not started · **Verdict:** —

## Thesis
—

## Rules as written
- **Universe:** largest US non-financials, top 3,000 by market cap
- **Four metrics:** accruals (lower better) · ROE (higher) · cash flow ÷ assets (higher) · debt ÷ assets (lower)
- **Accruals (doc):** (ΔCurrent assets − ΔCurrent liabilities − ΔCash + ΔCurrent debt − Depreciation) ÷ prior-year total assets
- **Score:** percentile-rank each metric so higher = better quality; sum the four
- **Positions:** long top 30%, short bottom 30%; equal weight
- **Rebalance:** annually, end of June

## Data map
—

> **Tier note:** Common data for this tier: point-in-time fundamentals (use filing date, not period end, to avoid look-ahead) from Massive financials with EDGAR XBRL backfill (`edgar_client.latest_asof`). Check financials history depth first (open check #3).

## Open questions
None flagged in the triage.

**Decisions:** none yet. (Resolve each line with Judin before building — never pick a definition silently.)

## Risk
- **Risk:** plausible diversifier; negatively correlated with value

## Backtest
Not run. When it is, results live in `results/D6/` (returns.csv · trades.csv · eda.png · report.md), ending in `tools/backtest_eda.py`.

## Notes
—
