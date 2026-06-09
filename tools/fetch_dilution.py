#!/usr/bin/env python
# coding: utf-8
"""
fetch_dilution.py
-----------------
At-a-glance low-float card: FLOAT SIZE + ROTATION + DILUTION RISK.

When you pull up a low-float name, this answers the three things fast:
  1. Float size  -> SMB band (>30M safe ... <1M do-not-trade)
  2. Rotation    -> PREMARKET volume (04:00–09:30 ET) / float (>1x notable, >2x extreme).
                    Float rotation + the whole read are a PRE-OPEN bias call.  [SSOT: low_float_master_filter]
  3. Dilution    -> Section 6 protocol auto-filled from SEC EDGAR:
                    live shelf (S-3/F-3 + EFFECT), ATM, warrants, cash runway,
                    offering count, reverse splits, share-count growth
                    -> Clean / Moderate / High / Serial + max long size.

Data: SEC EDGAR (free) for shares/float/filings; Polygon/Massive for price+volume.
SMB float bands and Section 6 dilution grading are reused verbatim from
workflows/low_float_master_filter.md (the SSOT) — not reinvented here.

Usage:
    python tools/fetch_dilution.py STI
    python tools/fetch_dilution.py STI LULU NXTT
    python tools/fetch_dilution.py --tickers STI,LULU
    python tools/fetch_dilution.py --watchlist names.txt
    python tools/fetch_dilution.py STI --float 2500000     # override float (shares) if you know it

Cards print to stdout and save to .tmp/dilution_<TICKER>_<date>.md
"""
import sys, os, re, argparse, datetime as dt, warnings
warnings.filterwarnings('ignore')
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd
import pytz
from tools.edgar_client import EdgarClient
from tools.fetch_polygon import fetch_bars
from tools.polygon_ref import ticker_overview, latest_news, short_interest, short_volume, free_float

NY_TZ = pytz.timezone('America/New_York')
PM_START, PM_END = '04:00', '09:29'    # premarket window (09:30 bar = first RTH bar)

# Windows console is cp1252; cards use unicode (arrows/emoji) — print safely.
try:
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
except Exception:
    pass

CACHE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '.tmp')

# ── SMB float bands (verbatim from the slide / low_float_master_filter) ───────
def smb_band(shares):
    """Return (label, description) for a float/share count, per SMB U bands."""
    if shares is None:
        return ('UNKNOWN', 'float not available')
    m = shares / 1e6
    if m < 1:   return ('DO NOT TRADE', '<1M — do not trade unless very experienced')
    if m < 5:   return ('EXTREME',      '1–5M — $1→$100 moves become possible')
    if m < 15:  return ('HIGH SQUEEZE', '5–15M — very high chance of squeezes + manipulation')
    if m < 30:  return ('CAUTION',      '15–30M — start to use caution')
    return ('RELATIVELY SAFE', '>30M — relatively safe')


BAND_EMOJI = {'DO NOT TRADE': '🔴', 'EXTREME': '🔴', 'HIGH SQUEEZE': '🟠',
              'CAUTION': '🟡', 'RELATIVELY SAFE': '🟢', 'UNKNOWN': '⚪'}


def fmt_sh(n):
    if n is None: return 'n/a'
    if n >= 1e9:  return f'{n/1e9:.2f}B'
    if n >= 1e6:  return f'{n/1e6:.2f}M'
    if n >= 1e3:  return f'{n/1e3:.1f}K'
    return f'{n:.0f}'


# ── premarket price + volume (Polygon) ───────────────────────────────────────
def premarket_snapshot(ticker, date):
    """
    Premarket read for `date`: (price, premarket_volume, last_ts, n_pm_bars).
    Float ROTATION is a pre-open metric — premarket volume (04:00–09:29 ET) ÷ float.
    If run during premarket, captures 04:00→now; if run after the open, the full
    completed premarket session. price = last premarket close (or last bar seen).
    """
    try:
        df = fetch_bars(ticker, 'minute', date, date, multiplier=1)
    except Exception:
        df = None
    if df is not None and not df.empty:
        if df.index.tz is None:
            df.index = df.index.tz_localize('UTC')
        df.index = df.index.tz_convert(NY_TZ)
        pm = df.between_time(PM_START, PM_END)
        pm_vol = float(pm['volume'].sum()) if len(pm) else 0.0
        ref = pm if len(pm) else df          # before any PM prints, fall back to last bar
        return float(ref['close'].iloc[-1]), pm_vol, ref.index[-1], len(pm)
    # No intraday bars (illiquid/OTC name or same-day data gap): fall back to a recent
    # daily close so the header price + warrant moneyness still render (#29). pm_vol=None
    # signals 'no premarket volume measured' (distinct from a true 0).
    try:
        start = (pd.Timestamp(date) - pd.Timedelta(days=7)).strftime('%Y-%m-%d')
        dd = fetch_bars(ticker, 'day', start, date, multiplier=1)
        if dd is not None and not dd.empty:
            return float(dd['close'].iloc[-1]), None, None, 0
    except Exception:
        pass
    return None, None, None, 0


