#!/usr/bin/env python
# coding: utf-8
"""
validate_card.py
----------------
Back-validation: does the dilution card's grade actually predict the fade?

Input : a gapper-universe CSV from scan_gappers.py (date,ticker,open,high,close,
        pm_gap,gap_open,...).
Method: for each UNIQUE ticker, compute the card's structural read ONCE (float
        band + dilution grade + flag count), as of its first gap date, reusing the
        exact fetch_dilution internals. Structural dilution (float, shelf, warrants,
        reverse-split history) is ~time-stable over a quarter, so one read per
        company is faithful enough for a first pass and keeps EDGAR load sane.
        Join that grade back to EVERY gap event and tabulate grade vs outcome.

Outcomes per event (all from the scan, no extra fetch):
    open_to_close = close/open - 1     (held vs faded from the open)
    high_to_close = close/high - 1     (give-back from the intraday high)
    faded         = open_to_close < 0

The question being answered:
    Do 🔴 SERIAL / 🟠 HIGH grades fade harder than 🟢 CLEAN ones?
    Do smaller float bands produce bigger (more violent) moves?

Usage:
    python tools/validate_card.py data/gapper_universe_Q2pilot.csv
"""

import os, sys, time, argparse, datetime as dt
import pandas as pd

sys.path.insert(0, os.path.dirname(__file__))
from edgar_client import EdgarClient
import fetch_dilution as fd

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

GRADE_ORDER = ["CLEAN", "MODERATE", "HIGH RISK", "SERIAL DILUTER", "UNKNOWN"]
BAND_ORDER  = ["RELATIVELY SAFE", "CAUTION", "HIGH SQUEEZE", "EXTREME",
               "DO NOT TRADE", "UNKNOWN"]


def structural_read(ec, ticker, as_of):
    """Compute the card's structural grade for one ticker as of `as_of` (date),
    POINT-IN-TIME: float and every dilution window are bounded to `as_of` so no
    post-gap filing leaks into a pre-gap grade. EDGAR-only by design — Polygon
    float/free-float are real-time (no as-of), so they'd reintroduce lookahead.
    Returns dict or None on failure."""
    cik = ec.ticker_to_cik(ticker)
    if not cik:
        return {"ticker": ticker, "grade": "UNKNOWN", "band": "UNKNOWN",
                "float_sh": None, "n_flags": None, "serial": None, "note": "no CIK"}
    facts = ec.companyfacts(cik)
    until = as_of.strftime("%Y-%m-%d")          # mirrors fetch_dilution --date contract
    so = ec.latest_asof(facts, ["EntityCommonStockSharesOutstanding",
                                "CommonStockSharesOutstanding"], as_of)
    float_sh = so[0]
    band = fd.smb_band(float_sh)[0]
    flags, serial, _, _ = fd.compute_dilution(ec, cik, facts, as_of, until=until)
    n_flags = sum(1 for f in flags if f["on"])
    grade, _ = fd.classify(n_flags, serial)
    return {"ticker": ticker, "grade": grade, "band": band,
            "float_sh": float_sh, "n_flags": n_flags, "serial": serial, "note": ""}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("universe_csv")
    ap.add_argument("--out", default=None)
    args = ap.parse_args()

    uni = pd.read_csv(args.universe_csv)
    uni["date"] = pd.to_datetime(uni["date"])
    uni["open_to_close"] = uni["close"] / uni["open"] - 1
    uni["high_to_close"] = uni["close"] / uni["high"] - 1
    uni["faded"] = uni["open_to_close"] < 0

    # first gap date per ticker = the as-of for its structural read
    first_date = uni.groupby("ticker")["date"].min()
    tickers = list(first_date.index)
    print(f"Universe: {len(uni)} events, {len(tickers)} unique tickers\n"
          f"Computing structural card per ticker (~5s each)...\n")

    ec = EdgarClient()
    reads = {}
    for i, tk in enumerate(tickers, 1):
        as_of = first_date[tk].date()
        try:
            r = structural_read(ec, tk, as_of)
        except Exception as e:
            r = {"ticker": tk, "grade": "UNKNOWN", "band": "UNKNOWN",
                 "float_sh": None, "n_flags": None, "serial": None, "note": str(e)[:60]}
        reads[tk] = r
        print(f"  {i}/{len(tickers)} {tk}: {r['grade']} · {r['band']} · "
              f"float={fd.fmt_sh(r['float_sh'])} · flags={r['n_flags']}"
              + (f"  [{r['note']}]" if r['note'] else ""))
        time.sleep(0.03)

    rd = pd.DataFrame(reads.values())
    scored = uni.merge(rd, on="ticker", how="left")
    out = args.out or args.universe_csv.replace(".csv", "_scored.csv")
    scored.to_csv(out, index=False)
    print(f"\nSaved scored events → {out}\n")

    # ── Tabulate ─────────────────────────────────────────────────────────────
    def bucket(df, col, order):
        g = df.groupby(col).agg(
            n=("ticker", "size"),
            pct_red=("faded", lambda s: round(s.mean() * 100)),
            med_open_to_close=("open_to_close", lambda s: round(s.median() * 100, 1)),
            med_giveback_from_high=("high_to_close", lambda s: round(s.median() * 100, 1)),
            med_pm_gap=("pm_gap", lambda s: round(s.median() * 100)),
        )
        g = g.reindex([x for x in order if x in g.index])
        return g

    print("=" * 78)
    print("OUTCOME BY DILUTION GRADE   (does a worse grade => harder fade?)")
    print("=" * 78)
    print(bucket(scored, "grade", GRADE_ORDER).to_string())
    print("\n" + "=" * 78)
    print("OUTCOME BY FLOAT BAND   (does a smaller float => bigger move?)")
    print("=" * 78)
    print(bucket(scored, "band", BAND_ORDER).to_string())

    print("\nLegend: pct_red=% closed below open · med_open_to_close=median open→close ·")
    print("        med_giveback_from_high=median close vs intraday high · med_pm_gap=median premarket gap")


if __name__ == "__main__":
    main()
