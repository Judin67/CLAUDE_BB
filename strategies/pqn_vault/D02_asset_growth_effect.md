---
id: D2
name: Asset Growth Effect
tier: D — Single stocks + fundamentals
strength: High
difficulty: Intermediate
source: Cooper, Gulen & Schill, "Asset Growth and the Cross-Section of Stock Returns"
doc: https://docs.google.com/document/d/11RHEq9lQkEimz7fAjgZpt5X3lXGCONi8qQBww35W_jQ
data_status: buildable
build_status: not started
verdict: 
---
# D2 · Asset Growth Effect

## At a glance
- **Tier:** D — Single stocks + fundamentals
- **Strength (PQN):** High · **Difficulty (PQN):** Intermediate
- **Source:** Cooper, Gulen & Schill, "Asset Growth and the Cross-Section of Stock Returns"
- **PQN doc:** [D2 on Drive](https://docs.google.com/document/d/11RHEq9lQkEimz7fAjgZpt5X3lXGCONi8qQBww35W_jQ)
- **Data status:** buildable · **Build status:** not started · **Verdict:** —

## Thesis
—

## Rules as written
- **Universe:** non-financial NYSE / AMEX / NASDAQ; implementation top 3,000 by market cap
- **Signal:** year-over-year % change in total assets
- **Positions:** deciles formed end of June; long lowest growth, short highest; equal weight
- **Rebalance:** annually

## Data map
- **Data:** annual total assets; financials excluded via SIC per ticker

> **Tier note:** Common data for this tier: point-in-time fundamentals (use filing date, not period end, to avoid look-ahead) from Massive financials with EDGAR XBRL backfill (`edgar_client.latest_asof`). Check financials history depth first (open check #3).

## Open questions
None flagged in the triage.

**Decisions:** none yet. (Resolve each line with Judin before building — never pick a definition silently.)

## Risk
—

## Backtest
Not run. When it is, results live in `results/D2/` (returns.csv · trades.csv · eda.png · report.md), ending in `tools/backtest_eda.py`.

## Notes
—