# ── dilution flags from EDGAR (Section 6 protocol) ───────────────────────────
def cash_runway_quarters(ec, facts):
    """cash / quarterly burn. None if cash-generating or data missing.
    A 0/None cash tag is treated as MISSING (IFRS/foreign filers book cash under a
    different tag) so it can't fake 'Low cash → 0.0q' (#11). Burn is annualized from the
    XBRL period length so a 3-month (10-Q) OCF isn't mistaken for a full year (#5)."""
    cash = None
    for tag in ['CashAndCashEquivalentsAtCarryingValue',
                'CashAndCashEquivalentsAtCarryingValueIncludingDiscontinuedOperations',
                'CashCashEquivalentsRestrictedCashAndRestrictedCashEquivalents', 'Cash']:
        v = ec.latest(facts, [tag])[0]
        if v:                              # skip 0 / None placeholders (#11)
            cash = v
            break
    if cash is None:
        return None, None
    ocf_df = ec.concept(facts, 'NetCashProvidedByUsedInOperatingActivities', unit='USD')
    if ocf_df.empty:
        return None, cash
    row = ocf_df.iloc[-1]
    ocf = row['val']
    if ocf is None or ocf >= 0:
        return float('inf'), cash          # generating cash → no raise pressure
    # annualize by the reporting-period length (10-Q ~90d, YTD ~180/270d, 10-K ~365d) (#5)
    days = (row['end'] - row['start']).days if (pd.notna(row.get('start')) and pd.notna(row.get('end'))) else None
    annual_burn = abs(ocf) * (365.0 / days) if (days and days > 0) else abs(ocf)
    quarterly_burn = annual_burn / 4.0
    if quarterly_burn == 0:
        return None, cash
    return cash / quarterly_burn, cash


def _share_series(ec, facts, since_date=None, until=None):
    """Clean shares-outstanding series: ONE row per period-end (the MAX value at each end,
    so a dual-class issuer's per-class rows collapse to the company total), positive only,
    sorted by end. This kills the multi-class/restatement interleave that faked splits (#3).
    since_date drops pre-listing predecessor rows; until bounds point-in-time runs (#18)."""
    df = ec.concept(facts, 'EntityCommonStockSharesOutstanding', taxonomies=('dei',), unit='shares', positive=True)
    if df.empty:
        df = ec.concept(facts, 'CommonStockSharesOutstanding', unit='shares', positive=True)
    if df.empty or not {'val', 'end'}.issubset(df.columns):
        return pd.DataFrame(columns=['end', 'val'])
    df = df.dropna(subset=['val', 'end'])
    if until is not None and 'filed' in df.columns:
        df = df[df['filed'] <= pd.Timestamp(until)]
    if since_date is not None:
        df = df[df['end'] >= pd.Timestamp(since_date)]
    if df.empty:
        return pd.DataFrame(columns=['end', 'val'])
    return df.groupby('end', as_index=False)['val'].max().sort_values('end').reset_index(drop=True)


def share_growth_6mo(ec, facts, since_date=None, until=None):
    """% change in shares outstanding over ~6 months. None if insufficient history.
    Reverse-split-aware: if a >40% step-down sits between base and now, the base is a
    post-split trough and the % is meaningless — suppress it rather than fire a fake
    'shares doubled' (#20). Uses the clean per-end series (no dual-class garbage) (#3)."""
    g = _share_series(ec, facts, since_date=since_date, until=until)
    if len(g) < 2:
        return None
    now_end, now_val = g['end'].iloc[-1], g['val'].iloc[-1]
    cutoff = now_end - pd.Timedelta(days=183)
    past = g[g['end'] <= cutoff]
    base_row = past.iloc[-1] if len(past) else g.iloc[0]
    base = base_row['val']
    if not base:
        return None
    window = g[g['end'] >= base_row['end']]['val'].values
    for i in range(1, len(window)):
        if window[i - 1] and window[i] and window[i] < 0.6 * window[i - 1]:
            return None                    # reverse split inside the window — not comparable (#20)
    return (now_val / base - 1.0) * 100.0


