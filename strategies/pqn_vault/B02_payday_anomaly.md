---
id: B2
name: Payday Anomaly
tier: B — Calendar timing
strength: Moderate
difficulty: Beginner
source: payday / turn-of-month research (the 16th calendar day)
doc: https://docs.google.com/document/d/11iKmTCPy2mpSm3Qq7O-HPkHOABwNSSWmceOaTHZnrj4
data_status: buildable
build_status: not started
verdict: 
---
# B2 · Payday Anomaly

## At a glance
- **Tier:** B — Calendar timing
- **Strength (PQN):** Moderate · **Difficulty (PQN):** Beginner
- **Source:** payday / turn-of-month research (the 16th calendar day)
- **PQN doc:** [B2 on Drive](https://docs.google.com/document/d/11iKmTCPy2mpSm3Qq7O-HPkHOABwNSSWmceOaTHZnrj4)
- **Data status:** buildable · **Build status:** not started · **Verdict:** —

## Thesis
—

## Rules as written
- **Universe:** SPY
- **Signal:** mid-month payday — semi-monthly pay on the 15th reaches the market on the 16th
- **Position:** 100% SPY for one session; cash otherwise

## Data map
- **Data:** daily closes → Massive aggs

## Open questions
- **⚠ Resolve before build:** the doc's rule text and code disagree. Rules say "the 16th, rolled back to prior Friday if a weekend; buy into the close of that session, exit next day". Code computes the **15th** rolled to Friday and enters on that date. Decide which session's return is being captured (target = the 16th's session).

**Decisions:** none yet. (Resolve each line with Judin before building — never pick a definition silently.)

## Risk
- **Risk:** no hedge; decaying as bi-weekly pay spreads

## Backtest
Not run. When it is, results live in `results/B2/` (returns.csv · trades.csv · eda.png · report.md), ending in `tools/backtest_eda.py`.

## Notes
—
