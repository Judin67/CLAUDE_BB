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
from tools.polygon_ref import ticker_overview, latest_news, short_interest, short_volume

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
        return None, None, None, 0
    if df.empty:
        return None, None, None, 0
    if df.index.tz is None:
        df.index = df.index.tz_localize('UTC')
    df.index = df.index.tz_convert(NY_TZ)
    pm = df.between_time(PM_START, PM_END)
    pm_vol = float(pm['volume'].sum()) if len(pm) else 0.0
    ref = pm if len(pm) else df          # before any PM prints, fall back to last bar
    price = float(ref['close'].iloc[-1])
    last_ts = ref.index[-1]
    return price, pm_vol, last_ts, len(pm)


# ── dilution flags from EDGAR (Section 6 protocol) ───────────────────────────
def cash_runway_quarters(ec, facts):
    """cash / quarterly burn. None if cash-generating or data missing."""
    cash = ec.latest(facts, ['CashAndCashEquivalentsAtCarryingValue',
                             'CashAndCashEquivalentsAtCarryingValueIncludingDiscontinuedOperations',
                             'Cash', 'CashCashEquivalentsRestrictedCashAndRestrictedCashEquivalents'])[0]
    ocf_df = ec.concept(facts, 'NetCashProvidedByUsedInOperatingActivities')
    if cash is None or ocf_df.empty:
        return None, cash
    # use most recent annual-ish operating cash flow as the burn base
    ocf = ocf_df.iloc[-1]['val']
    if ocf is None or ocf >= 0:
        return float('inf'), cash          # generating cash → no raise pressure
    quarterly_burn = abs(ocf) / 4.0
    if quarterly_burn == 0:
        return None, cash
    return cash / quarterly_burn, cash


def share_growth_6mo(ec, facts):
    """% change in shares outstanding over ~6 months. None if insufficient history."""
    df = ec.concept(facts, 'EntityCommonStockSharesOutstanding', taxonomies=('dei',))
    if df.empty:
        df = ec.concept(facts, 'CommonStockSharesOutstanding')
    df = df.dropna(subset=['val', 'filed'])
    if len(df) < 2:
        return None
    now = df.iloc[-1]
    cutoff = now['filed'] - pd.Timedelta(days=183)
    past = df[df['filed'] <= cutoff]
    if past.empty:
        past = df.iloc[[0]]
    base = past.iloc[-1]['val']
    if not base:
        return None
    return (now['val'] / base - 1.0) * 100.0


def extract_warrant_terms(ec, cik, since, price=None):
    """Pull warrant exercise price(s) + share count from the latest offering filing.
    Warrants have a fixed strike (unlike an ATM, which has no price). Heuristic prose
    parse — returns the most-common real strikes + a representative share count."""
    from collections import Counter
    filings = ec.recent_filings(cik, forms=['424B5', '424B4', '424B3', '424B2', 'S-1', 'F-1'], since=since)
    if filings.empty:
        return None
    for _, f in filings.head(5).iterrows():
        url = ec.filing_url(cik, f['accessionNumber'], f['primaryDocument'])
        text = ec.document_text(url)
        if not text:
            continue
        raw = [round(float(x), 4) for x in re.findall(r'exercise price of \$?([0-9]+(?:\.[0-9]+)?)', text, re.I)]
        if not raw:
            continue
        prefunded = sorted({s for s in raw if s < 0.05})
        real = [s for s in raw if s >= 0.05]
        strikes = sorted({s for s, _ in Counter(real).most_common(3)})
        shares = None
        for pat in [r'warrants?\s+to\s+purchase\s+(?:up\s+to\s+)?([0-9,]{4,})\s+shares',
                    r'([0-9,]{4,})\s+shares[^.]{0,70}?(?:issuable\s+)?upon[^.]{0,40}?exercise']:
            m = re.search(pat, text, re.I)
            if m:
                try:
                    shares = int(m.group(1).replace(',', '')); break
                except ValueError:
                    pass
        return dict(form=f['form'], date=f['filingDate'].date(),
                    strikes=strikes, prefunded=prefunded, shares=shares)
    return None


