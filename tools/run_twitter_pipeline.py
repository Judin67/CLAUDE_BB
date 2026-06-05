#!/usr/bin/env python
# coding: utf-8
"""
run_twitter_pipeline.py
------------------------
Daily pipeline: scrapes tweets from monitored traders, extracts $cashtags,
stores mentions in DuckDB, and prints the ticker list.

Usage:
    python tools/run_twitter_pipeline.py               # runs for prior trading day
    python tools/run_twitter_pipeline.py --date 2026-04-07

Outputs:
    data/twitter_pipeline.duckdb
        mentions(run_date, ticker, trader)
    Console: list of tickers found
"""

import argparse
import os
import sys
from datetime import date, datetime

import duckdb
import pandas as pd
import pytz

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from tools.fetch_twitter_mentions import fetch_mentions

# ── Trader list ───────────────────────────────────────────────────────────────
TRADERS = [
    "krisVerma88",
    "madaznfootballr",
    "TheShortSniper",
    "veptrader",
    "Jackaroo_trades",
]

# ── Config ────────────────────────────────────────────────────────────────────
DB_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "twitter_pipeline.duckdb")


# ── Database setup ────────────────────────────────────────────────────────────

def init_db(con: duckdb.DuckDBPyConnection) -> None:
    con.execute("""
        CREATE TABLE IF NOT EXISTS mentions (
            run_date  DATE    NOT NULL,
            ticker    VARCHAR NOT NULL,
            trader    VARCHAR NOT NULL,
            PRIMARY KEY (run_date, ticker, trader)
        )
    """)


def store_mentions(con: duckdb.DuckDBPyConnection, mentions_df: pd.DataFrame, run_date: date) -> None:
    if mentions_df.empty:
        return
    df = mentions_df.copy()
    df["run_date"] = run_date
    con.register("_mentions_staging", df[["run_date", "ticker", "trader"]])
    con.execute("""
        INSERT OR IGNORE INTO mentions (run_date, ticker, trader)
        SELECT run_date, ticker, trader FROM _mentions_staging
    """)
    con.unregister("_mentions_staging")


# ── Helpers ───────────────────────────────────────────────────────────────────

def _prior_trading_day() -> date:
    """Returns the most recent weekday before today (Mon-Fri, ignoring holidays)."""
    d = date.today()
    d -= __import__("datetime").timedelta(days=1)
    while d.weekday() >= 5:  # 5=Sat, 6=Sun
        d -= __import__("datetime").timedelta(days=1)
    return d


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Twitter trader mention scraper")
    parser.add_argument("--date", type=str, default=None,
                        help="Target date YYYY-MM-DD (default: prior trading day)")
    args = parser.parse_args()

    if args.date:
        run_date = datetime.strptime(args.date, "%Y-%m-%d").date()
    else:
        run_date = _prior_trading_day()

    date_str = run_date.strftime("%Y-%m-%d")
    print(f"\n{'='*60}")
    print(f"  Twitter Pipeline — {date_str}")
    print(f"  Traders monitored: {len(TRADERS)}")
    print(f"{'='*60}\n")

    # ── Init DB ──
    os.makedirs(os.path.join(os.path.dirname(__file__), "..", "data"), exist_ok=True)
    con = duckdb.connect(DB_PATH)
    init_db(con)

    # ── Scrape Twitter ──
    print("[STEP 1] Scraping Twitter mentions ...")
    mentions_df = fetch_mentions(TRADERS, run_date)

    if mentions_df.empty:
        print("[WARN] No cashtag mentions found. Exiting.")
        con.close()
        return

    store_mentions(con, mentions_df, run_date)
    con.close()

    tickers = mentions_df["ticker"].unique().tolist()

    print(f"\n{'='*60}")
    print(f"  [DONE] {date_str}")
    print(f"  Tickers found: {len(tickers)}")
    print(f"{'='*60}")
    print("\n  " + "  ".join(tickers))
    print()

    # Per-trader breakdown
    print("  Breakdown by trader:")
    for trader, group in mentions_df.groupby("trader"):
        print(f"    @{trader}: {group['ticker'].tolist()}")
    print()


if __name__ == "__main__":
    main()