def extract_warrant_terms(ec, cik, since, price=None):
    """Pull WARRANT exercise price(s) + share count from the latest offering filing.
    Heuristic prose parse, hardened: only accepts an 'exercise price of $X' that sits in
    warrant context (not a stock-OPTION / equity-incentive-plan / weighted-average exercise
    price) (#12); attaches a share count only when a single strike is shown and the count
    comes from the same 'warrants to purchase N ...' clause and is plausibly large (#13);
    pre-funded only when the text says so or the strike is nominal (<$0.001) (#35)."""
    from collections import Counter
    filings = ec.recent_filings(cik, forms=['424B5', '424B4', '424B3', '424B2', 'S-1', 'F-1'], since=since)
    if filings.empty:
        return None
    OPT_CTX = ('option', 'equity incentive', 'incentive plan', 'weighted average',
               'weighted-average', '401(k)', 'restricted stock')
    for _, f in filings.head(5).iterrows():
        url = ec.filing_url(cik, f['accessionNumber'], f['primaryDocument'])
        text = ec.document_text(url)
        if not text:
            continue
        strikes, prefunded = [], []
        for m in re.finditer(r'exercise price of \$?([0-9]+(?:\.[0-9]+)?)', text, re.I):
            val = round(float(m.group(1)), 4)
            ctx = text[max(0, m.start() - 90): m.end() + 90].lower()
            if 'warrant' not in ctx or any(k in ctx for k in OPT_CTX):
                continue                       # not a warrant strike → skip (#12)
            if 'pre-funded' in ctx or 'prefunded' in ctx or val < 0.001:   # (#35)
                prefunded.append(val)
            else:
                strikes.append(val)
        if not strikes and not prefunded:
            continue
        cnt = Counter(strikes)
        recurring = sorted({s for s, c in cnt.items() if c >= 2})
        if recurring:
            keep = recurring                                   # strikes that recur are the real ones
        elif price and strikes:
            keep = [min(strikes, key=lambda s: abs(s - price))]  # else the one nearest price (#12)
        elif strikes:
            keep = sorted({s for s, _ in cnt.most_common(2)})
        else:
            keep = []
        shares = None
        if len(keep) == 1:                                     # only attribute a count to a single strike (#13)
            for pat in [r'warrants?\s+to\s+purchase\s+(?:up\s+to\s+)?([0-9,]{5,})\s+(?:shares|ordinary|common)',
                        r'([0-9,]{5,})\s+(?:shares|ordinary shares|warrants)[^.]{0,60}?exercise price']:
                mm = re.search(pat, text, re.I)
                if mm:
                    try:
                        cand = int(mm.group(1).replace(',', ''))
                        if cand >= 50000:                      # reject spurious tiny counts (#13)
                            shares = cand
                        break
                    except ValueError:
                        pass
        return dict(form=f['form'], date=f['filingDate'].date(),
                    strikes=sorted(set(keep)), prefunded=sorted(set(prefunded)), shares=shares)
    return None


def reverse_splits_from_shares(ec, facts, lookback_days=365 * 5, since_date=None, until=None):
    """Detect reverse splits as >40% step-downs in the clean per-end share series.
    The per-end MAX collapse (in _share_series) removes the dual-class/restatement
    interleave that used to fake a split (#3); a genuine post-split re-issuance still
    leaves the trough visible so real splits (e.g. NXTT) are kept.
    Returns (count, [(date, before, after), ...])."""
    g = _share_series(ec, facts, since_date=since_date, until=until)
    if len(g) < 2:
        return 0, []
    cutoff = g['end'].max() - pd.Timedelta(days=lookback_days)
    g = g[g['end'] >= cutoff].reset_index(drop=True)
    vals = g[['end', 'val']].values
    drops = []
    for i in range(1, len(vals)):
        prev, cur = vals[i - 1][1], vals[i][1]
        if not (prev and cur and cur < 0.6 * prev):     # >40% step-down = candidate split
            continue
        # Reject interleave artifacts: a real reverse split STAYS down; a dual-class/
        # restatement blip rebounds back toward the pre-drop level next period (#3).
        nxt = vals[i + 1][1] if i + 1 < len(vals) else None
        if nxt is not None and nxt >= 0.7 * prev:
            continue
        drops.append((vals[i][0], prev, cur))
    return len(drops), drops


