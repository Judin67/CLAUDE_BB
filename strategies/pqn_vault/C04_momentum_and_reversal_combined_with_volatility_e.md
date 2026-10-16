---
id: C4
name: Momentum and Reversal Combined with Volatility Effect
tier: C — Single stocks, price + market cap
strength: Moderate
difficulty: Advanced
source: momentum/reversal-by-volatility study (1964–2009); Chan, Jegadeesh & Lakonishok; Hong, Lim & Stein
doc: https://docs.google.com/document/d/17Futo0lXZWY8N1rv8_MF4Z6ctzwc3n9H2D9NAgRFbjw
data_status: buildable
build_status: not started
verdict: 
---
# C4 · Momentum and Reversal Combined with Volatility Effect

## At a glance
- **Tier:** C — Single stocks, price + market cap
- **Strength (PQN):** Moderate · **Difficulty (PQN):** Advanced
- **Source:** momentum/reversal-by-volatility study (1964–2009); Chan, Jegadeesh & Lakonishok; Hong, Lim & Stein
- **PQN doc:** [C4 on Drive](https://docs.google.com/document/d/17Futo0lXZWY8N1rv8_MF4Z6ctzwc3n9H2D9NAgRFbjw)
- **Data status:** buildable · **Build status:** not started · **Verdict:** —

## Thesis
—

## Rules as written
- **Universe:** NYSE / AMEX / NASDAQ, price > $5, larger half by market cap (implementation: 1,000 most liquid, then larger half)
- **Signals:** 6-month return and annualized 6-month realized volatility, both skipping the most recent week (5 trading days)
- **Long:** top return quintile ∩ top volatility quintile; **Short:** bottom return quintile ∩ top volatility quintile
- **Weighting:** equal
- **Holding:** 6 months, overlapping tranches (1/6 of book per month)

## Data map
—

> **Tier note:** Common data for this tier: daily bars for the whole cross-section (grouped daily is one call per date), dollar volume for liquidity ranks, market cap for size ranks, delisted tickers for survivorship (open check #2).

## Open questions
None flagged in the triage.

**Decisions:** none yet. (Resolve each line with Judin before building — never pick a definition silently.)

## Risk
—

## Backtest
Not run. When it is, results live in `results/C4/` (returns.csv · trades.csv · eda.png · report.md), ending in `tools/backtest_eda.py`.

## Notes
—
