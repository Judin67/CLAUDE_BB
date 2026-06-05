#!/usr/bin/env python
# coding: utf-8
"""
ingest_deals.py
---------------
Scan a ticker's SEC offering filings, parse the deal (financier / type / warrant
terms / proceeds) from the prospectus prose, and store each into the financier DB.

Builds the financier fingerprint database one name at a time — run it on the
morning's names and it accumulates. Dedups by SEC accession number.

Usage:
    python tools/ingest_deals.py STI
    python tools/ingest_deals.py STI ABCD WXYZ
    python tools/ingest_deals.py --watchlist names.txt --since 2023-01-01

Then inspect:  python tools/financier_db.py
Data: SEC EDGAR (free). Parsing is heuristic prose extraction — verify outliers.
"""
import sys, os, re, argparse, datetime as dt, warnings
warnings.filterwarnings('ignore')
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import requests
from tools.edgar_client import EdgarClient
from tools.financier_db import connect, upsert_deal, summary

# Forms that describe an offering / supply event (high signal).
DEAL_FORMS = ['424B5', '424B4', '424B3', '424B2', '424B1', 'S-1', 'F-1']

# Known recurring low-float financiers — normalized name : regex.
KNOWN_FINANCIERS = {
    'H.C. Wainwright':        r'h\.?\s?c\.?\s?wainwright|wainwright\s*&\s*co',
    'Maxim Group':            r'maxim group',
    'A.G.P./Alliance Global': r'\ba\.?g\.?p\.?\b|alliance global partners',
    'EF Hutton':              r'ef hutton|kingswood',
    'ThinkEquity':            r'thinkequity',
    'Ladenburg Thalmann':     r'ladenburg',
    'Aegis Capital':          r'aegis capital',
    'Roth Capital':           r'roth capital|roth mkm|roth\s*/\s*mkm',
    'Craig-Hallum':           r'craig-?hallum',
    'Dawson James':           r'dawson james',
    'Univest Securities':     r'univest',
    'Chardan':                r'chardan',
    'Spartan Capital':        r'spartan capital',
    'WallachBeth':            r'wallachbeth',
    'The Benchmark Company':  r'benchmark company',
    'Lake Street':            r'lake street',
    'Northland':              r'northland (?:capital|securities)',
    'Rodman & Renshaw':       r'rodman\s*&?\s*renshaw',
    'Boral Capital':          r'boral capital|d\.?\s?boral',
    'Titan Partners':         r'titan partners',
    'Brookline Capital':      r'brookline capital',
    'Cantor Fitzgerald':      r'cantor fitzgerald',
    'Jefferies':              r'jefferies',
    'B. Riley':               r'b\.?\s?riley',
    'Aegis':                  r'\baegis\b',
    'Univest':                r'\bunivest\b',
}

ANCHORS = r'(placement agent|book-?running manager|underwrit|sole manager|representative of the underwriters|acted as|sales agent)'


def fetch_text(ec, url):
    try:
        html = requests.get(url, headers={'User-Agent': ec.ua}, timeout=45).text
    except Exception:
        return ''
    text = re.sub(r'<[^>]+>', ' ', html)
    text = re.sub(r'&#x[0-9a-fA-F]+;|&[a-z]+;', ' ', text)
    return re.sub(r'\s+', ' ', text)


def parse_deal_type(form, text):
    t = text.lower()
    # resale registration (selling holders) takes precedence — most S-1/As are this
    if 'selling securityholder' in t or 'selling stockholder' in t:
        return 'resale'
    if 'at-the-market offering' in t or 'at the market offering' in t or 'sales agreement' in t or 'atm program' in t:
        return 'ATM'
    if 'registered direct' in t:
        return 'registered_direct'
    if 'private placement' in t:
        return 'PIPE'
    if 'underwriting agreement' in t or 'firm commitment' in t:
        return 'public_offering'
    if form.startswith('424B'):
        return 'shelf_takedown'
    return 'unknown'


