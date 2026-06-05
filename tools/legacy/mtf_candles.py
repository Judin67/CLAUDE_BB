#!/usr/bin/env python
"""
MTF Slope Indicator — Candlestick Charts
=========================================
Generates candlestick charts with 9/21-SMA overlaid and a slope
re-alignment indicator panel below (MACD-style visual).

Usage:
    python tools/mtf_candles.py

Config at top of file: TICKERS, TIMEFRAMES, DATE, SETUP_WINDOW.
Data cached to .tmp/ as CSV — skips re-fetch on reruns.
"""

import sys
import time
import pytz
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.gridspec as gridspec
from matplotlib.lines import Line2D
import warnings
warnings.filterwarnings('ignore')

sys.path.insert(0, 'C:/Users/Trader/Desktop/CLAUDE_BB')
sys.path.insert(0, 'C:/Users/Trader/quant-project')

from tools.fetch_polygon import fetch_bars
from src.indicators import sma, slope_set
from src.signals import detect_mtf_slope_signals, label_signal_bars

# ── Config ─────────────────────────────────────────────────────────────────
TICKERS      = ['SPY']
TIMEFRAMES   = ['1m']
DATE         = '2026-03-20'
SLOW_WIN     = 21
FAST_WIN     = 9
SETUP_WINDOW = 10                # bars to look back for pullback
SLOPE_FACTOR = 0.2               # slope lookback = round(window * factor)

NY_TZ   = pytz.timezone('America/New_York')
RTH_START = '09:30'
RTH_END   = '16:00'

OUT_DIR  = 'C:/Users/Trader/Desktop/CLAUDE_BB/.tmp'
RATE_SLEEP = 13

# Polygon fetch windows
FETCH_END  = DATE
FETCH_RANGES = {
    '1m':  (7,  'minute', 1),   # (days_back, timespan, multiplier)
    '5m':  (60, 'minute', 5),
}

# ── Colors ─────────────────────────────────────────────────────────────────
BG       = '#0d0d1a'
PANEL    = '#131722'
UP_COL   = '#26a69a'
DN_COL   = '#ef5350'
SLOW_COL = '#2962ff'   # blue  — 21-SMA
FAST_COL = '#ff9800'   # amber — 9-SMA
ZERO_COL = '#555566'

# ── Data fetch with cache ──────────────────────────────────────────────────
def _cache_path(ticker, tf):
    return f'{OUT_DIR}/{ticker.lower()}_{tf}_ohlcv_{DATE}.csv'

def load_ohlcv(ticker, tf):
    path = _cache_path(ticker, tf)
    try:
        df = pd.read_csv(path, index_col=0, parse_dates=True)
        print(f'  {ticker} {tf}: loaded from cache ({len(df)} bars)')
        return df
    except FileNotFoundError:
        return None

def fetch_and_cache(ticker, tf):
    days_back, timespan, mult = FETCH_RANGES[tf]
    from_date = (pd.Timestamp(DATE) - pd.Timedelta(days=days_back)).strftime('%Y-%m-%d')
    print(f'  {ticker} {tf}: fetching from Polygon...')
    df = fetch_bars(ticker, timespan, from_date, FETCH_END, multiplier=mult)
    df.to_csv(_cache_path(ticker, tf))
    return df

def get_data():
    needed = []
    data = {}
    for t in TICKERS:
        data[t] = {}
        for tf in TIMEFRAMES:
            df = load_ohlcv(t, tf)
            if df is not None:
                data[t][tf] = df
            else:
                needed.append((t, tf))

    for i, (t, tf) in enumerate(needed):
        if i > 0:
            print(f'  waiting {RATE_SLEEP}s (rate limit)...')
            time.sleep(RATE_SLEEP)
        df = fetch_and_cache(t, tf)
        data[t][tf] = df

    return data

# ── Slope computation ──────────────────────────────────────────────────────
def compute_slopes(close):
    """Return DataFrame with fast_slope, slow_slope on same index as close."""
    slow_ma  = sma(close, SLOW_WIN)
    fast_ma  = sma(close, FAST_WIN)

    lb_slow  = max(1, round(SLOW_WIN * SLOPE_FACTOR))
    lb_fast  = max(1, round(FAST_WIN * SLOPE_FACTOR))

    slow_slope = slow_ma - slow_ma.shift(lb_slow)
    fast_slope = fast_ma - fast_ma.shift(lb_fast)

    return pd.DataFrame({'fast_slope': fast_slope, 'slow_slope': slow_slope}), slow_ma, fast_ma

