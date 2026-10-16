---
id: B7
name: Option-Expiration Week Effect
tier: B — Calendar timing
strength: Moderate
difficulty: Beginner
source: option-expiration-week effect research (market-maker hedge rebalancing)
doc: https://docs.google.com/document/d/1BNgEtbfsQ7PxprkF6t9_bIAGfiqhqXdVVI03IZcqh_4
data_status: buildable
build_status: not started
verdict: 
---
# B7 · Option-Expiration Week Effect

## At a glance
- **Tier:** B — Calendar timing
- **Strength (PQN):** Moderate · **Difficulty (PQN):** Beginner
- **Source:** option-expiration-week effect research (market-maker hedge rebalancing)
- **PQN doc:** [B7 on Drive](https://docs.google.com/document/d/1BNgEtbfsQ7PxprkF6t9_bIAGfiqhqXdVVI03IZcqh_4)
- **Data status:** buildable · **Build status:** not started · **Verdict:** —

## Thesis
—

## Rules as written
- **Universe:** OEF (S&P 100 ETF)
- **Signal:** monthly expiration = Friday before the third Saturday
- **Entry:** each Monday, if expiration is ≤ 5 days away → 100% OEF
- **Exit:** liquidate on expiration day

## Data map
- **Data:** daily closes → Massive aggs; expiration dates computed from the calendar
- **Data note:** when that Friday is a market holiday, expiration moves to Thursday — the calendar must handle it.

## Open questions
None flagged in the triage.

**Decisions:** none yet. (Resolve each line with Judin before building — never pick a definition silently.)

## Risk
- **Risk:** no hedge

## Backtest
Not run. When it is, results live in `results/B7/` (returns.csv · trades.csv · eda.png · report.md), ending in `tools/backtest_eda.py`.

## Notes
—
