---
id: C9
name: Short Term Reversal Effect in Stocks
tier: C — Single stocks, price + market cap
strength: Moderate
difficulty: Advanced
source: large-cap reversal-net-of-costs study; Nagel, "Evaporating Liquidity"; de Groot, Huij & Zhou
doc: https://docs.google.com/document/d/1ppuNA000L-wRst1Jx_kTStU6ybL_OUJabVQNLxW9KcI
data_status: buildable
build_status: not started
verdict: 
---
# C9 · Short Term Reversal Effect in Stocks

## At a glance
- **Tier:** C — Single stocks, price + market cap
- **Strength (PQN):** Moderate · **Difficulty (PQN):** Advanced
- **Source:** large-cap reversal-net-of-costs study; Nagel, "Evaporating Liquidity"; de Groot, Huij & Zhou
- **PQN doc:** [C9 on Drive](https://docs.google.com/document/d/1ppuNA000L-wRst1Jx_kTStU6ybL_OUJabVQNLxW9KcI)
- **Data status:** buildable · **Build status:** not started · **Verdict:** —

## Thesis
—

## Rules as written
- **Universe:** 500 most liquid US (price > $1) → top 100 by market cap
- **Long:** 10 lowest 1-week (5-day) returns; **Short:** 10 highest 1-month (21-day) returns
- **Weighting:** ±1/10 each
- **Rebalance:** weekly

## Data map
—

> **Tier note:** Common data for this tier: daily bars for the whole cross-section (grouped daily is one call per date), dollar volume for liquidity ranks, market cap for size ranks, delisted tickers for survivorship (open check #2).

## Open questions
None flagged in the triage.

**Decisions:** none yet. (Resolve each line with Judin before building — never pick a definition silently.)

## Risk
- **Risk:** liquidity-providing but short-volatility — strict risk control in crises

## Backtest
Not run. When it is, results live in `results/C9/` (returns.csv · trades.csv · eda.png · report.md), ending in `tools/backtest_eda.py`.

## Notes
—
