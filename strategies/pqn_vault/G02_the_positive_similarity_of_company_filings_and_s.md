---
id: G2
name: The Positive Similarity of Company Filings and Stock Returns
tier: G — EDGAR filings
strength: Moderate
difficulty: Intermediate
source: positive-language similarity study (extends "Lazy Prices")
doc: https://docs.google.com/document/d/1ZIkrPRUwlGoKhFRSG8Cz-paJ1SxYBLxQjE_etVAir-w
data_status: buildable
build_status: not started
verdict: 
---
# G2 · The Positive Similarity of Company Filings and Stock Returns

## At a glance
- **Tier:** G — EDGAR filings
- **Strength (PQN):** Moderate · **Difficulty (PQN):** Intermediate
- **Source:** positive-language similarity study (extends "Lazy Prices")
- **PQN doc:** [G2 on Drive](https://docs.google.com/document/d/1ZIkrPRUwlGoKhFRSG8Cz-paJ1SxYBLxQjE_etVAir-w)
- **Data status:** buildable · **Build status:** not started · **Verdict:** —

## Thesis
—

## Rules as written
- **Universe:** ~1,000 largest US stocks by market cap with a score and full price history
- **Signal:** cosine similarity of positive-language word-frequency vectors between the latest 10-K / 10-Q and the prior filing (0 = rewritten, 1 = identical)
- **Positions:** monthly deciles; **long bottom decile** (biggest change), **short top decile**; equal weight; stay flat if < 10 scored names
- **Rebalance:** monthly

## Data map
- **Data:** the doc uses a vendor score → build it yourself from EDGAR 10-K / 10-Q text with a public positive-word dictionary (e.g. Loughran-McDonald)

## Open questions
- **⚠ Resolve before build:** "the prior one" — compare against the prior filing of the same form type, or the prior filing of any type.

**Decisions:** none yet. (Resolve each line with Judin before building — never pick a definition silently.)

## Risk
—

## Backtest
Not run. When it is, results live in `results/G2/` (returns.csv · trades.csv · eda.png · report.md), ending in `tools/backtest_eda.py`.

## Notes
—
