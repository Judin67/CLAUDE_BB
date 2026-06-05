#!/usr/bin/env python
# coding: utf-8
"""
fetch_volume_indicator.py  —  Dr. S Indicator
-----------------------------------------------
Opening-window volume + range model.

Detects unusual opening participation (volume) and unusual opening displacement
(price range) relative to the last 14 sessions. No directional bias.

Signals:
  - Volume bars colored by 14-session slot average (green/dim/yellow)
  - Annotation: 14D avg opening range vs today's actual range + ratio

Usage:
    python tools/fetch_volume_indicator.py --ticker AAOI --date 2026-02-27
    python tools/fetch_volume_indicator.py --ticker NVDA --date 2026-03-30 --open-window 45
"""

import os
import sys
import argparse
import datetime
import warnings

import numpy as np
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import matplotlib.ticker as mticker
import matplotlib.patches as mpatches

warnings.filterwarnings("ignore")

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, "C:/Users/Trader/quant-project")

from tools.fetch_polygon import fetch_bars

# ── Default Config ──────────────────────────────────────────────────────────
TICKER      = "NVDA"
LOOKBACK    = 14
OUTLIER_SD  = 2.0
OPEN_WINDOW = 30         # minutes from 9:30 to evaluate

# Optional earnings overlay
EARNINGS_MODE        = False
ANCHOR_EARNINGS_DATE = "YYYY-MM-DD"
PHASE_LABEL          = "acceleration"

# ── Colors ──────────────────────────────────────────────────────────────────
BG     = "#0d0d1a"
PANEL  = "#131722"
TEXT   = "#c8c8d4"
GREEN  = "#26a69a"
RED    = "#ef5350"
BLUE   = "#4e9af1"
YELLOW = "#f1c40f"
PURPLE = "#9b59b6"
DIM    = "#3a3a55"

RTH_START = "09:30"
OUT_DIR   = os.path.join(os.path.dirname(__file__), "..", ".tmp")


# ── Data fetch ───────────────────────────────────────────────────────────────

def fetch_intraday(ticker, lookback, as_of_date=None, open_window=30):
    anchor  = as_of_date or datetime.date.today()
    from_dt = (anchor - datetime.timedelta(days=int(lookback * 1.7) + 5)).strftime("%Y-%m-%d")
    to_dt   = anchor.strftime("%Y-%m-%d")

    print(f"Fetching {ticker} 1m bars ({from_dt} to {to_dt})...")
    df = fetch_bars(ticker, "minute", from_dt, to_dt, multiplier=1)

    if df.empty:
        raise RuntimeError(f"No data returned for {ticker}.")

    df.index = df.index.tz_localize("UTC").tz_convert("America/New_York")
    df = df.between_time(RTH_START, "16:00")

    if df.empty:
        raise RuntimeError(f"No RTH bars found for {ticker}.")

    # Keep only the opening window
    bar_min  = df.index.hour * 60 + df.index.minute
    open_min = 9 * 60 + 30
    mask     = (bar_min >= open_min) & (bar_min < open_min + open_window)
    df       = df[mask]

    if df.empty:
        raise RuntimeError(f"No bars in opening window ({open_window}m) for {ticker}.")

    return df


# ── Slot ID ───────────────────────────────────────────────────────────────────

def assign_slot_id(df):
    bar_min  = df.index.hour * 60 + df.index.minute
    open_min = 9 * 60 + 30
    df = df.copy()
    df["slot_id"] = (bar_min - open_min).astype("int64")
    df["date"]    = np.array(df.index.date)
    return df


# ── Baseline ──────────────────────────────────────────────────────────────────

def compute_baseline(df, lookback):
    """
    Per slot_id: mean and std of bar volume across last `lookback` complete sessions.
    Also computes per-session opening range (high - low of full window) for HV.
    """
    unique_dates = sorted(df["date"].unique())

    if len(unique_dates) < 2:
        raise RuntimeError(
            f"Only {len(unique_dates)} session(s) found. Need at least 2. Widen date range."
        )

    hist_dates = unique_dates[-(lookback + 1):-1]
    n_hist     = len(hist_dates)
    if n_hist < lookback:
        print(f"  WARNING: Only {n_hist}/{lookback} baseline sessions available.")

    hist = df[df["date"].isin(hist_dates)].copy()

    # Per-slot volume baseline
    slot_baseline = (
        hist.groupby("slot_id")["volume"]
        .agg(mean_vol="mean", std_vol="std")
        .reset_index()
    )
    slot_baseline["std_vol"] = slot_baseline["std_vol"].replace(0, np.nan)

    # Per-session opening range for HV
    opening_ranges = []
    for d in hist_dates:
        sess = hist[hist["date"] == d]
        if sess.empty:
            continue
        opening_ranges.append(sess["high"].max() - sess["low"].min())

    hv_range_mean = float(np.mean(opening_ranges)) if opening_ranges else np.nan
    hv_range_std  = float(np.std(opening_ranges))  if len(opening_ranges) > 1 else np.nan

    return slot_baseline, hv_range_mean, hv_range_std


