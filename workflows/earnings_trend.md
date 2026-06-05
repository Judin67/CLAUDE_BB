# Workflow: Earnings Trend, Acceleration, Deceleration & Maturation Cycle Model

## Objective
For a given ticker, analyze the last 12 quarters of EPS and revenue data to:
1. Measure YoY growth rates and 2-quarter rolling averages
2. Detect acceleration or deceleration in the growth trend
3. Count consecutive quarters of 20%+ growth (streak)
4. Classify the stock into a cycle stage for institutional attractiveness screening
5. Check for an annual EPS breakout above the prior 4-year high

## When to Use
- Before entering a position: verify the stock is in an attractive growth phase
- Screening candidates: filter out decelerating or maturing stocks
- Monitoring holdings: detect early warning signs of cycle deterioration

## Required Inputs
- `ticker` — stock symbol (e.g., `RBLX`, `AAPL`)
- `POLYGON_API_KEY` — from `.env`

## Tool
```bash
python tools/fetch_earnings_trend.py --ticker RBLX
python tools/fetch_earnings_trend.py --ticker RBLX --no-chart
```

## Data Source
**Polygon `/vX/reference/financials`** — requires Starter tier or above.
If this returns 403, run `python tools/test_polygon_earnings.py` to verify tier access.

Fields used per quarter:
| Polygon field | Model variable |
|---|---|
| `period_of_report_date` | fiscalDateEnding |
| `filing_date` | reportedDate |
| `financials.income_statement.basic_earnings_per_share.value` | reportedEPS |
| `financials.income_statement.revenues.value` | totalRevenue |
| `financials.income_statement.net_income_loss.value` | netIncome |

## Model Logic

### Step 1 — Fetch
- Request 20 quarters (limit=20) to ensure 12 complete quarters after YoY shift math (which needs 4 prior quarters).
- Sort descending by `period_of_report_date`, then reverse → chronological order.
- Keep last 12 rows for the main analysis table.

### Step 2 — Growth Metrics
```python
YoY_EPS_%   = (reportedEPS / reportedEPS.shift(4) - 1) * 100
YoY_Sales_% = (totalRevenue / totalRevenue.shift(4) - 1) * 100
NetMargin_% = (netIncome / totalRevenue) * 100
EPS_2Q_Avg  = YoY_EPS_%.rolling(2).mean()
Sales_2Q_Avg = YoY_Sales_%.rolling(2).mean()
```
`shift(4)` compares each quarter to the same quarter one year ago.

### Step 3 — Acceleration / Deceleration
```python
EPS_Accel  = YoY_EPS_%.diff() > 0    # this Q's growth rate faster than prior Q
EPS_Decel  = YoY_EPS_%.diff() < 0
Sales_Accel = YoY_Sales_%.diff() > 0
```

### Step 4 — 20%+ Streak
Running count of consecutive quarters where `YoY_EPS_%` >= 20%. Resets to 0 on any miss.
- 1–2 quarters: early phase
- 3–5 quarters: confirmed growth stock
- 6+ quarters: exceptional, approaching maturation risk

### Step 5 — Cycle Stage Classification
Based on the most recent quarter:

| Stage | Condition |
|---|---|
| `TURNAROUND` | Prior base was <20% YoY avg, current quarter explodes ≥100% |
| `EARLY_ACCEL` | Streak 1–2Q, growth accelerating |
| `PEAK_ACCEL` | Streak 3+Q of 20%+ growth, still accelerating or holding |
| `DECEL_ONSET` | Streak ≥2Q but YoY growth declining QoQ for 1–2 consecutive quarters |
| `MATURING` | Streak broken or growth sub-20% for 2+ quarters |
| `WEAK` | Negative YoY EPS growth |

**Minimum thresholds for institutional attractiveness (from notes):**
- Bull market: 40–100%+ YoY in most recent 2–3 quarters
- Base minimum: 20–25% in most recent 1–3 quarters
- Turnaround: 100%+ in the most recent 1–2 quarters

### Step 6 — Breakout Year Check
Compares trailing 4-quarter EPS sum (annualized) to the prior 4-year high.
- Requires ~20 quarters of data — gracefully skips if insufficient
- A breakout above a multi-year range is a significant institutional signal

## Outputs

### Console Table (last 12 quarters)
```
Fiscal Date | EPS  | YoY EPS% | 2Q Avg% | Accel | Streak | Revenue | YoY Sales% | S.Accel | Margin%
```

### Summary Block
```
Ticker       : RBLX
Cycle Stage  : PEAK_ACCEL  (5Q streak of 20%+ growth)
EPS Streak   : 5Q of 20%+ growth
Latest YoY EPS   : +67.4%  |  2Q Avg: +61.2%
Latest YoY Sales : +34.1%  |  2Q Avg: +31.8%
Net Margin       : 8.2%
Breakout Year    : YES — trailing 4Q EPS $0.48 breaks prior 4yr high of $0.31
```

### Chart (dark theme, matches existing tools)
- Dashed blue line: YoY EPS Growth %
- Solid yellow line: 2Q Rolling Avg EPS %
- Dotted green line: YoY Sales Growth %
- Dashed red horizontal: 20% threshold reference
- x-axis: full fiscal date strings (YYYY-MM-DD)

## Interpreting Results

**What to look for (attractive setups):**
- Cycle stage: `TURNAROUND`, `EARLY_ACCEL`, or `PEAK_ACCEL`
- EPS growth accelerating QoQ with sales confirming
- Revenue growing in tandem (EPS without sales support is a warning sign)
- Net margin expanding or stable
- Breakout Year = YES (institutional catalyst)
- 2Q rolling avg rising, not flattening

**Red flags:**
- `DECEL_ONSET` — especially if from a high base (60%→30% is a big drop)
- Sales growing slower than EPS (margin compression likely)
- Streak broken after 4–6 quarters (maturation, cycle top risk)
- EPS positive but flat or decelerating for 2+ quarters

**Turnaround specifics:**
- Insist on 100%+ YoY in the most recent 1–2 quarters
- EPS and margins at or near new highs confirms the company is back on track
- Compare current annual growth rate vs. prior 3–5 year growth rate for context

## Edge Cases

| Situation | Handling |
|---|---|
| < 8 quarters returned | YoY will be NaN for early rows — expected, display as-is |
| Missing EPS or revenue | `pd.to_numeric(..., errors='coerce')` → NaN, excluded from streak/stage |
| Ticker not found | Empty `results` → print message and exit cleanly |
| API key missing | `ValueError` raised before any network call |
| 403 on endpoint | Prints instruction to run `test_polygon_earnings.py` |
| Negative EPS base (0 or <0 prior year) | YoY% will be NaN or misleading — displayed but not used for streak |

## Notes
- EPS is basic (not diluted) — from Polygon GAAP-reported figures
- `shift(4)` assumes no missing quarters. A gap will misalign YoY — acceptable for now
- Single-ticker run = 1 API call — no rate limiting needed
- For batch screening across multiple tickers: add 13-second sleep between calls (free tier limit)
- Do NOT use Alpha Vantage, yfinance, or TradingView
