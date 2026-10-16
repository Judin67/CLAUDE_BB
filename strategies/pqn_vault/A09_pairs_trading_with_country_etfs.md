---
id: A9
name: Pairs Trading with Country ETFs
tier: A — ETFs, price only
strength: Moderate
difficulty: Advanced
source: distance-method pairs trading applied to country ETFs
doc: https://docs.google.com/document/d/1NaTrxGmqhb1mKFErgoIhLktCcVVARVlyDz11okL3Hxg
data_status: buildable
build_status: not started
verdict: 
---
# A9 · Pairs Trading with Country ETFs

## At a glance
- **Tier:** A — ETFs, price only
- **Strength (PQN):** Moderate · **Difficulty (PQN):** Advanced
- **Source:** distance-method pairs trading applied to country ETFs
- **PQN doc:** [A9 on Drive](https://docs.google.com/document/d/1NaTrxGmqhb1mKFErgoIhLktCcVVARVlyDz11okL3Hxg)
- **Data status:** buildable · **Build status:** not started · **Verdict:** —

## Thesis
—

## Rules as written
- **Universe:** 22 country ETFs (EWA … EWU list above) + SPY reference
- **Formation:** 120 trading days; normalize each series to $1; distance = sum of squared deviations between normalized series
- **Selection:** 5 tightest pairs; re-select each 20-day trading period
- **Entry:** spread > 0.5 SD from its mean → long the cheap leg, short the rich leg
- **Exit:** reconvergence, or force-close after 20 trading days
- **Weighting:** equal across the 5 pairs; monitor daily

## Data map
- **Data:** daily closes → Massive aggs. The doc prefers total-return prices, so add dividends.

## Open questions
None flagged in the triage.

**Decisions:** none yet. (Resolve each line with Judin before building — never pick a definition silently.)

## Risk
- **Risk:** small positive equity correlation per source — not a hedge

## Backtest
Not run. When it is, results live in `results/A9/` (returns.csv · trades.csv · eda.png · report.md), ending in `tools/backtest_eda.py`.

## Notes
—
