---
id: P2
name: FED Model
tier: P — Partial / heavy lift
strength: Moderate
difficulty: Intermediate
source: stock-bond "yield gap" research
doc: https://docs.google.com/document/d/1DBOtXeefnB06eCGr2wNXkhKYf8NbahcSJI5vxv3M0I4
data_status: partial
build_status: not started
verdict: 
---
# P2 · FED Model

## At a glance
- **Tier:** P — Partial / heavy lift
- **Strength (PQN):** Moderate · **Difficulty (PQN):** Intermediate
- **Source:** stock-bond "yield gap" research
- **PQN doc:** [P2 on Drive](https://docs.google.com/document/d/1DBOtXeefnB06eCGr2wNXkhKYf8NbahcSJI5vxv3M0I4)
- **Data status:** partial · **Build status:** not started · **Verdict:** —

## Thesis
—

## Rules as written
- **Universe:** SPY (risky), SHY (cash)
- **Signal:** yield gap YG = ln(1 + E/P) − ln(1 + Y10)
- **Model:** monthly expanding-window OLS of market excess return on lagged YG; forecast next month
- **Position:** forecast > 0 → 100% SPY, else 100% SHY
- **Rebalance:** monthly

## Data map
- **Blocker:** S&P 500 earnings yield is not available (indices 403; the constituents DB is a current snapshot with no membership history). A self-built large-cap aggregate E/P is a proxy, not the S&P number. Yields via `/fed/v1` (open check #7).

## Open questions
- **⚠ Resolve before build:** the doc's formula text (`ln(1 + E/P)`) and code (`log(EY) − log(Y)`) differ.

**Decisions:** none yet. (Resolve each line with Judin before building — never pick a definition silently.)

## Risk
—

## Backtest
Not run. When it is, results live in `results/P2/` (returns.csv · trades.csv · eda.png · report.md), ending in `tools/backtest_eda.py`.

## Notes
—
