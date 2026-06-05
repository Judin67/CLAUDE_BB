#!/usr/bin/env python
# coding: utf-8
"""
slope_level_decouple.py
-----------------------
EMPIRICAL STUDY — SLOPE vs LEVEL DECOUPLING.

Mirrors cascade_grade_day.py methodology EXACTLY:
  - extended hours 04:00-20:00 ET, premarket seeded
  - 9-SMA, slope lookback=2, PERCENT slope, FLAT band +/-0.02
  - tz()->America/New_York, between_time('04:00','20:00'), rs() resample per TF

For each specimen, builds a per-MINUTE series (forward-filled from the 30m / 5m
SMA-and-slope) of:
    slope%  = 30m 9-SMA percent slope (2-bar lookback)
    level   = (price - 30m_9SMA) expressed in % and in 30m-ATR units
and quantifies the decoupling during the reversion window.

DECISIVE NUMBER reported per regime:
    max level-reversion depth (in % and ATR units) that occurs
    WHILE the higher-TF slope still reads UP (> +0.02).
"""
import sys, os, datetime as dt, warnings
warnings.filterwarnings('ignore')
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import numpy as np, pandas as pd, pytz
from tools.fetch_polygon import fetch_bars

FAST, LB, FLAT = 9, 2, 0.02
NY = pytz.timezone('America/New_York')
EXT_START, EXT_END = '04:00', '20:00'
ATR_N = 14   # ATR window on the resampled TF (standard Wilder-ish via simple mean of TR)


def tz(df):
    if df.index.tz is None:
        df.index = df.index.tz_localize('UTC')
    df.index = df.index.tz_convert(NY)
    return df


def rs(df, rule):
    return df.resample(rule).agg({'open': 'first', 'high': 'max', 'low': 'min',
                                  'close': 'last', 'volume': 'sum'}).dropna()


def slope_pct(c):
    ma = c.rolling(FAST).mean()
    sl = ((ma - ma.shift(LB)) / ma) * 100
    return sl, ma


def atr(df, n=ATR_N):
    h, l, c = df['high'], df['low'], df['close']
    pc = c.shift(1)
    tr = pd.concat([(h - l), (h - pc).abs(), (l - pc).abs()], axis=1).max(axis=1)
    return tr.rolling(n).mean()


def state_of(v):
    if pd.isna(v): return 'n/a'
    return 'UP' if v > FLAT else 'DOWN' if v < -FLAT else 'FLAT'


def build_tf(m1, rule):
    """Return per-bar DataFrame for a resampled TF with sma, slope, atr."""
    bars = rs(m1, rule)
    sl, ma = slope_pct(bars['close'])
    bars = bars.copy()
    bars['sma'] = ma
    bars['slope'] = sl
    bars['atr'] = atr(bars)
    return bars


def asof_series(tf_bars, col, minute_index):
    """Forward-fill a TF column onto a per-minute index (no lookahead: use the
    last CLOSED TF bar at or before each minute). reindex(method='ffill')."""
    s = tf_bars[col].dropna()
    return s.reindex(minute_index, method='ffill')


