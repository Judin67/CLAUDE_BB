---
id: C2
name: Momentum Effect in Stocks in Small Portfolios
tier: C — Single stocks, price + market cap
strength: Moderate
difficulty: Intermediate
source: Siganos (UK data); Ammann, Moellenbeck & Schmid
doc: https://docs.google.com/document/d/1k3H-LCs2Ivh397m9ymtzdYa9vdMnapqaX1C-h7nlZrU
data_status: buildable
build_status: not started
verdict: 
---
# C2 · Momentum Effect in Stocks in Small Portfolios

## At a glance
- **Tier:** C — Single stocks, price + market cap
- **Strength (PQN):** Moderate · **Difficulty (PQN):** Intermediate
- **Source:** Siganos (UK data); Ammann, Moellenbeck & Schmid
- **PQN doc:** [C2 on Drive](https://docs.google.com/document/d/1k3H-LCs2Ivh397m9ymtzdYa9vdMnapqaX1C-h7nlZrU)
- **Data status:** buildable · **Build status:** not started · **Verdict:** —

## Thesis
—

## Rules as written
- **Source rules:** UK listings excluding smallest 25% by market cap; 10 most extreme names each side
- **Implementation:** top 500 US stocks; trailing 12-month return (252 days, no skip); long top decile, short bottom decile; equal weight
- **Rebalance:** yearly

## Data map
—

> **Tier note:** Common data for this tier: daily bars for the whole cross-section (grouped daily is one call per date), dollar volume for liquidity ranks, market cap for size ranks, delisted tickers for survivorship (open check #2).

## Open questions
None flagged in the triage.

**Decisions:** none yet. (Resolve each line with Judin before building — never pick a definition silently.)

## Risk
- **Risk:** concentrated; momentum-crash prone

## Backtest
Not run. When it is, results live in `results/C2/` (returns.csv · trades.csv · eda.png · report.md), ending in `tools/backtest_eda.py`.

## Notes
—
