#!/usr/bin/env python
# coding: utf-8
"""
sma_lag_study.py
----------------
EMPIRICAL STUDY: SMA group delay (lag) + chasing/extension-understatement.

Mirrors cascade_grade_day.py methodology EXACTLY:
  - tz() -> America/New_York
  - between_time('04:00','20:00')  (extended-hours bars, premarket seeded)
  - rs() resample per TF
  - 9-SMA, PERCENT slope, 2-bar lookback, FLAT band +/-0.02

Two measurements:
  (1) GROUP DELAY: lag (bars/minutes) between price turn (local extreme of close)
      and 9-SMA slope sign flip. Cross-correlate d(price) vs d(SMA) for phase lag.
  (2) CHASING: at CRWD HOD and through reversion, compare extension |price - line|
      measured 3 ways (9-SMA, VWAP-from-open, 20-period MA). How much each line
      "moved toward" price (rose) during the spike — i.e. how much it chases.

No new strategy thresholds invented. Measure and report only.
"""
import sys, os, datetime as dt, warnings
warnings.filterwarnings('ignore')
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import numpy as np, pandas as pd, pytz
from tools.fetch_polygon import fetch_bars

FAST, LB, FLAT, SLOW = 9, 2, 0.02, 20
NY = pytz.timezone('America/New_York')
EXT_START, EXT_END = '04:00', '20:00'
RTH_START, RTH_END = '09:30', '16:00'


def tz(df):
    if df.index.tz is None:
        df.index = df.index.tz_localize('UTC')
    df.index = df.index.tz_convert(NY)
    return df


def rs(df, rule):
    return df.resample(rule).agg({'open': 'first', 'high': 'max', 'low': 'min',
                                  'close': 'last', 'volume': 'sum',
                                  'vwap': 'mean'}).dropna()


def slope_pct(c):
    """9-SMA, 2-bar PERCENT slope. Returns (slope_pct_series, ma_series)."""
    ma = c.rolling(FAST).mean()
    sl = ((ma - ma.shift(LB)) / ma) * 100
    return sl, ma


def state_of(v):
    if pd.isna(v): return 'n/a'
    return 'UP' if v > FLAT else 'DOWN' if v < -FLAT else 'FLAT'


def load_30m(ticker, date):
    """Build ext-hours 30m bars exactly like cascade_grade_day: 1m -> resample 30min."""
    tgt = pd.Timestamp(date).date()
    d3 = (tgt - dt.timedelta(days=6)).strftime('%Y-%m-%d')
    m1 = tz(fetch_bars(ticker, 'minute', d3, date, multiplier=1)).between_time(EXT_START, EXT_END)
    bars30 = rs(m1, '30min')
    return m1, bars30, tgt


def vwap_from_open(m1_today):
    """Cumulative VWAP anchored to RTH open (09:30), typical price, on 1m bars."""
    rth = m1_today.between_time(RTH_START, RTH_END).copy()
    tp = (rth['high'] + rth['low'] + rth['close']) / 3.0
    cum_pv = (tp * rth['volume']).cumsum()
    cum_v = rth['volume'].cumsum()
    return (cum_pv / cum_v)


# ============================================================================
# PART 1 — GROUP DELAY
# ============================================================================
def normxcorr(a, b, maxlag):
    """corr of a[:n-L] vs b[L:] for L=0..maxlag. b trails a => peak at L = lag."""
    a = (a - a.mean()) / (a.std() + 1e-12)
    b = (b - b.mean()) / (b.std() + 1e-12)
    n = len(a)
    out = {}
    for L in range(0, maxlag + 1):
        if n - L < 4:
            break
        out[L] = np.corrcoef(a[:n - L], b[L:])[0, 1]
    return out


