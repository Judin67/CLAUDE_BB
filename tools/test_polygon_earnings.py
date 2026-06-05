#!/usr/bin/env python
"""
Quick test — checks access to earnings/fundamental data on current Polygon tier.
"""

import os
import requests
from dotenv import load_dotenv

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', '.env'))
API_KEY  = os.getenv("POLYGON_API_KEY")
BASE_URL = "https://api.polygon.io"

def test(label, url, params=None):
    p = {"apiKey": API_KEY}
    if params:
        p.update(params)
    resp = requests.get(url, params=p)
    data = resp.json()
    status = data.get("status", resp.status_code)
    count  = len(data.get("results", []))
    msg    = data.get("message", data.get("error", ""))
    print(f"\n{label}")
    print(f"  status : {status}")
    if msg:
        print(f"  message: {msg}")
    if count:
        print(f"  results: {count} items")
        print(f"  sample : {data['results'][0]}")
    return status

# 1. Earnings calendar / financials
test(
    "Earnings financials (AAPL)",
    f"{BASE_URL}/vX/reference/financials",
    {"ticker": "AAPL", "limit": 3, "timeframe": "quarterly"}
)

# 2. Earnings surprise / estimates — via earnings endpoint
test(
    "Ticker events (AAPL) — earnings dates",
    f"{BASE_URL}/vX/reference/tickers/AAPL/events",
)

print("\nDone.")
