---
id: G1
name: Alpha Cloning – Following 13F Filings
tier: G — EDGAR filings
strength: Moderate
difficulty: Intermediate
source: Cohen, Polk & Silli, "Best Ideas"
doc: https://docs.google.com/document/d/1PF665ifntd6PT8qWqq-LkFr3AVgrEO-krIH3L3ddhUU
data_status: buildable
build_status: not started
verdict: 
---
# G1 · Alpha Cloning – Following 13F Filings

## At a glance
- **Tier:** G — EDGAR filings
- **Strength (PQN):** Moderate · **Difficulty (PQN):** Intermediate
- **Source:** Cohen, Polk & Silli, "Best Ideas"
- **PQN doc:** [G1 on Drive](https://docs.google.com/document/d/1PF665ifntd6PT8qWqq-LkFr3AVgrEO-krIH3L3ddhUU)
- **Data status:** buildable · **Build status:** not started · **Verdict:** —

## Thesis
—

## Rules as written
- **Universe:** stocks held by a chosen set of active mutual and hedge fund managers
- **Signal:** vote count = number of tracked managers holding the stock as a "best idea"
- **Weighting:** votes ÷ total votes
- **Lag:** holdings treated as known 2 months after the report
- **Rebalance:** quarterly, aligned to the 13F calendar; long-only

## Data map
- **Data:** EDGAR 13F-HR information tables

## Open questions
- **⚠ Resolve before build:** (1) which managers to track — not specified; (2) how a "best idea" is defined per manager — not specified in the doc (the Cohen/Polk/Silli paper is the reference); (3) 13F lists CUSIPs, not tickers — a CUSIP → ticker map is needed.

**Decisions:** none yet. (Resolve each line with Judin before building — never pick a definition silently.)

## Risk
—

## Backtest
Not run. When it is, results live in `results/G1/` (returns.csv · trades.csv · eda.png · report.md), ending in `tools/backtest_eda.py`.

## Notes
—
