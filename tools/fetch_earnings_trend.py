#!/usr/bin/env python
# coding: utf-8
"""
fetch_earnings_trend.py
-----------------------
Earnings trend, acceleration, deceleration & maturation cycle model.

Chart layout:
  Top panel    : Daily candlestick + 50-SMA + fiscal quarter brackets (Q1-Q4)
                 Breakout year highlighted if detected
  Bottom panel : YoY EPS% bars + 2Q rolling avg line (shared date axis)

Console output: compact summary table only

Usage:
    python tools/fetch_earnings_trend.py --ticker RBLX
    python tools/fetch_earnings_trend.py --ticker AAPL --no-chart
"""

import os
import sys
import argparse
import datetime
import requests
import pandas as pd
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.dates as mdates
from dotenv import load_dotenv

sys.path.insert(0, os.path.dirname(__file__))
from fetch_polygon import fetch_bars

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', '.env'))

API_KEY  = os.getenv("POLYGON_API_KEY")
BASE_URL = "https://api.polygon.io"

# Colors
BG    = "#0d0d1a"
PANEL = "#131722"
TEXT  = "#c8c8d4"
GREEN = "#26a69a"
RED   = "#ef5350"
BLUE  = "#4e9af1"
YELLOW = "#f1c40f"
DIM   = "#3a3a55"


# ── Fundamentals Fetch ────────────────────────────────────────────────────────

def fetch_quarterly_financials(ticker, limit=20):
    if not API_KEY:
        raise ValueError("POLYGON_API_KEY not found in .env")
    url = f"{BASE_URL}/vX/reference/financials"
    params = {
        "ticker":    ticker.upper(),
        "timeframe": "quarterly",
        "limit":     limit,
        "sort":      "period_of_report_date",
        "order":     "desc",
        "apiKey":    API_KEY,
    }
    resp = requests.get(url, params=params)
    data = resp.json()
    if resp.status_code == 403 or data.get("status") == "NOT_AUTHORIZED":
        raise PermissionError(
            "Polygon tier does not support /vX/reference/financials. "
            "Run tools/test_polygon_earnings.py to verify access."
        )
    if data.get("status") == "ERROR":
        raise RuntimeError(f"Polygon API error: {data.get('error', data)}")
    results = data.get("results", [])
    return list(reversed(results))  # oldest first


def parse_financials(results):
    rows = []
    for r in results:
        inc = r.get("financials", {}).get("income_statement", {})
        rows.append({
            "start_date":       r.get("start_date"),
            "fiscalDateEnding": r.get("end_date") or r.get("period_of_report_date"),
            "fiscal_period":    r.get("fiscal_period", ""),   # Q1, Q2, Q3, Q4
            "fiscal_year":      r.get("fiscal_year", ""),
            "reportedEPS":      (inc.get("basic_earnings_per_share") or {}).get("value"),
            "totalRevenue":     (inc.get("revenues") or {}).get("value"),
            "netIncome":        (inc.get("net_income_loss") or {}).get("value"),
        })
    df = pd.DataFrame(rows)
    df["fiscalDateEnding"] = pd.to_datetime(df["fiscalDateEnding"])
    df["start_date"]       = pd.to_datetime(df["start_date"])
    df["reportedEPS"]  = pd.to_numeric(df["reportedEPS"],  errors="coerce")
    df["totalRevenue"] = pd.to_numeric(df["totalRevenue"], errors="coerce")
    df["netIncome"]    = pd.to_numeric(df["netIncome"],    errors="coerce")
    df = df.sort_values("fiscalDateEnding").reset_index(drop=True)
    return df.tail(12).reset_index(drop=True)


# ── Model Metrics ─────────────────────────────────────────────────────────────

def compute_metrics(df):
    df = df.copy()
    df["YoY_EPS_%"]    = (df["reportedEPS"]  / df["reportedEPS"].shift(4)  - 1) * 100
    df["YoY_Sales_%"]  = (df["totalRevenue"] / df["totalRevenue"].shift(4) - 1) * 100
    df["NetMargin_%"]  = (df["netIncome"]     / df["totalRevenue"])               * 100
    df["EPS_2Q_Avg"]   = df["YoY_EPS_%"].rolling(2).mean()
    df["Sales_2Q_Avg"] = df["YoY_Sales_%"].rolling(2).mean()
    df["EPS_Accel"]    = df["YoY_EPS_%"].diff() > 0
    df["EPS_Decel"]    = df["YoY_EPS_%"].diff() < 0
    df["EPS_20pct+"]   = df["YoY_EPS_%"] >= 20

    streak = 0
    streaks = []
    for flag in df["EPS_20pct+"]:
        streak = streak + 1 if flag else 0
        streaks.append(streak)
    df["EPS_Streak"] = streaks
    df["q_label"]    = df["fiscal_period"] + " " + df["fiscal_year"].astype(str).str[-2:]
    return df


