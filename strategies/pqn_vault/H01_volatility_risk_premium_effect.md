---
id: H1
name: Volatility Risk Premium Effect
tier: H — Options
strength: Moderate
difficulty: Advanced
source: study of expected option returns (zero-beta ATM straddles lose ~3% / week)
doc: https://docs.google.com/document/d/1ot9RQrzWiUtuRF4t-9lHmhlm017BXk0Tt_145QmeeyE
data_status: buildable
build_status: not started
verdict: 
---
# H1 · Volatility Risk Premium Effect

## At a glance
- **Tier:** H — Options
- **Strength (PQN):** Moderate · **Difficulty (PQN):** Advanced
- **Source:** study of expected option returns (zero-beta ATM straddles lose ~3% / week)
- **PQN doc:** [H1 on Drive](https://docs.google.com/document/d/1ot9RQrzWiUtuRF4t-9lHmhlm017BXk0Tt_145QmeeyE)
- **Data status:** buildable · **Build status:** not started · **Verdict:** —

## Thesis
—

## Rules as written
- **Universe:** SPY options + SPY
- **Monthly trade:** sell an ATM straddle (call + put at the strike nearest spot, expiration nearest 30 days); buy a put at the strike nearest 85% of spot, same expiration
- **Cash:** remaining cash + collected premium held in SPY
- **Sizing (doc code):** contracts = margin remaining ÷ (spot × 100)
- **Rebalance:** monthly, open only when flat

## Data map
- **Data:** historical SPY option contract prices + expired-contract reference (**open check #5**)

## Open questions
- **⚠ Resolve before build:** the doc sizes by margin and also sets SPY to 100% of holdings — total exposure is ambiguous.

**Decisions:** none yet. (Resolve each line with Judin before building — never pick a definition silently.)

## Risk
- **Risk:** fat-tailed; the 15% OTM put is mandatory, not optional

## Backtest
Not run. When it is, results live in `results/H1/` (returns.csv · trades.csv · eda.png · report.md), ending in `tools/backtest_eda.py`.

## Notes
—
