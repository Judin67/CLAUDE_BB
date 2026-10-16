---
id: D12
name: Residual Momentum Factor
tier: D — Single stocks + fundamentals
strength: High
difficulty: Advanced
source: Blitz, Huij & Martens, "Residual Momentum"
doc: https://docs.google.com/document/d/1eFzpWCTXd2TXcmjPFDhdkhLle_ArmG6l_WYL84zwfic
data_status: buildable
build_status: not started
verdict: 
---
# D12 · Residual Momentum Factor

## At a glance
- **Tier:** D — Single stocks + fundamentals
- **Strength (PQN):** High · **Difficulty (PQN):** Advanced
- **Source:** Blitz, Huij & Martens, "Residual Momentum"
- **PQN doc:** [D12 on Drive](https://docs.google.com/document/d/1eFzpWCTXd2TXcmjPFDhdkhLle_ArmG6l_WYL84zwfic)
- **Data status:** buildable · **Build status:** not started · **Verdict:** —

## Thesis
—

## Rules as written
- **Source universe:** domestic primary NYSE / AMEX / NASDAQ, price > $1, excluding closed-end funds, REITs, unit trusts, ADRs, foreign; largest 10% by market cap. **Implementation:** top 500 by market cap.
- **Factor model:** each month regress each stock's past 36 monthly returns on market, size and value factor returns
- **Signal:** sum of the past 12 monthly residuals (excluding the most recent month) ÷ standard deviation of those residuals
- **Positions:** deciles; long top, short bottom; equal weight
- **Rebalance:** monthly

## Data map
- **Data:** size and value factors built from the same universe (market cap, book-to-market)
- **Data note:** needs 36 + 12 months of history per stock.

> **Tier note:** Common data for this tier: point-in-time fundamentals (use filing date, not period end, to avoid look-ahead) from Massive financials with EDGAR XBRL backfill (`edgar_client.latest_asof`). Check financials history depth first (open check #3).

## Open questions
- **⚠ Resolve before build:** the doc's text calls the regression intercept "the residual return", but its code (and the paper) uses the residuals. Use residuals.

**Decisions:** none yet. (Resolve each line with Judin before building — never pick a definition silently.)

## Risk
—

## Backtest
Not run. When it is, results live in `results/D12/` (returns.csv · trades.csv · eda.png · report.md), ending in `tools/backtest_eda.py`.

## Notes
—