def classify_cycle_stage(df):
    valid = df.dropna(subset=["YoY_EPS_%"])
    if valid.empty:
        return "UNKNOWN", "Insufficient data"
    latest = valid.iloc[-1]
    streak = int(latest["EPS_Streak"])
    yoy    = latest["YoY_EPS_%"]
    accel  = bool(latest["EPS_Accel"])
    decel  = bool(latest["EPS_Decel"])
    decel_2q = len(valid) >= 2 and bool(valid.iloc[-2]["EPS_Decel"]) and decel

    if yoy < 0:
        return "WEAK", f"Negative EPS growth ({yoy:.1f}%)"
    prior_low = len(valid) >= 3 and valid.iloc[-3]["EPS_2Q_Avg"] < 20
    if yoy >= 100 and (prior_low or streak <= 1):
        return "TURNAROUND", f"Explosion from low base ({yoy:.1f}%)"
    if streak >= 3 and decel_2q:
        return "DECEL_ONSET", f"{streak}Q streak, decelerating 2Q"
    if streak >= 2 and decel:
        return "DECEL_ONSET", f"{streak}Q streak, YoY declining"
    if streak >= 3:
        return "PEAK_ACCEL", f"{streak}Q of 20%+ EPS growth"
    if streak in (1, 2) and accel:
        return "EARLY_ACCEL", f"Early {streak}Q streak, accelerating"
    if streak == 0 and yoy >= 20:
        return "EARLY_ACCEL", f"Strong growth, streak restarting"
    return "MATURING", f"Sub-20% or streak broken ({yoy:.1f}%)"


def check_breakout_year(df_full):
    """Returns (bool, year_str_or_None). True if trailing 4Q EPS > prior 4yr high."""
    df = df_full.dropna(subset=["reportedEPS"]).copy()
    df = df.sort_values("fiscalDateEnding").reset_index(drop=True)
    if len(df) < 8:
        return False, None
    df["trailing_4Q"] = df["reportedEPS"].rolling(4).sum()
    df = df.dropna(subset=["trailing_4Q"])
    if len(df) < 5:
        return False, None
    current  = df.iloc[-1]["trailing_4Q"]
    prior_hi = df.iloc[:-4]["trailing_4Q"].max()
    if current > prior_hi:
        year = str(df.iloc[-1]["fiscal_year"])
        return True, year
    return False, None


# ── Charting ──────────────────────────────────────────────────────────────────

def draw_candles(ax, bars):
    for i, (_, row) in enumerate(bars.iterrows()):
        color = GREEN if row["close"] >= row["open"] else RED
        body_lo = min(row["open"], row["close"])
        body_hi = max(row["open"], row["close"])
        body_h  = max(body_hi - body_lo, row["close"] * 0.001)
        ax.add_patch(mpatches.Rectangle(
            (i - 0.35, body_lo), 0.7, body_h,
            color=color, zorder=2
        ))
        ax.plot([i, i], [row["low"],  body_lo], color=color, linewidth=0.7, zorder=1)
        ax.plot([i, i], [body_hi, row["high"]], color=color, linewidth=0.7, zorder=1)


def add_sma(ax, bars, window, color, label, lw=1.0):
    sma = bars["close"].rolling(window).mean()
    ax.plot(range(len(bars)), sma.values, color=color, linewidth=lw,
            label=label, zorder=3, alpha=0.85)


