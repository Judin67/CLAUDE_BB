#!/usr/bin/env python
# coding: utf-8
"""
cascade_premarket.py
--------------------
Premarket-aware Cascade stack read. Same engine as cascade_live.py
(imports its slope/state/cycle functions verbatim — single source of truth),
but feeds EXTENDED-HOURS bars (04:00 -> now) to the timing timeframes instead
of RTH-only, so the stack can be read before the 9:30 open.

Why: cascade_live.py slices 10s/1m/5m/30m/65m to RTH (09:30-16:00) and aborts
in premarket. The rulebook (cascade_core_rules.md) explicitly says start reading
cycles from premarket, and SMAs must use ext-hours bars seeded from premarket.

    Weekly -> Daily -> 4h -> 65m -> 30m -> 5m -> 1m -> 10s

Intraday TFs are built on ext-hours 1m (04:00-20:00) stitched across days so the
9-SMA is seeded; everything is then cut to "now". 4h/Daily/Weekly identical to
cascade_live.py. Cut at the last available bar today.

Usage:
    python tools/cascade_premarket.py TICKER [YYYY-MM-DD]

Data: Massive/Polygon paid tier (ext hours + 10s confirmed available).
"""
import sys, os, datetime as dt, argparse, warnings
warnings.filterwarnings('ignore')
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np
import pandas as pd
import pytz
from tools.fetch_polygon import fetch_bars
# import the EXACT methodology — do not re-implement
from tools.cascade_live import (sma, slope_pct, state_of, resample_cont,
                                 cycle_phase, STACK, FAST_WIN, LB)

