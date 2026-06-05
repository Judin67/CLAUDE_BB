#!/usr/bin/env python
# coding: utf-8
"""
regime_separation_study.py
--------------------------
EMPIRICAL STUDY — ML REGIME SEPARATION.

Tests whether "MR-within-trend" is statistically a distinct regime from
trend-continuation and parabolic-exhaustion, by building a per-bar feature
matrix over RTH for four labeled anchor sessions, then clustering (k=3).

Methodology mirrors cascade_grade_day.py EXACTLY:
  - tz() -> America/New_York
  - between_time('04:00','20:00') extended-hours seed
  - rs() resample per TF
  - slope_pct() = 9-SMA, 2-bar lookback, PERCENT slope
  - FLAT band +/-0.02

Per-bar features are computed at 1-minute resolution over RTH (09:30-16:00),
with every TF's slope/SMA forward-filled from its ext-hours-seeded series.

Anchors / labels (ground truth from Judin's logs):
  CRWD 2026-06-04 -> MR_WITHIN_TREND
  DELL 2026-06-01 -> TREND_PULLBACK
  MRVL 2026-06-03 -> PARABOLIC
  MRVL 2026-06-04 -> TREND_CHOP  (trend-up shallow chop; continuation family)
"""
import sys, os, datetime as dt, warnings
warnings.filterwarnings('ignore')
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import numpy as np, pandas as pd, pytz
from tools.fetch_polygon import fetch_bars

FAST, LB, FLAT = 9, 2, 0.02
NY = pytz.timezone('America/New_York')
EXT_START, EXT_END = '04:00', '20:00'
RTH_START, RTH_END = '09:30', '16:00'

ANCHORS = [
    ('CRWD', '2026-06-04', 'MR_WITHIN_TREND'),
    ('DELL', '2026-06-01', 'TREND_PULLBACK'),
    ('MRVL', '2026-06-03', 'PARABOLIC'),
    ('MRVL', '2026-06-04', 'TREND_CHOP'),
]


def slope_pct(c):
    """9-SMA, 2-bar lookback, percent slope. Returns (slope_series, ma_series)."""
    ma = c.rolling(FAST).mean()
    return ((ma - ma.shift(LB)) / ma) * 100, ma


def rs(df, rule):
    return df.resample(rule).agg({'open': 'first', 'high': 'max', 'low': 'min',
                                  'close': 'last', 'volume': 'sum'}).dropna()


def tz(df):
    if df.index.tz is None:
        df.index = df.index.tz_localize('UTC')
    df.index = df.index.tz_convert(NY)
    return df


def atr_series(df_ohlc, n=14):
    """Wilder-style ATR on the given bar set (used on the 30m TF)."""
    h, l, c = df_ohlc['high'], df_ohlc['low'], df_ohlc['close']
    pc = c.shift(1)
    tr = pd.concat([(h - l), (h - pc).abs(), (l - pc).abs()], axis=1).max(axis=1)
    return tr.rolling(n).mean()


def asof(series, ts):
    """Last value at-or-before ts (forward-fill semantics, no lookahead)."""
    if series is None:
        return np.nan
    sub = series[series.index <= ts]
    return sub.iloc[-1] if len(sub) else np.nan