def analyze(ticker, date, win_start, win_end, label, direction='reversion_down'):
    """
    direction reversion_down => measure how far price falls below/toward SMA from a high.
    Builds per-minute level vs slope for 30m and 5m; reports decoupling stats
    over [win_start, win_end] RTH window (HH:MM strings).
    """
    tgt = pd.Timestamp(date).date()
    d3 = (tgt - dt.timedelta(days=8)).strftime('%Y-%m-%d')  # seed for 1m/5m/30m

    m1 = tz(fetch_bars(ticker, 'minute', d3, date, multiplier=1)).between_time(EXT_START, EXT_END)

    out = {'ticker': ticker, 'date': date, 'label': label, 'window': f'{win_start}-{win_end}'}
    detail = {}

    for tf_name, rule in [('30m', '30min'), ('5m', '5min')]:
        bars = build_tf(m1, rule)
        # per-minute RTH index for the target day
        day1m = m1[m1.index.date == tgt]
        rth = day1m.between_time('09:30', '16:00')
        if not len(rth):
            continue
        idx = rth.index
        px = rth['close']
        sma_m = asof_series(bars, 'sma', idx)
        slope_m = asof_series(bars, 'slope', idx)
        atr_m = asof_series(bars, 'atr', idx)

        # level = price - sma  (signed). pct of price. ATR units.
        level_abs = px - sma_m
        level_pct = (level_abs / sma_m) * 100.0
        level_atr = level_abs / atr_m

        df = pd.DataFrame({
            'px': px, 'sma': sma_m, 'slope': slope_m, 'atr': atr_m,
            'level_abs': level_abs, 'level_pct': level_pct, 'level_atr': level_atr,
        })
        # restrict to the reversion window
        w = df.between_time(win_start, win_end).dropna(subset=['slope', 'sma'])
        if not len(w):
            continue

        slope_min = w['slope'].min()
        slope_max = w['slope'].max()
        slope_up_frac = float((w['slope'] > FLAT).mean())

        # --- REGIME-FAIR METRIC: max reversion-while-slope-UP across the window ---
        # For every minute where slope is UP, scan forward over the contiguous
        # UP-run and measure the deepest drop from any prior high to a later low,
        # all while slope > FLAT. This captures "how big a level reversion can the
        # slope gate miss" without cherry-picking one leg.
        up_mask = (w['slope'] > FLAT).values
        pxv = w['px'].values
        atrv = w['atr'].values
        smav = w['sma'].values
        best_dd_pct = 0.0
        best_dd_atr = 0.0
        best_dd_lvl_pct = 0.0   # deepest (price-sma)/sma swing within an UP run
        run_start = None
        for k in range(len(up_mask)):
            if up_mask[k]:
                if run_start is None:
                    run_start = k
            else:
                run_start = None
                continue
            # within current UP run [run_start..k], drawdown from running max
            seg = pxv[run_start:k + 1]
            run_max = seg.max()
            dd_pct = (pxv[k] - run_max) / run_max * 100.0
            a = atrv[k]
            dd_atr = (pxv[k] - run_max) / a if a and not np.isnan(a) else 0.0
            if dd_pct < best_dd_pct:
                best_dd_pct = dd_pct
            if not np.isnan(dd_atr) and dd_atr < best_dd_atr:
                best_dd_atr = dd_atr
        # deepest level dip below sma while slope UP (signed, in % and ATR)
        up_lvl = w[w['slope'] > FLAT]

        # During minutes where slope is UP (>+0.02): how deep did the level revert?
        up = w[w['slope'] > FLAT]
        # find the high px and the subsequent low px within the window (the actual reversion)
        hi_ts = w['px'].idxmax()
        lo_after = w.loc[hi_ts:, 'px']
        lo_ts = lo_after.idxmin()
        hi_px = w.loc[hi_ts, 'px']
        lo_px = w.loc[lo_ts, 'px']
        reversion_pct = (lo_px - hi_px) / hi_px * 100.0
        # ATR units of the reversion (use ATR at the low)
        atr_at_lo = w.loc[lo_ts, 'atr']
        reversion_atr = (lo_px - hi_px) / atr_at_lo if atr_at_lo and not np.isnan(atr_at_lo) else np.nan

        # Was slope UP across the whole reversion leg hi_ts..lo_ts?
        leg = w.loc[hi_ts:lo_ts]
        slope_during_leg_min = leg['slope'].min()
        slope_during_leg_max = leg['slope'].max()
        slope_stayed_up = bool((leg['slope'] > FLAT).all())
        slope_up_frac_leg = float((leg['slope'] > FLAT).mean())

        # Max level reversion (distance traveled in level terms) WHILE slope > FLAT.
        # level swing within UP-minutes:
        if len(up):
            level_pct_swing_up = up['level_pct'].max() - up['level_pct'].min()
            level_atr_swing_up = up['level_atr'].max() - up['level_atr'].min()
            level_pct_min_up = up['level_pct'].min()   # how far BELOW sma it got while UP
            level_pct_max_up = up['level_pct'].max()
            level_atr_min_up = up['level_atr'].min()
            level_atr_max_up = up['level_atr'].max()
        else:
            level_pct_swing_up = level_atr_swing_up = np.nan
            level_pct_min_up = level_pct_max_up = np.nan
            level_atr_min_up = level_atr_max_up = np.nan

        # crossing check: did price cross THROUGH the sma (level changed sign) while slope UP?
        crossed_through = False
        if len(up):
            crossed_through = bool((up['level_abs'].min() < 0) and (up['level_abs'].max() > 0))

        detail[tf_name] = {
            'slope_min': round(float(slope_min), 4),
            'slope_max': round(float(slope_max), 4),
            'slope_state_min': state_of(slope_min),
            'slope_state_max': state_of(slope_max),
            'slope_up_frac_window': round(slope_up_frac, 3),
            'hi_ts': hi_ts.strftime('%H:%M'),
            'hi_px': round(float(hi_px), 2),
            'lo_ts': lo_ts.strftime('%H:%M'),
            'lo_px': round(float(lo_px), 2),
            'reversion_pct': round(float(reversion_pct), 3),
            'reversion_atr': round(float(reversion_atr), 3) if not np.isnan(reversion_atr) else None,
            'slope_during_leg_min': round(float(slope_during_leg_min), 4),
            'slope_during_leg_max': round(float(slope_during_leg_max), 4),
            'slope_stayed_up_entire_leg': slope_stayed_up,
            'slope_up_frac_leg': round(slope_up_frac_leg, 3),
            'level_pct_min_while_up': round(float(level_pct_min_up), 3) if not np.isnan(level_pct_min_up) else None,
            'level_pct_max_while_up': round(float(level_pct_max_up), 3) if not np.isnan(level_pct_max_up) else None,
            'level_atr_min_while_up': round(float(level_atr_min_up), 3) if not np.isnan(level_atr_min_up) else None,
            'level_atr_max_while_up': round(float(level_atr_max_up), 3) if not np.isnan(level_atr_max_up) else None,
            'level_pct_swing_while_up': round(float(level_pct_swing_up), 3) if not np.isnan(level_pct_swing_up) else None,
            'level_atr_swing_while_up': round(float(level_atr_swing_up), 3) if not np.isnan(level_atr_swing_up) else None,
            'price_crossed_through_sma_while_up': crossed_through,
            'atr_value': round(float(w['atr'].iloc[-1]), 3) if not np.isnan(w['atr'].iloc[-1]) else None,
            # regime-fair: deepest drawdown that happens while slope is UP, anywhere in window
            'max_dd_while_up_pct': round(float(best_dd_pct), 3),
            'max_dd_while_up_atr': round(float(best_dd_atr), 3),
        }

    out['detail'] = detail
    return out