def add_quarter_brackets(ax_price, ax_eps, bars, df, is_breakout, breakout_year):
    """
    Shade each fiscal quarter on price chart with Q1-Q4 label.
    Highlight breakout year in a distinct color.
    Draw EPS% bars on the eps panel aligned to the same x positions.
    """
    bar_dates = pd.DatetimeIndex([pd.Timestamp(d.date()) for d in bars.index])

    # Quarter colors: alternating subtle bands
    q_colors = ["#1e2235", "#1e2820"]
    breakout_color = "#2a1f0a"  # warm highlight for breakout year

    eps_x      = []
    eps_y      = []
    avg_x      = []
    avg_y      = []
    eps_colors = []

    for _, row in df.iterrows():
        q_end   = row["fiscalDateEnding"]
        q_start = row["start_date"] if pd.notna(row["start_date"]) else q_end - pd.DateOffset(months=3)
        label   = row["q_label"]  # e.g. "Q1 24"
        fy      = str(row["fiscal_year"])

        # Find bar index positions
        i_start = int(bar_dates.searchsorted(pd.Timestamp(q_start.date())))
        i_end   = int(bar_dates.searchsorted(pd.Timestamp(q_end.date()), side="right")) - 1
        i_end   = min(i_end, len(bars) - 1)
        if i_start > len(bars) - 1:
            continue
        i_mid = (i_start + i_end) / 2

        # Choose band color
        use_color = breakout_color if (is_breakout and fy == str(breakout_year)) else q_colors[_ % 2]
        ax_price.axvspan(i_start, i_end + 1, alpha=0.18, color=use_color, zorder=0)

        # Q label at top of price panel
        y_top = ax_price.get_ylim()[1] if ax_price.get_ylim()[1] != 1.0 else bars["high"].max()
        ax_price.text(
            i_mid, 0, label,
            transform=ax_price.get_xaxis_transform(),
            ha="center", va="bottom", fontsize=6.5, color=TEXT,
            alpha=0.7, clip_on=True
        )

        # Breakout year annotation
        if is_breakout and fy == str(breakout_year) and i_start <= len(bars) - 1:
            ax_price.annotate(
                "Breakout Yr",
                xy=(i_mid, bars["high"].max()),
                xytext=(i_mid, bars["high"].max() * 1.01),
                ha="center", fontsize=7, color=YELLOW,
                arrowprops=dict(arrowstyle="-", color=YELLOW, lw=0.8),
            )

        # Collect EPS data for this quarter
        yoy = row["YoY_EPS_%"]
        avg = row["EPS_2Q_Avg"]
        if pd.notna(yoy):
            eps_x.append(i_mid)
            eps_y.append(yoy)
            eps_colors.append(GREEN if yoy >= 0 else RED)
        if pd.notna(avg):
            avg_x.append(i_mid)
            avg_y.append(avg)

    # YoY EPS% line
    if len(eps_x) >= 2:
        ax_eps.plot(eps_x, eps_y, color=BLUE, linewidth=1.5,
                    marker="o", markersize=4, linestyle="--", label="YoY EPS%", zorder=2)

    # 2Q rolling avg line
    if len(avg_x) >= 2:
        ax_eps.plot(avg_x, avg_y, color=YELLOW, linewidth=2.0,
                    marker="o", markersize=4, label="2Q Avg", zorder=3)

    ax_eps.axhline(20,  color=RED,  linestyle="--", linewidth=0.8, alpha=0.6)
    ax_eps.axhline(0,   color=TEXT, linestyle="-",  linewidth=0.5, alpha=0.25)


