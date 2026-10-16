---
id: C8
name: Betting Against Beta Factor in Stocks
tier: C — Single stocks, price + market cap
strength: High
difficulty: Advanced
source: Frazzini & Pedersen, "Betting Against Beta"
doc: https://docs.google.com/document/d/1L01M0INDTtNl8qy81L9VLr74vzpOIz_Nkxw2G1hKgiE
data_status: buildable
build_status: not started
verdict: 
---
# C8 · Betting Against Beta Factor in Stocks

## At a glance
- **Tier:** C — Single stocks, price + market cap
- **Strength (PQN):** High · **Difficulty (PQN):** Advanced
- **Source:** Frazzini & Pedersen, "Betting Against Beta"
- **PQN doc:** [C8 on Drive](https://docs.google.com/document/d/1L01M0INDTtNl8qy81L9VLr74vzpOIz_Nkxw2G1hKgiE)
- **Data status:** buildable · **Build status:** not started · **Verdict:** —

## Thesis
—

## Rules as written
- **Universe:** 1,000 most liquid US stocks, price > $5; SPY = market
- **Signal:** 252-day beta vs SPY
- **Positions:** long bottom-beta decile, short top-beta decile
- **Leverage:** long leg × min(cap, 1 / mean beta); short leg × min(cap, 1 / mean beta); doc code caps at 2×
- **Weighting:** classic = weighted by ranked beta; doc's simplification = equal weight within deciles
- **Rebalance:** monthly

## Data map
—

> **Tier note:** Common data for this tier: daily bars for the whole cross-section (grouped daily is one call per date), dollar volume for liquidity ranks, market cap for size ranks, delisted tickers for survivorship (open check #2).

## Open questions
None flagged in the triage.

**Decisions:** none yet. (Resolve each line with Judin before building — never pick a definition silently.)

## Risk
- **Risk:** partial hedge; crowded low-beta valuations

## Backtest
Not run. When it is, results live in `results/C8/` (returns.csv · trades.csv · eda.png · report.md), ending in `tools/backtest_eda.py`.

## Notes
—
