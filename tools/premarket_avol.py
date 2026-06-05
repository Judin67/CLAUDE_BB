#!/usr/bin/env python
# coding: utf-8
"""
premarket_avol.py
-----------------
Computes premarket and after-hours volume relative to 21-day AVOL.

Faithfully replicates the TOS extended-hours AVOL logic:

    ### daily AVOL ###
    def daily_volume = volume(period = AggregationPeriod.DAY);
    def AVOL = Average(daily_volume[1], AVOL_length);

    # AfterHours Volume  (subtractFirstBarVolume = yes by default)
    def ah = getTime() > regularTradingEnd(getYYYYMMDD());
    def firstAHVolume = if ah and !ah[1] then volume else firstAHVolume[1];
    def ahVol = if ah and !ah[1]
                then if subtractFirstBarVolume then 0 else volume
                else if ah
                then ahVol[1] + volume - (if !ah[1] and subtractFirstBarVolume then firstAHVolume else 0)
                else ahVol[1];

    # PreMarket Volume
    def pm = getTime() < regularTradingStart(getYYYYMMDD());
    def pmVol = if pm and !pm[1]
                then volume
                else if pm
                then pmVol[1] + volume
                else pmVol[1];

    # Total ExtendedHours Volume
    def comVol = if pm then ahVol + pmVol else comVol[1];

Usage:
    from tools.premarket_avol import compute_eh_avol, scan_eh_avol

    # Single ticker
    df = compute_eh_avol("NVDA")

    # Multi-ticker scan, sorted by pm_pct_avol descending
    df = scan_eh_avol(["NVDA", "TSLA", "AAPL"])
"""

import os
import sys
import pandas as pd
from datetime import date, timedelta

# Allow running directly from tools/ or from project root
sys.path.insert(0, os.path.dirname(__file__))
from fetch_polygon import fetch_bars


AVOL_LENGTH_DEFAULT    = 21
MARKET_OPEN            = pd.Timestamp("09:30").time()  # regularTradingStart
MARKET_CLOSE           = pd.Timestamp("16:00").time()  # regularTradingEnd
SUBTRACT_FIRST_BAR     = True                          # matches TOS default


def _classify(pct_avol: float) -> str:
    """
    Thresholds:
      below 10%        → "ignore"
      10% to under 20% → "maybe"
      20% and above    → "watch"
    """
    if pct_avol < 10:
        return "ignore"
    elif pct_avol < 20:
        return "maybe"
    else:
        return "watch"


