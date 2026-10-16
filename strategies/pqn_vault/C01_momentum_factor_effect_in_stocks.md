---
id: C1
name: Momentum Factor Effect in Stocks
tier: C — Single stocks, price + market cap
strength: High
difficulty: Intermediate
source: momentum "fact and fiction" article; Griffin, Ji & Martin; Barroso & Santa-Clara, "Managing the Risk of Momentum"
doc: https://docs.google.com/document/d/1WAFaqL8mcwO6NX0gzM3KSgGXXoo1t9JpoU2P3_UZkcE
data_status: buildable
build_status: not started
verdict: 
---
# C1 · Momentum Factor Effect in Stocks

## At a glance
- **Tier:** C — Single stocks, price + market cap
- **Strength (PQN):** High · **Difficulty (PQN):** Intermediate
- **Source:** momentum "fact and fiction" article; Griffin, Ji & Martin; Barroso & Santa-Clara, "Managing the Risk of Momentum"
- **PQN doc:** [C1 on Drive](https://docs.google.com/document/d/1WAFaqL8mcwO6NX0gzM3KSgGXXoo1t9JpoU2P3_UZkcE)
- **Data status:** buildable · **Build status:** not started · **Verdict:** —

## Thesis
—

## Rules as written
- **Universe:** top 500 by dollar volume on NYSE / NASDAQ / AMEX
- **Signal:** 12-1 momentum — return from 252 days ago to ~21 days ago (skip the latest month)
- **Positions:** long top quintile, short bottom quintile; equal weight (±1/N)
- **Rebalance:** monthly, month start

## Data map
—

> **Tier note:** Common data for this tier: daily bars for the whole cross-section (grouped daily is one call per date), dollar volume for liquidity ranks, market cap for size ranks, delisted tickers for survivorship (open check #2).

## Open questions
None flagged in the triage.

**Decisions:** none yet. (Resolve each line with Judin before building — never pick a definition silently.)

## Risk
- **Risk:** momentum crashes after bear-market rebounds; doc points to volatility-scaled variants

## Backtest
Not run. When it is, results live in `results/C1/` (returns.csv · trades.csv · eda.png · report.md), ending in `tools/backtest_eda.py`.

## Notes
—