def parse_financier(text):
    """Prefer a known financier appearing near an underwriter/agent anchor."""
    anchors = [m.start() for m in re.finditer(ANCHORS, text, re.I)]
    # 1) known financier within 250 chars of an anchor
    for norm, pat in KNOWN_FINANCIERS.items():
        for m in re.finditer(pat, text, re.I):
            if any(abs(m.start() - a) < 250 for a in anchors):
                return norm, text[max(0, m.start()-40):m.start()+60].strip()
    # 2) any known financier anywhere
    for norm, pat in KNOWN_FINANCIERS.items():
        m = re.search(pat, text, re.I)
        if m:
            return norm, text[max(0, m.start()-40):m.start()+60].strip()
    # 3) extract a Proper-Noun name right before "acted as ... placement agent/underwriter"
    m = re.search(r'([A-Z][\w&.,\- ]{2,40}?),?\s+(?:acted as|served as)[^.]{0,40}'
                  r'(?:placement agent|underwriter|sales agent)', text)
    if m:
        return m.group(1).strip(), m.group(0)[:90].strip()
    return None, None


def parse_warrant(text):
    """Return (strike, shares). Strike = most-common 'exercise price' (skips ~$0 pre-funded;
    mode is robust to one-off outliers in tables)."""
    from collections import Counter
    strikes = [round(float(x), 4) for x in re.findall(r'exercise price of \$?([0-9]+(?:\.[0-9]+)?)', text, re.I)]
    strikes = [s for s in strikes if s >= 0.05]          # drop pre-funded ~$0.005
    strike = Counter(strikes).most_common(1)[0][0] if strikes else None
    shares = None
    for pat in [r'warrants?\s+to\s+purchase\s+(?:up\s+to\s+)?([0-9,]{4,})\s+shares',
                r'([0-9,]{4,})\s+shares[^.]{0,60}?issuable upon[^.]{0,40}?exercise',
                r'exercise of\s+(?:up to\s+)?([0-9,]{4,})\s+(?:warrants|shares)']:
        m = re.search(pat, text, re.I)
        if m:
            try:
                shares = int(m.group(1).replace(',', '')); break
            except ValueError:
                pass
    return strike, shares


def parse_proceeds(text):
    m = re.search(r'gross proceeds of (?:approximately )?\$?([0-9]+(?:\.[0-9]+)?)\s*(million|billion)?', text, re.I)
    if not m:
        return None
    val = float(m.group(1))
    unit = (m.group(2) or '').lower()
    return val * (1e9 if unit == 'billion' else 1e6 if unit == 'million' else 1.0)


def ingest_ticker(ec, con, ticker, since):
    cik = ec.ticker_to_cik(ticker)
    if not cik:
        print(f"  {ticker}: no CIK — skip"); return 0
    company = ec.company_name(ticker)
    filings = ec.recent_filings(cik, forms=DEAL_FORMS, since=since)
    if filings.empty:
        print(f"  {ticker}: no offering filings since {since}"); return 0
    n = 0
    for _, f in filings.iterrows():
        url = ec.filing_url(cik, f['accessionNumber'], f['primaryDocument'])
        text = fetch_text(ec, url)
        if not text:
            continue
        fin, fin_raw = parse_financier(text)
        strike, shares = parse_warrant(text)
        deal = {
            'cik': cik, 'accession': f['accessionNumber'], 'ticker': ticker, 'company': company,
            'filing_date': f['filingDate'].date(), 'form': f['form'],
            'deal_type': parse_deal_type(f['form'], text),
            'financier': fin, 'financier_raw': fin_raw,
            'gross_proceeds': parse_proceeds(text),
            'warrant_strike': strike, 'warrant_shares': shares, 'url': url,
        }
        upsert_deal(con, deal)
        n += 1
        print(f"  {ticker} {f['form']:>6} {f['filingDate'].date()}  "
              f"{deal['deal_type']:<15} agent={fin or '-':<24} "
              f"warr=${strike if strike else '-'}/{shares if shares else '-'}sh")
    return n


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('tickers', nargs='*')
    ap.add_argument('--watchlist')
    ap.add_argument('--since', default='2022-01-01')
    args = ap.parse_args()

    tickers = [t.upper() for t in args.tickers]
    if args.watchlist and os.path.exists(args.watchlist):
        with open(args.watchlist) as f:
            tickers += [ln.strip().upper() for ln in f if ln.strip() and not ln.startswith('#')]
    tickers = list(dict.fromkeys(tickers))
    if not tickers:
        ap.error('no tickers given')

    ec = EdgarClient()
    con = connect()
    total = 0
    for t in tickers:
        print(f"\n{t}:")
        total += ingest_ticker(ec, con, t, args.since)
    print(f"\nIngested/updated {total} filings across {len(tickers)} ticker(s).")
    print("DB summary:", summary(con))
    con.close()


if __name__ == '__main__':
    main()