def reverse_splits_from_shares(ec, facts, lookback_days=365 * 5):
    """Detect reverse splits as >40% step-downs in the shares-outstanding series.
    Far more reliable than full-text 'reverse stock split' (boilerplate-ridden).
    Returns (count, [(date, before, after), ...])."""
    df = ec.concept(facts, 'EntityCommonStockSharesOutstanding', taxonomies=('dei',))
    if df.empty:
        df = ec.concept(facts, 'CommonStockSharesOutstanding')
    df = df.dropna(subset=['val', 'end']).sort_values('end').drop_duplicates('end', keep='last')
    if len(df) < 2:
        return 0, []
    cutoff = df['end'].max() - pd.Timedelta(days=lookback_days)
    df = df[df['end'] >= cutoff]
    vals = df[['end', 'val']].values
    drops = []
    for i in range(1, len(vals)):
        prev, cur = vals[i - 1][1], vals[i][1]
        if prev and cur and cur < 0.6 * prev:      # >40% step-down = reverse split
            drops.append((vals[i][0], prev, cur))
    return len(drops), drops


def compute_dilution(ec, cik, facts, today):
    """Return (flags list[(name,bool,detail)], serial_bool, notes list)."""
    yr_ago  = (today - dt.timedelta(days=365)).strftime('%Y-%m-%d')
    mo_ago  = (today - dt.timedelta(days=30)).strftime('%Y-%m-%d')
    yr5_ago = (today - dt.timedelta(days=365*5)).strftime('%Y-%m-%d')
    yr2_ago = (today - dt.timedelta(days=365*2)).strftime('%Y-%m-%d')

    # shelf: recent S-3/F-3/S-1 + an EFFECT notice = live shelf. S-3ASR/F-3ASR are
    # automatic shelves (effective on filing, no EFFECT notice issued).
    shelf = ec.recent_filings(cik, forms=['S-3', 'F-3', 'S-1', 'F-1'], since=yr2_ago)
    effect = ec.recent_filings(cik, forms=['EFFECT'], since=yr2_ago)
    is_asr = (not shelf.empty) and shelf['form'].str.contains('ASR').any()
    shelf_live = (not shelf.empty) and ((not effect.empty) or is_asr)
    shelf_detail = (f"{shelf.iloc[0]['form']} filed {shelf.iloc[0]['filingDate'].date()}"
                    f"{' (ASR auto-effective)' if is_asr else (' + EFFECT ' + str(effect.iloc[0]['filingDate'].date()) if not effect.empty else ' (no EFFECT seen)')}"
                    if not shelf.empty else 'no recent shelf')

    # offerings in last 12mo (424B5 = takedown/offering prospectus)
    offers = ec.recent_filings(cik, forms=['424B5', '424B3', '424B4'], since=yr_ago)
    n_offers = len(offers)
    diluted_30d = (not offers.empty) and (offers['filingDate'].max() >= pd.Timestamp(mo_ago))

    # ATM facility (full-text)
    atm_hits = ec.full_text_count('at-the-market', cik=cik, startdt=yr2_ago)
    atm_active = atm_hits > 0

    # reverse split: detect from share-count step-downs (reliable), not full-text.
    rs_count, rs_drops = reverse_splits_from_shares(ec, facts)
    rev_split = rs_count > 0
    rs_detail = ('; '.join(f"{d[0].date()} ({(today - d[0].date()).days}d ago) {fmt_sh(d[1])}->{fmt_sh(d[2])}"
                           for d in rs_drops)
                 if rs_count else 'no step-down in share count')

    # warrants present (presence only; near-money/repricing needs prose)
    warr_hits = ec.full_text_count('warrant', cik=cik, startdt=yr2_ago)

    # cash runway
    runway, cash = cash_runway_quarters(ec, facts)
    runway_lt2 = (runway is not None and runway < 2)
    runway_lt1 = (runway is not None and runway < 1)
    runway_txt = ('cash-generating' if runway == float('inf')
                  else f'{runway:.1f} quarters' if runway is not None else 'n/a')

    # share-count growth
    growth = share_growth_6mo(ec, facts)
    float_double = (growth is not None and growth >= 100)

    # ── counted risk flags (deterministic) — plain-language for one-glance reads ──
    flags = [
        dict(key='Live shelf',       on=shelf_live,
             risk='Live shelf — company can sell new stock at any time',  detail=shelf_detail),
        dict(key='Active ATM',       on=atm_active,
             risk='Active ATM — can sell shares into the market anytime, unannounced (most dangerous)',
             detail=(f'{atm_hits} filing mentions' if atm_active else 'none found')),
        dict(key='Low cash',         on=runway_lt2,
             risk='Low cash (under ~2 quarters) — likely to raise soon',  detail=runway_txt),
        dict(key='Frequent offerings', on=n_offers >= 3,
             risk='Frequent offerings (3+ in 12 months)',  detail=f'{n_offers} offering prospectuses in 12mo'),
        dict(key='Recent dilution',  on=diluted_30d,
             risk='Just diluted — an offering in the last 30 days',
             detail=(f'last offering {offers["filingDate"].max().date()}' if not offers.empty else 'none')),
        dict(key='Reverse split',    on=rev_split,
             risk='Reverse-split history (last 5y)',  detail=rs_detail),
        dict(key='Shares doubled',   on=float_double,
             risk='Share count doubled in 6 months (active dilution)',
             detail=(f'{growth:+.0f}% in 6mo' if growth is not None else 'n/a')),
    ]

    # ── serial-diluter check (any 4 of SSOT list; 5 computable) ──
    serial = sum([n_offers >= 3, atm_active, rs_count >= 2, runway_lt1, float_double]) >= 4

    warr_note = (f'{warr_hits} mentions in filings — exercise price & repricing need a filing read (ask me)'
                 if warr_hits else 'none found in filings')
    return flags, serial, warr_note


