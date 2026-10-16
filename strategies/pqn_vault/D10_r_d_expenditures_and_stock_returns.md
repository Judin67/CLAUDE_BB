---
id: D10
name: R&D Expenditures and Stock Returns
tier: D — Single stocks + fundamentals
strength: Moderate
difficulty: Intermediate
source: Chan, Lakonishok & Sougiannis, "The Stock Market Valuation of Research and Development Expenditures"
doc: https://docs.google.com/document/d/1vtXza48RFncO9Dbe2kBtj8e6DbR-SSwcxKEZM8FopHQ
data_status: buildable
build_status: not started
verdict: 
---
# D10 · R&D Expenditures and Stock Returns

## At a glance
- **Tier:** D — Single stocks + fundamentals
- **Strength (PQN):** Moderate · **Difficulty (PQN):** Intermediate
- **Source:** Chan, Lakonishok & Sougiannis, "The Stock Market Valuation of Research and Development Expenditures"
- **PQN doc:** [D10 on Drive](https://docs.google.com/document/d/1vtXza48RFncO9Dbe2kBtj8e6DbR-SSwcxKEZM8FopHQ)
- **Data status:** buildable · **Build status:** not started · **Verdict:** —

## Thesis
—

## Rules as written
- **Universe:** NYSE / NASDAQ / AMEX with reported R&D, price > $5
- **Signal:** weighted 5-year R&D (weights 1.0, 0.8, 0.6, 0.4, 0.2, newest first) ÷ current market cap
- **Positions:** end of April; long top quintile, short bottom; equal weight
- **Rebalance:** yearly

## Data map
- **Data note:** needs 5 years of R&D per firm before its first score.

> **Tier note:** Common data for this tier: point-in-time fundamentals (use filing date, not period end, to avoid look-ahead) from Massive financials with EDGAR XBRL backfill (`edgar_client.latest_asof`). Check financials history depth first (open check #3).

## Open questions
None flagged in the triage.

**Decisions:** none yet. (Resolve each line with Judin before building — never pick a definition silently.)

## Risk
- **Risk:** very low beta (~0.006 per doc) but still suffers in bear markets

## Backtest
Not run. When it is, results live in `results/D10/` (returns.csv · trades.csv · eda.png · report.md), ending in `tools/backtest_eda.py`.

## Notes
—