def build_chart(ticker, bars, df, stage, stage_desc, is_breakout, breakout_year):
    matplotlib.rcParams.update({
        "text.color":      TEXT,
        "axes.labelcolor": TEXT,
        "xtick.color":     TEXT,
        "ytick.color":     TEXT,
        "font.size":       9,
    })

    fig, (ax_p, ax_e) = plt.subplots(
        2, 1, figsize=(14, 9),
        gridspec_kw={"height_ratios": [3, 1]},
        facecolor=BG
    )
    for ax in (ax_p, ax_e):
        ax.set_facecolor(PANEL)
        for spine in ax.spines.values():
            spine.set_edgecolor(DIM)

    # ── Price panel
    draw_candles(ax_p, bars)
    add_sma(ax_p, bars, 50,  BLUE,   "50-SMA", lw=1.2)
    add_sma(ax_p, bars, 200, "#9b59b6", "200-SMA", lw=1.0)

    ax_p.set_xlim(-1, len(bars) + 1)
    ax_p.set_ylim(bars["low"].min() * 0.97, bars["high"].max() * 1.03)

    # x-tick labels: every ~30 bars
    tick_step = max(len(bars) // 8, 30)
    tick_idx  = list(range(0, len(bars), tick_step))
    tick_lbl  = [bars.index[i].strftime("%b '%y") for i in tick_idx]
    ax_p.set_xticks(tick_idx)
    ax_p.set_xticklabels(tick_lbl, fontsize=8)
    ax_p.set_ylabel("Price", fontsize=9)
    ax_p.legend(loc="upper left", facecolor=PANEL, edgecolor=DIM,
                labelcolor=TEXT, fontsize=8, framealpha=0.8)
    ax_p.set_title(
        f"{ticker} | {stage}  ({stage_desc})",
        color=TEXT, fontsize=11, pad=8, loc="left"
    )

    # ── Add brackets + EPS bars (after axes are set so ylim is known)
    add_quarter_brackets(ax_p, ax_e, bars, df, is_breakout, breakout_year)

    # ── EPS panel formatting
    ax_e.set_xlim(ax_p.get_xlim())
    ax_e.set_xticks(tick_idx)
    ax_e.set_xticklabels(tick_lbl, fontsize=8)
    ax_e.set_ylabel("YoY EPS %", fontsize=9)
    ax_e.legend(loc="upper left", facecolor=PANEL, edgecolor=DIM,
                labelcolor=TEXT, fontsize=8, framealpha=0.8)

    ax_e.legend(loc="upper left", facecolor=PANEL, edgecolor=DIM,
                labelcolor=TEXT, fontsize=8, framealpha=0.8)

    plt.tight_layout(h_pad=0.4)
    plt.show()


# ── Summary Table ─────────────────────────────────────────────────────────────

def print_summary(ticker, df, stage, stage_desc, is_breakout, breakout_year):
    valid = df.dropna(subset=["YoY_EPS_%"])
    if valid.empty:
        print("No EPS data.")
        return
    latest = valid.iloc[-1]
    yoy_e  = latest["YoY_EPS_%"]
    avg_e  = latest["EPS_2Q_Avg"]
    yoy_s  = latest["YoY_Sales_%"]
    margin = latest["NetMargin_%"]
    streak = int(latest["EPS_Streak"])
    bkout  = f"YES ({breakout_year})" if is_breakout else "No"

    hdr = f"  {'Metric':<20} {'Latest':>10}  {'2Q Avg':>10}  {'Streak':>8}"
    row_e = f"  {'YoY EPS %':<20} {yoy_e:>+9.1f}%  {avg_e:>+9.1f}%  {streak:>6}Q"
    row_s = f"  {'YoY Sales %':<20} {yoy_s:>+9.1f}%" if pd.notna(yoy_s) else f"  {'YoY Sales %':<20} {'N/A':>10}"
    row_m = f"  {'Net Margin %':<20} {margin:>+9.1f}%" if pd.notna(margin) else f"  {'Net Margin %':<20} {'N/A':>10}"
    row_b = f"  {'Breakout Year':<20} {bkout}"

    print(f"\n{'-'*55}")
    print(f"  {ticker}  |  Stage: {stage}")
    print(f"{'-'*55}")
    print(hdr)
    print(row_e)
    print(row_s)
    print(row_m)
    print(row_b)
    print(f"{'-'*55}\n")


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--ticker",   required=True)
    parser.add_argument("--no-chart", action="store_true")
    args = parser.parse_args()
    ticker = args.ticker.upper()

    print(f"Fetching data for {ticker}...")

    # Fundamentals
    try:
        results = fetch_quarterly_financials(ticker, limit=20)
    except (PermissionError, RuntimeError) as e:
        print(f"ERROR: {e}")
        sys.exit(1)

    if not results:
        print(f"No earnings data found for {ticker}.")
        sys.exit(0)

    df = parse_financials(results)
    df = compute_metrics(df)
    stage, stage_desc     = classify_cycle_stage(df)
    is_breakout, bk_year  = check_breakout_year(parse_financials(results))

    print_summary(ticker, df, stage, stage_desc, is_breakout, bk_year)

    if args.no_chart:
        return

    # Daily price bars (3 years to cover 12 quarters)
    to_dt   = datetime.date.today().strftime("%Y-%m-%d")
    from_dt = (datetime.date.today() - datetime.timedelta(days=3*365)).strftime("%Y-%m-%d")
    print(f"Fetching daily bars ({from_dt} to {to_dt})...")
    bars = fetch_bars(ticker, "day", from_dt, to_dt)

    if bars.empty:
        print("No price data returned.")
        return

    build_chart(ticker, bars, df, stage, stage_desc, is_breakout, bk_year)


if __name__ == "__main__":
    main()