def measure_lag_one_tf(cl, tf_label, bar_min, tgt):
    """
    cl = ext-hours close series for ONE timeframe (already warmed from premarket).
    Measures, on today's RTH window:
      (A) discrete event lag: price local extreme of close -> next 9-SMA slope sign flip
      (B) cross-correlation phase lag of d(price) vs d(9-SMA) in bars
    Returns dict of bar-unit lags. The 9-SMA group-delay property is in BAR units
    (theoretical (N-1)/2 = 4 bars), so this is comparable across TFs.
    """
    sl, ma = slope_pct(cl)
    mask = (cl.index.date == tgt) & (cl.index.time >= dt.time(9, 30)) & (cl.index.time <= dt.time(16, 0))
    cd, sld, mad = cl[mask], sl[mask], ma[mask]
    cd, sld, mad = cd.dropna(), sld.dropna(), mad.dropna()
    cd = cd.loc[mad.index]  # align
    n = len(cd)
    print(f"\n  --- {tf_label} (1 bar = {bar_min} min) | {n} RTH bars ---")
    if n < FAST + LB + 3:
        print(f"      too few bars to measure lag on {tf_label}")
        return None

    cv = cd.values
    # (A) discrete events. Use a small prominence guard so micro-wiggles don't dominate.
    rng = np.nanmax(cv) - np.nanmin(cv)
    prom = 0.0005 * np.nanmean(cv)  # ~5bps of price; tiny, just kills flat ties
    extremes = []
    for k in range(1, len(cv) - 1):
        if cv[k] > cv[k - 1] and cv[k] >= cv[k + 1] and (cv[k] - min(cv[k-1], cv[k+1])) > prom:
            extremes.append((k, cd.index[k], 'local_high', cv[k]))
        elif cv[k] < cv[k - 1] and cv[k] <= cv[k + 1] and (max(cv[k-1], cv[k+1]) - cv[k]) > prom:
            extremes.append((k, cd.index[k], 'local_low', cv[k]))

    slv = sld.values
    flips = []
    for k in range(1, len(slv)):
        if np.sign(slv[k]) != np.sign(slv[k - 1]):
            flips.append((k, sld.index[k], 'to_UP' if slv[k] > 0 else 'to_DOWN'))

    event_lags = []
    for k, ts, kind, px in extremes:
        want = 'to_DOWN' if kind == 'local_high' else 'to_UP'
        cand = [(fk, fts, fd) for fk, fts, fd in flips if fk >= k and fd == want]
        if cand:
            fk, fts, fd = cand[0]
            event_lags.append(fk - k)
    n_high = sum(1 for e in extremes if e[2] == 'local_high')
    n_low = sum(1 for e in extremes if e[2] == 'local_low')
    print(f"      (A) discrete: {len(extremes)} price extremes ({n_high}H/{n_low}L), "
          f"{len(flips)} slope flips, {len(event_lags)} matched")
    ev_bars = np.mean(event_lags) if event_lags else np.nan
    ev_med = np.median(event_lags) if event_lags else np.nan
    if event_lags:
        print(f"          event lag: mean {ev_bars:.2f} bars ({ev_bars*bar_min:.0f} min), "
              f"median {ev_med:.1f} bars ({ev_med*bar_min:.0f} min)  raw={event_lags}")

    # (B) cross-correlation, d(price) vs d(9-SMA)
    dp = np.diff(cd.values)
    dm = np.diff(mad.values)
    maxlag = min(8, len(dp) - 4)
    xc_bars = np.nan
    if maxlag >= 1:
        xc = normxcorr(dp, dm, maxlag)
        # restrict "best" to a sane window (0..6 bars); end-effects can spike far lags
        sane = {L: v for L, v in xc.items() if L <= 6}
        best = max(sane, key=sane.get)
        xc_bars = best
        line = "  ".join(f"L{L}:{xc[L]:+.2f}" for L in sorted(xc) if L <= 6)
        print(f"      (B) xcorr d(px)~d(9SMA): {line}")
        print(f"          peak at L={best} bars ({best*bar_min} min), corr {xc[best]:+.2f}")
    return {'tf': tf_label, 'bar_min': bar_min, 'event_bars': ev_bars,
            'event_med_bars': ev_med, 'xcorr_bars': xc_bars,
            'n_events': len(event_lags)}


