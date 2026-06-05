# Workflow: Dr. S Indicator

## Objective

Detect unusual opening participation and unusual opening displacement at the start of the session.

Two questions answered:
- **Was the volume heavy?** — each 1m bar's volume vs the 14-session average for that same minute
- **Was the price range unusual?** — today's opening range (high - low) vs the 14-session average opening range

No directional bias. Both signals measure magnitude only.

---

## Required Inputs

| Parameter | Type | Notes |
|-----------|------|-------|
| `TICKER` | string | Any Polygon-supported equity ticker |
| `LOOKBACK` | int | Sessions for baseline (default: 14) |
| `OUTLIER_SD` | float | Z-score threshold for outlier flag (default: 2.0) |
| `OPEN_WINDOW` | int | Minutes from 9:30 to analyze (default: 30). Data outside this window is ignored. |

Earnings mode adds:

| Parameter | Type | Notes |
|-----------|------|-------|
| `EARNINGS_MODE` | bool | Set to `True` to activate |
| `ANCHOR_EARNINGS_DATE` | string | `"YYYY-MM-DD"` — the earnings event you want to anchor at phase 0 |
| `PHASE_LABEL` | string | e.g. `"acceleration"` — appears in chart title only |

---

## Invocation

```bash
conda activate my_quant_lab_py310
python tools/dr_s_indicator.py --ticker AAOI --date 2026-02-27
python tools/dr_s_indicator.py --ticker NVDA --date 2026-03-30 --open-window 45
python tools/dr_s_indicator.py --ticker TSLA --no-chart
```

---

## Model Logic

1. **Fetch** 1m OHLCV bars via `fetch_bars()` (Polygon/Massive).  
   Window: last `lookback × 1.7 + 5` calendar days.

2. **Trim to opening window only** — 9:30 to `9:30 + OPEN_WINDOW` minutes. All other bars discarded.

3. **Assign `slot_id`** = minutes since 9:30 (slot 0 = 9:30, slot 1 = 9:31, etc.).

4. **Build baseline** from the last `LOOKBACK` complete sessions (current session excluded):
   - Per slot: `mean_vol` and `std_vol` of bar volume across those sessions
   - Per session: `high - low` of the full opening window → averaged → `14D avg range`

5. **Compute indicators** for the analysis session:
   - `rel_vol  = bar_volume / mean_vol`
   - `z_score  = (bar_volume - mean_vol) / std_vol`
   - `outlier  = |z_score| >= OUTLIER_SD`
   - `today_range = high - low of the full opening window`

---

## Outputs

| Output | Location | Format |
|--------|----------|--------|
| Chart (.png) | `.tmp/{ticker}_1m_open{N}_{YYYYMMDD}.png` | 2-panel dark chart |
| Data cache (.csv) | `.tmp/{ticker}_1m_open{N}_{YYYYMMDD}.csv` | Opening window bars + indicators |
| Console summary | stdout | Key metrics |

### Chart panels
- **Panel 1 (top, large):** 1m candlesticks + VWAP. Annotation box (top right): 14D avg range, today's range, ratio.
- **Panel 2 (bottom):** 1m volume bars — green = above slot avg, dim = below, yellow = outlier. Dashed line = 14D slot average.
- X-axis covers the opening window only (9:30 → 9:30 + OPEN_WINDOW). Ticks every 5 minutes.
- If earnings mode: yellow dotted verticals at earnings dates, labeled P0/P1/P2…

### Console summary (example)
```
--------------------------------------------------------
  AAOI  |  1m  |  14-session baseline  |  open: 30m
--------------------------------------------------------
  Opening window         : 09:30 - 10:00
  Sessions in baseline   : 14
  14D Avg Range (30m)  : $2.83
  Today's opening range  : $12.20  (4.31x)
  Vol outlier bars       : 27
--------------------------------------------------------
```

---

## Interpreting Results

| Signal | What it means |
|--------|--------------|
| Range ratio > 1.5x | Opening range was wider than normal — unusual displacement |
| Range ratio > 2x | Significantly wider — strong catalyst likely present |
| Range ratio > 3x | Extreme — rare, institutional-level activity |
| Vol outlier bars high (e.g. 27/30) | Nearly every minute had above-normal volume — sustained participation |
| Both ratio > 2x AND most bars outliers | Institutional footprint — confirms the Dr. S setup |
| High ratio, few outlier bars | Price moved but volume was thin — lower conviction |
| Many outlier bars, low ratio | Volume without movement — absorption near open price |

---

## Earnings Mode: When and How

Use when you want context on whether the open occurred during a specific earnings cycle phase.

```python
# In tools/dr_s_indicator.py
EARNINGS_MODE        = True
ANCHOR_EARNINGS_DATE = "2024-08-28"
PHASE_LABEL          = "acceleration"
```

P0 = anchor event, P1 = next quarter, P2 = next, etc. Base model runs unchanged; earnings lines are overlay only.

---

## Edge Cases

| Situation | Behavior |
|-----------|----------|
| Fewer than 14 sessions available | WARNING printed; uses however many sessions exist |
| Session with zero volume on a slot | `std_vol = NaN` → `z_score = NaN` → no outlier flag |
| Ticker has < 2 sessions in window | Hard error — widen date range or check ticker |
| `OPEN_WINDOW` extends past market close | Clamped to 16:00 by RTH filter |
| Anchor earnings date not in Polygon data | Falls back silently; earnings overlay skipped |
| Before-market run (no today bars) | Tool runs on last 14 complete sessions; no current session on chart |
| Polygon rate limit hit | Tool sleeps 13s between paginated requests automatically |

---

## Data Source

**Polygon/Massive only.**  
API key: `POLYGON_API_KEY` in `.env`.
