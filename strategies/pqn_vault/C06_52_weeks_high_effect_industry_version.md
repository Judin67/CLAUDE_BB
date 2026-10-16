---
id: C6
name: 52-Weeks High Effect (industry version)
tier: C — Single stocks, price + market cap
strength: Moderate
difficulty: Advanced
source: George & Hwang, "The 52-Week High and Momentum Investing" + industry extension
doc: https://docs.google.com/document/d/1wFWGfx_m4bkebNVzYgpNiXhMs2gDCrkjPcRBz_MsjGg
data_status: buildable
build_status: not started
verdict: 
---
# C6 · 52-Weeks High Effect (industry version)

## At a glance
- **Tier:** C — Single stocks, price + market cap
- **Strength (PQN):** Moderate · **Difficulty (PQN):** Advanced
- **Source:** George & Hwang, "The 52-Week High and Momentum Investing" + industry extension
- **PQN doc:** [C6 on Drive](https://docs.google.com/document/d/1wFWGfx_m4bkebNVzYgpNiXhMs2gDCrkjPcRBz_MsjGg)
- **Data status:** buildable · **Build status:** not started · **Verdict:** —

## Thesis
—

## Rules as written
- **Universe:** top ~500 by dollar volume on NYSE / AMEX / NASDAQ, grouped by industry
- **Signal:** PRILAG = price ÷ 252-day high; industry score = market-cap-weighted average PRILAG
- **Positions:** long stocks in the 6 highest-scoring industries, short the 6 lowest
- **Weighting:** equal weight within selected industries
- **Holding:** 3 months, tranched (1/3 of book rebalanced each month); month-end evaluation

## Data map
- **Data:** industry from SIC code per ticker (the list-endpoint SIC filter is silently ignored)

> **Tier note:** Common data for this tier: daily bars for the whole cross-section (grouped daily is one call per date), dollar volume for liquidity ranks, market cap for size ranks, delisted tickers for survivorship (open check #2).

## Open questions
- **⚠ Resolve before build:** industry granularity — the doc does not say which SIC level defines an "industry".

**Decisions:** none yet. (Resolve each line with Judin before building — never pick a definition silently.)

## Risk
—

## Backtest
Not run. When it is, results live in `results/C6/` (returns.csv · trades.csv · eda.png · report.md), ending in `tools/backtest_eda.py`.

## Notes
—
