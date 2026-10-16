---
id: C3
name: Consistent Momentum Strategy
tier: C — Single stocks, price + market cap
strength: High
difficulty: Intermediate
source: firm-level momentum-consistency study
doc: https://docs.google.com/document/d/1ituRqBq-sZ8ufV2S2cKHSrAvoeeDGbMRWI_ZXJ6aXBc
data_status: buildable
build_status: not started
verdict: 
---
# C3 · Consistent Momentum Strategy

## At a glance
- **Tier:** C — Single stocks, price + market cap
- **Strength (PQN):** High · **Difficulty (PQN):** Intermediate
- **Source:** firm-level momentum-consistency study
- **PQN doc:** [C3 on Drive](https://docs.google.com/document/d/1ituRqBq-sZ8ufV2S2cKHSrAvoeeDGbMRWI_ZXJ6aXBc)
- **Data status:** buildable · **Build status:** not started · **Verdict:** —

## Thesis
—

## Rules as written
- **Universe:** top 500 by dollar volume, ≥ 7 months of history
- **Windows:** return t−7→t−1 months and return t−6→t months
- **Long:** top decile in **both** windows; **Short:** bottom decile in both
- **Timing:** one-month skip between formation and holding; hold 6 months, no rebalancing during the hold
- **Weighting:** equal

## Data map
—

> **Tier note:** Common data for this tier: daily bars for the whole cross-section (grouped daily is one call per date), dollar volume for liquidity ranks, market cap for size ranks, delisted tickers for survivorship (open check #2).

## Open questions
- **⚠ Resolve before build:** the doc's code indexes price windows newest-first (`w[0] / w[-1]`); confirm the window slicing matches the stated t−7→t−1 / t−6→t definitions.

**Decisions:** none yet. (Resolve each line with Judin before building — never pick a definition silently.)

## Risk
—

## Backtest
Not run. When it is, results live in `results/C3/` (returns.csv · trades.csv · eda.png · report.md), ending in `tools/backtest_eda.py`.

## Notes
—