NY_TZ = pytz.timezone('America/New_York')
EXT_START, EXT_END = '04:00', '20:00'      # extended hours window
CACHE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '.tmp')


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
        return os.path.join(CACHE_DIR, f'{TICKER.lower()}_pm_{tag}_{DATE}.csv')

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

    d10 = (target - dt.timedelta(days=12)).strftime('%Y-%m-%d')
    d60 = (target - dt.timedelta(days=70)).strftime('%Y-%m-%d')
    d1y = (target - dt.timedelta(days=400)).strftime('%Y-%m-%d')

    print(f"Fetching {TICKER} for {DATE} (paid tier, EXT HOURS)...")
    df_1m_all  = load_or_fetch('1m',  lambda: fetch_bars(TICKER, 'minute', d10, DATE, multiplier=1))
    df_10s_all = load_or_fetch('10s', lambda: fetch_bars(TICKER, 'second', DATE, DATE, multiplier=10))
    df_hr_all  = load_or_fetch('hr',  lambda: fetch_bars(TICKER, 'hour',   d60, DATE, multiplier=1))
    df_day     = load_or_fetch('day', lambda: fetch_bars(TICKER, 'day',    d1y, DATE, multiplier=1))

    if df_1m_all.empty:
        print("No 1m data returned — aborting."); sys.exit(1)

    # EXT-HOURS slices (04:00-20:00), stitched across days for SMA seeding
    ext_1m_all = df_1m_all.between_time(EXT_START, EXT_END)
    df_1m_today = ext_1m_all[ext_1m_all.index.date == target]
    if df_1m_today.empty:
        print(f"No ext-hours 1m bars for {DATE} yet. Latest: "
              f"{ext_1m_all.index[-1] if len(ext_1m_all) else 'none'}")
        sys.exit(1)

    now_ts  = df_1m_today.index[-1]
    last_px = df_1m_today['close'].iloc[-1]

    # ── Build close series per TF (cut to <= now) ────────────────────────────
    ext_1m = ext_1m_all[ext_1m_all.index <= now_ts]
    series = {}

    if not df_10s_all.empty:
        ext_10s = df_10s_all.between_time(EXT_START, EXT_END)
        ext_10s = ext_10s[(ext_10s.index.date == target) & (ext_10s.index <= now_ts)]
        series['10s'] = ext_10s['close'] if len(ext_10s) else None
    else:
        series['10s'] = None

    series['1m']  = ext_1m['close']
    series['5m']  = resample_cont(ext_1m, '5min')['close']
    series['30m'] = resample_cont(ext_1m, '30min')['close']
    series['65m'] = resample_cont(ext_1m, '65min')['close']
    df_hr = df_hr_all[df_hr_all.index <= now_ts]
    series['4h']  = resample_cont(df_hr, '4h')['close'] if len(df_hr) else None
    series['Daily']  = df_day['close'] if len(df_day) else None
    series['Weekly'] = df_day['close'].resample('1W').last().dropna() if len(df_day) else None

    # ── Slope + state per TF ─────────────────────────────────────────────────
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
        st  = rows[tf]['state']
        rows[tf]['aligned'] = (st == gst and st in ('UP', 'DOWN'))
        if rows[tf]['series'] is not None:
            ph, _, _ = cycle_phase(rows[tf]['series'], gst)
            rows[tf]['phase'] = ph
        else:
            rows[tf]['phase'] = '—'

    # ── Print stack table ────────────────────────────────────────────────────
    print("\n" + "=" * 80)
    print(f"CASCADE PREMARKET STACK — {TICKER} @ {now_ts.strftime('%H:%M')} ET   ${last_px:.4f}")
    print("=" * 80)
    print(f"{'TF':>7} {'slope%':>9}  {'state':<5}  {'gate':>7}  {'aligned':<8} {'phase'}")
    print("-" * 80)
    for tf in STACK:
        r = rows[tf]
        sl = f"{r['slope']:+.3f}" if pd.notna(r['slope']) else '   —'
        al = '—' if r.get('aligned') is None else ('YES' if r['aligned'] else 'no')
        gate = r.get('gate') or '—'
        print(f"{tf:>7} {sl:>9}  {r['state']:<5}  {gate:>7}  {al:<8} {r.get('phase','')}")

    # ── Directional read ─────────────────────────────────────────────────────
    print("\n" + "-" * 80)
    day_st = rows['30m']['state']
    bias = {'UP': 'LONG / UP', 'DOWN': 'SHORT / DOWN'}.get(day_st, 'NO BIAS (30m flat)')
    print(f"PREMARKET BIAS (30m gate): {bias}")

    higher = ['Weekly', 'Daily', '4h', '65m']
    if day_st in ('UP', 'DOWN'):
        agree    = [tf for tf in higher if rows[tf]['state'] == day_st]
        disagree = [tf for tf in higher if rows[tf]['state'] in ('UP', 'DOWN') and rows[tf]['state'] != day_st]
        print(f"Higher-TF context: agree [{','.join(agree) or '-'}]  disagree [{','.join(disagree) or '-'}]  "
              f"-> {'aligned' if not disagree else 'mixed — reduce conviction'}")
    else:
        print("Higher-TF context: 30m flat — no premarket bias yet.")

    pulling = [tf for tf in STACK if 'PULLBACK' in str(rows[tf].get('phase', ''))]
    firing  = [tf for tf in STACK if 'FIRED' in str(rows[tf].get('phase', '')) or 'REALIGN' in str(rows[tf].get('phase', ''))]
    if pulling:
        print(f"In Type 2 PULLBACK: {', '.join(pulling)}  -> no signal below the highest of these until it realigns")
    if firing:
        print(f"Fresh REALIGN/FIRED: {', '.join(firing)}")

    # ── Premarket volume + proximity + range ─────────────────────────────────
    avg_vol = df_1m_today['volume'].mean()
    print(f"\nAvg 1m volume (premarket): {avg_vol:,.0f}  -> "
          f"{'PASS (>=100k)' if avg_vol >= 100_000 else 'light (premarket; RTH will differ)'}")

    ma_5m = sma(series['5m'], FAST_WIN).dropna()
    if len(ma_5m):
        ref = ma_5m.iloc[-1]
        prox = abs(last_px - ref) / ref * 100
        print(f"Price vs 5m 9-SMA: ${last_px:.4f} vs ${ref:.4f}  ({prox:.3f}% away)  -> "
              f"{'at the mean (<=0.25%)' if prox <= 0.25 else 'extended (>0.25%)'}")

    pmh, pml = df_1m_today['high'].max(), df_1m_today['low'].min()
    op = df_1m_today['open'].iloc[0]
    print(f"PM High ${pmh:.4f}  PM Low ${pml:.4f}  Last ${last_px:.4f}  "
          f"({(last_px - pml) / (pmh - pml) * 100:.0f}% of PM range)  |  "
          f"{((last_px / op) - 1) * 100:+.2f}% since 04:00")

    # prior day close for gap context
    if len(df_day) >= 1:
        prior = df_day[df_day.index.date < target]
        if len(prior):
            pc = prior['close'].iloc[-1]
            print(f"Prior close ${pc:.4f}  -> gap {((last_px / pc) - 1) * 100:+.2f}%")

    print(f"\nTime: {now_ts.strftime('%H:%M')} ET — PREMARKET (open 09:30)")
    print("Note: timing TFs built on EXT-HOURS bars (04:00->now), stitched across days.")
    print("      PULLBACK = pre-entry ALERT; FIRED = entry. Manual snapshot — re-run to refresh.")
    print("=" * 80)


if __name__ == '__main__':
    main()
