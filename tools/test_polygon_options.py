#!/usr/bin/env python
"""
Quick test — checks what options data is accessible on current Polygon tier.
Tests: options chain snapshot, single contract OHLCV, Greeks.
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
    count  = len(data.get("results", data.get("result", [])))
    msg    = data.get("message", data.get("error", ""))
    print(f"\n{label}")
    print(f"  status : {status}")
    if msg:
        print(f"  message: {msg}")
    if count:
        print(f"  results: {count} items")
    return status

# 1. Options chain snapshot for SPY (requires paid)
test(
    "Options chain snapshot (SPY)",
    f"{BASE_URL}/v3/snapshot/options/SPY",
    {"limit": 5}
)

# 2. Single options contract OHLCV (may be free)
# SPY 550 call expiring 2026-03-20
test(
    "Options contract bars (SPY 550C 2026-03-20)",
    f"{BASE_URL}/v2/aggs/ticker/O:SPY260320C00550000/range/1/day/2026-03-01/2026-03-20",
)

# 3. Options contract snapshot with Greeks (requires paid)
test(
    "Options contract snapshot with Greeks (SPY 550C)",
    f"{BASE_URL}/v3/snapshot/options/SPY/O:SPY260320C00550000",
)

print("\nDone.")
