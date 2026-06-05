#!/usr/bin/env python
# coding: utf-8
"""
fetch_volume_mtf.py
-------------------
Multi-timeframe 14-day normalized volume indicator.

Fetches 1m bars ONCE, resamples to 1m / 5m / 15m / 30m, builds a
14-session slot baseline for each timeframe, and draws everything on
one chart for a single session.

Chart layout (top to bottom):
  [1] Candlesticks (1m) + VWAP
  [2] Volume bars (1m, color-coded by z-score) + 14D slot avg
  [3] Z-score — 1m
  [4] Z-score — 5m
  [5] Z-score — 15m
  [6] Z-score — 30m

Color coding (volume bars and z-score zones):
  YELLOW = spike — |z-score| >= 2 (unusually high OR low vs. same time of day)
  GREEN  = above the 14D slot average (but not extreme)
  GRAY   = below the 14D slot average

Usage:
    python tools/fetch_volume_mtf.py --ticker MU --date 2026-03-30
    python tools/fetch_volume_mtf.py --ticker NVDA
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
import matplotlib.patches as mpatches
import matplotlib.ticker as mticker

warnings.filterwarnings("ignore")

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, "C:/Users/Trader/quant-project")

from tools.fetch_polygon import fetch_bars

# ── Config ──────────────────────────────────────────────────────────────────
TICKER     = "NVDA"
LOOKBACK   = 14
OUTLIER_SD = 2.0
TIMEFRAMES = [1, 5, 15, 30]   # all four — fetched from 1m via resample

# ── Colors ───────────────────────────────────────────────────────────────────
BG     = "#0d0d1a"
PANEL  = "#131722"
TEXT   = "#c8c8d4"
GREEN  = "#26a69a"
RED    = "#ef5350"
BLUE   = "#4e9af1"
YELLOW = "#f1c40f"
DIM    = "#3a3a55"
PURPLE = "#9b59b6"

RTH_START = "09:30"
RTH_END   = "16:00"
OUT_DIR   = os.path.join(os.path.dirname(__file__), "..", ".tmp")


# ── Data ─────────────────────────────────────────────────────────────────────

def fetch_1m(ticker, lookback, as_of):
    """Fetch raw 1m bars for the full baseline window, RTH only, NY tz."""
    anchor  = as_of or datetime.date.today()
    from_dt = (anchor - datetime.timedelta(days=int(lookback * 1.7) + 5)).strftime("%Y-%m-%d")
    to_dt   = anchor.strftime("%Y-%m-%d")
    print(f"Fetching {ticker} 1m bars ({from_dt} to {to_dt})...")
    df = fetch_bars(ticker, "minute", from_dt, to_dt, multiplier=1)
    if df.empty:
        raise RuntimeError(f"No data for {ticker}.")
    df.index = df.index.tz_localize("UTC").tz_convert("America/New_York")
    df = df.between_time(RTH_START, RTH_END)
    if df.empty:
        raise RuntimeError(f"No RTH bars for {ticker}.")
    return df


def resample_ohlcv(df_1m, tf_minutes):
    """Resample 1m OHLCV bars to tf_minutes resolution."""
    if tf_minutes == 1:
        return df_1m.copy()
    rule = f"{tf_minutes}min"
    agg  = {
        "open":         "first",
        "high":         "max",
        "low":          "min",
        "close":        "last",
        "volume":       "sum",
        "transactions": "sum",
    }
    if "vwap" in df_1m.columns:
        agg["vwap"] = "mean"
    df = df_1m.resample(rule, closed="left", label="left").agg(agg)
    df = df.dropna(subset=["close"])
    df = df.between_time(RTH_START, RTH_END)
    return df


def assign_slot_id(df, tf_minutes):
    open_min = 9 * 60 + 30
    bar_min  = df.index.hour * 60 + df.index.minute
    df = df.copy()
    df["slot_id"] = ((bar_min - open_min) // tf_minutes).astype("int64")
    df["date"]    = np.array(df.index.date)
    return df


def build_baseline(df, lookback):
    dates     = sorted(df["date"].unique())
    if len(dates) < 2:
        raise RuntimeError("Not enough sessions for a baseline.")
    hist_dates = dates[-(lookback + 1):-1]
    hist = df[df["date"].isin(hist_dates)]
    bl   = (
        hist.groupby("slot_id")["volume"]
        .agg(mean_vol="mean", std_vol="std")
        .reset_index()
    )
    bl["std_vol"] = bl["std_vol"].replace(0, np.nan)
    return bl


def add_indicators(df, baseline):
    df = df.reset_index()
    df = df.merge(baseline, on="slot_id", how="left")
    df = df.set_index("timestamp")
    df["rel_vol"] = df["volume"] / df["mean_vol"]
    df["z_score"] = (df["volume"] - df["mean_vol"]) / df["std_vol"]
    df["outlier"] = df["z_score"].abs() >= OUTLIER_SD
    return df


def prepare_tf(df_1m, tf_minutes, lookback):
    """Full pipeline for one timeframe: resample → slot IDs → baseline → indicators."""
    df = resample_ohlcv(df_1m, tf_minutes)
    df = assign_slot_id(df, tf_minutes)
    df = add_indicators(df, build_baseline(df, lookback))
    return df


# ── Helpers ───────────────────────────────────────────────────────────────────

def _minutes_x(ts_index):
    """Convert timestamps to minutes-since-open (for shared x-axis)."""
    return np.array([(ts.hour * 60 + ts.minute) - 570 for ts in ts_index])


def _vol_fmt(v, _):
    if v >= 1_000_000:
        return f"{v/1e6:.1f}M"
    if v >= 1_000:
        return f"{v/1e3:.0f}K"
    return str(int(v))


def _note(ax, text, loc="upper left"):
    """Add an explanatory text bubble (note box) to an axis."""
    anchors = {
        "upper left":  (0.01, 0.97, "top",    "left"),
        "upper right": (0.99, 0.97, "top",    "right"),
        "lower left":  (0.01, 0.03, "bottom", "left"),
    }
    x, y, va, ha = anchors.get(loc, anchors["upper left"])
    ax.text(x, y, text,
            transform=ax.transAxes, va=va, ha=ha,
            color=TEXT, fontsize=6.5, linespacing=1.4,
            bbox=dict(boxstyle="round,pad=0.35", facecolor="#1a1a2e",
                      edgecolor=DIM, alpha=0.85))


def _annotate_peaks(ax, x_vals, z_vals, threshold, n=3):
    """Label the top-N outlier bars with their z-score value."""
    abs_z   = np.abs(z_vals)
    indices = np.where(abs_z >= threshold)[0]
    if len(indices) == 0:
        return
    top     = sorted(indices, key=lambda i: abs_z[i], reverse=True)[:n]
    for i in top:
        xi, zi = x_vals[i], z_vals[i]
        offset_y = 0.35 if zi >= 0 else -0.35
        ax.annotate(
            f"z={zi:+.1f}",
            xy=(xi, zi),
            xytext=(xi, zi + offset_y * 2.5),
            color=YELLOW, fontsize=6.5, ha="center", va="center",
            arrowprops=dict(arrowstyle="-", color=YELLOW, lw=0.5),
        )


# ── Chart ─────────────────────────────────────────────────────────────────────

def build_mtf_chart(ticker, tf_data, chart_date, as_of_date):
    """
    tf_data : dict  { tf_minutes : full_df_with_indicators }
    chart_date : datetime.date — which session to display
    """
    matplotlib.rcParams.update({
        "text.color":      TEXT,
        "axes.labelcolor": TEXT,
        "xtick.color":     TEXT,
        "ytick.color":     TEXT,
        "font.size":       9,
    })

    n_panels    = 2 + len(TIMEFRAMES)   # candles + vol + one per TF
    h_ratios    = [3.5, 1.5] + [1.0] * len(TIMEFRAMES)

    fig = plt.figure(figsize=(18, 14), facecolor=BG)
    gs  = gridspec.GridSpec(n_panels, 1, height_ratios=h_ratios, hspace=0.06)
    axes = [fig.add_subplot(gs[0])]
    for i in range(1, n_panels):
        axes.append(fig.add_subplot(gs[i], sharex=axes[0]))

    for ax in axes:
        ax.set_facecolor(PANEL)
        for spine in ax.spines.values():
            spine.set_edgecolor(DIM)
        ax.grid(axis="y", color=DIM, linewidth=0.4, alpha=0.45)
        ax.tick_params(axis="both", length=3, color=DIM)
        plt.setp(ax.get_xticklabels(), visible=False)

    ax_candle = axes[0]
    ax_vol    = axes[1]
    ax_z      = {tf: axes[2 + i] for i, tf in enumerate(TIMEFRAMES)}

    # ── Filter to chart_date ─────────────────────────────────────────────────
    def day_slice(df):
        mask = np.array([ts.date() for ts in df.index]) == chart_date
        return df[mask]

    df_1m_day = day_slice(tf_data[1])
    if df_1m_day.empty:
        print(f"No 1m bars for {chart_date}.")
        return

    x_1m = _minutes_x(df_1m_day.index)   # x-axis in minutes-since-open

    # ── Panel 0: Candlesticks + VWAP ────────────────────────────────────────
    for i, (_, row) in enumerate(df_1m_day.iterrows()):
        up    = row["close"] >= row["open"]
        color = GREEN if up else RED
        lo    = min(row["open"], row["close"])
        hi    = max(row["open"], row["close"])
        body  = max(hi - lo, row["close"] * 0.0005)
        ax_candle.add_patch(mpatches.Rectangle(
            (x_1m[i] - 0.4, lo), 0.8, body, color=color, zorder=2
        ))
        ax_candle.plot([x_1m[i], x_1m[i]], [row["low"], lo],   color=color, lw=0.5, zorder=1)
        ax_candle.plot([x_1m[i], x_1m[i]], [hi, row["high"]], color=color, lw=0.5, zorder=1)

    typ  = (df_1m_day["high"] + df_1m_day["low"] + df_1m_day["close"]) / 3
    vwap = (typ * df_1m_day["volume"]).cumsum() / df_1m_day["volume"].cumsum()
    ax_candle.plot(x_1m, vwap.values, color=PURPLE, linewidth=1.3,
                   linestyle="--", alpha=0.9, label="VWAP", zorder=3)

    pad = (df_1m_day["high"].max() - df_1m_day["low"].min()) * 0.03
    ax_candle.set_ylim(df_1m_day["low"].min() - pad, df_1m_day["high"].max() + pad)
    ax_candle.set_ylabel("Price", fontsize=8)
    ax_candle.set_title(
        f"{ticker}  |  {chart_date.strftime('%b %d, %Y')}  |  "
        f"14-Day Normalized Volume  (baseline: {LOOKBACK} sessions, outlier threshold: +/-{OUTLIER_SD}sd)",
        color=TEXT, fontsize=11, pad=6, loc="left"
    )
    ax_candle.legend(loc="upper left", facecolor=PANEL, edgecolor=DIM,
                     labelcolor=TEXT, fontsize=7, framealpha=0.8)
    _note(ax_candle,
          "Candlestick colors:\n"
          "  Green  = up bar  (close >= open)\n"
          "  Red    = down bar\n"
          "  Purple = VWAP (Volume-Weighted Avg Price)",
          loc="upper right")

    # ── Panel 1: 1m Volume bars (colored by z-score) ─────────────────────────
    for i, (_, row) in enumerate(df_1m_day.iterrows()):
        if row.get("outlier", False):
            c = YELLOW
        elif pd.notna(row.get("mean_vol")) and row["volume"] >= row["mean_vol"]:
            c = GREEN
        else:
            c = DIM
        ax_vol.bar(x_1m[i], row["volume"], color=c, width=0.8, zorder=2)

    if df_1m_day["mean_vol"].notna().any():
        ax_vol.plot(x_1m, df_1m_day["mean_vol"].values,
                    color=TEXT, linewidth=1.0, linestyle="--", alpha=0.6,
                    label="14D slot avg", zorder=3)
    ax_vol.set_ylabel("Vol (1m)", fontsize=7)
    ax_vol.yaxis.set_major_formatter(mticker.FuncFormatter(_vol_fmt))
    ax_vol.legend(loc="upper left", facecolor=PANEL, edgecolor=DIM,
                  labelcolor=TEXT, fontsize=6.5, framealpha=0.8)
    _note(ax_vol,
          "Volume bar colors:\n"
          "  YELLOW = spike  (z-score >= 2sd or <= -2sd)\n"
          "           Volume is unusually high or low vs.\n"
          "           the same minute over the last 14 sessions\n"
          "  GREEN  = above the 14-day slot average\n"
          "  GRAY   = below the 14-day slot average\n"
          "  Dashed = 14-day average for each slot",
          loc="upper right")

    # ── Panels 2-5: Z-score per timeframe ────────────────────────────────────
    tf_colors = {1: BLUE, 5: GREEN, 15: "#ff9800", 30: "#e040fb"}

    for tf in TIMEFRAMES:
        ax = ax_z[tf]
        df_tf_day = day_slice(tf_data[tf])
        if df_tf_day.empty:
            ax.set_ylabel(f"Z {tf}m", fontsize=7)
            continue

        x_tf = _minutes_x(df_tf_day.index)
        z    = df_tf_day["z_score"].fillna(0).values
        col  = tf_colors[tf]

        # Bars colored by outlier, line on top
        bar_c = [YELLOW if abs(zi) >= OUTLIER_SD else DIM for zi in z]
        ax.bar(x_tf, z, color=bar_c, width=tf * 0.85, zorder=1, alpha=0.5)
        ax.plot(x_tf, z, color=col, linewidth=1.1, zorder=2, label=f"{tf}m z-score")

        # Threshold lines
        ax.axhline( OUTLIER_SD, color=YELLOW, linestyle="--", linewidth=0.7, alpha=0.7)
        ax.axhline(-OUTLIER_SD, color=YELLOW, linestyle="--", linewidth=0.7, alpha=0.7)
        ax.axhline(0, color=TEXT, linestyle="-", linewidth=0.4, alpha=0.2)

        # Fill outlier zones
        ax.fill_between(x_tf,  OUTLIER_SD, z, where=(z >=  OUTLIER_SD),
                        color=YELLOW, alpha=0.12, zorder=0)
        ax.fill_between(x_tf, -OUTLIER_SD, z, where=(z <= -OUTLIER_SD),
                        color=RED,    alpha=0.12, zorder=0)

        # Annotate ±2sd threshold lines at right edge
        x_right = x_tf[-1] if len(x_tf) > 0 else 389
        ax.text(x_right + 1, OUTLIER_SD,  f"+{OUTLIER_SD}sd",
                color=YELLOW, fontsize=5.5, va="bottom", ha="left", clip_on=True)
        ax.text(x_right + 1, -OUTLIER_SD, f"-{OUTLIER_SD}sd",
                color=YELLOW, fontsize=5.5, va="top",    ha="left", clip_on=True)

        # Label peak outlier bars
        _annotate_peaks(ax, x_tf, z, OUTLIER_SD, n=2)

        ax.set_ylabel(f"Z  {tf}m", fontsize=7)
        ax.legend(loc="upper left", facecolor=PANEL, edgecolor=DIM,
                  labelcolor=TEXT, fontsize=6.5, framealpha=0.8)

        # Note bubble on the first z-score panel only (to avoid repetition)
        if tf == TIMEFRAMES[0]:
            _note(ax,
                  "Z-score = how unusual this bar's volume is\n"
                  "          vs. the same time-of-day over\n"
                  "          the last 14 sessions.\n"
                  "  z > +2  = unusually HIGH volume\n"
                  "  z < -2  = unusually LOW volume\n"
                  "  Yellow fill = outlier zone",
                  loc="upper right")

    # ── X-axis ticks: time of day ─────────────────────────────────────────────
    tick_min  = list(range(0, 390, 30))                        # every 30 min
    tick_lbl  = [f"{9 + (m + 30) // 60}:{(m + 30) % 60:02d}"
                 for m in tick_min]
    # Simpler: just map 0→9:30, 30→10:00, 60→10:30 ...
    def fmt_min(m):
        total = 570 + m
        return f"{total // 60}:{total % 60:02d}"
    tick_lbl = [fmt_min(m) for m in tick_min]

    bottom_ax = axes[-1]
    plt.setp(bottom_ax.get_xticklabels(), visible=True)
    bottom_ax.set_xticks(tick_min)
    bottom_ax.set_xticklabels(tick_lbl, fontsize=7)
    bottom_ax.set_xlabel("Time (NY)", fontsize=8)
    axes[0].set_xlim(-2, 392)

    # ── Save ─────────────────────────────────────────────────────────────────
    os.makedirs(OUT_DIR, exist_ok=True)
    ds       = chart_date.strftime("%Y%m%d")
    out_path = os.path.join(OUT_DIR, f"{ticker.lower()}_mtf_volume_{ds}.png")
    plt.savefig(out_path, dpi=130, bbox_inches="tight", facecolor=BG)
    print(f"Chart saved : {out_path}")
    plt.show()


# ── Summary ───────────────────────────────────────────────────────────────────

def print_mtf_summary(ticker, tf_data, chart_date):
    print(f"\n{'-'*60}")
    print(f"  {ticker}  |  {chart_date}  |  MTF Volume Summary")
    print(f"  Baseline: {LOOKBACK} sessions  |  Outlier: |z| >= {OUTLIER_SD}")
    print(f"{'-'*60}")
    print(f"  {'TF':<6}  {'Outlier bars':<14}  {'Max |z|':<10}  {'Latest z':<10}")
    print(f"  {'-'*50}")
    for tf in TIMEFRAMES:
        df  = tf_data[tf]
        mask = np.array([ts.date() for ts in df.index]) == chart_date
        day  = df[mask]
        if day.empty:
            print(f"  {tf}m      no data")
            continue
        out_cnt = int(day["outlier"].sum())
        max_z   = day["z_score"].abs().max()
        last_z  = day["z_score"].iloc[-1]
        print(f"  {tf}m     {out_cnt:<14}  {max_z:<10.2f}  {last_z:+.2f}")
    print(f"{'-'*60}\n")


# ── Main ─────────────────────────────────────────────────────────────────────

def parse_args():
    p = argparse.ArgumentParser(description="MTF Normalized Volume Indicator")
    p.add_argument("--ticker",   default=TICKER)
    p.add_argument("--lookback", type=int, default=LOOKBACK)
    p.add_argument("--date",     default=None,
                   help="Analysis date YYYY-MM-DD (default: today)")
    p.add_argument("--no-chart", action="store_true")
    return p.parse_args()


def main():
    args    = parse_args()
    ticker  = args.ticker.upper()
    lookback = args.lookback
    as_of   = datetime.date.fromisoformat(args.date) if args.date else None
    chart_date = as_of or datetime.date.today()

    # 1. Fetch 1m once
    df_1m = fetch_1m(ticker, lookback, as_of)

    # 2. Build each timeframe
    tf_data = {}
    for tf in TIMEFRAMES:
        print(f"  Computing {tf}m baseline + indicators...")
        tf_data[tf] = prepare_tf(df_1m, tf, lookback)

    # 3. Summary
    print_mtf_summary(ticker, tf_data, chart_date)

    # 4. Chart
    if not args.no_chart:
        build_mtf_chart(ticker, tf_data, chart_date, as_of)


if __name__ == "__main__":
    main()