def compute_indicators(df_day, slot_baseline, outlier_sd, hv_range_mean, hv_range_std):
    df = df_day.copy().sort_index()

    df = df.reset_index()
    df = df.merge(slot_baseline, on="slot_id", how="left")
    df = df.set_index("timestamp")

    df["rel_vol"] = df["volume"] / df["mean_vol"]
    df["z_score"] = (df["volume"] - df["mean_vol"]) / df["std_vol"]
    df["outlier"] = df["z_score"].abs() >= outlier_sd

    today_range = float(df["high"].max() - df["low"].min())
    range_z     = float((today_range - hv_range_mean) / hv_range_std) if not np.isnan(hv_range_std) else np.nan

    return df, today_range, range_z


# ── Optional earnings overlay ─────────────────────────────────────────────────

def fetch_earnings_dates(ticker, anchor_date):
    try:
        from fetch_earnings_trend import fetch_quarterly_financials
    except ImportError as e:
        print(f"  WARNING: Cannot import fetch_earnings_trend — {e}")
        return []
    try:
        results = fetch_quarterly_financials(ticker, limit=20)
    except (PermissionError, RuntimeError) as e:
        print(f"  WARNING: Earnings fetch failed — {e}")
        return []

    anchor_ts = pd.Timestamp(anchor_date)
    dates = []
    for r in results:
        raw = r.get("end_date") or r.get("period_of_report_date")
        if not raw:
            continue
        ts = pd.Timestamp(raw)
        if ts >= anchor_ts:
            dates.append(ts)

    dates = sorted(set(dates))
    return [{"date": d, "phase_position": i} for i, d in enumerate(dates)]


# ── Chart helpers ─────────────────────────────────────────────────────────────

def _vol_formatter(v, _):
    if v >= 1_000_000:
        return f"{v/1_000_000:.1f}M"
    if v >= 1_000:
        return f"{v/1_000:.0f}K"
    return str(int(v))


def _draw_candles(ax, df, x):
    for i, (_, row) in zip(x, df.iterrows()):
        up    = row["close"] >= row["open"]
        color = GREEN if up else RED
        lo    = min(row["open"], row["close"])
        hi    = max(row["open"], row["close"])
        body  = max(hi - lo, row["close"] * 0.0005)
        ax.add_patch(mpatches.Rectangle(
            (i - 0.4, lo), 0.8, body, color=color, zorder=2
        ))
        ax.plot([i, i], [row["low"],  lo], color=color, linewidth=0.6, zorder=1)
        ax.plot([i, i], [hi, row["high"]], color=color, linewidth=0.6, zorder=1)


def _compute_vwap(df):
    typ = (df["high"] + df["low"] + df["close"]) / 3
    return (typ * df["volume"]).cumsum() / df["volume"].cumsum()


# ── Chart ─────────────────────────────────────────────────────────────────────

