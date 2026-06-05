#!/usr/bin/env python
# coding: utf-8
"""
cascade_grade_day.py  (v2 — extended-hours)
-------------------------------------------
Full-stack Cascade entry scan with EXTENDED-HOURS SMAs.

Every timeframe's 9-SMA/slope is computed on 04:00-20:00 bars, seeded from
this session's premarket (and prior days for the slow TFs) so the line is
fully warmed at 09:30 — never RTH-only, never prior-day-stitched warmup.
This is the fix for the MRVL 2026-06-03 seeding bug (RTH-only inverted the
30m to "+UP/long" and hid the 09:33 open short).

Methodology matches cascade_live.py: 9-SMA, slope lookback=2, pct slope,
FLAT band +/-0.02%, Type-2 window=10 bars. Each TF gated by the one above.

Usage:
    python tools/cascade_grade_day.py MRVL 2026-06-03
"""
import sys, os, argparse, datetime as dt, warnings
warnings.filterwarnings('ignore')
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import numpy as np, pandas as pd, pytz
from tools.fetch_polygon import fetch_bars

FAST, LB, FLAT, WIN = 9, 2, 0.02, 10
NY = pytz.timezone('America/New_York')
EXT_START, EXT_END = '04:00', '20:00'        # extended-hours seed window
RTH_START, RTH_END = '09:30', '16:00'        # display/scan window
STACK = ['Weekly', 'Daily', '4h', '65m', '30m', '5m', '1m', '10s']
ENTRY_TFS = ['30m', '5m', '1m', '10s']        # tradeable entry timeframes


def slope_pct(c):
    ma = c.rolling(FAST).mean()
    return ((ma - ma.shift(LB)) / ma) * 100, ma


def state_of(v):
    if pd.isna(v): return 'n/a'
    return 'UP' if v > FLAT else 'DOWN' if v < -FLAT else 'FLAT'


def rs(df, rule):
    return df.resample(rule).agg({'open': 'first', 'high': 'max', 'low': 'min',
                                  'close': 'last', 'volume': 'sum'}).dropna()