def part1_group_delay(ticker, date):
    print("\n" + "=" * 90)
    print(f"PART 1 — GROUP DELAY (lag: price turn -> 9-SMA slope flip)  {ticker} {date}")
    print("Theoretical group delay of a 9-SMA = (N-1)/2 = 4 bars (in bar units, any TF).")
    print("=" * 90)
    m1, bars30, tgt = load_30m(ticker, date)

    # Build the entry-TF close series exactly like cascade_grade_day: 1m, 5m, 30m
    series = {
        '1m':  (m1['close'], 1),
        '5m':  (rs(m1, '5min')['close'], 5),
        '30m': (bars30['close'], 30),
    }

    # Always show the coarse 30m tape (this is the TF the framework reads for direction)
    c = bars30['close']; sl, ma = slope_pct(c)
    mask = (c.index.date == tgt) & (c.index.time >= dt.time(9, 30)) & (c.index.time <= dt.time(16, 0))
    cd, sld, mad = c[mask], sl[mask], ma[mask]
    print(f"\n30m tape (today RTH) — note the slope STATE barely/never flips intraday:")
    print(f"{'time':>6} {'close':>9} {'9SMA':>9} {'slope%':>8} {'state':>6}")
    for ts in cd.index:
        print(f"{ts.strftime('%H:%M'):>6} {cd[ts]:>9.2f} {mad[ts]:>9.2f} {sld[ts]:>+8.3f} {state_of(sld[ts]):>6}")

    results = {}
    for tf, (cl, bm) in series.items():
        r = measure_lag_one_tf(cl, tf, bm, tgt)
        if r:
            results[tf] = r
    return results


