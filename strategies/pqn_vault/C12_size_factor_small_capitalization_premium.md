---
id: C12
name: Size Factor – Small Capitalization Premium
tier: C — Single stocks, price + market cap
strength: Moderate
difficulty: Intermediate
source: Fama & French, "The Cross-Section of Expected Stock Returns"; Alquist, Israel & Moskowitz, "Fact, Fiction, and the Size Effect"
doc: https://docs.google.com/document/d/1NpfkhRi_DLDPAoOmIqEaJIfrHahc-A3VgX3ApCe0x5g
data_status: buildable
build_status: not started
verdict: 
---
# C12 · Size Factor – Small Capitalization Premium

## At a glance
- **Tier:** C — Single stocks, price + market cap
- **Strength (PQN):** Moderate · **Difficulty (PQN):** Intermediate
- **Source:** Fama & French, "The Cross-Section of Expected Stock Returns"; Alquist, Israel & Moskowitz, "Fact, Fiction, and the Size Effect"
- **PQN doc:** [C12 on Drive](https://docs.google.com/document/d/1NpfkhRi_DLDPAoOmIqEaJIfrHahc-A3VgX3ApCe0x5g)
- **Data status:** buildable · **Build status:** not started · **Verdict:** —

## Thesis
—

## Rules as written
- **Universe:** NYSE / AMEX / NASDAQ, implementation top 3,000 by market cap
- **Positions:** quintiles by market cap (canonical = deciles); long smallest, short largest
- **Weighting:** equal; 100% long / 100% short
- **Rebalance:** yearly

## Data map
—

> **Tier note:** Common data for this tier: daily bars for the whole cross-section (grouped daily is one call per date), dollar volume for liquidity ranks, market cap for size ranks, delisted tickers for survivorship (open check #2).

## Open questions
None flagged in the triage.

**Decisions:** none yet. (Resolve each line with Judin before building — never pick a definition silently.)

## Risk
- **Risk:** not a hedge — small caps suffer into downturns

## Backtest
Not run. When it is, results live in `results/C12/` (returns.csv · trades.csv · eda.png · report.md), ending in `tools/backtest_eda.py`.

## Notes
—
