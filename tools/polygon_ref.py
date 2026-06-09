#!/usr/bin/env python
# coding: utf-8
"""
polygon_ref.py
--------------
Reference / non-OHLCV data from Massive/Polygon REST (standalone — no MCP).
Companion to fetch_polygon.py (which does aggregates). Used by the dilution card
for: ticker overview (sector/locale), news (catalyst), short interest, short volume.

    from tools.polygon_ref import ticker_overview, latest_news, short_interest, short_volume
"""
import os
import requests
from dotenv import load_dotenv

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', '.env'))
API_KEY = os.getenv("POLYGON_API_KEY")
BASE = "https://api.polygon.io"


def poly_get(path, params=None):
    p = dict(params or {})
    p["apiKey"] = API_KEY
    try:
        r = requests.get(BASE + path, params=p, timeout=30)
    except Exception:
        return None
    if r.status_code != 200:
        return {"_status": r.status_code, "_error": r.text[:160]}
    return r.json()


def ticker_overview(ticker):
    return poly_get(f"/v3/reference/tickers/{ticker.upper()}")


def latest_news(ticker, limit=3, until=None):
    p = {"ticker": ticker.upper(), "limit": limit, "order": "desc", "sort": "published_utc"}
    if until:                       # point-in-time: no news after the card date
        p["published_utc.lte"] = until
    return poly_get("/v2/reference/news", p)


def free_float(ticker):
    """Latest FREE FLOAT (tradable shares) from Massive /stocks/vX/float.

    Excludes insiders, 5%+ holders, lockups, strategic/controlling stakes — i.e.
    real free float, NOT shares outstanding. Returns the result dict with keys
    free_float, free_float_percent, effective_date, ticker (or None/_status)."""
    d = poly_get("/stocks/vX/float", {"ticker": ticker.upper(), "limit": 1})
    if not d or "_status" in d:
        return d
    res = d.get("results") or []
    return res[0] if res else None


def short_interest(ticker, until=None):
    p = {"ticker": ticker.upper(), "sort": "settlement_date.desc", "limit": 1}
    if until:
        p["settlement_date.lte"] = until
    return poly_get("/stocks/v1/short-interest", p)


def short_volume(ticker, until=None):
    p = {"ticker": ticker.upper(), "sort": "date.desc", "limit": 1}
    if until:
        p["date.lte"] = until
    return poly_get("/stocks/v1/short-volume", p)


if __name__ == "__main__":
    import sys, json
    t = sys.argv[1].upper() if len(sys.argv) > 1 else "STI"
    for name, fn in [("OVERVIEW", ticker_overview), ("NEWS", latest_news),
                     ("SHORT_INTEREST", short_interest), ("SHORT_VOLUME", short_volume)]:
        d = fn(t)
        print(f"\n===== {name} ({t}) =====")
        if not d:
            print("  (no data / request failed)"); continue
        if "_status" in d:
            print(f"  HTTP {d['_status']}: {d.get('_error')}"); continue
        res = d.get("results")
        print(json.dumps(res if res is not None else d, indent=1, default=str)[:1500])
