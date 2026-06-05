#!/usr/bin/env python
# coding: utf-8
"""
chart_intraday.py
-----------------
Plots 1m and 5m candlestick charts with:
  - Cumulative intraday VWAP (NOT the per-bar Polygon vwap column)
  - Volume panel (green/red matching candle)
Each timeframe opens in its own separate window.

Usage:
    python tools/chart_intraday.py --ticker FIG --date 2025-08-01
"""

import argparse
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import matplotlib
matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.gridspec as gridspec
import pandas as pd

from tools.fetch_polygon import fetch_bars

RTH_START = "09:30"
RTH_END   = "16:00"


def to_et(df):
    """Convert UTC index to US/Eastern, strip tzinfo for clean plotting."""
    df.index = pd.to_datetime(df.index, utc=True).tz_convert("America/New_York").tz_localize(None)
    return df


def filter_rth(df):
    times = df.index.time
    start = pd.Timestamp(RTH_START).time()
    end   = pd.Timestamp(RTH_END).time()
    return df[(times >= start) & (times <= end)]


def calc_vwap(df):
    """Proper cumulative intraday VWAP."""
    tp = (df["high"] + df["low"] + df["close"]) / 3
    return (tp * df["volume"]).cumsum() / df["volume"].cumsum()


def bar_width_td(df):
    if len(df) < 2:
        return pd.Timedelta(minutes=1)
    return (df.index[1] - df.index[0]) * 0.7


def plot_chart(df, title, out_path=None):
    fig = plt.figure(figsize=(18, 9), facecolor="#121212")
    gs = gridspec.GridSpec(2, 1, height_ratios=[3, 1], hspace=0.05)

    ax_price = fig.add_subplot(gs[0])
    ax_vol   = fig.add_subplot(gs[1], sharex=ax_price)

    ax_price.set_facecolor("#1e1e1e")
    ax_vol.set_facecolor("#1e1e1e")

    width = bar_width_td(df)
    vwap  = calc_vwap(df)

    for ts, row in df.iterrows():
        color = "#26a69a" if row["close"] >= row["open"] else "#ef5350"
        body_bottom = min(row["open"], row["close"])
        body_height = abs(row["close"] - row["open"]) or (row["close"] * 0.0001)
        ax_price.bar(ts, body_height, bottom=body_bottom, width=width,
                     color=color, linewidth=0)
        ax_price.vlines(ts, row["low"], row["high"], color=color, linewidth=0.8)
        ax_vol.bar(ts, row["volume"], width=width, color=color, linewidth=0)

    ax_price.plot(df.index, vwap, color="#ffeb3b", linewidth=1.5, label="VWAP", zorder=5)

    # Styling — price panel
    ax_price.set_title(title, color="white", fontsize=13, pad=8)
    ax_price.tick_params(colors="#aaa", labelsize=8)
    ax_price.legend(loc="upper left", fontsize=9, facecolor="#1e1e1e",
                    labelcolor="white", framealpha=0.8)
    ax_price.set_xlim(df.index[0] - pd.Timedelta(minutes=2),
                      df.index[-1] + pd.Timedelta(minutes=2))
    for spine in ax_price.spines.values():
        spine.set_edgecolor("#444")
    plt.setp(ax_price.get_xticklabels(), visible=False)

    # Styling — volume panel
    ax_vol.set_ylabel("Volume", color="#aaa", fontsize=8)
    ax_vol.tick_params(colors="#aaa", labelsize=7)
    ax_vol.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M"))
    ax_vol.xaxis.set_major_locator(mdates.MinuteLocator(byminute=range(0, 60, 30)))
    plt.setp(ax_vol.xaxis.get_majorticklabels(), rotation=45, ha="right", color="#aaa")
    for spine in ax_vol.spines.values():
        spine.set_edgecolor("#444")

    fig.tight_layout()

    if out_path:
        plt.savefig(out_path, dpi=150, bbox_inches="tight", facecolor=fig.get_facecolor())
        print(f"Saved: {out_path}")

    return fig


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--ticker", default="FIG")
    parser.add_argument("--date",   default="2025-08-01")
    args = parser.parse_args()

    ticker = args.ticker.upper()
    date   = args.date

    print(f"Fetching 1m bars for {ticker} on {date}...")
    df1 = fetch_bars(ticker, "minute", date, date, multiplier=1)
    df1 = to_et(df1)
    df1 = filter_rth(df1)

    print(f"Fetching 5m bars for {ticker} on {date}...")
    df5 = fetch_bars(ticker, "minute", date, date, multiplier=5)
    df5 = to_et(df5)
    df5 = filter_rth(df5)

    if df1.empty and df5.empty:
        print("No data returned. Check ticker/date or Polygon subscription.")
        return

    out_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".tmp")
    os.makedirs(out_dir, exist_ok=True)

    if not df1.empty:
        out1 = os.path.join(out_dir, f"{ticker}_{date}_1m.png")
        plot_chart(df1, f"{ticker}  |  1 Minute  |  {date}  (ET)", out_path=out1)
    else:
        print("No 1m data.")

    if not df5.empty:
        out5 = os.path.join(out_dir, f"{ticker}_{date}_5m.png")
        plot_chart(df5, f"{ticker}  |  5 Minute  |  {date}  (ET)", out_path=out5)
    else:
        print("No 5m data.")

    plt.show()


if __name__ == "__main__":
    main()
