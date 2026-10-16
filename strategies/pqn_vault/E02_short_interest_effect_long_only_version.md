---
id: E2
name: Short Interest Effect – Long-Only Version
tier: E — Short interest
strength: Moderate
difficulty: Beginner
source: Asquith, Pathak & Ritter
doc: https://docs.google.com/document/d/194GKwEsOT-xyir1tbNAhZujQLjN3o0CAhN9s_0fp9TQ
data_status: buildable
build_status: not started
verdict: 
---
# E2 · Short Interest Effect – Long-Only Version

## At a glance
- **Tier:** E — Short interest
- **Strength (PQN):** Moderate · **Difficulty (PQN):** Beginner
- **Source:** Asquith, Pathak & Ritter
- **PQN doc:** [E2 on Drive](https://docs.google.com/document/d/194GKwEsOT-xyir1tbNAhZujQLjN3o0CAhN9s_0fp9TQ)
- **Data status:** buildable · **Build status:** not started · **Verdict:** —

## Thesis
—

## Rules as written
- **Universe:** all NYSE / AMEX / NASDAQ stocks
- **Signal:** short interest ÷ shares outstanding
- **Holdings:** the least-shorted **1%** of the universe (doc code `top_pct=0.01`); equal weight
- **Rebalance:** monthly, first trading day

## Data map
—

> **Tier note:** Common data: Massive `/stocks/v1/short-interest` (FINRA bi-monthly settlements). Both docs define the ratio on **shares outstanding** — `tools/short_float.py` uses **free float** (different denominator; float feed has known garbage rows). Key the signal to publication date, not settlement date. Check history depth (open check #4).

## Open questions
None flagged in the triage.

**Decisions:** none yet. (Resolve each line with Judin before building — never pick a definition silently.)

## Risk
- **Risk:** long-only, high market correlation

## Backtest
Not run. When it is, results live in `results/E2/` (returns.csv · trades.csv · eda.png · report.md), ending in `tools/backtest_eda.py`.

## Notes
—
