#!/usr/bin/env python
"""
Stop loss visualization — first 2 signals for a given ticker/tf.
Shows entry price and stop level on candlestick chart.
"""

import sys
import pytz
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.gridspec as gridspec
import warnings
warnings.filterwarnings('ignore')

sys.path.insert(0, 'C:/Users/Trader/Desktop/CLAUDE_BB')
sys.path.insert(0, 'C:/Users/Trader/quant-project')

from src.indicators import sma
from src.signals import detect_mtf_slope_signals, label_signal_bars

# ── Config ──────────────────────────────────────────────────────────────────
TICKER       = 'SPY'
TF           = '1m'
DATE         = '2026-03-20'
SLOW_WIN     = 21
FAST_WIN     = 9
SETUP_WINDOW = 10
SLOPE_FACTOR = 0.2
BARS_CONTEXT = 30   # bars to show before/after each signal

NY_TZ     = pytz.timezone('America/New_York')
RTH_START = '09:30'
RTH_END   = '16:00'

BG       = '#0d0d1a'
PANEL    = '#131722'
UP_COL   = '#26a69a'
DN_COL   = '#ef5350'
SLOW_COL = '#2962ff'
FAST_COL = '#ff9800'

OUT_DIR  = 'C:/Users/Trader/Desktop/CLAUDE_BB/.tmp'

# ── Load cached data ────────────────────────────────────────────────────────
path = f'{OUT_DIR}/{TICKER.lower()}_{TF}_ohlcv_{DATE}.csv'
ohlcv_full = pd.read_csv(path, index_col=0, parse_dates=True)

# Convert to NY
idx = ohlcv_full.index
if idx.tz is None:
    idx = idx.tz_localize('UTC')
idx = idx.tz_convert(NY_TZ)
ohlcv_full.index = idx

# Filter to RTH
ohlcv = ohlcv_full.loc[f'{DATE} {RTH_START}':f'{DATE} {RTH_END}']

# ── Compute slopes and signals ───────────────────────────────────────────────
close = ohlcv_full['close']

slow_ma    = sma(close, SLOW_WIN)
fast_ma    = sma(close, FAST_WIN)
lb_slow    = max(1, round(SLOW_WIN * SLOPE_FACTOR))
lb_fast    = max(1, round(FAST_WIN * SLOPE_FACTOR))
slow_slope = slow_ma - slow_ma.shift(lb_slow)
fast_slope = fast_ma - fast_ma.shift(lb_fast)

slope_df = pd.DataFrame({'fast_slope': fast_slope, 'slow_slope': slow_slope})
sig_full = label_signal_bars(
    slope_df,
    detect_mtf_slope_signals(slope_df, 'long',  SETUP_WINDOW),
    detect_mtf_slope_signals(slope_df, 'short', SETUP_WINDOW),
)

# Filter to RTH
slope_rth = slope_df.reindex(ohlcv.index)
sig_rth   = sig_full.reindex(ohlcv.index, fill_value=False)
slow_ma_rth = slow_ma.reindex(ohlcv.index)
fast_ma_rth = fast_ma.reindex(ohlcv.index)
fs_rth = slope_rth['fast_slope']

# ── Compute stop for each signal ─────────────────────────────────────────────
def compute_stop(ts, direction, ohlcv, fs_rth, setup_window):
    """
    Find the pullback window before signal ts.
    Returns (stop_price, stop_candle_ts) where stop_candle_ts is the bar that defines the stop.
    Long: lowest LOW of pullback bars (fs <= 0)
    Short: highest HIGH of pullback bars (fs >= 0)
    """
    ts_list = ohlcv.index.tolist()
    idx = ts_list.index(ts)

    start = max(0, idx - setup_window)
    pullback_bars = []
    for j in range(start, idx):
        bar_ts = ts_list[j]
        fs_val = fs_rth.iloc[j] if j < len(fs_rth) else None
        if fs_val is None:
            continue
        if direction == 'long' and fs_val <= 0:
            pullback_bars.append(bar_ts)
        elif direction == 'short' and fs_val >= 0:
            pullback_bars.append(bar_ts)

    if not pullback_bars:
        return None, None

    if direction == 'long':
        stop_price = ohlcv.loc[pullback_bars, 'low'].min()
        stop_ts    = ohlcv.loc[pullback_bars, 'low'].idxmin()
    else:
        stop_price = ohlcv.loc[pullback_bars, 'high'].max()
        stop_ts    = ohlcv.loc[pullback_bars, 'high'].idxmax()

    return stop_price, stop_ts

# Collect all signals with direction and stop
signals = []
for ts in sig_rth.index:
    if sig_rth.loc[ts, 'signal_long']:
        stop, stop_ts = compute_stop(ts, 'long', ohlcv, fs_rth, SETUP_WINDOW)
        entry = ohlcv.loc[ts, 'close']
        signals.append({'ts': ts, 'direction': 'long', 'entry': entry, 'stop': stop, 'stop_ts': stop_ts})
    if sig_rth.loc[ts, 'signal_short']:
        stop, stop_ts = compute_stop(ts, 'short', ohlcv, fs_rth, SETUP_WINDOW)
        entry = ohlcv.loc[ts, 'close']
        signals.append({'ts': ts, 'direction': 'short', 'entry': entry, 'stop': stop, 'stop_ts': stop_ts})

# Sort by time, take first 2
signals.sort(key=lambda x: x['ts'])
first_two = signals[:2]

