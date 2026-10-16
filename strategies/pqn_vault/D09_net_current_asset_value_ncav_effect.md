---
id: D9
name: Net Current Asset Value (NCAV) Effect
tier: D — Single stocks + fundamentals
strength: Moderate
difficulty: Intermediate
source: Xiao & Arnold, "Testing Benjamin Graham's Net Current Asset Value Strategy in London"
doc: https://docs.google.com/document/d/1GXr0uF0mllBBNy-tzk9JAgnRJbRbQ_NUdhW9y2WWfBE
data_status: buildable
build_status: not started
verdict: 
---
# D9 · Net Current Asset Value (NCAV) Effect

## At a glance
- **Tier:** D — Single stocks + fundamentals
- **Strength (PQN):** Moderate · **Difficulty (PQN):** Intermediate
- **Source:** Xiao & Arnold, "Testing Benjamin Graham's Net Current Asset Value Strategy in London"
- **PQN doc:** [D9 on Drive](https://docs.google.com/document/d/1GXr0uF0mllBBNy-tzk9JAgnRJbRbQ_NUdhW9y2WWfBE)
- **Data status:** buildable · **Build status:** not started · **Verdict:** —

## Thesis
—

## Rules as written
- **Source universe:** London-listed, excluding multi-share-class, foreign, lightly-regulated-market and financial firms. **Implementation:** top 3,000 US by market cap.
- **Signal:** NCAV ÷ market value, where NCAV = current assets − **all** liabilities
- **Filter:** NCAV/MV > 1.5
- **Weighting:** equal across all qualifiers; cash if none
- **Rebalance:** formed July, hold one year

## Data map
—

> **Tier note:** Common data for this tier: point-in-time fundamentals (use filing date, not period end, to avoid look-ahead) from Massive financials with EDGAR XBRL backfill (`edgar_client.latest_asof`). Check financials history depth first (open check #3).

## Open questions
- **⚠ Resolve before build:** the doc's code proxies NCAV with working capital (current assets − current liabilities), which ignores long-term liabilities. Use the stated definition.

**Decisions:** none yet. (Resolve each line with Judin before building — never pick a definition silently.)

## Risk
—

## Backtest
Not run. When it is, results live in `results/D9/` (returns.csv · trades.csv · eda.png · report.md), ending in `tools/backtest_eda.py`.

## Notes
—
