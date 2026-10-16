---
id: D1
name: Value (Book-to-Market) Factor
tier: D — Single stocks + fundamentals
strength: High
difficulty: Intermediate
source: Asness, Frazzini, Israel & Moskowitz, "Fact, Fiction, and Value Investing"; Fama & French
doc: https://docs.google.com/document/d/1rvA0z6KY0twu2K9ZbOdzJ_ScvIXyEJ_vMDp1yQCVwNA
data_status: buildable
build_status: not started
verdict: 
---
# D1 · Value (Book-to-Market) Factor

## At a glance
- **Tier:** D — Single stocks + fundamentals
- **Strength (PQN):** High · **Difficulty (PQN):** Intermediate
- **Source:** Asness, Frazzini, Israel & Moskowitz, "Fact, Fiction, and Value Investing"; Fama & French
- **PQN doc:** [D1 on Drive](https://docs.google.com/document/d/1rvA0z6KY0twu2K9ZbOdzJ_ScvIXyEJ_vMDp1yQCVwNA)
- **Data status:** buildable · **Build status:** not started · **Verdict:** —

## Thesis
—

## Rules as written
- **Universe:** NYSE / AMEX / NASDAQ with valid P/B; top 3,000 by market cap
- **Signal:** P/B (inverse of book-to-market)
- **Positions:** quintiles; long lowest P/B, short highest P/B; equal weight; 100% long / 100% short
- **Rebalance:** monthly

## Data map
- **Data:** book equity (stockholders' equity) ÷ market cap

> **Tier note:** Common data for this tier: point-in-time fundamentals (use filing date, not period end, to avoid look-ahead) from Massive financials with EDGAR XBRL backfill (`edgar_client.latest_asof`). Check financials history depth first (open check #3).

## Open questions
None flagged in the triage.

**Decisions:** none yet. (Resolve each line with Judin before building — never pick a definition silently.)

## Risk
- **Risk:** not a hedge; value tied to liquidity and growth risk

## Backtest
Not run. When it is, results live in `results/D1/` (returns.csv · trades.csv · eda.png · report.md), ending in `tools/backtest_eda.py`.

## Notes
—