def compute_dilution(ec, cik, facts, today, list_date=None, edgar_so=None,
                     poly_total=None, is_adr=False, until=None):
    """Return (flags, serial_bool, warr_note, ctx).
    list_date gates share-history flags so a de-SPAC's predecessor series doesn't fake
    alarms. edgar_so=(val,asof) + poly_total enable post-period reverse-split inference.
    until bounds every window for point-in-time (historical --date) runs."""
    yr_ago  = (today - dt.timedelta(days=365)).strftime('%Y-%m-%d')
    mo_ago  = (today - dt.timedelta(days=30)).strftime('%Y-%m-%d')
    yr2_ago = (today - dt.timedelta(days=365*2)).strftime('%Y-%m-%d')
    hist_start = max(yr2_ago, list_date) if list_date else yr2_ago

    # ── shelves vs one-shot registrations, with date-correct EFFECT pairing (#15,#22) ──
    shelf = ec.recent_filings(cik, forms=['S-3', 'S-3ASR', 'F-3', 'F-3ASR'], since=yr2_ago, until=until)
    s1reg = ec.recent_filings(cik, forms=['S-1', 'F-1'], since=yr2_ago, until=until)
    effect = ec.recent_filings(cik, forms=['EFFECT'], since=yr2_ago, until=until)

    def _reg_status(reg):
        """live?, detail — an EFFECT only counts if filed on/after the registration (#15)."""
        if reg.empty:
            return False, None
        top = reg.iloc[0]
        is_asr = 'ASR' in str(top['form'])
        eff = effect[effect['filingDate'] >= top['filingDate']] if not effect.empty else effect
        if is_asr:
            return True, f"{top['form']} filed {top['filingDate'].date()} (ASR auto-effective)"
        if not eff.empty:
            return True, f"{top['form']} filed {top['filingDate'].date()} + EFFECT {eff.iloc[0]['filingDate'].date()}"
        return False, f"{top['form']} filed {top['filingDate'].date()} (pending effectiveness)"

    shelf_live, shelf_detail = _reg_status(shelf)
    s1_live, s1_detail = _reg_status(s1reg)
    shelf_detail = shelf_detail or 'no recent S-3/F-3 shelf'

    # ── offerings in 12mo, deduped (EDGAR double-lists 424B3 rows) (#26) ──
    offers = ec.recent_filings(cik, forms=['424B5', '424B3', '424B4'], since=yr_ago, until=until)
    if not offers.empty:
        offers = offers.drop_duplicates(subset=['filingDate', 'primaryDocDescription'])
    n_offers = len(offers)
    last_offer = offers['filingDate'].max() if not offers.empty else None
    diluted_30d = (last_offer is not None) and (last_offer >= pd.Timestamp(mo_ago))

    # ── ATM: require an equity ATM SALES-AGREEMENT phrase on an equity carrier form,
    #    not the bare 'at-the-market' (debt-prospectus / risk-factor boilerplate) (#9) ──
    atm_forms = '424B5,8-K,10-Q,10-K,20-F,6-K,S-3,F-3'
    atm_hits = max(ec.full_text_count(p, cik=cik, forms=atm_forms, startdt=yr2_ago, enddt=until)
                   for p in ('"at-the-market offering" "sales agreement"',
                             '"ATM Sales Agreement"',
                             '"Open Market Sale Agreement"',
                             '"At Market Issuance Sales Agreement"'))
    atm_active = atm_hits > 0

    # ── reverse split: per-end step-down + post-period Polygon mismatch (#8) + full-text (#24) ──
    rs_count, rs_drops = reverse_splits_from_shares(ec, facts, since_date=list_date, until=until)
    rs_inferred = False
    rs_extra = None
    if (not is_adr) and edgar_so and edgar_so[0] and poly_total and poly_total < 0.6 * edgar_so[0]:
        rs_inferred = True
        rs_extra = f"EDGAR {fmt_sh(edgar_so[0])} → current {fmt_sh(poly_total)} (~{edgar_so[0]/poly_total:.0f}:1 split after last filing)"
    rs_fulltext = ec.full_text_count('"reverse stock split"', cik=cik,
                                     forms='8-K,6-K,10-Q,10-K,20-F,424B5', startdt=hist_start, enddt=until)
    rev_split = rs_count > 0 or rs_inferred or rs_fulltext > 0
    parts = []
    if rs_drops:
        parts.append('; '.join(f"{d[0].date()} ({(today - d[0].date()).days}d ago) {fmt_sh(d[1])}->{fmt_sh(d[2])}" for d in rs_drops))
    if rs_extra:
        parts.append(rs_extra)
    if not rs_drops and not rs_inferred and rs_fulltext:
        parts.append(f"{rs_fulltext} 'reverse stock split' filing(s) — date not parsed, verify")
    rs_detail = '; '.join(parts) if parts else 'no step-down in share count'

    warr_hits = ec.full_text_count('"warrants to purchase"', cik=cik, startdt=hist_start, enddt=until)

    runway, cash = cash_runway_quarters(ec, facts)
    runway_lt2 = (runway is not None and runway < 2)
    runway_lt1 = (runway is not None and runway < 1)
    runway_txt = ('cash-generating' if runway == float('inf')
                  else f'{runway:.1f} quarters' if runway is not None else 'n/a')

    growth = share_growth_6mo(ec, facts, since_date=list_date, until=until)
    float_double = (growth is not None and growth >= 100)

    flags = [
        dict(key='Live shelf',       on=shelf_live,
             risk='Live shelf — company can sell new stock at any time',  detail=shelf_detail),
        dict(key='Registered offering', on=s1_live,
             risk='Live S-1/F-1 registration — registered stock can be sold (one-shot, not an evergreen shelf)',
             detail=s1_detail or 'none'),
        dict(key='Active ATM',       on=atm_active,
             risk='Active ATM — can sell shares into the market anytime, unannounced (most dangerous)',
             detail=(f'{atm_hits} sales-agreement filing(s)' if atm_active else 'none found')),
        dict(key='Low cash',         on=runway_lt2,
             risk='Low cash (under ~2 quarters) — likely to raise soon',  detail=runway_txt),
        dict(key='Frequent offerings', on=n_offers >= 3,
             risk='Frequent offerings (3+ in 12 months)',  detail=f'{n_offers} distinct offerings in 12mo'),
        dict(key='Recent dilution',  on=diluted_30d,
             risk='Just diluted — an offering in the last 30 days',
             detail=(f'last offering {last_offer.date()}' if last_offer is not None else 'none')),
        dict(key='Reverse split',    on=rev_split,
             risk='Reverse-split history / recent split',  detail=rs_detail),
        dict(key='Shares doubled',   on=float_double,
             risk='Share count doubled in 6 months (active dilution)',
             detail=(f'{growth:+.0f}% in 6mo' if growth is not None else 'n/a')),
    ]

    # serial diluter: any 4 of the 5 computable conditions
    serial = sum([n_offers >= 3, atm_active, rs_count >= 2, runway_lt1, float_double]) >= 4

    warr_note = (f'referenced in {warr_hits} post-listing filing(s) — no terms auto-parsed; exercise price & repricing need a filing read (ask me)'
                 if warr_hits else 'none found in post-listing filings')
    ctx = dict(last_offer_date=last_offer, rs_inferred=rs_inferred)
    return flags, serial, warr_note, ctx