def build_chart(ticker, df_analysis, hv_range, today_range, lookback, outlier_sd,
                open_window, chart_date=None, earnings_events=None, phase_label=""):

    matplotlib.rcParams.update({
        "text.color":      TEXT,
        "axes.labelcolor": TEXT,
        "xtick.color":     TEXT,
        "ytick.color":     TEXT,
        "font.size":       9,
    })

    fig = plt.figure(figsize=(14, 9), facecolor=BG)
    gs  = gridspec.GridSpec(2, 1, height_ratios=[2.5, 1.5], hspace=0.06)

    ax_price = fig.add_subplot(gs[0])
    ax_vol   = fig.add_subplot(gs[1], sharex=ax_price)

    for ax in (ax_price, ax_vol):
        ax.set_facecolor(PANEL)
        for spine in ax.spines.values():
            spine.set_edgecolor(DIM)
        ax.grid(axis="y", color=DIM, linewidth=0.4, alpha=0.5)
        ax.tick_params(axis="both", which="both", length=3, color=DIM)

    x = np.arange(len(df_analysis))

    # ── Panel 1: Candlesticks + VWAP ────────────────────────────────────────
    _draw_candles(ax_price, df_analysis, x)
    vwap = _compute_vwap(df_analysis)
    ax_price.plot(x, vwap.values, color=PURPLE, linewidth=1.2,
                  linestyle="--", alpha=0.85, label="VWAP", zorder=3)

    price_pad = (df_analysis["high"].max() - df_analysis["low"].min()) * 0.08
    ax_price.set_ylim(df_analysis["low"].min() - price_pad,
                      df_analysis["high"].max() + price_pad)
    ax_price.set_xlim(-1, len(df_analysis) + 1)
    ax_price.set_ylabel("Price", fontsize=8)

    # ── Annotation box ───────────────────────────────────────────────────────
    if not np.isnan(hv_range) and today_range > 0:
        ratio     = today_range / hv_range
        ratio_str = f"{ratio:.2f}x"
        ratio_col = YELLOW if ratio >= 1.5 else GREEN if ratio >= 1.0 else TEXT

        ann_text = (
            f"14D Avg Range ({open_window}m)  ${hv_range:.2f}\n"
            f"Today's range          ${today_range:.2f}  ({ratio_str})"
        )
        ax_price.text(
            0.99, 0.97, ann_text,
            transform=ax_price.transAxes,
            va="top", ha="right",
            fontsize=8.5,
            color=ratio_col,
            bbox=dict(boxstyle="round,pad=0.45", facecolor="#1a1a2e",
                      edgecolor=DIM, alpha=0.90),
            family="monospace",
        )


    open_end_m   = 9 * 60 + 30 + open_window
    open_end_str = f"{open_end_m // 60:02d}:{open_end_m % 60:02d}"
    date_label   = chart_date.strftime("%b %d, %Y") if chart_date else ""
    title_suffix = f"   [{phase_label}]" if (earnings_events and phase_label) else ""
    ax_price.set_title(
        f"{ticker}  |  Dr. S Indicator  |  {date_label}  |  Open window 09:30-{open_end_str}  |  "
        f"{lookback}-session baseline{title_suffix}",
        color=TEXT, fontsize=11, pad=6, loc="left",
    )
    ax_price.legend(loc="upper left", facecolor=PANEL, edgecolor=DIM,
                    labelcolor=TEXT, fontsize=7, framealpha=0.8)
    plt.setp(ax_price.get_xticklabels(), visible=False)

    # ── Panel 2: Volume bars ─────────────────────────────────────────────────
    bar_colors = []
    for _, row in df_analysis.iterrows():
        if row.get("outlier", False):
            bar_colors.append(YELLOW)
        elif pd.notna(row.get("mean_vol")) and row["volume"] >= row["mean_vol"]:
            bar_colors.append(GREEN)
        else:
            bar_colors.append(DIM)

    ax_vol.bar(x, df_analysis["volume"].values, color=bar_colors, width=0.8, zorder=2)

    if df_analysis["mean_vol"].notna().any():
        ax_vol.plot(x, df_analysis["mean_vol"].values, color=TEXT, linewidth=1.0,
                    linestyle="--", alpha=0.55, label=f"{lookback}D slot avg", zorder=3)

    ax_vol.set_ylabel("Volume", fontsize=8)
    ax_vol.yaxis.set_major_formatter(mticker.FuncFormatter(_vol_formatter))
    ax_vol.legend(loc="upper left", facecolor=PANEL, edgecolor=DIM,
                  labelcolor=TEXT, fontsize=7, framealpha=0.8)

    # Earnings verticals
    if earnings_events:
        ts_list   = df_analysis.index.tolist()
        event_map = {e["date"].date(): e["phase_position"] for e in earnings_events}
        for i, ts in enumerate(ts_list):
            if ts.date() in event_map:
                for ax in (ax_price, ax_vol):
                    ax.axvline(i, color=YELLOW, linestyle=":", linewidth=0.9, alpha=0.7)
                ax_price.text(i, ax_price.get_ylim()[1],
                              f"P{event_map[ts.date()]}",
                              color=YELLOW, fontsize=7, va="top", ha="left")

    # ── X-axis ticks: HH:MM every 5 minutes ─────────────────────────────────
    tick_idx, tick_lbl = [], []
    for i, ts in enumerate(df_analysis.index):
        if ts.minute % 5 == 0:
            tick_idx.append(i)
            tick_lbl.append(ts.strftime("%H:%M"))
    ax_vol.set_xticks(tick_idx)
    ax_vol.set_xticklabels(tick_lbl, fontsize=7)

    # ── Save ─────────────────────────────────────────────────────────────────
    os.makedirs(OUT_DIR, exist_ok=True)
    ds       = (chart_date or datetime.date.today()).strftime("%Y%m%d")
    out_path = os.path.join(OUT_DIR,
                            f"{ticker.lower()}_1m_open{open_window}_{ds}.png")
    plt.savefig(out_path, dpi=130, bbox_inches="tight", facecolor=BG)
    print(f"Chart saved : {out_path}")
    plt.show()