def classify(n_flags, serial):
    if serial or n_flags >= 5:
        return 'SERIAL DILUTER', '0% (do not trade long)'
    if n_flags >= 3:
        return 'HIGH RISK', '25%'
    if n_flags == 2:
        return 'MODERATE', '50%'
    return 'CLEAN', '100%'


# ── profile / catalyst / squeeze helpers (Polygon REST + EDGAR submissions) ──
US_STATES = {'AL', 'AK', 'AZ', 'AR', 'CA', 'CO', 'CT', 'DE', 'FL', 'GA', 'HI', 'ID', 'IL', 'IN',
             'IA', 'KS', 'KY', 'LA', 'ME', 'MD', 'MA', 'MI', 'MN', 'MS', 'MO', 'MT', 'NE', 'NV',
             'NH', 'NJ', 'NM', 'NY', 'NC', 'ND', 'OH', 'OK', 'OR', 'PA', 'RI', 'SC', 'SD', 'TN',
             'TX', 'UT', 'VT', 'VA', 'WA', 'WV', 'WI', 'WY', 'DC', 'PR', 'GU', 'VI', 'AS', 'MP'}


def profile_bits(ec, cik, ticker):
    ov = {}
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
    domicile = f"USA ({incorp})" if us_incorp else (incorp or 'unknown')
    foreign_forms = ec.recent_filings(cik, forms=['20-F', '6-K', 'F-1', 'F-3', 'F-4'], since='2021-01-01')
    locale = ov.get('locale')
    desc = (ov.get('description') or '').lower()
    is_foreign = (bool(incorp) and not us_incorp) or (not foreign_forms.empty) or (locale and locale != 'us')
    is_china = ('china' in desc) or ('china' in incorp.lower()) or ('hong kong' in desc and 'china' in desc)
    return dict(sector=(ov.get('sic_description') or '').title() or '—',
                mcap=ov.get('market_cap'), domicile=domicile, is_foreign=is_foreign, is_china=is_china,
                forms=sorted(set(foreign_forms['form'])) if not foreign_forms.empty else [])


def catalyst_line(ticker):
    try:
        res = (latest_news(ticker, 3) or {}).get('results') or []
    except Exception:
        res = []
    if not res:
        return None
    n = res[0]
    pub = (n.get('publisher') or {}).get('name', '')
    return f"{n.get('title', '').strip()}  _({pub}, {(n.get('published_utc') or '')[:10]})_"


def squeeze_pair(ticker):
    si = sv = None
    try:
        si = ((short_interest(ticker) or {}).get('results') or [None])[0]
    except Exception:
        si = None
    try:
        sv = ((short_volume(ticker) or {}).get('results') or [None])[0]
    except Exception:
        sv = None
    return si, sv


