---
id: C5
name: 12 Month Cycle in Cross-Section of Stock Returns
tier: C — Single stocks, price + market cap
strength: Moderate
difficulty: Advanced
source: Heston & Sadka
doc: https://docs.google.com/document/d/1caLFzVMFjjWbJ-1Kv5JPnH6yGXoMFxcibTA_kXzGteY
data_status: buildable
build_status: not started
verdict: 
---
# C5 · 12 Month Cycle in Cross-Section of Stock Returns

## At a glance
- **Tier:** C — Single stocks, price + market cap
- **Strength (PQN):** Moderate · **Difficulty (PQN):** Advanced
- **Source:** Heston & Sadka
- **PQN doc:** [C5 on Drive](https://docs.google.com/document/d/1caLFzVMFjjWbJ-1Kv5JPnH6yGXoMFxcibTA_kXzGteY)
- **Data status:** buildable · **Build status:** not started · **Verdict:** —

## Thesis
—

## Rules as written
- **Source universe:** top 30% by market cap, NYSE + AMEX. **Implementation:** top US stocks by market cap on NYSE / AMEX / NASDAQ (up to 500), REITs excluded.
- **Signal:** the stock's return in the same calendar month one year ago
- **Positions:** deciles; long winners, short losers
- **Weighting:** source = equal; implementation = market-cap weighted per leg
- **Rebalance:** monthly

## Data map
- **Data:** REIT exclusion via SIC code, read per ticker

> **Tier note:** Common data for this tier: daily bars for the whole cross-section (grouped daily is one call per date), dollar volume for liquidity ranks, market cap for size ranks, delisted tickers for survivorship (open check #2).

## Open questions
None flagged in the triage.

**Decisions:** none yet. (Resolve each line with Judin before building — never pick a definition silently.)

## Risk
—

## Backtest
Not run. When it is, results live in `results/C5/` (returns.csv · trades.csv · eda.png · report.md), ending in `tools/backtest_eda.py`.

## Notes
—
