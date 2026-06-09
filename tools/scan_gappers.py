#!/usr/bin/env python
# coding: utf-8
"""
scan_gappers.py
---------------
Market-wide historical premarket-gapper scanner (Polygon/Massive).

Two-stage funnel, built to be cheap first and expensive only on survivors:

  Stage 1 (one API call per day): Polygon GROUPED DAILY aggregates returns OHLCV
          for EVERY listed ticker on a date. We flag candidates whose day-HIGH is
          >= gap_min over the prior trading day's close, above a price floor, with
          real daily volume. Using HIGH (not open) catches names that ran intraday
          even if they opened modestly or faded by the close.

  Stage 2 (one minute-bar fetch per candidate): pull 04:00-09:29 ET premarket bars
          and keep only names with >= pm_vol_min premarket SHARES. Records the true
          premarket gap (PM high / prior close) and premarket volume.

Survivors = a clean validation universe of *real* premarket gappers — the names a
low-float trader would actually have been looking at that morning.

Usage (CLI):
    python tools/scan_gappers.py --start 2026-05-01 --end 2026-05-31
    python tools/scan_gappers.py --start 2026-03-01 --end 2026-05-31 \
        --gap-min 0.50 --pm-vol-min 50000 --price-min 0.50

Import:
    from tools.scan_gappers import scan_gappers
    df = scan_gappers("2026-05-01", "2026-05-31")
"""

import os
import sys
import time
import re
import argparse
import requests
import pandas as pd
from datetime import date, timedelta

sys.path.insert(0, os.path.dirname(__file__))
from fetch_polygon import fetch_bars, API_KEY, BASE_URL

# Windows console can't encode emoji/arrows under cp1252
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

MARKET_OPEN  = pd.Timestamp("09:30").time()
PM_START     = pd.Timestamp("04:00").time()

# ── Defaults ──────────────────────────────────────────────────────────────────
GAP_MIN_DEFAULT      = 0.50      # PREMARKET gap >= 50% over prior close (the morning setup)
PM_MIN_MIN_DEFAULT   = 100_000   # >= 100k shares in at least one premarket MINUTE (a real surge)
PRICE_MIN_DEFAULT    = 0.50      # price floor (cut sub-penny noise)
VOL_MIN_DEFAULT      = 1_000_000 # full-day volume floor (must actually have traded)
OPEN_NET_DEFAULT     = 0.25      # stage-1 cheap net: RTH open >= 25% over prior close


def is_derivative(t: str) -> bool:
    """Heuristic: drop warrants/units/rights so the universe is common stock only.
    5+ char tickers ending in W (warrant), U (unit), or R (right), or any with a dot."""
    if "." in t:
        return True
    if len(t) >= 5 and t[-1] in ("W", "U", "R"):
        return True
    return False


def grouped_daily(day: str, include_otc: bool = False) -> dict:
    """
    One call → every listed ticker's daily OHLCV for `day` (YYYY-MM-DD).
    Returns {ticker: {o,h,l,c,v,vw,n}} or {} on a non-trading day.
    """
    url = f"{BASE_URL}/v2/aggs/grouped/locale/us/market/stocks/{day}"
    params = {
        "adjusted":   "true",
        "include_otc": str(include_otc).lower(),
        "apiKey":      API_KEY,
    }
    resp = requests.get(url, params=params)
    data = resp.json()
    if data.get("status") == "NOT_AUTHORIZED":
        raise PermissionError(data.get("message"))
    out = {}
    for r in data.get("results", []) or []:
        t = r.get("T")
        if t:
            out[t] = r
    return out


def _premarket_stats(ticker: str, day: str):
    """
    Fetch `day` minute bars; return premarket (04:00-09:29 ET) stats:
        (pm_vol_total, pm_minute_max, pm_high)
    pm_minute_max = the single busiest premarket minute's share volume.
    Returns (0, 0, None) if no premarket data.
    """
    df = fetch_bars(ticker, "minute", day, day)
    if df.empty:
        return 0, 0, None
    idx = df.index.tz_localize("UTC").tz_convert("America/New_York")
    df = df.set_axis(idx)
    pm = df[(idx.time >= PM_START) & (idx.time < MARKET_OPEN)]
    if pm.empty:
        return 0, 0, None
    return (int(pm["volume"].sum()),
            int(pm["volume"].max()),
            float(pm["high"].max()))