def build_features_for_anchor(ticker, date, label):
    tgt = pd.Timestamp(date).date()
    d3  = (tgt - dt.timedelta(days=6)).strftime('%Y-%m-%d')
    d6  = (tgt - dt.timedelta(days=12)).strftime('%Y-%m-%d')
    d130 = (tgt - dt.timedelta(days=200)).strftime('%Y-%m-%d')

    m1  = tz(fetch_bars(ticker, 'minute', d3,  date, multiplier=1)).between_time(EXT_START, EXT_END)
    hr  = tz(fetch_bars(ticker, 'hour',   d6,  date, multiplier=1)).between_time(EXT_START, EXT_END)
    day = tz(fetch_bars(ticker, 'day',    d130, date, multiplier=1))

    bars = {
        '1m':  m1,
        '5m':  rs(m1, '5min'),
        '30m': rs(m1, '30min'),
        '4h':  rs(hr, '4h') if len(hr) else None,
        'Daily': day if len(day) else None,
    }
    # close series per TF
    close = {tf: (b['close'] if b is not None else None) for tf, b in bars.items()}

    slopes, smas = {}, {}
    for tf, cl in close.items():
        if cl is None or len(cl.dropna()) < FAST + LB:
            slopes[tf] = None; smas[tf] = None; continue
        sl, ma = slope_pct(cl)
        slopes[tf] = sl.dropna(); smas[tf] = ma.dropna()

    # 30m ATR (for price-minus-30mSMA in ATR units)
    atr30 = atr_series(bars['30m'], 14) if bars['30m'] is not None else None

    # Iterate over today's RTH at 1m resolution
    day1m = m1[m1.index.date == tgt].between_time(RTH_START, RTH_END)
    rows = []
    s30 = slopes['30m']
    for ts in day1m.index:
        px = day1m['close'].loc[ts]

        sl30 = asof(slopes['30m'], ts)
        sl5  = asof(slopes['5m'],  ts)
        sl1  = asof(slopes['1m'],  ts)
        sl4h = asof(slopes['4h'],  ts)
        slD  = asof(slopes['Daily'], ts)
        ma30 = asof(smas['30m'], ts)
        atrv = asof(atr30, ts)

        # sign-agreement across the 3 entry TFs (30m,5m,1m): +1 all-up, -1 all-down, frac otherwise
        def sgn(v):
            if pd.isna(v): return 0
            return 1 if v > FLAT else -1 if v < -FLAT else 0
        signs = [sgn(sl30), sgn(sl5), sgn(sl1)]
        sign_agree = sum(signs) / 3.0       # in [-1, 1]; |.|=1 means full agreement

        # 30m slope curvature = delta of 30m slope vs the prior 30m slope value (per-30m-bar)
        if s30 is not None:
            past = s30[s30.index <= ts]
            curv30 = (past.iloc[-1] - past.iloc[-2]) if len(past) >= 2 else np.nan
        else:
            curv30 = np.nan

        # price minus 30m SMA, in 30m-ATR units
        px_minus_sma_atr = ((px - ma30) / atrv) if (not pd.isna(ma30) and not pd.isna(atrv) and atrv > 0) else np.nan

        # reversion depth from recent intraday extreme (running HOD/LOD up to ts), in ATR units.
        # signed: how far price has reverted DOWN from the running high (negative) /
        # UP from the running low (positive). We report depth-from-HOD as the canonical
        # "fade the spike" coordinate: (px - runHOD)/ATR  (<=0).
        upto = day1m.loc[:ts]
        run_hod = upto['high'].max()
        run_lod = upto['low'].min()
        rev_from_hod_atr = ((px - run_hod) / atrv) if (not pd.isna(atrv) and atrv > 0) else np.nan
        rev_from_lod_atr = ((px - run_lod) / atrv) if (not pd.isna(atrv) and atrv > 0) else np.nan

        rows.append({
            'ticker': ticker, 'date': date, 'label': label, 'ts': ts, 'px': px,
            'sl30': sl30, 'sl5': sl5, 'sl1': sl1, 'sl4h': sl4h, 'slD': slD,
            'sign_agree': sign_agree, 'curv30': curv30,
            'px_minus_sma_atr': px_minus_sma_atr,
            'rev_from_hod_atr': rev_from_hod_atr, 'rev_from_lod_atr': rev_from_lod_atr,
        })
    return pd.DataFrame(rows)


# Feature columns used for clustering
FEATURES = ['sl30', 'sl5', 'sl1', 'sl4h', 'slD', 'sign_agree', 'curv30',
            'px_minus_sma_atr', 'rev_from_hod_atr', 'rev_from_lod_atr']