# ── NY time filter ─────────────────────────────────────────────────────────
def to_ny(df_or_series):
    """Convert UTC-naive index → NY-aware, then filter to RTH."""
    idx = df_or_series.index
    if idx.tz is None:
        idx = idx.tz_localize('UTC')
    idx = idx.tz_convert(NY_TZ)
    out = df_or_series.copy()
    out.index = idx
    return out

def filter_rth(df_or_series, date=DATE):
    obj = to_ny(df_or_series)
    start = f'{date} {RTH_START}'
    end   = f'{date} {RTH_END}'
    return obj.loc[start:end]

# ── Candlestick renderer ───────────────────────────────────────────────────
def draw_candles(ax, ohlcv, slow_ma, fast_ma, sig_df):
    """Top panel: candlesticks + MAs + signal markers."""
    if ohlcv.empty:
        ax.text(0.5, 0.5, 'No data', ha='center', va='center',
                color='white', transform=ax.transAxes)
        return

    xs     = np.arange(len(ohlcv))
    opens  = ohlcv['open'].values
    highs  = ohlcv['high'].values
    lows   = ohlcv['low'].values
    closes = ohlcv['close'].values
    hw     = 0.35

    price_range = highs.max() - lows.min()

    for i, (o, h, l, c) in enumerate(zip(opens, highs, lows, closes)):
        col = UP_COL if c >= o else DN_COL
        ax.plot([i, i], [l, h], color=col, linewidth=0.8, zorder=1)
        body_h = max(abs(c - o), price_range * 0.001)
        ax.add_patch(mpatches.Rectangle(
            (i - hw, min(o, c)), hw * 2, body_h,
            color=col, zorder=2, linewidth=0))

    # MAs
    slow_vals = slow_ma.values
    fast_vals = fast_ma.values
    ax.plot(xs, slow_vals, color=SLOW_COL, linewidth=1.4, zorder=3,
            label=f'{SLOW_WIN}-SMA (trend)')
    ax.plot(xs, fast_vals, color=FAST_COL, linewidth=1.0, zorder=3,
            label=f'{FAST_WIN}-SMA (momentum)')

    # Signal markers
    ts_list = ohlcv.index.tolist()
    offset  = price_range * 0.007

    for ts in sig_df.index[sig_df['signal_long']]:
        if ts in ts_list:
            i = ts_list.index(ts)
            ax.scatter(i, lows[i] - offset, marker='^', color='lime',
                       s=120, zorder=5, linewidths=0)

    for ts in sig_df.index[sig_df['signal_short']]:
        if ts in ts_list:
            i = ts_list.index(ts)
            ax.scatter(i, highs[i] + offset, marker='v', color='#ff4444',
                       s=120, zorder=5, linewidths=0)

    # X-axis ticks
    _apply_time_ticks(ax, ohlcv, xs)
    ax.set_facecolor(PANEL)
    ax.tick_params(colors='#888899', labelsize=7, length=3)
    ax.yaxis.set_tick_params(labelcolor='#888899')
    for spine in ax.spines.values():
        spine.set_edgecolor('#2a2a3e')
    ax.grid(axis='y', color='#1e1e2e', linewidth=0.5)
    ax.legend(loc='upper right', fontsize=7.5, facecolor='#1a1a2e',
              labelcolor='white', framealpha=0.85)