# ── build one card ───────────────────────────────────────────────────────────
def build_card(ec, ticker, date, float_override=None):
    today = pd.Timestamp(date).date()
    cik = ec.ticker_to_cik(ticker)
    if not cik:
        return f"## {ticker}\n  ⚠ no SEC CIK found (not an SEC filer? foreign? wrong ticker)\n"
    name = ec.company_name(ticker)
    facts = ec.companyfacts(cik)

    shares_out = ec.latest(facts, ['EntityCommonStockSharesOutstanding',
                                   'CommonStockSharesOutstanding'])
    pub_float  = ec.latest(facts, ['EntityPublicFloat'])
    price, pm_vol, pm_ts, n_pm = premarket_snapshot(ticker, date)

    so_val, so_asof = shares_out[0], shares_out[1]
    pf_val, pf_asof = pub_float[0], pub_float[1]

    # Float in shares: shares outstanding is EDGAR's reliable recent figure and the
    # basis for the SMB band + rotation. Public float ($) is annual/stale and in
    # DOLLARS — never convert it with the current price (price drift => nonsense, and
    # can exceed shares outstanding). A known float is passed via --float. Override wins.
    if float_override:
        float_sh = float_override
        float_lbl = f"Float (manual): **{fmt_sh(float_sh)}**"
    else:
        float_sh = so_val
        float_lbl = f"Float (shares outstanding): **{fmt_sh(float_sh)}**"
    band = smb_band(float_sh)

    rotation = (pm_vol / float_sh) if (pm_vol and float_sh) else None

    flags, serial, warr_note = compute_dilution(ec, cik, facts, today)
    n_flags = sum(1 for f in flags if f['on'])
    cls, max_size = classify(n_flags, serial)

    L = []
    L.append(f"## {ticker} · {name} · CIK {cik}")
    px = f"${price:.2f}" if price else "$?"
    pmv = fmt_sh(pm_vol) if pm_vol else "0"
    asof = pm_ts.strftime('%H:%M ET') if pm_ts is not None else '?'
    L.append(f"`{px}  PM vol {pmv}  ·  asof {asof}  ·  premarket read {today}`\n")

    # PROFILE (sector / domicile) + CATALYST (why it's moving)
    prof = profile_bits(ec, cik, ticker)
    flag = ' 🇨🇳' if prof['is_china'] else (' 🌐' if prof['is_foreign'] else '')
    forms = f" (files {','.join(prof['forms'])})" if prof['forms'] and prof['is_foreign'] else ''
    mcap = f" · mkt cap ${fmt_sh(prof['mcap'])}" if prof.get('mcap') else ''
    L.append(f"**PROFILE:** {prof['sector'] or '—'}{mcap} · domicile **{prof['domicile']}**{flag}{forms}")
    cat = catalyst_line(ticker)
    if cat:
        L.append(f"**CATALYST:** {cat}")
    L.append("")

    L.append("**FLOAT SIZE**")
    L.append(f"- {float_lbl} → {BAND_EMOJI.get(band[0],'')} **{band[0]}**  _({band[1]}; asof {so_asof.date() if so_asof is not None else '?'})_")
    if pf_val:
        L.append(f"- Public float: ${fmt_sh(pf_val)}  _(SEC value in $, asof {pf_asof.date() if pf_asof is not None else '?'} — not a share count)_")
    if not float_override:
        L.append("- _True free float may be below shares outstanding (insider/restricted). Pass `--float N` if you know the real number._")
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
    si, sv = squeeze_pair(ticker)
    if si or sv:
        parts, si_pct, dtc = [], None, None
        if si and si.get('short_interest'):
            si_sh = si['short_interest']
            si_pct = (si_sh / float_sh * 100) if float_sh else None
            parts.append(f"SI {fmt_sh(si_sh)}" + (f" ({si_pct:.1f}% of float)" if si_pct is not None else ""))
        if si and si.get('days_to_cover') is not None:
            dtc = si['days_to_cover']; parts.append(f"days-to-cover {dtc:g}")
        if sv and sv.get('short_volume_ratio') is not None:
            parts.append(f"daily short-vol {sv['short_volume_ratio']:.0f}%")
        if si_pct is not None or dtc is not None:
            hot = (si_pct or 0) > 30 or (dtc or 0) > 5
            warm = (si_pct or 0) > 20 or (dtc or 0) > 3
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

    # Warrants: show fixed strike(s) + shares + moneyness vs price (unlike an ATM, warrants HAVE a price)
    wt = None
    try:
        wt = extract_warrant_terms(ec, cik, (today - dt.timedelta(days=730)).strftime('%Y-%m-%d'), price)
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
    L.append("_Float band + rotation use shares outstanding (true free float may be lower). Warrant strikes & underwriter patterns need a prose read._")
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
