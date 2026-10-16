---
id: C7
name: Low Volatility Factor Effect in Stocks
tier: C — Single stocks, price + market cap
strength: High
difficulty: Intermediate
source: global low-volatility study (1986–2006); Clarke, de Silva & Thorley; Baker, Bradley & Wurgler
doc: https://docs.google.com/document/d/1dKtSYcmOGPTT17oaQhM4sB1ZboFT0jHL3wwN76CMA-U
data_status: buildable
build_status: not started
verdict: 
---
# C7 · Low Volatility Factor Effect in Stocks

## At a glance
- **Tier:** C — Single stocks, price + market cap
- **Strength (PQN):** High · **Difficulty (PQN):** Intermediate
- **Source:** global low-volatility study (1986–2006); Clarke, de Silva & Thorley; Baker, Bradley & Wurgler
- **PQN doc:** [C7 on Drive](https://docs.google.com/document/d/1dKtSYcmOGPTT17oaQhM4sB1ZboFT0jHL3wwN76CMA-U)
- **Data status:** buildable · **Build status:** not started · **Verdict:** —

## Thesis
—

## Rules as written
- **Universe:** US large caps with fundamentals (implementation: top 3,000 by market cap)
- **Signal:** standard deviation of weekly returns
- **Selection:** lowest-volatility quartile (original study: lowest decile); equal weight; long-only
- **Rebalance:** monthly, month end

## Data map
—

> **Tier note:** Common data for this tier: daily bars for the whole cross-section (grouped daily is one call per date), dollar volume for liquidity ranks, market cap for size ranks, delisted tickers for survivorship (open check #2).

## Open questions
- **⚠ Resolve before build:** lookback — the doc says "past three years" but its code comment says "roughly 252 trading days".

**Decisions:** none yet. (Resolve each line with Judin before building — never pick a definition silently.)

## Risk
- **Risk:** long-only softens drawdowns; long-short (lowest decile vs highest) is the hedge version

## Backtest
Not run. When it is, results live in `results/C7/` (returns.csv · trades.csv · eda.png · report.md), ending in `tools/backtest_eda.py`.

## Notes
—