def tz(df):
    if df.index.tz is None:
        df.index = df.index.tz_localize('UTC')
    df.index = df.index.tz_convert(NY)
    return df


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('ticker'); ap.add_argument('date')
    args = ap.parse_args()
    T, D = args.ticker.upper(), args.date
    tgt = pd.Timestamp(D).date()

    d3  = (tgt - dt.timedelta(days=6)).strftime('%Y-%m-%d')    # 1m/5m/30m/65m seed
    d6  = (tgt - dt.timedelta(days=12)).strftime('%Y-%m-%d')   # 4h seed
    d25 = (tgt - dt.timedelta(days=40)).strftime('%Y-%m-%d')   # daily
    d130= (tgt - dt.timedelta(days=200)).strftime('%Y-%m-%d')  # weekly

    print(f"Fetching {T} {D} on EXTENDED hours (04:00-20:00, premarket seeded)...")
    m1  = tz(fetch_bars(T, 'minute', d3,  D, multiplier=1)).between_time(EXT_START, EXT_END)
    s10 = tz(fetch_bars(T, 'second', D,   D, multiplier=10)).between_time(EXT_START, EXT_END)
    hr  = tz(fetch_bars(T, 'hour',   d6,  D, multiplier=1)).between_time(EXT_START, EXT_END)
    day = tz(fetch_bars(T, 'day',    d130, D, multiplier=1))

    series = {
        '10s':   s10['close'],
        '1m':    m1['close'],
        '5m':    rs(m1, '5min')['close'],
        '30m':   rs(m1, '30min')['close'],
        '65m':   rs(m1, '65min')['close'],
        '4h':    rs(hr, '4h')['close'] if len(hr) else None,
        'Daily': day['close'] if len(day) else None,
        'Weekly':day['close'].resample('1W').last().dropna() if len(day) else None,
    }
    slopes = {}
    for tf, cl in series.items():
        if cl is None or len(cl.dropna()) < FAST + LB:
            slopes[tf] = None; continue
        sl, _ = slope_pct(cl); slopes[tf] = sl.dropna()

    def slope_at(tf, ts):
        s = slopes.get(tf)
        if s is None: return np.nan
        sub = s[s.index <= ts]; return sub.iloc[-1] if len(sub) else np.nan
    def state_at(tf, ts):
        return state_of(slope_at(tf, ts))

    # premarket warmup report
    print("\nPremarket warmup (bars before 09:30 today):")
    for tf in STACK:
        s = slopes.get(tf)
        if s is None: print(f"  {tf:>6}: n/a"); continue
        pre = s[(s.index.date == tgt) & (s.index.time < dt.time(9, 30))]
        first = s[s.index.date == tgt]
        warm = 'WARM at 09:30' if len(pre) else ('warms ' + first.index[0].strftime('%H:%M') if len(first) else 'n/a')
        print(f"  {tf:>6}: {len(pre):>4} premkt bars -> {warm}")

    # ── entry scan over today's RTH, ext-hours-seeded SMAs ──
    # NEW-INTRADAY-EXTREME GATE (the rule, plain & simple):
    #   A short is VALID only if a NEW intraday LOW was made within the active leg.
    #   A long is VALID only if a NEW intraday HIGH was made within the active leg.
    #   No new extreme = the leg isn't trending = NOT a valid entry (not just reduced).
    #   Verified on MRVL 2026-06-03: 294.01 LOD @ 09:49 held all day, so every short
    #   after 09:49 (10:55, 14:32, and the live 11:10/13:47 fills) is INVALID.
    day1m  = m1[m1.index.date == tgt].between_time(RTH_START, RTH_END)
    run_lod = day1m['low'].cummin()
    run_hod = day1m['high'].cummax()
    NEW_EXTREME_LOOKBACK = 10   # minutes; a new extreme must be this recent to confirm the leg

    def made_new_extreme(direction, ts):
        """Real-time, no hindsight: did the running intraday extreme move in the
        trade's direction within the last NEW_EXTREME_LOOKBACK minutes?"""
        cutoff = ts - pd.Timedelta(minutes=NEW_EXTREME_LOOKBACK)
        if direction == 'SHORT':
            cur = run_lod[run_lod.index <= ts]
            if not len(cur): return False
            past = run_lod[run_lod.index <= cutoff]
            base = past.iloc[-1] if len(past) else float('inf')   # pre-open => opening leg
            return cur.iloc[-1] < base
        else:
            cur = run_hod[run_hod.index <= ts]
            if not len(cur): return False
            past = run_hod[run_hod.index <= cutoff]
            base = past.iloc[-1] if len(past) else float('-inf')
            return cur.iloc[-1] > base
    print("\n" + "=" * 96)
    print(f"CASCADE ENTRY SCAN (ext-hours stack) — {T} {D}")
    print("=" * 96)
    print(f"{'time':>9} {'TF':>4} {'px':>8} {'entrySl':>8} {'gate':>5} {'gateSt':>6}  {'conf':>11}  stack(W D 4h 65 30 5 1 10s)")
    print("-" * 96)

    fires = []
    for i, tf in enumerate(ENTRY_TFS):
        gate = STACK[STACK.index(tf) - 1]
        s = slopes.get(tf)
        if s is None: continue
        sd = s[(s.index.date == tgt)]
        sd = sd[(sd.index.time >= dt.time(9, 30)) & (sd.index.time <= dt.time(16, 0))]
        for j in range(1, len(sd)):
            ts = sd.index[j]; cur, prev = sd.iloc[j], sd.iloc[j - 1]
            w = sd.iloc[max(0, j - WIN):j]
            gst = state_at(gate, ts)
            short = gst == 'DOWN' and (w > 0).any() and prev >= 0 > cur
            long_ = gst == 'UP'   and (w < 0).any() and prev <= 0 < cur
            if not (short or long_): continue
            px = series[tf][series[tf].index <= ts].iloc[-1]
            d = 'SHORT' if short else 'LONG'
            valid = made_new_extreme(d, ts)          # the new-intraday-extreme gate
            snap = ' '.join({'UP': 'U', 'DOWN': 'D', 'FLAT': '.', 'n/a': '-'}[state_at(x, ts)] for x in STACK)
            fires.append((ts, tf, d, px, cur, gate, gst, valid, snap))

    fires.sort(key=lambda x: x[0])
    valid_fires = [f for f in fires if f[7]]

    print("VALID entries (made a new intraday extreme in the trade's direction):")
    print(f"{'time':>9} {'TF':>4} {'px':>8} {'entrySl':>8} {'gate':>5} {'gateSt':>6}  {'dir':>5}  stack(W D 4h 65 30 5 1 10s)")
    print("-" * 96)
    for ts, tf, d, px, cur, gate, gst, valid, snap in valid_fires:
        print(f"{ts.strftime('%H:%M:%S'):>9} {tf:>4} {px:>8.2f} {cur:>+8.3f} {gate:>5} {gst:>6}  {d:>5}  {snap}")

    print(f"\n{len(valid_fires)} VALID / {len(fires)} raw fires. "
          f"INVALID = fired but no new intraday {('low/high')} in last {NEW_EXTREME_LOOKBACK}m "
          f"(leg not trending -> not a real entry).")
    print("Stack order: Weekly Daily 4h 65m 30m 5m 1m 10s  (U=UP D=DOWN .=FLAT)")


if __name__ == '__main__':
    main()