def classify(n_flags, serial, flags=None):
    """Grade + max long size. High-signal flags floor the grade even if alone (#10):
    a real ATM or a fresh (<30d) offering caps you at MODERATE; both → HIGH."""
    atm = diluted = False
    if flags:
        on = {f['key']: f['on'] for f in flags}
        atm, diluted = on.get('Active ATM', False), on.get('Recent dilution', False)
    if serial or n_flags >= 5:
        return 'SERIAL DILUTER', '0% (do not trade long)'
    if n_flags >= 3 or (atm and diluted):
        return 'HIGH RISK', '25%'
    if n_flags == 2 or atm or diluted:
        return 'MODERATE', '50%'
    return 'CLEAN', '100%'


# ── profile / catalyst / squeeze helpers (Polygon REST + EDGAR submissions) ──
US_STATES = {'AL', 'AK', 'AZ', 'AR', 'CA', 'CO', 'CT', 'DE', 'FL', 'GA', 'HI', 'ID', 'IL', 'IN',
             'IA', 'KS', 'KY', 'LA', 'ME', 'MD', 'MA', 'MI', 'MN', 'MS', 'MO', 'MT', 'NE', 'NV',
             'NH', 'NJ', 'NM', 'NY', 'NC', 'ND', 'OH', 'OK', 'OR', 'PA', 'RI', 'SC', 'SD', 'TN',
             'TX', 'UT', 'VT', 'VA', 'WA', 'WV', 'WI', 'WY', 'DC', 'PR', 'GU', 'VI', 'AS', 'MP'}


def profile_bits(ec, cik, ticker, ov=None):
    if ov is None:
        try:
            ov = (ticker_overview(ticker) or {}).get('results') or {}
        except Exception:
            ov = {}
    sub = {}
    try:
        sub = ec.submissions(cik) or {}
    except Exception:
        sub = {}
    incorp = (sub.get('stateOfIncorporationDescription') or sub.get('stateOfIncorporation') or '').strip()
    us_incorp = incorp.upper() in US_STATES
    foreign_forms = ec.recent_filings(cik, forms=['20-F', '6-K', 'F-1', 'F-3', 'F-4'], since='2021-01-01')
    locale = ov.get('locale')
    desc = (ov.get('description') or '').lower()
    biz_cc = ((sub.get('addresses') or {}).get('business') or {}).get('stateOrCountry', '') or ''
    homepage = (ov.get('homepage_url') or '').lower()
    is_foreign = (bool(incorp) and not us_incorp) or (not foreign_forms.empty) or (locale and locale != 'us')

    # CHINA (#14): require a real domicile/operational signal — SEC business-address country
    # code (F4=China, K3=Hong Kong), a .cn homepage, an operational phrase, or >=2 PRC term
    # mentions — so a single stray 'china' sentence (e.g. Ford) doesn't false-positive.
    blob = f"{desc} {incorp.lower()}"
    prc_hits = len(re.findall(r'\bprc\b', blob))            # 'PRC' is unambiguous in filings
    china_hits = blob.count('china') + blob.count('hong kong')
    china_addr = biz_cc.upper() in ('F4', 'K3')            # SEC country codes: F4=China, K3=HK
    china_url = homepage.endswith('.cn') or '.cn/' in homepage
    china_op = bool(re.search(r'(headquarter|based|incorporat|located|principal executive)\w*[^.]{0,50}(china|hong kong|prc)', blob))
    # 'PRC' once, OR China/HK named twice, OR a hard address/url/operational signal — a lone
    # 'china' mention (e.g. Ford's market-share sentence) is NOT enough.
    is_china = china_addr or china_url or china_op or prc_hits >= 1 or china_hits >= 2

    # DOMICILE (#28): fall back past EDGAR's blank stateOfIncorporation to other signals.
    if us_incorp:
        domicile = f"USA ({incorp})"
    elif incorp:
        domicile = incorp
    elif is_china:
        domicile = 'China/HK'
    elif is_foreign:
        domicile = 'foreign (non-US filer)'
    else:
        domicile = 'USA?'
    return dict(sector=(ov.get('sic_description') or '').title() or '—',
                mcap=ov.get('market_cap'), domicile=domicile, is_foreign=is_foreign, is_china=is_china,
                forms=sorted(set(foreign_forms['form'])) if not foreign_forms.empty else [])


def catalyst_line(ticker, until=None):
    try:
        res = (latest_news(ticker, 3, until=until) or {}).get('results') or []
    except Exception:
        res = []
    if not res:
        return None
    n = res[0]
    pub = (n.get('publisher') or {}).get('name', '')
    return f"{n.get('title', '').strip()}  _({pub}, {(n.get('published_utc') or '')[:10]})_"