# ============================================================================
# PART 2 — CHASING / extension understatement (CRWD)
# ============================================================================
def part2_chasing(ticker, date, hod_time='10:04', revert_to='10:30'):
    print("\n" + "=" * 90)
    print(f"PART 2 — CHASING / extension understatement  {ticker} {date}")
    print("=" * 90)
    m1, bars30, tgt = load_30m(ticker, date)

    c30 = bars30['close']
    sl30, ma30 = slope_pct(c30)          # 30m 9-SMA
    slow30 = c30.rolling(SLOW).mean()    # 30m 20-period MA (steadier line)

    m1t = m1[m1.index.date == tgt].between_time(RTH_START, RTH_END)
    vwap = vwap_from_open(m1t)            # 1m cumulative VWAP from open

    # Align the 30m lines onto the 1m grid (forward-fill: line value as-known at each minute)
    ma9_1m = ma30.reindex(m1t.index, method='ffill')
    ma20_1m = slow30.reindex(m1t.index, method='ffill')
    px = m1t['close']

    print(f"\n30m line values across the morning (as known at each 1m, ffill):")
    print(f"  9-SMA(30m) warms with premarket seed; 20-SMA(30m) needs {SLOW} 30m bars.")

    # --- timeline table around HOD and reversion ---
    open_ts = m1t.index[0]
    hod_ts = m1t['high'].idxmax()
    hod_px = m1t['high'].max()
    print(f"\n  RTH open  : {open_ts.strftime('%H:%M')}  px {px.iloc[0]:.2f}")
    print(f"  HOD       : {hod_ts.strftime('%H:%M')}  high {hod_px:.2f}")

    # show a window from open through reversion
    def extrow(ts):
        p = px.asof(ts)
        v = vwap.asof(ts)
        m9 = ma9_1m.asof(ts)
        m20 = ma20_1m.asof(ts)
        return p, v, m9, m20

    print(f"\n  EXTENSION measured 3 ways  ext = price - line  (positive = price above line)")
    print(f"  {'time':>6} {'price':>9} {'|p-9SMA|':>9} {'|p-VWAP|':>9} {'|p-20SMA|':>10}"
          f"  {'9SMA':>9} {'VWAP':>9} {'20SMA':>9}")
    # sample minutes: open, every ~10 min to HOD, HOD, then reversion every few min
    times = []
    cur = open_ts
    while cur <= m1t.index[-1]:
        times.append(cur)
        cur = cur + pd.Timedelta(minutes=5)
    # ensure HOD included
    for ts in sorted(set(times) | {hod_ts}):
        if ts < open_ts or ts > pd.Timestamp(f"{date} 11:00", tz=NY):
            continue
        p, v, m9, m20 = extrow(ts)
        if any(pd.isna(x) for x in (p, v, m9, m20)):
            tag = '  <-- HOD' if ts == hod_ts else ''
            print(f"  {ts.strftime('%H:%M'):>6} {p:>9.2f} {'n/a':>9} "
                  f"{abs(p-v):>9.2f} {'n/a':>10}  {'n/a':>9} {v:>9.2f} {'n/a':>9}{tag}")
            continue
        tag = '  <-- HOD' if ts == hod_ts else ''
        print(f"  {ts.strftime('%H:%M'):>6} {p:>9.2f} {abs(p-m9):>9.2f} "
              f"{abs(p-v):>9.2f} {abs(p-m20):>10.2f}  {m9:>9.2f} {v:>9.2f} {m20:>9.2f}{tag}")

    # --- core quantification: over the 09:30 -> HOD run, how much did each line RISE? ---
    p_open = px.asof(open_ts)
    p_hod = hod_px
    spike_pts = p_hod - p_open

    def rise(line):
        a = line.asof(open_ts); b = line.asof(hod_ts)
        if pd.isna(a) or pd.isna(b): return np.nan, np.nan
        r = b - a
        return r, (r / spike_pts * 100 if spike_pts else np.nan)

    r9, f9 = rise(ma9_1m)
    rv, fv = rise(vwap)
    r20, f20 = rise(ma20_1m)

    print(f"\n  RUN: {open_ts.strftime('%H:%M')} -> HOD {hod_ts.strftime('%H:%M')}  "
          f"price {p_open:.2f} -> {p_hod:.2f}  = +{spike_pts:.2f} pts")
    print(f"  How much each LINE rose over that run (and % of the spike it 'absorbed'/chased):")
    print(f"    9-SMA(30m)  rose {r9:>7.2f} pts  = {f9:>5.1f}% of the {spike_pts:.2f}-pt spike")
    print(f"    VWAP(open)  rose {rv:>7.2f} pts  = {fv:>5.1f}% of the spike")
    print(f"    20-SMA(30m) rose {r20 if not pd.isna(r20) else float('nan'):>7.2f} pts  "
          f"= {f20:>5.1f}% of the spike" if not pd.isna(r20) else
          f"    20-SMA(30m) rose     n/a (needs {SLOW} 30m bars; not warmed this early)")

    # --- extension AT the HOD measured each way (the 'ruler' difference) ---
    eh9 = p_hod - ma9_1m.asof(hod_ts)
    ehv = p_hod - vwap.asof(hod_ts)
    eh20 = (p_hod - ma20_1m.asof(hod_ts)) if not pd.isna(ma20_1m.asof(hod_ts)) else np.nan
    print(f"\n  EXTENSION AT HOD (the ruler reading you'd fade against):")
    print(f"    vs 9-SMA(30m) : {eh9:>7.2f} pts  ({eh9/p_hod*100:>5.2f}%)")
    print(f"    vs VWAP(open) : {ehv:>7.2f} pts  ({ehv/p_hod*100:>5.2f}%)")
    if not pd.isna(eh20):
        print(f"    vs 20-SMA(30m): {eh20:>7.2f} pts  ({eh20/p_hod*100:>5.2f}%)")
    else:
        print(f"    vs 20-SMA(30m): n/a (not warmed)")
    print(f"  => The 9-SMA understates the stretch by {ehv-eh9:>.2f} pts vs VWAP "
          f"(it had chased {r9:.2f} pts up into the spike).")

    # --- COVER TARGET drift: where is each 'mean' line at HOD vs at the reversion low ---
    # find the post-HOD reversion low within the next ~40 min
    post = px[(px.index > hod_ts) & (px.index <= hod_ts + pd.Timedelta(minutes=40))]
    if len(post):
        rev_ts = post.idxmin(); rev_px = post.min()
        print(f"\n  COVER-TARGET DRIFT (the mean you'd cover at is itself moving):")
        print(f"    reversion low {rev_px:.2f} @ {rev_ts.strftime('%H:%M')}")
        for nm, line in [('9-SMA(30m)', ma9_1m), ('VWAP(open)', vwap), ('20-SMA(30m)', ma20_1m)]:
            a = line.asof(hod_ts); b = line.asof(rev_ts)
            if pd.isna(a) or pd.isna(b):
                print(f"    {nm:>11}: n/a")
                continue
            print(f"    {nm:>11}: {a:.2f} (@HOD) -> {b:.2f} (@rev)  moved {b-a:+.2f} pts "
                  f"in {int((rev_ts-hod_ts).total_seconds()/60)} min")

    return {'spike_pts': spike_pts, 'f9': f9, 'fv': fv,
            'ext_hod_9sma': eh9, 'ext_hod_vwap': ehv,
            'understate_pts': ehv - eh9, 'chase_pts_9sma': r9}


