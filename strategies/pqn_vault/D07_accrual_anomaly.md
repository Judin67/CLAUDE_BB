---
id: D7
name: Accrual Anomaly
tier: D — Single stocks + fundamentals
strength: Moderate
difficulty: Advanced
source: Sloan (1996) lineage; LaFond, "Is the Accrual Anomaly a Global Anomaly?"; Detzel, Schabel & Strauss
doc: https://docs.google.com/document/d/1BLjB3B_Kmr0KOrMBviA-sP8skTmIdkfQtiAvP7aLeC4
data_status: buildable
build_status: not started
verdict: 
---
# D7 · Accrual Anomaly

## At a glance
- **Tier:** D — Single stocks + fundamentals
- **Strength (PQN):** Moderate · **Difficulty (PQN):** Advanced
- **Source:** Sloan (1996) lineage; LaFond, "Is the Accrual Anomaly a Global Anomaly?"; Detzel, Schabel & Strauss
- **PQN doc:** [D7 on Drive](https://docs.google.com/document/d/1BLjB3B_Kmr0KOrMBviA-sP8skTmIdkfQtiAvP7aLeC4)
- **Data status:** buildable · **Build status:** not started · **Verdict:** —

## Thesis
—

## Rules as written
- **Universe:** ~1,000 most liquid, largest with complete fundamentals
- **Signal:** BS_ACC = (ΔCA − ΔCash) − (ΔCL − ΔSTD − ΔITP) − Dep, scaled by average total assets (CA current assets, CL current liabilities, STD current debt, ITP income taxes payable, Dep depreciation & amortization)
- **Positions:** deciles; long lowest accruals, short highest; equal weight
- **Rebalance:** once a year in spring (April / May, after annual reports)

## Data map
- **Data note:** the doc's filter drops any name with a zero in any required field (e.g. zero taxes payable).

> **Tier note:** Common data for this tier: point-in-time fundamentals (use filing date, not period end, to avoid look-ahead) from Massive financials with EDGAR XBRL backfill (`edgar_client.latest_asof`). Check financials history depth first (open check #3).

## Open questions
None flagged in the triage.

**Decisions:** none yet. (Resolve each line with Judin before building — never pick a definition silently.)

## Risk
—

## Backtest
Not run. When it is, results live in `results/D7/` (returns.csv · trades.csv · eda.png · report.md), ending in `tools/backtest_eda.py`.

## Notes
—