def squeeze_pair(ticker, until=None):
    si = sv = None
    try:
        si = ((short_interest(ticker, until=until) or {}).get('results') or [None])[0]
    except Exception:
        si = None
    try:
        sv = ((short_volume(ticker, until=until) or {}).get('results') or [None])[0]
    except Exception:
        sv = None
    return si, sv


# ── build one card ───────────────────────────────────────────────────────────
def build_card(ec, ticker, date, float_override=None):
    today = pd.Timestamp(date).date()
    # point-in-time: when --date is in the past, bound every window to it (no future leak) (#18)
    until = date if today < dt.date.today() else None
    cik = ec.ticker_to_cik(ticker)
    if not cik:
        return f"## {ticker}\n  ⚠ no SEC CIK found (not an SEC filer? foreign? wrong ticker)\n"
    name = ec.company_name(ticker)
    facts = ec.companyfacts(cik)

    shares_out = ec.latest(facts, ['EntityCommonStockSharesOutstanding',
                                   'CommonStockSharesOutstanding'])
    pub_float  = ec.latest(facts, ['EntityPublicFloat'])
    price, pm_vol, pm_ts, n_pm = premarket_snapshot(ticker, date)

    edgar_so_val, edgar_so_asof = shares_out[0], shares_out[1]   # EDGAR-native (for split inference)
    so_val, so_asof = edgar_so_val, edgar_so_asof
    pf_val, pf_asof = pub_float[0], pub_float[1]

    # Polygon overview (fetched once) — listing date, security type, current share counts.
    ov = (ticker_overview(ticker) or {}).get('results') or {}
    name = ov.get('name') or name              # Polygon name is fresher after a rename (#27)
    list_date = ov.get('list_date')
    is_adr = (ov.get('type') in ('ADRC', 'ADRP', 'ADRR')) or ('depositary' in (ov.get('name') or '').lower())
    poly_class = ov.get('share_class_shares_outstanding')   # listed class / ADS count
    poly_weighted = ov.get('weighted_shares_outstanding')   # company total (all classes)
    poly_total = (poly_weighted or poly_class) if not is_adr else (poly_class or poly_weighted)

    # Resolve a TRUSTWORTHY shares-outstanding (so_val/so_src):
    #  - ADR: EDGAR reports foreign ORDINARY shares, not the listed ADS — always prefer the
    #    Polygon ADS (share_class) count (#6).
    #  - else stale when: missing/zero, predates listing (de-SPAC predecessor shell), or just
    #    old (FPIs report annually — >120d is likely superseded by a split/issue/conversion) (#7,#30).
    so_age = (pd.Timestamp(today) - so_asof).days if so_asof is not None else None
    so_stale = (so_val is None or not so_val
                or (list_date and so_asof is not None and so_asof < pd.Timestamp(list_date))
                or (so_age is not None and so_age > 120))
    if is_adr and poly_class:
        so_val, so_asof, so_src = poly_class, None, 'Polygon ADS'
    elif so_stale and poly_total:
        so_val, so_asof, so_src = poly_total, None, 'Polygon'
    else:
        so_src = 'EDGAR'

    # FREE FLOAT (tradable shares) from Massive — excludes insiders/5%+ holders/lockups.
    ff = free_float(ticker)
    ff_sh = ff.get('free_float') if isinstance(ff, dict) else None
    ff_date = ff.get('effective_date') if isinstance(ff, dict) else None

    # Sanity: free float can NEVER exceed shares outstanding (#2). If it does, our shares-out
    # is stale/low or the wrong class — prefer Polygon total; if still impossible, flag it.
    ff_warn = None
    if ff_sh and so_val and ff_sh > so_val * 1.02:
        if poly_total and poly_total >= ff_sh:
            so_val, so_asof, so_src = poly_total, None, 'Polygon'
        else:
            ff_warn = "⚠ free-float feed exceeds known share count — both may be stale; verify"

    # Float-in-shares priority: manual override > Massive free float > shares outstanding.
    # `float_sh` is the EFFECTIVE tradable count used for band/rotation/squeeze; capped at
    # shares-out so an over-stated feed can't mis-band a thin name 'SAFE'.
    if float_override:
        float_sh = float_override
        float_lbl = f"Float (manual): **{fmt_sh(float_sh)}**"
        float_asof = so_asof
    elif ff_sh:
        float_sh = min(ff_sh, so_val) if so_val else ff_sh
        pct = (float_sh / so_val * 100) if so_val else None          # same denominator we print (#2)
        pct_txt = f" · {pct:.0f}% of shares out" if pct else ""
        float_lbl = f"Free float: **{fmt_sh(ff_sh)}**{pct_txt}"
        float_asof = pd.Timestamp(ff_date) if ff_date else so_asof
    else:
        float_sh = so_val
        src = 'ADS count' if is_adr else 'shares outstanding'
        float_lbl = f"Float ({src} — no free-float data): **{fmt_sh(float_sh)}**"
        float_asof = so_asof
    band = smb_band(float_sh)

    rotation = (pm_vol / float_sh) if (pm_vol and float_sh) else None

    flags, serial, warr_note, ctx = compute_dilution(
        ec, cik, facts, today, list_date=list_date,
        edgar_so=(edgar_so_val, edgar_so_asof), poly_total=poly_total, is_adr=is_adr, until=until)
    # Reverse split executed after the last EDGAR point: Polygon total << EDGAR latest (#8)
    if ctx.get('rs_inferred') and so_src != 'EDGAR':
        float_asof = float_asof  # display already on Polygon count
    n_flags = sum(1 for f in flags if f['on'])
    cls, max_size = classify(n_flags, serial, flags)

    # Free-float snapshot predates a later offering → understated float/band (#19)
    last_offer = ctx.get('last_offer_date')
    if ff_sh and float_asof is not None and last_offer is not None and pd.Timestamp(last_offer) > pd.Timestamp(float_asof):
        ff_warn = (ff_warn + " · " if ff_warn else "") + \
            f"⚠ free-float snapshot ({float_asof.date()}) predates an offering filed {pd.Timestamp(last_offer).date()} — true float likely higher; pass --float N"

    L = []
    L.append(f"## {ticker} · {name} · CIK {cik}")
    px = f"${price:.2f}" if price else "$?"
    pmv = fmt_sh(pm_vol) if pm_vol else "0"
    asof = pm_ts.strftime('%H:%M ET') if pm_ts is not None else '?'
    L.append(f"`{px}  PM vol {pmv}  ·  asof {asof}  ·  premarket read {today}`\n")

    # PROFILE (sector / domicile) + CATALYST (why it's moving)
    prof = profile_bits(ec, cik, ticker, ov=ov)
    flag = ' 🇨🇳' if prof['is_china'] else (' 🌐' if prof['is_foreign'] else '')
    forms = f" (files {','.join(prof['forms'])})" if prof['forms'] and prof['is_foreign'] else ''
    mcap = f" · mkt cap ${fmt_sh(prof['mcap'])}" if prof.get('mcap') else ''
    L.append(f"**PROFILE:** {prof['sector'] or '—'}{mcap} · domicile **{prof['domicile']}**{flag}{forms}")
    cat = catalyst_line(ticker, until=until)
    if cat:
        L.append(f"**CATALYST:** {cat}")
    L.append("")

    L.append("**FLOAT SIZE**")
    L.append(f"- {float_lbl} → {BAND_EMOJI.get(band[0],'')} **{band[0]}**  _({band[1]}; asof {float_asof.date() if float_asof is not None else '?'})_")
    if ff_warn:
        L.append(f"- {ff_warn}")
    if ff_sh and so_val:
        soa = so_asof.date() if so_asof is not None else 'current'
        unit_lbl = 'ADS — listed, tradable basis' if is_adr else 'total, not tradable'
        L.append(f"- Shares outstanding: {fmt_sh(so_val)}  _({so_src}, asof {soa} — {unit_lbl})_")
    if is_adr:
        L.append("- _ADR/ADS name: EDGAR reports foreign ordinary shares; band uses the listed ADS count._")
    if pf_val:
        L.append(f"- Public float: ${fmt_sh(pf_val)}  _(SEC value in $, asof {pf_asof.date() if pf_asof is not None else '?'} — not a share count)_")
    if not float_override and not ff_sh:
        L.append("- _No free-float feed hit; using shares outstanding. True free float may be far lower (insider/restricted). Pass `--float N` if you know it._")
    L.append("")

    L.append("**PREMARKET ROTATION**")
    if rotation is not None:
        tag = '🔴 >2x extreme supply pressure' if rotation >= 2 else ('🟠 >1x full rotation' if rotation >= 1 else 'below 1x')
        L.append(f"- {fmt_sh(pm_vol)} PM vol ÷ {fmt_sh(float_sh)} float = **{rotation:.2f}x**  {tag}  _(04:00–{asof})_\n")
    elif float_sh and not pm_vol:
        L.append("- no premarket volume yet (pre-04:00 or illiquid name)\n")
    else:
        L.append("- n/a (missing volume or float)\n")

    # SQUEEZE (shorts) — short interest %float + days-to-cover + daily short-vol ratio
    si, sv = squeeze_pair(ticker, until=until)
    if si or sv:
        # denominator label: SI% is only true "of float" when we have a real free float (#17)
        si_denom = 'free float' if ff_sh else ('ADS' if is_adr else 'shares out')
        parts, si_pct, dtc = [], None, None
        if si and si.get('short_interest'):
            si_sh = si['short_interest']
            si_pct = (si_sh / float_sh * 100) if float_sh else None
            parts.append(f"SI {fmt_sh(si_sh)}" + (f" ({si_pct:.1f}% of {si_denom})" if si_pct is not None else ""))
        if si and si.get('days_to_cover') is not None:
            dtc = si['days_to_cover']; parts.append(f"days-to-cover {dtc:g}")
        if sv and sv.get('short_volume_ratio') is not None:
            parts.append(f"daily short-vol {sv['short_volume_ratio']:.0f}%")
        if si_pct is not None or dtc is not None:
            # days-to-cover alone (often inflated by a stale/thin avg-volume feed) must NOT
            # read 'high squeeze fuel' when short interest is a trivial % of float (#16).
            sip = si_pct or 0
            hot = sip > 30 or (dtc and dtc > 5 and sip >= 5)
            warm = sip > 20 or (dtc and dtc > 3 and sip >= 5)
            if not ff_sh and sip and sip < 20:
                tag = '⚪ SI% vs shares-out (no free-float data — true % higher); read with care'
            else:
                tag = '🔴 high squeeze fuel' if hot else ('🟠 elevated' if warm else '🟢 low squeeze risk (shorts light)')
        else:
            tag = ''
        asof_si = f"  _(SI asof {si.get('settlement_date')})_" if si and si.get('settlement_date') else ''
        L.append("**SQUEEZE (shorts)**")
        L.append(f"- {' · '.join(parts)}  {tag}{asof_si}\n")

    grade_emoji = {'CLEAN': '🟢', 'MODERATE': '🟡', 'HIGH RISK': '🟠', 'SERIAL DILUTER': '🔴'}.get(cls, '')
    L.append(f"**DILUTION RISK → {grade_emoji} {cls} · max long size {max_size}**  _({n_flags} of {len(flags)} risk flags)_")
    L.append("")
    risks = [f for f in flags if f['on']]
    clears = [f['key'] for f in flags if not f['on']]
    if risks:
        for f in risks:
            L.append(f"- 🔴 **{f['risk']}**  _({f['detail']})_")
    else:
        L.append("- 🟢 **No dilution risk flags triggered**")
    if clears:
        L.append(f"- 🟢 Clean on: {' · '.join(clears)}")

    # Warrants: show fixed strike(s) + shares + moneyness vs price (unlike an ATM, warrants HAVE a price).
    # Scan window starts no earlier than the current listing so a de-SPAC's predecessor
    # offering docs (old shell's warrants/units) aren't parsed as this company's.
    warr_since = (today - dt.timedelta(days=730)).strftime('%Y-%m-%d')
    if list_date and list_date > warr_since:
        warr_since = list_date
    wt = None
    try:
        wt = extract_warrant_terms(ec, cik, warr_since, price)
    except Exception:
        wt = None
    if wt and wt['strikes']:
        lo = min(wt['strikes'])
        money = ''
        if price:
            if price >= lo:        money = f' · 🔴 in-the-money vs ${price:.2f} (holders profit → exercise & sell = overhang)'
            elif price >= lo * 0.8: money = f' · 🟠 near-money vs ${price:.2f}'
            else:                   money = f' · 🟢 out-of-money vs ${price:.2f}'
        strikes_s = ', '.join(f'${s:g}' for s in wt['strikes'])
        sh_pct = f" ({wt['shares']/float_sh*100:.0f}% of float)" if wt['shares'] and float_sh else ''
        sh = f"{fmt_sh(wt['shares'])} sh{sh_pct} " if wt['shares'] else ''
        pf = f" · +pre-funded @ ${wt['prefunded'][0]:g} (≈free shares)" if wt['prefunded'] else ''
        L.append(f"- ⚠️ **Warrants:** {sh}@ {strikes_s}{money}{pf}  _(from {wt['form']} {wt['date']}; auto-parsed — verify)_")
    else:
        L.append(f"- ⚠️ Warrants: {warr_note}")

    L.append("\n_Sources: shares/float/filings = SEC EDGAR (free) · price/volume = Polygon/Massive._")
    L.append("_Float band + rotation use Massive free float (tradable shares) when available, else shares outstanding. Warrant strikes & underwriter patterns need a prose read._")
    return "\n".join(L) + "\n"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('tickers', nargs='*', help='one or more tickers')
    ap.add_argument('--tickers', dest='tickers_csv', help='comma-separated tickers')
    ap.add_argument('--watchlist', help='file with one ticker per line')
    ap.add_argument('--date', default=dt.date.today().strftime('%Y-%m-%d'))
    ap.add_argument('--float', dest='float_override', type=float, default=None,
                    help='manual float in shares (single-ticker only)')
    args = ap.parse_args()

    tickers = list(args.tickers)
    if args.tickers_csv:
        tickers += [t.strip() for t in args.tickers_csv.split(',') if t.strip()]
    if args.watchlist and os.path.exists(args.watchlist):
        with open(args.watchlist) as f:
            tickers += [ln.strip().upper() for ln in f if ln.strip() and not ln.startswith('#')]
    tickers = [t.upper() for t in dict.fromkeys(tickers)]   # dedupe, keep order
    if not tickers:
        ap.error('no tickers given (positional, --tickers, or --watchlist)')

    ec = EdgarClient()
    os.makedirs(CACHE_DIR, exist_ok=True)
    for t in tickers:
        try:
            card = build_card(ec, t, args.date,
                              float_override=args.float_override if len(tickers) == 1 else None)
        except Exception as e:
            card = f"## {t}\n  ⚠ error: {e}\n"
        print("\n" + "=" * 70)
        print(card)
        out = os.path.join(CACHE_DIR, f"dilution_{t}_{args.date}.md")
        with open(out, 'w', encoding='utf-8') as f:
            f.write(card)
    print("=" * 70)
    print(f"Saved {len(tickers)} card(s) to {CACHE_DIR}/dilution_*_{args.date}.md")


if __name__ == '__main__':
    main()
