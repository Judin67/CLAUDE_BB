#!/usr/bin/env python
# coding: utf-8
"""
cascade_live.py
---------------
Live Cascade directional read across the FULL timeframe stack:

    Weekly -> Daily -> 4h -> 65m -> 30m -> 5m -> 1m -> 10s

Each timeframe is gated by the one directly above it. Prints a stack table
(slope state + gate alignment + cycle phase), then a plain-language direction
+ entry read with volume and proximity checks.

Usage:
    python tools/cascade_live.py TICKER [YYYY-MM-DD]
    python tools/cascade_live.py MNTS
    python tools/cascade_live.py TSLA 2026-05-26

Data: Massive/Polygon paid tier (10s/second-level confirmed available).
Methodology matches the Cascade chart scripts:
    9-SMA, slope lookback = round(9*0.2)=2, pct slope, FLAT band = +/-0.02%.

Bar construction:
    10s  : second bars (multiplier=10), today, RTH
    1m   : 1m bars, RTH
    5m   : resample 1m -> 5min, RTH
    30m  : resample 1m -> 30min, RTH
    65m  : resample 1m -> 65min, anchored to each session open (6 bars/day, RTH)
    4h   : resample FULL-SESSION hourly (incl pre/post) -> 4h, midnight-anchored
           (04:00 / 08:00 / 12:00 / 16:00 / 20:00 ET buckets). Extended hours ON.
    Daily: daily bars
    Weekly: resample daily -> 1W

Direction read is TOP-DOWN per the rulebook: day bias = 30m gate; higher TFs
(65m/4h/Daily/Weekly) are context/agreement; lower TFs (5m/1m/10s) are timing.
Cycle phase: PULLBACK = pre-entry ALERT ("get ready"); FIRED = realignment/entry.
Note: 195m is the clean session-tiling alternative to 4h (2 bars/day, 9:30-anchored);
this tool runs 4h by choice.
"""
import sys, os, argparse, datetime as dt, warnings
warnings.filterwarnings('ignore')
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np
import pandas as pd
import pytz
from tools.fetch_polygon import fetch_bars

# ── Constants (match chart methodology) ──────────────────────────────────────
FAST_WIN     = 9
SLOPE_FACTOR = 0.2
LB           = max(1, round(FAST_WIN * SLOPE_FACTOR))   # = 2
FLAT_THRESH  = 0.02     # % band: UP > +0.02, DOWN < -0.02, else FLAT
SETUP_WINDOW = 10       # bars to look back for a Type 2 pullback
NY_TZ        = pytz.timezone('America/New_York')
RTH_START, RTH_END = '09:30', '16:00'
CACHE_DIR    = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '.tmp')

# Stack order (high -> low). Each TF's gate is the entry directly above it.
STACK = ['Weekly', 'Daily', '4h', '65m', '30m', '5m', '1m', '10s']


def sma(s, w):
    return s.rolling(w).mean()


def slope_pct(close):
    """9-SMA percent slope series for a close-price series."""
    ma = sma(close, FAST_WIN)
    return ((ma - ma.shift(LB)) / ma) * 100, ma


def state_of(v):
    if v >  FLAT_THRESH: return 'UP'
    if v < -FLAT_THRESH: return 'DOWN'
    return 'FLAT'


def resample_session_anchored(df1m, minutes):
    """Resample 1m OHLCV to N-minute bars anchored to each session's first bar."""
    parts = []
    for _, g in df1m.groupby(df1m.index.normalize()):
        r = g.resample(f'{minutes}min', origin=g.index[0]).agg(
            {'open': 'first', 'high': 'max', 'low': 'min',
             'close': 'last', 'volume': 'sum'}).dropna()
        parts.append(r)
    return pd.concat(parts) if parts else df1m.iloc[0:0]


def resample_cont(df, rule):
    """Continuous resample (stitched across days)."""
    return df.resample(rule).agg(
        {'open': 'first', 'high': 'max', 'low': 'min',
         'close': 'last', 'volume': 'sum'}).dropna()