if __name__ == '__main__':
    print("#" * 90)
    print("# SMA LAG + GROUP DELAY + CHASING — empirical study (ext-hours bars, 9-SMA 2-bar pct slope)")
    print("#" * 90)

    # PART 1: group delay on two specimens
    r_crwd = part1_group_delay('CRWD', '2026-06-04')
    r_mrvl = part1_group_delay('MRVL', '2026-06-03')

    # PART 2: chasing on CRWD
    r_chase = part2_chasing('CRWD', '2026-06-04')

    print("\n" + "#" * 90)
    print("# SUMMARY — group delay measured in BAR units (theory: (9-1)/2 = 4 bars)")
    print("#" * 90)
    print(f"{'specimen':>16} {'TF':>4} {'bar_min':>7} {'event_lag':>16} {'xcorr_lag':>14} {'n_ev':>5}")
    for name, res in [('CRWD 2026-06-04', r_crwd), ('MRVL 2026-06-03', r_mrvl)]:
        for tf in ('1m', '5m', '30m'):
            r = res.get(tf)
            if not r: continue
            eb = r['event_bars']; xb = r['xcorr_bars']; bm = r['bar_min']
            ev_s = f"{eb:.1f}b={eb*bm:.0f}min" if not pd.isna(eb) else "n/a"
            xc_s = f"{xb:.0f}b={xb*bm:.0f}min" if not pd.isna(xb) else "n/a"
            print(f"{name:>16} {tf:>4} {bm:>7} {ev_s:>16} {xc_s:>14} {r['n_events']:>5}")
    print(f"\nCHASING (CRWD 06-04):")
    print(f"  09:30->HOD spike {r_chase['spike_pts']:.2f} pts.")
    print(f"  Fraction of the spike each line CHASED (rose into it):")
    print(f"     9-SMA(30m) {r_chase['f9']:.1f}%   VWAP(open) {r_chase['fv']:.1f}%")
    print(f"  Extension reading AT HOD: vs 9-SMA {r_chase['ext_hod_9sma']:.2f} pts | "
          f"vs VWAP {r_chase['ext_hod_vwap']:.2f} pts")
    print(f"  9-SMA shows a LARGER number here only because it sits lower (stale/lagging), "
          f"NOT because it is steadier.")