def main():
    print("Fetching + building per-bar feature matrix (ext-hours seeded, 1m RTH)...\n")
    frames = []
    for t, d, lab in ANCHORS:
        df = build_features_for_anchor(t, d, lab)
        print(f"  {t} {d} [{lab}]: {len(df)} RTH bars, "
              f"{df[FEATURES].dropna().shape[0]} complete-feature bars")
        frames.append(df)
    full = pd.concat(frames, ignore_index=True)

    # Drop bars with any NaN feature (warmup edges)
    work = full.dropna(subset=FEATURES).reset_index(drop=True)
    print(f"\nTotal usable bars: {len(work)}  (from {len(full)} raw)")
    print("Per-label bar counts:")
    print(work['label'].value_counts().to_string())

    X = work[FEATURES].values.astype(float)

    # ---- standardize (z-score) ----
    used_sklearn = True
    try:
        from sklearn.preprocessing import StandardScaler
        from sklearn.cluster import KMeans
        from sklearn.mixture import GaussianMixture
        from sklearn.metrics import silhouette_score, silhouette_samples
        Xz = StandardScaler().fit_transform(X)
    except Exception as e:
        used_sklearn = False
        print(f"\n[sklearn unavailable: {e}] -> hand-rolling z-score + KMeans/silhouette in numpy")
        mu, sd = X.mean(0), X.std(0); sd[sd == 0] = 1.0
        Xz = (X - mu) / sd

    print(f"\nMethod: {'sklearn (StandardScaler + KMeans + GaussianMixture + silhouette)' if used_sklearn else 'numpy hand-rolled (z-score + Lloyd KMeans + silhouette)'}")
    print("Features:", FEATURES)

    K = 3
    if used_sklearn:
        km = KMeans(n_clusters=K, n_init=25, random_state=42).fit(Xz)
        km_lab = km.labels_
        sil = silhouette_score(Xz, km_lab)
        sil_samp = silhouette_samples(Xz, km_lab)
        gm = GaussianMixture(n_components=K, covariance_type='full',
                             n_init=10, random_state=42).fit(Xz)
        gm_lab = gm.predict(Xz)
        try:
            gm_sil = silhouette_score(Xz, gm_lab)
        except Exception:
            gm_sil = float('nan')
        centroids = km.cluster_centers_
    else:
        km_lab, centroids, sil, sil_samp = numpy_kmeans_sil(Xz, K, seed=42)
        gm_lab, gm_sil = km_lab, sil  # no GMM in fallback

    work = work.copy()
    work['km'] = km_lab
    work['gm'] = gm_lab if used_sklearn else km_lab
    work['sil'] = sil_samp

    # ---------- (1) cluster -> label crosstab ----------
    print("\n" + "=" * 78)
    print("(1) k=3 CLUSTER  x  TRUE-LABEL CONFUSION (KMeans)")
    print("=" * 78)
    ct = pd.crosstab(work['km'], work['label'])
    print(ct.to_string())
    print("\nRow-normalized (what each cluster is made of):")
    print((ct.div(ct.sum(1), axis=0) * 100).round(1).astype(str).add('%').to_string())
    print("\nColumn-normalized (where each regime's bars land):")
    print((ct.div(ct.sum(0), axis=1) * 100).round(1).astype(str).add('%').to_string())

    # map each cluster to its plurality label
    cl2lab = ct.idxmax(axis=1).to_dict()
    print("\nCluster -> plurality label:")
    for c in sorted(cl2lab): print(f"  cluster {c}: {cl2lab[c]}  (n={ct.loc[c].sum()})")

    # GMM crosstab (sklearn only)
    if used_sklearn:
        print("\n--- GaussianMixture (k=3) confusion for cross-check ---")
        ctg = pd.crosstab(work['gm'], work['label'])
        print(ctg.to_string())
        print(f"GMM silhouette: {gm_sil:.3f}")

    # ---------- separation metrics ----------
    print("\n" + "=" * 78)
    print("SEPARATION METRICS")
    print("=" * 78)
    print(f"KMeans silhouette (overall): {sil:.3f}   [-1..1; >0.5 strong, 0.25-0.5 weak, <0.25 poor]")
    print("Mean silhouette per TRUE label (how internally cohesive / separable each regime is):")
    print(work.groupby('label')['sil'].mean().round(3).to_string())

    # ---------- centroid distances in z-space between TRUE-LABEL centroids ----------
    print("\nTRUE-LABEL centroids in z-space, pairwise Euclidean distance:")
    labs = sorted(work['label'].unique())
    cents = {L: work.loc[work['label'] == L, FEATURES].pipe(
                lambda d: (d.values - X.mean(0)) / (X.std(0) if (X.std(0) != 0).all() else 1)).mean(0)
             for L in labs}
    # use the same z-transform consistently
    mu_, sd_ = X.mean(0), X.std(0); sd_[sd_ == 0] = 1.0
    cents = {L: ((work.loc[work['label'] == L, FEATURES].values - mu_) / sd_).mean(0) for L in labs}
    dmat = pd.DataFrame(index=labs, columns=labs, dtype=float)
    for a in labs:
        for b in labs:
            dmat.loc[a, b] = float(np.linalg.norm(cents[a] - cents[b]))
    print(dmat.round(2).to_string())

    # ---------- (2) most-separating features for MR_WITHIN_TREND ----------
    print("\n" + "=" * 78)
    print("(2) FEATURES THAT MOST SEPARATE MR_WITHIN_TREND FROM THE REST")
    print("=" * 78)
    mr = work['label'] == 'MR_WITHIN_TREND'
    other = ~mr
    rows = []
    for i, f in enumerate(FEATURES):
        a = work.loc[mr, f].values
        b = work.loc[other, f].values
        ma_, mb_ = a.mean(), b.mean()
        sp = np.sqrt(((a.var() * len(a)) + (b.var() * len(b))) / (len(a) + len(b)))  # pooled-ish sd
        sp = sp if sp > 0 else 1e-9
        cohen_d = (ma_ - mb_) / sp
        rows.append((f, ma_, mb_, ma_ - mb_, cohen_d))
    sep = pd.DataFrame(rows, columns=['feature', 'MR_mean', 'other_mean', 'diff', 'cohen_d'])
    sep['abs_d'] = sep['cohen_d'].abs()
    sep = sep.sort_values('abs_d', ascending=False)
    pd.set_option('display.width', 200)
    print(sep[['feature', 'MR_mean', 'other_mean', 'diff', 'cohen_d']].round(3).to_string(index=False))
    print("\nTop discriminators (|Cohen d| desc):", ', '.join(sep['feature'].head(3).tolist()))

    # raw per-label feature means table for transparency
    print("\nPer-label RAW feature means (un-standardized):")
    print(work.groupby('label')[FEATURES].mean().round(3).T.to_string())

    # ---------- (3) confusion-style summary: do MR bars get their own cluster? ----------
    print("\n" + "=" * 78)
    print("(3) DO MR_WITHIN_TREND BARS LAND IN THE TREND CLUSTER OR THEIR OWN?")
    print("=" * 78)
    mr_clusters = work.loc[mr, 'km'].value_counts()
    dom_cluster = mr_clusters.idxmax()
    dom_frac = mr_clusters.max() / mr_clusters.sum()
    dom_lab = cl2lab[dom_cluster]
    # what fraction of that dominant cluster is actually MR?
    purity = (work.loc[work['km'] == dom_cluster, 'label'] == 'MR_WITHIN_TREND').mean()
    print(f"MR_WITHIN_TREND bar distribution across clusters:\n{mr_clusters.to_string()}")
    print(f"\nDominant MR cluster = {dom_cluster} (holds {dom_frac*100:.1f}% of MR bars).")
    print(f"That cluster's plurality label = {dom_lab}.")
    print(f"That cluster's MR-purity = {purity*100:.1f}% (fraction of its bars that are MR).")
    own = (dom_lab == 'MR_WITHIN_TREND')
    print(f"\n=> MR bars {'OCCUPY THEIR OWN cluster' if own else 'FALL INTO the ' + str(dom_lab) + ' cluster'}.")

    # also: of the TREND-family clusters, do MR bars contaminate them?
    trend_fam = {'TREND_PULLBACK', 'TREND_CHOP'}
    trend_clusters = [c for c, L in cl2lab.items() if L in trend_fam]
    mr_in_trend = work.loc[mr, 'km'].isin(trend_clusters).mean()
    para_clusters = [c for c, L in cl2lab.items() if L == 'PARABOLIC']
    mr_in_para = work.loc[mr, 'km'].isin(para_clusters).mean()
    print(f"\nShare of MR bars sitting in a TREND-family cluster:   {mr_in_trend*100:.1f}%")
    print(f"Share of MR bars sitting in the PARABOLIC cluster:    {mr_in_para*100:.1f}%")

    # ---------- ROBUSTNESS: confound check ----------
    # slD/sl4h absolute magnitudes are partly TICKER-specific (CRWD daily slope just
    # happens to be smaller than MRVL/DELL). Re-cluster on framework-shape features only:
    # the ones that encode "high-TF aligned UP while low-TF stretched & reverting",
    # WITHOUT the raw higher-TF slope magnitude. If MR still separates, the separation
    # is a regime property, not a per-name slope-scale artifact.
    print("\n" + "=" * 78)
    print("ROBUSTNESS CHECK A — drop raw higher-TF slope magnitudes (slD, sl4h)")
    print("  cluster on shape features only: sign_agree, curv30, px_minus_sma_atr,")
    print("  rev_from_hod_atr, rev_from_lod_atr, sl30, sl5, sl1")
    print("=" * 78)
    SHAPE = ['sign_agree', 'curv30', 'px_minus_sma_atr', 'rev_from_hod_atr',
             'rev_from_lod_atr', 'sl30', 'sl5', 'sl1']
    if used_sklearn:
        from sklearn.preprocessing import StandardScaler as _SS
        from sklearn.cluster import KMeans as _KM
        from sklearn.metrics import silhouette_score as _ss
        Xs = _SS().fit_transform(work[SHAPE].values.astype(float))
        kl = _KM(n_clusters=3, n_init=25, random_state=42).fit_predict(Xs)
        ssA = _ss(Xs, kl)
    else:
        mu2, sd2 = work[SHAPE].values.mean(0), work[SHAPE].values.std(0); sd2[sd2 == 0] = 1
        Xs = (work[SHAPE].values - mu2) / sd2
        kl, _, ssA, _ = numpy_kmeans_sil(Xs, 3, seed=42)
    work['kmA'] = kl
    ctA = pd.crosstab(work['kmA'], work['label'])
    print(ctA.to_string())
    cl2labA = ctA.idxmax(axis=1).to_dict()
    mrA = work.loc[mr, 'kmA'].value_counts()
    domA = mrA.idxmax()
    print(f"\nsilhouette (shape-only): {ssA:.3f}")
    print(f"MR dominant cluster = {domA}, plurality label = {cl2labA[domA]}, "
          f"holds {mrA.max()/mrA.sum()*100:.1f}% of MR bars, "
          f"purity {(work.loc[work['kmA']==domA,'label']=='MR_WITHIN_TREND').mean()*100:.1f}%")

    # ---------- ROBUSTNESS B: leave-one-anchor cross-check ----------
    # The MR class is ONE session (CRWD 6/4). 75 bars = 1 day, autocorrelated.
    # So "its own cluster" could just mean "CRWD-the-name separates", not "MR-the-regime".
    # We CANNOT resolve this with one MR session — flag it explicitly.
    print("\n" + "=" * 78)
    print("ROBUSTNESS CHECK B — sample-honesty note")
    print("=" * 78)
    print("MR_WITHIN_TREND = 75 bars from a SINGLE session (CRWD 2026-06-04).")
    print("75 intraday 1m bars are heavily autocorrelated -> effective N is closer to")
    print("a handful of independent observations, NOT 75. 'Own cluster at 100% purity'")
    print("is consistent with a distinct regime, but is ALSO consistent with 'CRWD that")
    print("day simply had a lower Daily-slope scale than MRVL/DELL'. One MR anchor cannot")
    print("separate regime-identity from name/day-identity. This is EXPLORATORY evidence.")

    # save matrix for reference
    out = os.path.join(os.path.dirname(__file__), '..', '.tmp')
    os.makedirs(out, exist_ok=True)
    work.to_csv(os.path.join(out, 'regime_feature_matrix.csv'), index=False)
    print(f"\nFeature matrix saved -> .tmp/regime_feature_matrix.csv")
    print(f"\nMETHOD_USED={'sklearn' if used_sklearn else 'numpy'}")


