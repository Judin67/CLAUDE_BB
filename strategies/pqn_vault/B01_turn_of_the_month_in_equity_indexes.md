---
id: B1
name: Turn of the Month in Equity Indexes
tier: B — Calendar timing
strength: Moderate
difficulty: Beginner
source: McConnell & Xu, "Equity Returns at the Turn of the Month"; Lakonishok & Smidt (1988)
doc: https://docs.google.com/document/d/155xMH35zOooazrZtnWIv_lOYaCAbUcNvEfPUN6s5cUM
data_status: buildable
build_status: not started
verdict: 
---
# B1 · Turn of the Month in Equity Indexes

## At a glance
- **Tier:** B — Calendar timing
- **Strength (PQN):** Moderate · **Difficulty (PQN):** Beginner
- **Source:** McConnell & Xu, "Equity Returns at the Turn of the Month"; Lakonishok & Smidt (1988)
- **PQN doc:** [B1 on Drive](https://docs.google.com/document/d/155xMH35zOooazrZtnWIv_lOYaCAbUcNvEfPUN6s5cUM)
- **Data status:** buildable · **Build status:** not started · **Verdict:** —

## Thesis
—

## Rules as written
- **Universe:** SPY
- **Entry:** buy at the open one day before month end (some studies use four days before)
- **Exit:** sell at the close of the 3rd trading day of the new month
- **Position:** 100% in window, cash otherwise

## Data map
- **Data:** daily OHLC → Massive aggs; trading-day calendar

## Open questions
None flagged in the triage.

**Decisions:** none yet. (Resolve each line with Judin before building — never pick a definition silently.)

## Risk
- **Risk:** no hedge; calendar effects can drift

## Backtest
Not run. When it is, results live in `results/B1/` (returns.csv · trades.csv · eda.png · report.md), ending in `tools/backtest_eda.py`.

## Notes
—
