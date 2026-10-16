---
id: E1
name: Short Interest Effect – Long-Short Version
tier: E — Short interest
strength: Moderate
difficulty: Intermediate
source: Asquith, Pathak & Ritter, "Short Interest, Institutional Ownership, and Stock Returns"
doc: https://docs.google.com/document/d/1ixWnVQrQvhdlXDx8IMHPNL2fk3DZjcawb8KHsx0AEVg
data_status: buildable
build_status: not started
verdict: 
---
# E1 · Short Interest Effect – Long-Short Version

## At a glance
- **Tier:** E — Short interest
- **Strength (PQN):** Moderate · **Difficulty (PQN):** Intermediate
- **Source:** Asquith, Pathak & Ritter, "Short Interest, Institutional Ownership, and Stock Returns"
- **PQN doc:** [E1 on Drive](https://docs.google.com/document/d/1ixWnVQrQvhdlXDx8IMHPNL2fk3DZjcawb8KHsx0AEVg)
- **Data status:** buildable · **Build status:** not started · **Verdict:** —

## Thesis
—

## Rules as written
- **Universe:** all NYSE / AMEX / NASDAQ stocks
- **Signal:** short interest ÷ shares outstanding
- **Positions:** deciles; long lowest, short highest; equal weight, symmetric legs
- **Rebalance:** monthly, first trading day

## Data map
—

> **Tier note:** Common data: Massive `/stocks/v1/short-interest` (FINRA bi-monthly settlements). Both docs define the ratio on **shares outstanding** — `tools/short_float.py` uses **free float** (different denominator; float feed has known garbage rows). Key the signal to publication date, not settlement date. Check history depth (open check #4).

## Open questions
None flagged in the triage.

**Decisions:** none yet. (Resolve each line with Judin before building — never pick a definition silently.)

## Risk
- **Risk:** hedge value unresolved per doc

## Backtest
Not run. When it is, results live in `results/E1/` (returns.csv · trades.csv · eda.png · report.md), ending in `tools/backtest_eda.py`.

## Notes
—