print(f"\nFirst 2 signals for {TICKER} {TF}:")
for s in first_two:
    print(f"  {s['direction'].upper():5s} @ {s['ts'].strftime('%H:%M')} | entry={s['entry']:.2f} | stop={s['stop']:.2f}")

# ── Plot each signal in its own zoomed window ────────────────────────────────
ts_list = ohlcv.index.tolist()

for s in first_two:
    sig_idx = ts_list.index(s['ts'])
    i_start = max(0, sig_idx - BARS_CONTEXT)
    i_end   = min(len(ts_list) - 1, sig_idx + BARS_CONTEXT)

    ohlcv_w    = ohlcv.iloc[i_start:i_end+1]
    slow_ma_w  = slow_ma_rth.iloc[i_start:i_end+1]
    fast_ma_w  = fast_ma_rth.iloc[i_start:i_end+1]
    xs         = np.arange(len(ohlcv_w))
    sig_local  = sig_idx - i_start   # index within window

    opens  = ohlcv_w['open'].values
    highs  = ohlcv_w['high'].values
    lows   = ohlcv_w['low'].values
    closes = ohlcv_w['close'].values
    hw     = 0.35
    price_range = highs.max() - lows.min()

    fig, ax = plt.subplots(figsize=(14, 7))
    fig.patch.set_facecolor(BG)
    ax.set_facecolor(PANEL)

    # Candles
    for i, (o, h, l, c) in enumerate(zip(opens, highs, lows, closes)):
        col = UP_COL if c >= o else DN_COL
        ax.plot([i, i], [l, h], color=col, linewidth=0.8, zorder=1)
        body_h = max(abs(c - o), price_range * 0.001)
        ax.add_patch(mpatches.Rectangle(
            (i - hw, min(o, c)), hw * 2, body_h,
            color=col, zorder=2, linewidth=0))

    # MAs
    ax.plot(xs, slow_ma_w.values, color=SLOW_COL, linewidth=1.4, zorder=3, label=f'{SLOW_WIN}-SMA')
    ax.plot(xs, fast_ma_w.values, color=FAST_COL, linewidth=1.0, zorder=3, label=f'{FAST_WIN}-SMA')

    direction  = s['direction']
    entry_col  = 'lime' if direction == 'long' else '#ff4444'
    offset     = price_range * 0.007
    ts_list_w  = ohlcv_w.index.tolist()

    # Entry arrow + label
    if direction == 'long':
        ax.scatter(sig_local, lows[sig_local] - offset, marker='^',
                   color='lime', s=160, zorder=8, linewidths=0)
        ax.text(sig_local, lows[sig_local] - offset * 5,
                'entry', color='lime', fontsize=8, ha='center', va='top', zorder=9)
    else:
        ax.scatter(sig_local, highs[sig_local] + offset, marker='v',
                   color='#ff4444', s=160, zorder=8, linewidths=0)
        ax.text(sig_local, highs[sig_local] + offset * 5,
                'entry', color='#ff4444', fontsize=8, ha='center', va='bottom', zorder=9)

    # Stop arrow on the defining candle + label
    if s['stop_ts'] is not None and s['stop_ts'] in ts_list_w:
        stop_local = ts_list_w.index(s['stop_ts'])
        if direction == 'long':
            # stop is the lowest low — arrow below that candle pointing up
            ax.scatter(stop_local, lows[stop_local] - offset, marker='x',
                       color='#ff9800', s=120, zorder=8, linewidths=1.5)
            ax.text(stop_local, lows[stop_local] - offset * 5,
                    f'stop\n{s["stop"]:.2f}', color='#ff9800', fontsize=8,
                    ha='center', va='top', zorder=9)
        else:
            # stop is the highest high — marker above that candle
            ax.scatter(stop_local, highs[stop_local] + offset, marker='x',
                       color='#ff9800', s=120, zorder=8, linewidths=1.5)
            ax.text(stop_local, highs[stop_local] + offset * 5,
                    f'stop\n{s["stop"]:.2f}', color='#ff9800', fontsize=8,
                    ha='center', va='bottom', zorder=9)

    # Horizontal stop line across chart
    ax.axhline(s['stop'], color='#ff9800', linewidth=0.8, linestyle='--', alpha=0.5, zorder=6)

    # Time ticks
    step = max(1, len(xs) // 8)
    ax.set_xticks(xs[::step])
    ax.set_xticklabels(
        [ohlcv_w.index[i].strftime('%H:%M') for i in xs[::step]],
        fontsize=8, color='#888899')
    ax.set_xlim(-0.8, len(xs) + 4)  # extra space for labels on right

    ax.tick_params(colors='#888899', labelsize=7)
    ax.yaxis.set_tick_params(labelcolor='#888899')
    for spine in ax.spines.values():
        spine.set_edgecolor('#2a2a3e')
    ax.grid(axis='y', color='#1e1e2e', linewidth=0.5)
    ax.legend(loc='upper left', fontsize=8, facecolor='#1a1a2e',
              labelcolor='white', framealpha=0.85)

    time_str = s['ts'].strftime('%H:%M')
    ax.set_title(
        f"{TICKER} {TF}  ·  {direction.upper()} signal @ {time_str}  ·  "
        f"entry={s['entry']:.2f}  stop={s['stop']:.2f}  ({DATE})",
        color='white', fontsize=11, loc='left', pad=10)

    out = f"{OUT_DIR}/mtf_stop_{TICKER.lower()}_{direction}_{time_str.replace(':', '')}.png"
    plt.savefig(out, dpi=150, bbox_inches='tight', facecolor=BG)
    plt.close()
    print(f"  Saved: {out}")

print('\nDone.')