def pp(out):
    print('\n' + '=' * 100)
    print(f"{out['ticker']} {out['date']}  [{out['label']}]   reversion window {out['window']} ET")
    print('=' * 100)
    for tf, d in out['detail'].items():
        print(f"\n  --- {tf} ---")
        print(f"    slope over window: min {d['slope_min']:+.4f} ({d['slope_state_min']})  max {d['slope_max']:+.4f} ({d['slope_state_max']})  | frac minutes UP: {d['slope_up_frac_window']}")
        print(f"    reversion leg: HI {d['hi_px']} @ {d['hi_ts']} -> LO {d['lo_px']} @ {d['lo_ts']}  = {d['reversion_pct']:+.2f}%  ({d['reversion_atr']} ATR)")
        print(f"    slope DURING the leg: min {d['slope_during_leg_min']:+.4f}  max {d['slope_during_leg_max']:+.4f}  | stayed UP entire leg: {d['slope_stayed_up_entire_leg']}  (UP frac {d['slope_up_frac_leg']})")
        print(f"    LEVEL while slope UP:  px-vs-SMA min {d['level_pct_min_while_up']}%  ({d['level_atr_min_while_up']} ATR)   max {d['level_pct_max_while_up']}% ({d['level_atr_max_while_up']} ATR)")
        print(f"    LEVEL swing while UP:  {d['level_pct_swing_while_up']}%  ({d['level_atr_swing_while_up']} ATR)   | crossed THROUGH SMA while slope UP: {d['price_crossed_through_sma_while_up']}")
        print(f"    >>> MAX DRAWDOWN-WHILE-SLOPE-UP (regime-fair):  {d['max_dd_while_up_pct']:+.2f}%  ({d['max_dd_while_up_atr']:+.2f} ATR)")


SPECIMENS = [
    # ticker, date, win_start, win_end, label
    ('CRWD', '2026-06-04', '09:30', '11:00', 'MR-within-trend'),
    ('DELL', '2026-06-01', '09:30', '12:30', 'trend-cascade pullback'),
    ('MRVL', '2026-06-03', '09:30', '16:00', 'parabolic/exhaustion'),
]

if __name__ == '__main__':
    results = []
    for t, d, ws, we, lbl in SPECIMENS:
        print(f"\nFetching {t} {d} ({lbl}) ext-hours...")
        try:
            r = analyze(t, d, ws, we, lbl)
            results.append(r)
            pp(r)
        except Exception as e:
            import traceback
            print(f"ERROR {t} {d}: {e}")
            traceback.print_exc()

    # compact comparison
    print('\n\n' + '#' * 100)
    print('COMPARISON — decisive number: max LEVEL reversion that occurs WHILE 30m slope still reads UP')
    print('#' * 100)
    print(f"{'specimen':>26} {'regime':>22} | {'30m slope range':>22} | {'maxDD-while-UP%':>15} {'DD-ATR':>7} | {'thru SMA(up)':>12}")
    for r in results:
        d30 = r['detail'].get('30m', {})
        if not d30: continue
        sr = f"{d30['slope_min']:+.3f}..{d30['slope_max']:+.3f}"
        print(f"{r['ticker']+' '+r['date']:>26} {r['label']:>22} | {sr:>22} | {d30['max_dd_while_up_pct']:>14.2f}% {d30['max_dd_while_up_atr']:>7.2f} | {str(d30['price_crossed_through_sma_while_up']):>12}")
