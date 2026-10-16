---
id: A10
name: Reversal Effect in International Equity ETFs
tier: A — ETFs, price only
strength: Moderate
difficulty: Intermediate
source: winner-loser reversal in 16 national indices; Balvers, Wu & Gilliland; Spierdijk, Bikker & Van den Hoek
doc: https://docs.google.com/document/d/1vJc7mrxIWouW92oZpB-chb8FvuRdL-TG-KJZt2jLeko
data_status: buildable
build_status: not started
verdict: 
---
# A10 · Reversal Effect in International Equity ETFs

## At a glance
- **Tier:** A — ETFs, price only
- **Strength (PQN):** Moderate · **Difficulty (PQN):** Intermediate
- **Source:** winner-loser reversal in 16 national indices; Balvers, Wu & Gilliland; Spierdijk, Bikker & Van den Hoek
- **PQN doc:** [A10 on Drive](https://docs.google.com/document/d/1vJc7mrxIWouW92oZpB-chb8FvuRdL-TG-KJZt2jLeko)
- **Data status:** buildable · **Build status:** not started · **Verdict:** —

## Thesis
—

## Rules as written
- **Universe:** the country ETF list above + SPY
- **Signal:** trailing 36-month return (756 trading days)
- **Positions:** long the 4 worst, short the 4 best; ±1/4 each
- **Rebalance:** every three years

## Data map
- **Data:** daily closes → Massive aggs
- **Data note:** rebalances are three years apart, so a backtest has very few independent periods.

## Open questions
None flagged in the triage.

**Decisions:** none yet. (Resolve each line with Judin before building — never pick a definition silently.)

## Risk
- **Risk:** no hedge; losers can keep falling in a crisis

## Backtest
Not run. When it is, results live in `results/A10/` (returns.csv · trades.csv · eda.png · report.md), ending in `tools/backtest_eda.py`.

## Notes
—
