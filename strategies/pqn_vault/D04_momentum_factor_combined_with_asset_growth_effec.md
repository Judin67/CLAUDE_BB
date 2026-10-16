---
id: D4
name: Momentum Factor Combined with Asset Growth Effect
tier: D — Single stocks + fundamentals
strength: High
difficulty: Advanced
source: momentum × asset-growth interaction study
doc: https://docs.google.com/document/d/1_9Be-PKr5juaZXS_8VfMRTGLpYDgkXDkzxxy64DfQaY
data_status: buildable
build_status: not started
verdict: 
---
# D4 · Momentum Factor Combined with Asset Growth Effect

## At a glance
- **Tier:** D — Single stocks + fundamentals
- **Strength (PQN):** High · **Difficulty (PQN):** Advanced
- **Source:** momentum × asset-growth interaction study
- **PQN doc:** [D4 on Drive](https://docs.google.com/document/d/1_9Be-PKr5juaZXS_8VfMRTGLpYDgkXDkzxxy64DfQaY)
- **Data status:** buildable · **Build status:** not started · **Verdict:** —

## Thesis
—

## Rules as written
- **Universe:** NYSE / AMEX / NASDAQ excluding names below the 20th NYSE market-cap percentile; implementation 500 most liquid
- **Sort 1:** total-asset growth t−2 → t−1 (July cut-off) → keep top decile (highest growth)
- **Sort 2:** within it, 11-month return skipping the most recent month → quintiles
- **Positions:** long top momentum quintile, short bottom; equal weight
- **Rebalance:** monthly, **flat in January** (hold February–December)

## Data map
—

> **Tier note:** Common data for this tier: point-in-time fundamentals (use filing date, not period end, to avoid look-ahead) from Massive financials with EDGAR XBRL backfill (`edgar_client.latest_asof`). Check financials history depth first (open check #3).

## Open questions
None flagged in the triage.

**Decisions:** none yet. (Resolve each line with Judin before building — never pick a definition silently.)

## Risk
- **Risk:** positive in NBER recession months per source

## Backtest
Not run. When it is, results live in `results/D4/` (returns.csv · trades.csv · eda.png · report.md), ending in `tools/backtest_eda.py`.

## Notes
—
