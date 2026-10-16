---
id: C11
name: Pairs Trading with Stocks
tier: C — Single stocks, price + market cap
strength: Moderate
difficulty: Advanced
source: distance-method pairs study (US 1962–2002); Lucey & Walshe; Chen, Chen & Li; Do & Faff
doc: https://docs.google.com/document/d/1QBZVjCiggvYe3DAKN2x3Tl2j43cv0K-ozC354Sabs5Q
data_status: buildable
build_status: not started
verdict: 
---
# C11 · Pairs Trading with Stocks

## At a glance
- **Tier:** C — Single stocks, price + market cap
- **Strength (PQN):** Moderate · **Difficulty (PQN):** Advanced
- **Source:** distance-method pairs study (US 1962–2002); Lucey & Walshe; Chen, Chen & Li; Do & Faff
- **PQN doc:** [C11 on Drive](https://docs.google.com/document/d/1QBZVjCiggvYe3DAKN2x3Tl2j43cv0K-ozC354Sabs5Q)
- **Data status:** buildable · **Build status:** not started · **Verdict:** —

## Thesis
—

## Rules as written
- **Universe:** top 500 by dollar volume, price > $5
- **Formation:** 12 months; normalize prices to $1; distance = sum of squared deviations
- **Selection:** smallest-distance pairs (original top 20; implementation caps 5 concurrent open pairs)
- **Entry:** spread > 2 SD → short rich leg, long cheap leg, dollar-neutral
- **Exit:** spread reverts inside the band
- **Re-form:** every 6 months; monitor daily

## Data map
—

> **Tier note:** Common data for this tier: daily bars for the whole cross-section (grouped daily is one call per date), dollar volume for liquidity ranks, market cap for size ranks, delisted tickers for survivorship (open check #2).

## Open questions
None flagged in the triage.

**Decisions:** none yet. (Resolve each line with Judin before building — never pick a definition silently.)

## Risk
- **Risk:** historically positive in crises (1987, 2008 per Bowen & Hutchinson); edge has decayed

## Backtest
Not run. When it is, results live in `results/C11/` (returns.csv · trades.csv · eda.png · report.md), ending in `tools/backtest_eda.py`.

## Notes
—
