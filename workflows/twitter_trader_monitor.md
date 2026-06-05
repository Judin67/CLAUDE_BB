# Workflow: Twitter Trader Monitor

## Objective
Scrape daily tweets from a list of low-float traders, extract every $cashtag they mention, fetch 1-minute intraday bars (premarket through after-hours) from Polygon for each ticker, and store everything in DuckDB for later analysis and classification.

## When to Run
After 8:00 PM ET on trading days. By that point all monitored traders have posted their recaps and alerts for the session.

## Invocation
```bash
# For today
python tools/run_twitter_pipeline.py

# For a specific date
python tools/run_twitter_pipeline.py --date 2026-04-07
```

## Required Credentials
Add to `.env`:
```
TWITTER_USERNAME=your_twitter_handle   # no @
TWITTER_EMAIL=your_email@example.com
TWITTER_PASSWORD=your_password
POLYGON_API_KEY=...                    # already set
```

## Outputs
`data/twitter_pipeline.duckdb` — two tables:

| Table | Columns |
|---|---|
| `mentions` | `run_date, ticker, trader` |
| `intraday_bars` | `date, ticker, ts, open, high, low, close, volume, vwap` |

`ts` is stored in ET (America/New_York). Bars cover 4:00 AM – 8:00 PM ET.

## Querying the Database
```python
import duckdb
con = duckdb.connect("data/twitter_pipeline.duckdb")

# What tickers were mentioned today?
con.execute("SELECT ticker, COUNT(DISTINCT trader) as traders FROM mentions WHERE run_date = '2026-04-07' GROUP BY ticker ORDER BY traders DESC").df()

# Get 1m bars for a ticker
con.execute("SELECT * FROM intraday_bars WHERE ticker = 'ACMR' AND date = '2026-04-07' ORDER BY ts").df()

# Which traders mentioned a specific ticker?
con.execute("SELECT trader FROM mentions WHERE ticker = 'ACMR' AND run_date = '2026-04-07'").df()
```

## Trader List
Defined in `tools/run_twitter_pipeline.py` → `TRADERS` constant. Edit that list to add or remove handles.

Current list:
- `krisVerma88`
- `madazfootballr`
- `TheShortSniper`
- `veptrader`
- `Jackaroo_trades`

## Edge Cases

| Situation | Behavior |
|---|---|
| Private or suspended account | Skipped with `[WARN]`, pipeline continues |
| Trader posted no tweets today | No rows written for that trader |
| Ticker not found on Polygon | Skipped with `[WARN]` |
| Pipeline re-run for same date | Safe — `INSERT OR IGNORE` prevents duplicates |
| Weekend or holiday date | Polygon returns no bars; mentions still stored |
| Twitter cookies expired | Auto-detected, deleted, fresh login performed |
| `$AI`, `$IT`, etc. false positives | Filtered by `SKIP_TICKERS` set in `fetch_twitter_mentions.py` |

## Dependencies
```bash
pip install twikit duckdb
```
Install into conda env `my_quant_lab_py310`.

## File Map
```
tools/fetch_twitter_mentions.py   ← Twitter scraper (twikit)
tools/run_twitter_pipeline.py     ← Orchestrator
data/twitter_pipeline.duckdb      ← Persistent storage
.tmp/twitter_cookies.json         ← Cached Twitter session (auto-managed)
```
