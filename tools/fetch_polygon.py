#!/usr/bin/env python
# coding: utf-8
"""
fetch_polygon.py
----------------
Fetches OHLCV bars from Massive/Polygon REST API.

Usage:
    from tools.fetch_polygon import fetch_bars

    close = fetch_bars("SPY", "day",    "2024-01-01", "2026-03-21")
    close = fetch_bars("SPY", "minute", "2026-03-01", "2026-03-21", multiplier=5)
    close = fetch_bars("SPY", "minute", "2026-03-18", "2026-03-21", multiplier=30)

Returns:
    pd.Series of close prices with tz-naive DatetimeIndex, sorted ascending.

Notes:
    - PAID real-time tier (active). Same-day intraday requests work directly —
      no delayed-plan workaround needed. Real-time trades/quotes confirmed.
    - 10-second bars are available: fetch_bars(t, "second", d, d, multiplier=10).
    - Extended hours (premarket 04:00 + RTH + after-hours to 20:00) are included
      in intraday aggregates. Filter to RTH yourself only if a TF requires it.
    - Pagination is handled automatically via next_url.
"""

import os
import time
import requests
import pandas as pd
from dotenv import load_dotenv

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', '.env'))

API_KEY  = os.getenv("POLYGON_API_KEY")
BASE_URL = "https://api.polygon.io"
RATE_LIMIT_SLEEP = 0.1  # paid real-time tier: no meaningful rate cap; tiny pause is courtesy only


def fetch_bars(ticker, timespan, from_date, to_date, multiplier=1,
               adjusted=True, sort="asc", limit=50000):
    """
    Fetch aggregate bars from Massive/Polygon.

    Args:
        ticker     : e.g. "SPY", "AAPL"
        timespan   : "minute", "hour", "day", "week", "month"
        from_date  : "YYYY-MM-DD"
        to_date    : "YYYY-MM-DD"
        multiplier : bar size multiplier (e.g. 5 for 5-minute bars)
        adjusted   : split/dividend adjusted (default True)
        sort       : "asc" or "desc"
        limit      : results per request (max 50000)

    Returns:
        pd.DataFrame with columns: open, high, low, close, volume, vwap, transactions
        Index: DatetimeIndex (tz-naive, UTC converted)
    """
    if not API_KEY:
        raise ValueError("POLYGON_API_KEY not found in .env")

    url = f"{BASE_URL}/v2/aggs/ticker/{ticker}/range/{multiplier}/{timespan}/{from_date}/{to_date}"
    params = {
        "adjusted": str(adjusted).lower(),
        "sort":     sort,
        "limit":    limit,
        "apiKey":   API_KEY,
    }

    results = []
    page = 0

    while url:
        if page > 0:
            time.sleep(RATE_LIMIT_SLEEP)

        resp = requests.get(url, params=params if page == 0 else {"apiKey": API_KEY})
        data = resp.json()

        if data.get("status") == "ERROR":
            raise RuntimeError(f"Polygon API error: {data.get('error', data)}")

        if data.get("status") == "NOT_AUTHORIZED":
            raise PermissionError(f"Not authorized — upgrade plan: {data.get('message')}")

        batch = data.get("results", [])
        results.extend(batch)

        url = data.get("next_url")
        params = None  # next_url already includes all params except apiKey
        page += 1

    if not results:
        return pd.DataFrame(columns=["open", "high", "low", "close", "volume", "vwap", "transactions"])

    df = pd.DataFrame(results)
    df = df.rename(columns={
        "t": "timestamp",
        "o": "open",
        "h": "high",
        "l": "low",
        "c": "close",
        "v": "volume",
        "vw": "vwap",
        "n": "transactions",
    })

    df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms", utc=True).dt.tz_convert(None)
    df = df.set_index("timestamp").sort_index()
    df = df[["open", "high", "low", "close", "volume", "vwap", "transactions"]]

    return df


def fetch_close(ticker, timespan, from_date, to_date, multiplier=1):
    """
    Convenience wrapper — returns only the close price as a Series.
    """
    df = fetch_bars(ticker, timespan, from_date, to_date, multiplier=multiplier)
    return df["close"].rename(ticker)


if __name__ == "__main__":
    # Quick test
    import datetime
    today     = datetime.date.today().strftime("%Y-%m-%d")
    week_ago  = (datetime.date.today() - datetime.timedelta(days=7)).strftime("%Y-%m-%d")
    year_ago  = (datetime.date.today() - datetime.timedelta(days=365)).strftime("%Y-%m-%d")

    print("Testing daily bars (1 year)...")
    daily = fetch_close("SPY", "day", year_ago, today)
    print(f"  bars: {len(daily)} | range: {daily.index[0]} to {daily.index[-1]}")

    print("Testing 5m bars (last week)...")
    bars_5m = fetch_close("SPY", "minute", week_ago, today, multiplier=5)
    print(f"  bars: {len(bars_5m)} | range: {bars_5m.index[0]} to {bars_5m.index[-1]}")

    print("All tests passed.")
