# Legacy tools — Gen-1 "MTF Slope" charts (NOT CURRENT)

These two scripts are the **first generation** of what is now the **Cascade** strategy.
They are kept for reference only. **Do not use them as a template.** They have been
superseded — anything you need is in the current tools/docs below.

## Files

- `mtf_candles.py` — candlestick chart + slope-indicator panel + signal triangles
- `mtf_stop_viz.py` — zoomed entry/stop chart for the first 2 signals

## Why they are retired (do not copy these patterns)

| Legacy behavior | Current rule (use this instead) |
|---|---|
| 9-SMA **and** 21-SMA | 9-SMA only (see `workflows/cascade_core_rules.md` chart standards) |
| **Absolute** slope (`ma - ma.shift`) | **Percent** slope, lookback 2, FLAT band ±0.02% |
| Hardcoded `SPY` / `2026-03-20` | Cascade is for **stocks in play**, never SPY on a random day |
| No VWAP, no volume panel | Gold cumulative VWAP + volume panel required |
| 1m / 5m only | Full stack: Weekly→Daily→4h→65m→30m→5m→1m→10s |
| Imports `quant-project/src` (`detect_mtf_slope_signals`, etc.) | Logic now lives self-contained in `tools/cascade_live.py` |
| `RATE_SLEEP = 13` (free tier) | Paid real-time tier — no meaningful rate cap |

## What replaced them

- **Live stack read / signal logic** → `tools/cascade_live.py`
- **Charts** → `tools/chart_intraday.py` + the `.tmp/chart_qqq_today.py` template
- **Rules / source of truth** → `workflows/cascade_core_rules.md`

Archived 2026-05-26 during the Cascade cleanup.