# ── Summary ───────────────────────────────────────────────────────────────────

def print_summary(ticker, df, hv_range, today_range, range_z, lookback, outlier_sd, open_window):
    open_end_m  = 9 * 60 + 30 + open_window
    open_end    = f"{open_end_m // 60:02d}:{open_end_m % 60:02d}"
    outlier_cnt = int(df["outlier"].sum())
    ratio       = today_range / hv_range if (not np.isnan(hv_range) and hv_range > 0) else float("nan")
    range_z_str = f"{range_z:+.2f}" if not np.isnan(range_z) else "n/a"

    print(f"\n{'-'*56}")
    print(f"  {ticker}  |  1m  |  {lookback}-session baseline  |  open: {open_window}m")
    print(f"{'-'*56}")
    print(f"  Opening window         : 09:30 - {open_end}")
    print(f"  Sessions in baseline   : {lookback}")
    print(f"  14D Avg Range ({open_window}m)  : ${hv_range:.2f}")
    print(f"  Today's opening range  : ${today_range:.2f}  ({ratio:.2f}x)")
    print(f"  Range z-score          : {range_z_str}")
    print(f"  Vol outlier bars       : {outlier_cnt}")
    print(f"{'-'*56}\n")


# ── Main ──────────────────────────────────────────────────────────────────────

def parse_args():
    p = argparse.ArgumentParser(
        description="Dr. S Indicator — Opening-Window Volume + Range"
    )
    p.add_argument("--ticker",      default=TICKER)
    p.add_argument("--lookback",    type=int, default=LOOKBACK)
    p.add_argument("--open-window", type=int, default=OPEN_WINDOW, dest="open_window",
                   help=f"Minutes from 9:30 to evaluate (default: {OPEN_WINDOW})")
    p.add_argument("--date",        default=None,
                   help="Analysis date YYYY-MM-DD (default: today)")
    p.add_argument("--no-chart",    action="store_true")
    return p.parse_args()


def main():
    args        = parse_args()
    ticker      = args.ticker.upper()
    lookback    = args.lookback
    open_window = args.open_window
    as_of       = datetime.date.fromisoformat(args.date) if args.date else None

    # 1. Fetch (opening window only)
    df = fetch_intraday(ticker, lookback, as_of_date=as_of, open_window=open_window)

    # 2. Slot IDs
    df = assign_slot_id(df)

    # 3. Baseline
    slot_baseline, hv_range, hv_range_std = compute_baseline(df, lookback)

    # 4. Isolate analysis date and compute indicators
    unique_dates  = sorted(df["date"].unique())
    analysis_date = as_of or unique_dates[-1]
    day_mask      = np.array([d == analysis_date for d in df["date"]])

    if not day_mask.any():
        raise RuntimeError(f"No bars found for {analysis_date}.")

    df_analysis, today_range, range_z = compute_indicators(
        df[day_mask], slot_baseline, OUTLIER_SD, hv_range, hv_range_std
    )

    # 5. Earnings overlay (optional)
    earnings_events = None
    if EARNINGS_MODE:
        earnings_events = fetch_earnings_dates(ticker, ANCHOR_EARNINGS_DATE)
        if not earnings_events:
            print("  WARNING: No earnings dates found — earnings overlay skipped.")

    # 6. CSV cache
    os.makedirs(OUT_DIR, exist_ok=True)
    date_str = analysis_date.strftime("%Y%m%d")
    csv_path = os.path.join(
        OUT_DIR, f"{ticker.lower()}_1m_open{open_window}_{date_str}.csv"
    )
    df_analysis.to_csv(csv_path)
    print(f"Data cached : {csv_path}")

    # 7. Summary
    print_summary(ticker, df_analysis, hv_range, today_range, range_z, lookback, OUTLIER_SD, open_window)

    # 8. Chart
    if not args.no_chart:
        build_chart(ticker, df_analysis, hv_range, today_range, lookback, OUTLIER_SD,
                    open_window, chart_date=analysis_date,
                    earnings_events=earnings_events, phase_label=PHASE_LABEL)


if __name__ == "__main__":
    main()
