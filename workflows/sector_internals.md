# Workflow: Sector Internals System

**Objective:** Track intraday sector rotation, relative strength vs SPY, and VWAP status for all 11 SPDR sector ETFs.

**Notebook:** `C:/Users/Trader/quant-project/notebooks/technicals/sector_internals.ipynb`

**Environment:** `my_quant_lab_py310`

---

## Inputs Required

| Input | Value | Notes |
|-------|-------|-------|
| `INTERVAL` | `'5m'` | Change to `'1m'` for higher resolution |
| `LOOKBACK_DAYS` | `1` | Set to `5` for week view |
| `BENCHMARK` | `'SPY'` | Can change to `'QQQ'` for tech-heavy days |

No API keys required — uses yfinance (free).

---

## When to Run

| Time | Why |
|------|-----|
| 9:00–9:30 AM | Pre-market sector bias from futures |
| 9:30–10:30 AM | First hour rotation — who's leading the open |
| 11:00 AM | Midday reset — check if leaders are holding |
| 3:00–3:30 PM | Late-day rotation check before MOC |

---

## What to Look For

**Bullish tape:**
- 8+ sectors above VWAP
- Leaders holding RS > +0.5% above SPY
- No sector breaking below -1% RS

**Bearish tape:**
- 8+ sectors below VWAP
- Leaders rolling over (RS declining intraday)
- Energy or defensives (XLU, XLP) leading

**Rotation signal:**
- Laggard sector flipping from negative to positive RS mid-session
- Technology (XLK) diverging from broader tape

**Avoid trading when:**
- All sectors moving in lockstep with SPY (macro-driven, no alpha)
- RS lines are flat/compressed (low dispersion)

---

## Outputs

- Heatmap: RS vs SPY for all 11 sectors (saved inline in notebook)
- Line chart: Intraday RS evolution
- Print summary: Leaders, laggards, VWAP count

---

## Upgrade Path (When Polygon is Active)

Replace `yf.download()` in cell 3 with:
```python
from tools.fetch_polygon import fetch_intraday
closes = fetch_intraday(tickers, interval='5', days=LOOKBACK_DAYS)
```

This will also enable actual market internals:
- `$ADD` — NYSE Advance-Decline line
- `$VOLD` — NYSE Volume Delta (up vol - down vol)
- `$TICK` — NYSE Tick (upticks - downticks)

---

## Known Issues / Notes

- yfinance 5m data is delayed ~15 min during market hours
- Pre-market data (before 9:30) may be sparse — expected
- TradingView websocket approach was tested and is broken — do not use
- `tradingview_datafetch_template.ipynb` is a placeholder, not production-ready
