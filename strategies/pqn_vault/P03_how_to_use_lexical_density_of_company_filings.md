---
id: P3
name: How to Use Lexical Density of Company Filings
tier: P — Partial / heavy lift
strength: Moderate
difficulty: Advanced
source: filings-language dataset study (~6,000 US stocks)
doc: https://docs.google.com/document/d/1dbTdnrjQXb6zqWFLkr8s1jFYPJBX3cG63ykPox5NuAg
data_status: partial
build_status: not started
verdict: 
---
# P3 · How to Use Lexical Density of Company Filings

## At a glance
- **Tier:** P — Partial / heavy lift
- **Strength (PQN):** Moderate · **Difficulty (PQN):** Advanced
- **Source:** filings-language dataset study (~6,000 US stocks)
- **PQN doc:** [P3 on Drive](https://docs.google.com/document/d/1dbTdnrjQXb6zqWFLkr8s1jFYPJBX3cG63ykPox5NuAg)
- **Data status:** partial · **Build status:** not started · **Verdict:** —

## Thesis
—

## Rules as written
- **Universe:** top 500 by dollar volume on NYSE / NASDAQ / AMEX
- **Signals (vendor):** lexical density ("share of information-carrying words rather than filler") and specific density ("how many finance-related terms appear")
- **Positions:** per metric, long top decile, short bottom decile; equal weight; the two metric sleeves split the book 50 / 50
- **Rebalance:** monthly; universe reselected quarterly

## Data map
- **Blocker:** both metrics are vendor-defined. A self-built version from EDGAR text is an approximation, not the paper's score.

## Open questions
None flagged in the triage.

**Decisions:** none yet. (Resolve each line with Judin before building — never pick a definition silently.)

## Risk
—

## Backtest
Not run. When it is, results live in `results/P3/` (returns.csv · trades.csv · eda.png · report.md), ending in `tools/backtest_eda.py`.

## Notes
—