# ── Slope indicator renderer ───────────────────────────────────────────────
def draw_slope_indicator(ax, ohlcv, slope_df, sig_df):
    """Bottom panel: slow/fast slope lines + zero + signal dots."""
    xs      = np.arange(len(ohlcv))
    ts_list = ohlcv.index.tolist()

    # Align slope to RTH bars
    ss = slope_df['slow_slope'].reindex(ohlcv.index)
    fs = slope_df['fast_slope'].reindex(ohlcv.index)

    ax.plot(xs, ss.values, color=SLOW_COL, linewidth=1.4, label=f'{SLOW_WIN}-SMA slope')
    ax.plot(xs, fs.values, color=FAST_COL, linewidth=1.0, label=f'{FAST_WIN}-SMA slope')

    # Fill fast slope above/below zero
    ax.fill_between(xs, fs.values, 0,
                    where=(fs.values > 0), color=UP_COL, alpha=0.15)
    ax.fill_between(xs, fs.values, 0,
                    where=(fs.values < 0), color=DN_COL, alpha=0.15)

    ax.axhline(0, color=ZERO_COL, linewidth=0.8, linestyle='--')

    # Signal dots on slope panel
    for ts in sig_df.index[sig_df['signal_long']]:
        if ts in ts_list:
            i = ts_list.index(ts)
            ax.scatter(i, 0, marker='^', color='lime', s=80, zorder=5, linewidths=0)

    for ts in sig_df.index[sig_df['signal_short']]:
        if ts in ts_list:
            i = ts_list.index(ts)
            ax.scatter(i, 0, marker='v', color='#ff4444', s=80, zorder=5, linewidths=0)

    _apply_time_ticks(ax, ohlcv, xs)
    ax.set_facecolor(PANEL)
    ax.tick_params(colors='#888899', labelsize=7, length=3)
    ax.yaxis.set_tick_params(labelcolor='#888899')
    for spine in ax.spines.values():
        spine.set_edgecolor('#2a2a3e')
    ax.grid(axis='y', color='#1e1e2e', linewidth=0.5)
    ax.set_ylabel('Slope', color='#888899', fontsize=7)
    ax.legend(loc='upper right', fontsize=7, facecolor='#1a1a2e',
              labelcolor='white', framealpha=0.85)

# ── Helpers ────────────────────────────────────────────────────────────────
def _apply_time_ticks(ax, df, xs, n_ticks=8):
    step = max(1, len(xs) // n_ticks)
    ax.set_xticks(xs[::step])
    ax.set_xticklabels(
        [df.index[i].strftime('%H:%M') for i in xs[::step]],
        fontsize=7, color='#888899')
    ax.set_xlim(-0.8, len(xs) - 0.2)

# ── Main ───────────────────────────────────────────────────────────────────
def main():
    print(f'Loading data...')
    data = get_data()

    for ticker in TICKERS:
        for tf in TIMEFRAMES:
            ohlcv_full = data[ticker][tf]

            # Convert to NY and filter to RTH on DATE
            ohlcv_ny   = to_ny(ohlcv_full)
            close_full = to_ny(ohlcv_full['close'])

            # Compute slopes on full series (need warmup history before RTH)
            slope_df, slow_ma_full, fast_ma_full = compute_slopes(close_full)

            # Signal detection on full series, then filter to RTH for display
            sig_full = label_signal_bars(
                slope_df,
                detect_mtf_slope_signals(slope_df, 'long',  SETUP_WINDOW),
                detect_mtf_slope_signals(slope_df, 'short', SETUP_WINDOW),
            )

            # Filter everything to RTH on DATE
            ohlcv    = filter_rth(ohlcv_ny,       DATE)
            slow_ma  = filter_rth(slow_ma_full,   DATE)
            fast_ma  = filter_rth(fast_ma_full,   DATE)
            slope_rth = filter_rth(slope_df,      DATE)
            sig_rth   = filter_rth(sig_full,      DATE)

            n_long  = sig_rth['signal_long'].sum()
            n_short = sig_rth['signal_short'].sum()
            print(f'\n{ticker} {tf} — March 20 RTH')
            print(f'  Bars:          {len(ohlcv)}')
            print(f'  Long signals:  {n_long}')
            print(f'  Short signals: {n_short}')

            # ── Build figure ─────────────────────────────────────────────
            fig = plt.figure(figsize=(18, 10))
            fig.patch.set_facecolor(BG)
            gs = gridspec.GridSpec(2, 1, height_ratios=[3, 1], hspace=0.08)

            ax_price = fig.add_subplot(gs[0])
            ax_slope = fig.add_subplot(gs[1], sharex=ax_price)

            draw_candles(ax_price, ohlcv, slow_ma, fast_ma, sig_rth)
            draw_slope_indicator(ax_slope, ohlcv, slope_rth, sig_rth)

            ax_price.tick_params(labelbottom=False)

            fig.suptitle(
                f'{ticker}  ·  {tf}  ·  MTF Slope Re-alignment  ·  {DATE}  (NY time)',
                color='white', fontsize=12, x=0.02, ha='left', y=0.98,
            )

            out = f'{OUT_DIR}/mtf_{ticker.lower()}_{tf}_{DATE}.png'
            plt.savefig(out, dpi=150, bbox_inches='tight', facecolor=BG)
            plt.close()
            print(f'  Saved: {out}')

    print('\nDone.')

if __name__ == '__main__':
    main()
