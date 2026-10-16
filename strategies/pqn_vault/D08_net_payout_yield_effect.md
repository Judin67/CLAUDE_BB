---
id: D8
name: Net Payout Yield Effect
tier: D — Single stocks + fundamentals
strength: High
difficulty: Intermediate
source: Boudoukh, Michaely, Richardson & Roberts, "On the Importance of Measuring Payout Yield"; Gray & Vogel
doc: https://docs.google.com/document/d/1cQVy6bz5z-QL_TrEo4kWVLG8sPI36udDKF8cy3Zt1Lo
data_status: buildable
build_status: not started
verdict: 
---
# D8 · Net Payout Yield Effect

## At a glance
- **Tier:** D — Single stocks + fundamentals
- **Strength (PQN):** High · **Difficulty (PQN):** Intermediate
- **Source:** Boudoukh, Michaely, Richardson & Roberts, "On the Importance of Measuring Payout Yield"; Gray & Vogel
- **PQN doc:** [D8 on Drive](https://docs.google.com/document/d/1cQVy6bz5z-QL_TrEo4kWVLG8sPI36udDKF8cy3Zt1Lo)
- **Data status:** buildable · **Build status:** not started · **Verdict:** —

## Thesis
—

## Rules as written
- **Universe:** 500 most liquid on NYSE / AMEX / NASDAQ
- **Signal:** net payout yield = (dividends + repurchases − common stock issuance) ÷ year-end market cap (cash-flow repurchase measure)
- **Positions:** deciles; **long-only** top decile; equal weight
- **Rebalance:** formed end of June, hold one year

## Data map
- **Data:** cash-flow statement dividends paid, repurchases of common stock, proceeds from common stock issuance (XBRL)

> **Tier note:** Common data for this tier: point-in-time fundamentals (use filing date, not period end, to avoid look-ahead) from Massive financials with EDGAR XBRL backfill (`edgar_client.latest_asof`). Check financials history depth first (open check #3).

## Open questions
- **⚠ Resolve before build:** the doc's code formula (`total_yield × market_cap − issuance ÷ market_cap`) does not match its own rule text. Build from the rule text.

**Decisions:** none yet. (Resolve each line with Judin before building — never pick a definition silently.)

## Risk
- **Risk:** long-only, high market correlation

## Backtest
Not run. When it is, results live in `results/D8/` (returns.csv · trades.csv · eda.png · report.md), ending in `tools/backtest_eda.py`.

## Notes
—
