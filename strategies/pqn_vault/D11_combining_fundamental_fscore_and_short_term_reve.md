---
id: D11
name: Combining Fundamental FSCORE and Short-Term Reversals
tier: D — Single stocks + fundamentals
strength: High
difficulty: Intermediate
source: FSCORE-anchored reversal study; Piotroski FSCORE
doc: https://docs.google.com/document/d/1w7AsVp92FeMId7eG0-_jGLmEnaCj_9VY6vu8PpXVbRc
data_status: buildable
build_status: not started
verdict: 
---
# D11 · Combining Fundamental FSCORE and Short-Term Reversals

## At a glance
- **Tier:** D — Single stocks + fundamentals
- **Strength (PQN):** High · **Difficulty (PQN):** Intermediate
- **Source:** FSCORE-anchored reversal study; Piotroski FSCORE
- **PQN doc:** [D11 on Drive](https://docs.google.com/document/d/1w7AsVp92FeMId7eG0-_jGLmEnaCj_9VY6vu8PpXVbRc)
- **Data status:** buildable · **Build status:** not started · **Verdict:** —

## Thesis
—

## Rules as written
- **Universe:** common US stocks > $5, top 500 by dollar volume → largest 40% by market cap
- **FSCORE (9 points, 1 each):** ROA > 0 · operating cash flow > 0 · ROA rising · cash flow > earnings (low accruals) · leverage falling · current ratio rising · no new shares issued · gross margin rising · asset turnover rising
- **Reversal signal:** past 1-month (21-day) return
- **Long:** 1-month return < 0 AND FSCORE 7–9; **Short:** 1-month return > 0 AND FSCORE 0–3
- **Weighting:** equal
- **Rebalance:** monthly

## Data map
—

> **Tier note:** Common data for this tier: point-in-time fundamentals (use filing date, not period end, to avoid look-ahead) from Massive financials with EDGAR XBRL backfill (`edgar_client.latest_asof`). Check financials history depth first (open check #3).

## Open questions
None flagged in the triage.

**Decisions:** none yet. (Resolve each line with Judin before building — never pick a definition silently.)

## Risk
- **Risk:** liquidity-providing but short-volatility

## Backtest
Not run. When it is, results live in `results/D11/` (returns.csv · trades.csv · eda.png · report.md), ending in `tools/backtest_eda.py`.

## Notes
—
