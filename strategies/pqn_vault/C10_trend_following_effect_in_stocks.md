---
id: C10
name: Trend-following Effect in Stocks
tier: C — Single stocks, price + market cap
strength: Moderate
difficulty: Advanced
source: Wilcox & Crittenden, "Does Trend Following Work on Stocks?"
doc: https://docs.google.com/document/d/1JiPCN6xHibzCSvx_W21AtXDOXEF84XWKrwZk6pOGUyA
data_status: buildable
build_status: not started
verdict: 
---
# C10 · Trend-following Effect in Stocks

## At a glance
- **Tier:** C — Single stocks, price + market cap
- **Strength (PQN):** Moderate · **Difficulty (PQN):** Advanced
- **Source:** Wilcox & Crittenden, "Does Trend Following Work on Stocks?"
- **PQN doc:** [C10 on Drive](https://docs.google.com/document/d/1JiPCN6xHibzCSvx_W21AtXDOXEF84XWKrwZk6pOGUyA)
- **Data status:** buildable · **Build status:** not started · **Verdict:** —

## Thesis
—

## Rules as written
- **Universe:** 100 most liquid US stocks, price > $5
- **Entry:** close ≥ highest close in the stock's entire available history
- **Exit:** 10-period ATR trailing stop; stop = price − 1 ATR, only ratchets up
- **Holdings:** every entered, not-stopped name; equal weight
- **Rebalance:** daily; doc assumes ~0.5% round-turn costs

## Data map
- **Data:** daily OHLC (for ATR)
- **Data note:** "all-time high" = highest close since the first bar on the plan (open check #1).

> **Tier note:** Common data for this tier: daily bars for the whole cross-section (grouped daily is one call per date), dollar volume for liquidity ranks, market cap for size ranks, delisted tickers for survivorship (open check #2).

## Open questions
None flagged in the triage.

**Decisions:** none yet. (Resolve each line with Judin before building — never pick a definition silently.)

## Risk
- **Risk:** long-only, no hedge

## Backtest
Not run. When it is, results live in `results/C10/` (returns.csv · trades.csv · eda.png · report.md), ending in `tools/backtest_eda.py`.

## Notes
—