def compute_eh_avol(ticker: str, avol_length: int = AVOL_LENGTH_DEFAULT,
                    subtract_first_bar: bool = SUBTRACT_FIRST_BAR,
                    as_of_date=None) -> pd.DataFrame:
    """
    Compute premarket, after-hours, and combined extended-hours volume vs AVOL
    for a single ticker.

    Parameters
    ----------
    ticker             : stock symbol, e.g. "NVDA"
    avol_length        : rolling lookback in trading days (default 21, matches TOS)
    subtract_first_bar : exclude first AH bar from ahVol (default True, matches TOS)
    as_of_date         : date to treat as "today" (default: date.today())
                         Supports historical back-runs by passing a specific date.

    Returns
    -------
    pd.DataFrame with one row and columns:
        symbol | avol
        | pm_vol  | pm_pct_avol  | pm_label
        | ah_vol  | ah_pct_avol  | ah_label
        | eh_vol  | eh_pct_avol  | eh_label
    """
    if as_of_date is None:
        as_of_date = date.today()

    # ── Part 1: AVOL ──────────────────────────────────────────────────────────
    # TOS: daily_volume[1] → excludes today; Average over avol_length prior days.
    # Buffer of +10 covers weekends and holidays without hardcoding a multiplier.
    daily_from = as_of_date - timedelta(days=avol_length + 15)
    daily_to   = as_of_date - timedelta(days=1)   # yesterday = last complete day

    daily_df = fetch_bars(ticker, "day", str(daily_from), str(daily_to))

    if len(daily_df) < avol_length:
        raise ValueError(
            f"{ticker}: only {len(daily_df)} daily bars available, "
            f"need at least {avol_length}. Widen the lookback window."
        )

    # Take the last avol_length complete trading days
    avol = daily_df["volume"].iloc[-avol_length:].mean()

    # ── Part 2: Intraday bars for today ───────────────────────────────────────
    intraday_df = fetch_bars(ticker, "minute", str(as_of_date), str(as_of_date))

    pm_vol = 0
    ah_vol = 0

    if not intraday_df.empty:
        # fetch_polygon returns tz-naive UTC timestamps; convert to NY time
        # (same pattern used in fetch_volume_mtf.py)
        intraday_df.index = (
            intraday_df.index
            .tz_localize("UTC")
            .tz_convert("America/New_York")
        )

        # ── Part 2a: Premarket Volume ──────────────────────────────────────────
        # TOS: pm = getTime() < regularTradingStart(getYYYYMMDD())
        # pmVol is a simple running total — no first-bar subtraction for PM.
        pm_mask = intraday_df.index.time < MARKET_OPEN
        pm_vol  = int(intraday_df.loc[pm_mask, "volume"].sum())

        # ── Part 2b: After-Hours Volume ────────────────────────────────────────
        # TOS: ah = getTime() > regularTradingEnd(getYYYYMMDD())
        # subtractFirstBarVolume = yes (default):
        #   → first AH bar is captured in firstAHVolume but ahVol starts at 0
        #   → accumulation begins from the second AH bar onward
        # This removes the closing bar which often contains mixed RTH/AH prints.
        ah_mask = intraday_df.index.time >= MARKET_CLOSE
        ah_df   = intraday_df.loc[ah_mask]

        if not ah_df.empty:
            if subtract_first_bar:
                # Skip index 0 — the first bar right at close
                ah_vol = int(ah_df["volume"].iloc[1:].sum())
            else:
                ah_vol = int(ah_df["volume"].sum())

    # ── Part 3: %AVOL calculations ────────────────────────────────────────────
    # Exact floats; rounded to 1dp in the output row
    pm_pct_avol = (pm_vol / avol) * 100
    ah_pct_avol = (ah_vol / avol) * 100

    # TOS: comVol = ahVol + pmVol  (total extended hours)
    eh_vol      = pm_vol + ah_vol
    eh_pct_avol = (eh_vol / avol) * 100

    return pd.DataFrame([{
        "symbol":       ticker,
        "avol":         round(avol),
        # premarket
        "pm_vol":       pm_vol,
        "pm_pct_avol":  round(pm_pct_avol, 1),
        "pm_label":     _classify(pm_pct_avol),
        # after-hours
        "ah_vol":       ah_vol,
        "ah_pct_avol":  round(ah_pct_avol, 1),
        "ah_label":     _classify(ah_pct_avol),
        # combined extended hours
        "eh_vol":       eh_vol,
        "eh_pct_avol":  round(eh_pct_avol, 1),
        "eh_label":     _classify(eh_pct_avol),
    }])


def scan_eh_avol(tickers: list, avol_length: int = AVOL_LENGTH_DEFAULT,
                 subtract_first_bar: bool = SUBTRACT_FIRST_BAR,
                 as_of_date=None) -> pd.DataFrame:
    """
    Run compute_eh_avol for multiple tickers.

    Returns a DataFrame sorted by pm_pct_avol descending (highest relative
    premarket activity at the top).
    """
    frames = []
    for ticker in tickers:
        try:
            frames.append(
                compute_eh_avol(ticker, avol_length, subtract_first_bar, as_of_date)
            )
        except Exception as e:
            print(f"[WARN] {ticker}: {e}")

    if not frames:
        return pd.DataFrame(columns=[
            "symbol", "avol",
            "pm_vol", "pm_pct_avol", "pm_label",
            "ah_vol", "ah_pct_avol", "ah_label",
            "eh_vol", "eh_pct_avol", "eh_label",
        ])

    result = pd.concat(frames, ignore_index=True)
    return result.sort_values("pm_pct_avol", ascending=False).reset_index(drop=True)


# ── Backwards-compatible aliases ──────────────────────────────────────────────
compute_pm_avol = compute_eh_avol
scan_pm_avol    = scan_eh_avol


if __name__ == "__main__":
    tickers = ["NVDA", "TSLA", "AAPL"]
    print(f"Computing extended-hours %AVOL for: {tickers}\n")
    result = scan_eh_avol(tickers)
    print(result.to_string(index=False))
