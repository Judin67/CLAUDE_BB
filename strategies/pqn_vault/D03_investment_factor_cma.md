---
id: D3
name: Investment Factor (CMA)
tier: D — Single stocks + fundamentals
strength: Moderate
difficulty: Advanced
source: Fama & French, "A Five-Factor Asset Pricing Model"
doc: https://docs.google.com/document/d/15DttfkACMYhA4rNcibxfy2qy-Oon-RQXWNlf-LH7J5s
data_status: buildable
build_status: not started
verdict: 
---
# D3 · Investment Factor (CMA)

## At a glance
- **Tier:** D — Single stocks + fundamentals
- **Strength (PQN):** Moderate · **Difficulty (PQN):** Advanced
- **Source:** Fama & French, "A Five-Factor Asset Pricing Model"
- **PQN doc:** [D3 on Drive](https://docs.google.com/document/d/15DttfkACMYhA4rNcibxfy2qy-Oon-RQXWNlf-LH7J5s)
- **Data status:** buildable · **Build status:** not started · **Verdict:** —

## Thesis
—

## Rules as written
- **Source rules:** investment = growth of total assets for fiscal year ending t−1; independent 5 × 5 size × investment sorts on NYSE breakpoints; long biggest-size / lowest-investment, short biggest-size / highest-investment; value-weighted
- **Implementation:** top 3,000 by market cap; quintiles on investment; long lowest, short highest; equal weight
- **Rebalance:** annually, June

## Data map
—

> **Tier note:** Common data for this tier: point-in-time fundamentals (use filing date, not period end, to avoid look-ahead) from Massive financials with EDGAR XBRL backfill (`edgar_client.latest_asof`). Check financials history depth first (open check #3).

## Open questions
- **⚠ Resolve before build:** the doc's code divides a growth figure by total assets again (`asset_growth_1y / total_assets`) — looks double-scaled. Use the Fama-French definition.

**Decisions:** none yet. (Resolve each line with Judin before building — never pick a definition silently.)

## Risk
—

## Backtest
Not run. When it is, results live in `results/D3/` (returns.csv · trades.csv · eda.png · report.md), ending in `tools/backtest_eda.py`.

## Notes
- **Note:** same core signal as D2 (asset growth) — building both is largely redundant.