def cycle_phase(slope_series, gate_state):
    """
    Classify where this TF is in its cycle relative to its gate, per the rulebook.

      PULLBACK = pre-entry ALERT: this TF's slope is against its (aligned) gate.
      FIRED    = ENTRY: slope was against the gate within the last SETUP_WINDOW
                 bars AND just crossed back through zero on the current bar.

    Returns (phase, fired_long, fired_short).
    """
    s = slope_series.dropna()
    if len(s) < 2:
        return 'n/a', False, False
    cur  = s.iloc[-1]
    prev = s.iloc[-2]
    # the SETUP_WINDOW bars BEFORE the current bar (the pullback look-back)
    window = s.iloc[-(SETUP_WINDOW + 1):-1]

    # Long context: gate up. Pullback = slope negative; FIRED = strict cross back > 0.
    if gate_state == 'UP':
        if cur < 0:
            return 'PULLBACK (vs UP gate)', False, False
        went_neg   = (window < 0).any()
        crossed_up = prev <= 0 < cur          # crossed back above zero THIS bar
        if went_neg and crossed_up:
            return 'REALIGN/FIRED long', True, False
        return 'trend up', False, False
    # Short context: gate down. Pullback = slope positive; FIRED = strict cross back < 0.
    if gate_state == 'DOWN':
        if cur > 0:
            return 'PULLBACK (vs DOWN gate)', False, False
        went_pos   = (window > 0).any()
        crossed_dn = prev >= 0 > cur          # crossed back below zero THIS bar
        if went_pos and crossed_dn:
            return 'REALIGN/FIRED short', False, True
        return 'trend down', False, False
    return f'gate FLAT ({state_of(cur)})', False, False


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('ticker')
    ap.add_argument('date', nargs='?', default=dt.date.today().strftime('%Y-%m-%d'))
    ap.add_argument('--no-cache', action='store_true')
    args = ap.parse_args()

    TICKER = args.ticker.upper()
    DATE = args.date
    target = pd.Timestamp(DATE).date()
    os.makedirs(CACHE_DIR, exist_ok=True)

    def cache_path(tag):
        return os.path.join(CACHE_DIR, f'{TICKER.lower()}_{tag}_{DATE}.csv')

    def load_or_fetch(tag, fetch_fn):
        p = cache_path(tag)
        if os.path.exists(p) and not args.no_cache:
            df = pd.read_csv(p, index_col=0, parse_dates=True)
            if df.index.tz is None:
                df.index = df.index.tz_localize('UTC')
        else:
            df = fetch_fn()
            if df.empty:
                return df
            df.to_csv(p)
            if df.index.tz is None:
                df.index = df.index.tz_localize('UTC')
        df.index = df.index.tz_convert(NY_TZ)
        return df

    d10 = (target - dt.timedelta(days=12)).strftime('%Y-%m-%d')   # 1m / 10s window
    d60 = (target - dt.timedelta(days=70)).strftime('%Y-%m-%d')   # hourly window
    d1y = (target - dt.timedelta(days=400)).strftime('%Y-%m-%d')  # daily window

    print(f"Fetching {TICKER} for {DATE} (paid tier)...")
    df_1m_all  = load_or_fetch('1m',  lambda: fetch_bars(TICKER, 'minute', d10, DATE, multiplier=1))
    df_10s_all = load_or_fetch('10s', lambda: fetch_bars(TICKER, 'second', DATE, DATE, multiplier=10))
    df_hr_all  = load_or_fetch('hr',  lambda: fetch_bars(TICKER, 'hour',   d60, DATE, multiplier=1))
    df_day     = load_or_fetch('day', lambda: fetch_bars(TICKER, 'day',    d1y, DATE, multiplier=1))

    if df_1m_all.empty:
        print("No 1m data returned — aborting."); sys.exit(1)

    # RTH slices (intraday TFs are RTH-only; 4h deliberately keeps the full session — see below)
    rth_1m_all = df_1m_all.between_time(RTH_START, RTH_END)
    df_1m = rth_1m_all[rth_1m_all.index.date == target]
    if df_1m.empty:
        print(f"No RTH 1m bars for {DATE}. Latest in pull: {rth_1m_all.index[-1].date() if len(rth_1m_all) else 'none'}")
        sys.exit(1)

    last_px = df_1m['close'].iloc[-1]
    now_ts  = df_1m.index[-1]

    # ── Build close series per timeframe ─────────────────────────────────────
    series = {}

    # 10s (today only, RTH)
    if not df_10s_all.empty:
        rth_10s = df_10s_all.between_time(RTH_START, RTH_END)
        rth_10s = rth_10s[rth_10s.index.date == target]
        series['10s'] = rth_10s['close'] if len(rth_10s) else None
    else:
        series['10s'] = None

    series['1m']  = rth_1m_all['close']  # seeded across days, sliced at read time
    series['5m']  = resample_cont(rth_1m_all, '5min')['close']
    series['30m'] = resample_cont(rth_1m_all, '30min')['close']
    series['65m'] = resample_session_anchored(rth_1m_all, 65)['close']
    # 4h: full-session hourly (incl pre/post), midnight-anchored 4h buckets — extended hours ON
    series['4h']  = resample_cont(df_hr_all, '4h')['close'] if len(df_hr_all) else None
    series['Daily']  = df_day['close'] if len(df_day) else None
    series['Weekly'] = df_day['close'].resample('1W').last().dropna() if len(df_day) else None

    # ── Compute current slope + state per TF ─────────────────────────────────
    rows = {}
    for tf in STACK:
        cl = series.get(tf)
        if cl is None or len(cl.dropna()) < FAST_WIN + LB:
            rows[tf] = {'slope': np.nan, 'state': 'n/a', 'series': None}
            continue
        sl, _ = slope_pct(cl)
        sl = sl.dropna()
        if sl.empty:
            rows[tf] = {'slope': np.nan, 'state': 'n/a', 'series': None}
            continue
        rows[tf] = {'slope': sl.iloc[-1], 'state': state_of(sl.iloc[-1]), 'series': sl}

    # ── Gate alignment + cycle phase ─────────────────────────────────────────
    for i, tf in enumerate(STACK):
        gate = STACK[i - 1] if i > 0 else None
        rows[tf]['gate'] = gate
        if gate is None or rows[gate]['state'] in ('n/a',):
            rows[tf]['aligned'] = None
            rows[tf]['phase'] = '—'
            continue
        gst = rows[gate]['state']
        st = rows[tf]['state']
        rows[tf]['aligned'] = (st == gst and st in ('UP', 'DOWN'))
        if rows[tf]['series'] is not None:
            ph, _, _ = cycle_phase(rows[tf]['series'], gst)
            rows[tf]['phase'] = ph
        else:
            rows[tf]['phase'] = '—'

    # ── Print stack table ────────────────────────────────────────────────────
    print("\n" + "=" * 78)
    print(f"CASCADE STACK — {TICKER} @ {now_ts.strftime('%H:%M')} ET   ${last_px:.4f}")
    print("=" * 78)
    print(f"{'TF':>7} {'slope%':>9}  {'state':<5}  {'gate':>7}  {'aligned':<8} {'phase'}")
    print("-" * 78)
    for tf in STACK:
        r = rows[tf]
        sl = f"{r['slope']:+.3f}" if pd.notna(r['slope']) else '   —'
        al = '—' if r.get('aligned') is None else ('YES' if r['aligned'] else 'no')
        gate = r.get('gate') or '—'
        print(f"{tf:>7} {sl:>9}  {r['state']:<5}  {gate:>7}  {al:<8} {r.get('phase','')}")

    # ── Directional read — TOP-DOWN per the rulebook ────────────────────────
    print("\n" + "-" * 78)
    # Day bias is set by the 30m gate (rules: "30m slope = day bias" for intraday entries).
    day_st = rows['30m']['state']
    bias = {'UP': 'LONG / UP', 'DOWN': 'SHORT / DOWN'}.get(day_st, 'NO BIAS (30m flat)')
    print(f"DAY BIAS (30m gate): {bias}")

    # Higher-TF context: do the bigger timeframes agree with the 30m bias?
    higher = ['Weekly', 'Daily', '4h', '65m']
    if day_st in ('UP', 'DOWN'):
        agree    = [tf for tf in higher if rows[tf]['state'] == day_st]
        disagree = [tf for tf in higher if rows[tf]['state'] in ('UP', 'DOWN') and rows[tf]['state'] != day_st]
        print(f"Higher-TF context: agree [{','.join(agree) or '-'}]  disagree [{','.join(disagree) or '-'}]  "
              f"-> {'clean trend day' if not disagree else 'mixed — reduce conviction'}")
    else:
        print("Higher-TF context: 30m flat — no intraday bias; wait for the gate to pick a side.")

    # Active pullback (lowest TF currently in PULLBACK)
    pulling = [tf for tf in STACK if 'PULLBACK' in str(rows[tf].get('phase', ''))]
    firing  = [tf for tf in STACK if 'FIRED' in str(rows[tf].get('phase', '')) or 'REALIGN' in str(rows[tf].get('phase', ''))]
    if pulling:
        print(f"In Type 2 PULLBACK: {', '.join(pulling)}  -> per rule, no signal below the highest of these until it realigns")
    if firing:
        print(f"Fresh REALIGN/FIRED: {', '.join(firing)}")

    # ── Volume + proximity (1m entry context) ────────────────────────────────
    avg_vol = df_1m['volume'].mean()
    print(f"\nAvg 1m volume (session): {avg_vol:,.0f}  -> "
          f"{'PASS (>=100k)' if avg_vol >= 100_000 else 'FAIL (<100k, signals unreliable)'}")

    ma_5m = sma(series['5m'], FAST_WIN).dropna()
    if len(ma_5m):
        ref = ma_5m.iloc[-1]
        prox = abs(last_px - ref) / ref * 100
        print(f"Price vs 5m 9-SMA: ${last_px:.4f} vs ${ref:.4f}  ({prox:.3f}% away)  -> "
              f"{'PASS (<=0.25%)' if prox <= 0.25 else 'EXTENDED (>0.25%) — reduce/skip'}")

    hod, lod = df_1m['high'].max(), df_1m['low'].min()
    op = df_1m['open'].iloc[0]
    print(f"HOD ${hod:.4f}  LOD ${lod:.4f}  Last ${last_px:.4f}  "
          f"({(last_px - lod) / (hod - lod) * 100:.0f}% of range)  |  "
          f"{((last_px / op) - 1) * 100:+.2f}% on day")

    t = now_ts.time()
    win = ("OPEN TREND (9:30-10:30)" if t < dt.time(10, 30)
           else "DEAD ZONE (10:30-13:00) — algo skips" if t < dt.time(13, 0)
           else "RE-ENGAGE (13:00-16:00)")
    print(f"Time window: {win}")
    print("Note: 10s live (paid tier). 4h = full-session hourly->4h (ext hours ON); 65m session-anchored.")
    print("      PULLBACK = pre-entry ALERT; FIRED = entry. Manual snapshot — re-run to refresh.")
    print("=" * 78)


if __name__ == '__main__':
    main()