def numpy_kmeans_sil(Xz, K, seed=0, iters=200):
    rng = np.random.default_rng(seed)
    # k-means++ init
    n = len(Xz)
    idx = [rng.integers(n)]
    for _ in range(1, K):
        d2 = np.min([((Xz - Xz[c]) ** 2).sum(1) for c in idx], axis=0)
        probs = d2 / d2.sum()
        idx.append(rng.choice(n, p=probs))
    C = Xz[idx].copy()
    lab = np.zeros(n, dtype=int)
    for _ in range(iters):
        D = np.stack([((Xz - C[k]) ** 2).sum(1) for k in range(K)], axis=1)
        new = D.argmin(1)
        if (new == lab).all():
            lab = new; break
        lab = new
        for k in range(K):
            if (lab == k).any():
                C[k] = Xz[lab == k].mean(0)
    # silhouette
    sil_samp = np.zeros(n)
    for i in range(n):
        same = lab == lab[i]
        same[i] = False
        a = np.linalg.norm(Xz[same] - Xz[i], axis=1).mean() if same.any() else 0.0
        b = np.inf
        for k in range(K):
            if k == lab[i]: continue
            m = lab == k
            if m.any():
                b = min(b, np.linalg.norm(Xz[m] - Xz[i], axis=1).mean())
        sil_samp[i] = 0.0 if max(a, b) == 0 else (b - a) / max(a, b)
    return lab, C, sil_samp.mean(), sil_samp


if __name__ == '__main__':
    main()
