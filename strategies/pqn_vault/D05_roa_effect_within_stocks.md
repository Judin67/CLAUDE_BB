---
id: D5
name: ROA Effect within Stocks
tier: D — Single stocks + fundamentals
strength: High
difficulty: Intermediate
source: Hou, Xue & Zhang (q-factor model)
doc: https://docs.google.com/document/d/1JetnwYgOyYanbeZAGcjmgXtojvd2fCWYMz4B6P9Do6Y
data_status: buildable
build_status: not started
verdict: 
---
# D5 · ROA Effect within Stocks

## At a glance
- **Tier:** D — Single stocks + fundamentals
- **Strength (PQN):** High · **Difficulty (PQN):** Intermediate
- **Source:** Hou, Xue & Zhang (q-factor model)
- **PQN doc:** [D5 on Drive](https://docs.google.com/document/d/1JetnwYgOyYanbeZAGcjmgXtojvd2fCWYMz4B6P9Do6Y)
- **Data status:** buildable · **Build status:** not started · **Verdict:** —

## Thesis
—

## Rules as written
- **Universe:** top 500 by dollar volume, price > $5
- **Size split:** two halves by market cap
- **Signal:** ROA = quarterly income before extraordinary items ÷ one-quarter-lagged total assets
- **Positions:** deciles within each size half; long top 3 deciles of each half, short bottom 3 deciles of each half; equal weight
- **Rebalance:** monthly

## Data map
—

> **Tier note:** Common data for this tier: point-in-time fundamentals (use filing date, not period end, to avoid look-ahead) from Massive financials with EDGAR XBRL backfill (`edgar_client.latest_asof`). Check financials history depth first (open check #3).

## Open questions
- **⚠ Resolve before build:** "extraordinary items" were removed from US GAAP in 2015, so that income line is not reported in recent filings — pick the replacement income concept.

**Decisions:** none yet. (Resolve each line with Judin before building — never pick a definition silently.)

## Risk
—

## Backtest
Not run. When it is, results live in `results/D5/` (returns.csv · trades.csv · eda.png · report.md), ending in `tools/backtest_eda.py`.

## Notes
—