def scan_gappers(start: str, end: str,
                 gap_min: float = GAP_MIN_DEFAULT,
                 pm_min_min: int = PM_MIN_MIN_DEFAULT,
                 price_min: float = PRICE_MIN_DEFAULT,
                 vol_min: int = VOL_MIN_DEFAULT,
                 open_net: float = OPEN_NET_DEFAULT,
                 include_otc: bool = False,
                 keep_derivatives: bool = False,
                 verbose: bool = True) -> pd.DataFrame:
    """
    Scan [start, end] inclusive for premarket gappers. See module docstring.

    A name is kept iff (stage 2): premarket gap >= gap_min AND the busiest
    premarket minute traded >= pm_min_min shares.

    Returns DataFrame sorted by date then pm_gap desc, columns:
        date | ticker | prev_close | open | high | close | day_vol
        | gap_high | gap_open | pm_vol | pm_min_max | pm_high | pm_gap
    """
    d0 = date.fromisoformat(start)
    d1 = date.fromisoformat(end)

    prev_close = {}      # {ticker: prior trading day's close}
    candidates = []      # stage-1 survivors awaiting premarket check
    days_scanned = 0

    # Seed prev_close from the trading day BEFORE start (walk back up to 7 cal days)
    seed = d0 - timedelta(days=1)
    for _ in range(7):
        g = grouped_daily(seed.isoformat(), include_otc)
        if g:
            prev_close = {t: r["c"] for t, r in g.items() if r.get("c")}
            if verbose:
                print(f"[seed] prior closes from {seed} ({len(prev_close)} tickers)")
            break
        seed -= timedelta(days=1)

    # ── Stage 1: grouped-daily sweep, one call per calendar day ──────────────
    cur = d0
    while cur <= d1:
        g = grouped_daily(cur.isoformat(), include_otc)
        if not g:                       # weekend / holiday
            cur += timedelta(days=1)
            continue
        days_scanned += 1
        day_str = cur.isoformat()
        day_hits = 0
        for t, r in g.items():
            if not keep_derivatives and is_derivative(t):
                continue
            o, h, c, v = r.get("o"), r.get("h"), r.get("c"), r.get("v", 0)
            pc = prev_close.get(t)
            if not (pc and h and o and c):
                continue
            if c < price_min and o < price_min:
                continue
            if v < vol_min:
                continue
            gap_open = o / pc - 1.0
            gap_high = h / pc - 1.0
            # Cheap net: open >= open_net OR intraday high >= gap_min.
            # Catches premarket gappers that hold into the open AND those that
            # already faded by 9:30 (still printed a big high). Premarket gap is
            # confirmed precisely in stage 2.
            if gap_open < open_net and gap_high < gap_min:
                continue
            candidates.append({
                "date": day_str, "ticker": t, "prev_close": round(pc, 4),
                "open": round(o, 4), "high": round(h, 4), "close": round(c, 4),
                "day_vol": int(v),
                "gap_high": round(gap_high, 4),
                "gap_open": round(gap_open, 4),
            })
            day_hits += 1
        if verbose:
            print(f"[stage1] {day_str}: {len(g)} tickers, {day_hits} net candidates")
        # roll prev_close forward to this day's closes
        prev_close = {t: r["c"] for t, r in g.items() if r.get("c")}
        cur += timedelta(days=1)

    if verbose:
        print(f"\n[stage1] {days_scanned} trading days, "
              f"{len(candidates)} raw candidates → premarket check...\n")

    # ── Stage 2: premarket gap + per-minute surge check per candidate ────────
    rows = []
    for i, cand in enumerate(candidates, 1):
        try:
            pm_vol, pm_min_max, pm_high = _premarket_stats(cand["ticker"], cand["date"])
        except Exception as e:
            if verbose:
                print(f"  [warn] {cand['ticker']} {cand['date']}: {e}")
            continue
        pm_gap = (pm_high / cand["prev_close"] - 1.0) if pm_high else None
        ok = (pm_gap is not None and pm_gap >= gap_min and pm_min_max >= pm_min_min)
        if not ok:
            if verbose:
                why = (f"pm_gap={pm_gap:.2f}" if pm_gap is not None else "pm_gap=NA")
                print(f"  [stage2] {i}/{len(candidates)} {cand['ticker']} "
                      f"{cand['date']}: {why} pm_min_max={pm_min_max:,}  skip")
            continue
        cand = {**cand, "pm_vol": pm_vol, "pm_min_max": pm_min_max,
                "pm_high": round(pm_high, 4) if pm_high else None,
                "pm_gap": round(pm_gap, 4)}
        rows.append(cand)
        if verbose:
            print(f"  [stage2] {i}/{len(candidates)} {cand['ticker']} "
                  f"{cand['date']}: pm_gap={cand['pm_gap']} pm_min_max={pm_min_max:,}  KEEP")
        time.sleep(0.05)

    cols = ["date", "ticker", "prev_close", "open", "high", "close", "day_vol",
            "gap_high", "gap_open", "pm_vol", "pm_min_max", "pm_high", "pm_gap"]
    if not rows:
        return pd.DataFrame(columns=cols)
    df = pd.DataFrame(rows)[cols]
    return df.sort_values(["date", "pm_gap"], ascending=[True, False]).reset_index(drop=True)


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="Market-wide historical premarket-gapper scanner")
    ap.add_argument("--start", required=True, help="YYYY-MM-DD")
    ap.add_argument("--end", required=True, help="YYYY-MM-DD")
    ap.add_argument("--gap-min", type=float, default=GAP_MIN_DEFAULT,
                    help=f"min PREMARKET gap vs prior close (default {GAP_MIN_DEFAULT})")
    ap.add_argument("--pm-min-min", type=int, default=PM_MIN_MIN_DEFAULT,
                    help=f"min shares in busiest premarket minute (default {PM_MIN_MIN_DEFAULT})")
    ap.add_argument("--price-min", type=float, default=PRICE_MIN_DEFAULT,
                    help=f"min price floor (default {PRICE_MIN_DEFAULT})")
    ap.add_argument("--vol-min", type=int, default=VOL_MIN_DEFAULT,
                    help=f"min full-day volume (default {VOL_MIN_DEFAULT})")
    ap.add_argument("--open-net", type=float, default=OPEN_NET_DEFAULT,
                    help=f"stage-1 net: min RTH-open gap (default {OPEN_NET_DEFAULT})")
    ap.add_argument("--otc", action="store_true", help="include OTC tickers")
    ap.add_argument("--keep-derivatives", action="store_true",
                    help="keep warrants/units/rights (default: dropped)")
    ap.add_argument("--out", default=None, help="CSV output path")
    args = ap.parse_args()

    df = scan_gappers(args.start, args.end,
                      gap_min=args.gap_min, pm_min_min=args.pm_min_min,
                      price_min=args.price_min, vol_min=args.vol_min,
                      open_net=args.open_net, include_otc=args.otc,
                      keep_derivatives=args.keep_derivatives)

    print("\n" + "=" * 70)
    print(f"GAPPER UNIVERSE  {args.start} → {args.end}  "
          f"(pm_gap>={args.gap_min:.0%}, pm_minute>={args.pm_min_min:,})")
    print("=" * 70)
    if df.empty:
        print("No gappers matched the filters.")
    else:
        print(f"{len(df)} names\n")
        print(df.to_string(index=False))

    out = args.out or os.path.join(
        os.path.dirname(__file__), "..", "data",
        f"gapper_universe_{args.start}_{args.end}.csv")
    if not df.empty:
        os.makedirs(os.path.dirname(out), exist_ok=True)
        df.to_csv(out, index=False)
        print(f"\nSaved → {out}")
