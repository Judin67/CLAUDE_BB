#!/usr/bin/env python
# coding: utf-8
"""
edgar_client.py
---------------
Free SEC EDGAR data layer (raw requests — no SDK, matches house style).

Pulls everything needed for low-float dilution work straight from the public
SEC JSON APIs. No API key, no cost. SEC only requires a contact User-Agent
header (read from .env: SEC_EDGAR_USER_AGENT) and a 10 req/sec rate limit.

Endpoints used:
    Ticker -> CIK : https://www.sec.gov/files/company_tickers.json
    Submissions   : https://data.sec.gov/submissions/CIK{cik10}.json
    XBRL facts    : https://data.sec.gov/api/xbrl/companyfacts/CIK{cik10}.json
    Full-text     : https://efts.sec.gov/LATEST/search-index?q=...

Reusable from other tools:
    from tools.edgar_client import EdgarClient
    ec = EdgarClient()
    cik = ec.ticker_to_cik("STI")
    facts = ec.companyfacts(cik)
    filings = ec.recent_filings(cik, forms=["S-3", "424B5", "8-K"])
    hits = ec.full_text_search("at-the-market", cik=cik, forms="424B5")

Designed so an MCP server could wrap this class later with zero changes.
"""
import os
import re
import time
import json
import datetime as dt

import requests
import pandas as pd
from dotenv import load_dotenv

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', '.env'))

CACHE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '.tmp')
DEFAULT_UA = "Judin Toussaint judintoussaint@gmail.com"
RATE_SLEEP = 0.15            # ~6-7 req/s, comfortably under SEC's 10/s cap


class EdgarClient:
    def __init__(self, user_agent=None, cache_dir=CACHE_DIR):
        self.ua = user_agent or os.getenv("SEC_EDGAR_USER_AGENT", DEFAULT_UA)
        self.cache_dir = cache_dir
        os.makedirs(self.cache_dir, exist_ok=True)
        self._tickers = None
        self._last_call = 0.0

    # ── low-level GET (rate-limited, UA-headered) ────────────────────────────
    def _headers(self):
        return {"User-Agent": self.ua, "Accept-Encoding": "gzip, deflate"}

    def _get(self, url, params=None, host="data.sec.gov"):
        wait = RATE_SLEEP - (time.time() - self._last_call)
        if wait > 0:
            time.sleep(wait)
        h = self._headers()
        h["Host"] = host
        last_exc = None
        for attempt in range(4):
            if attempt:
                time.sleep(0.5 * attempt)
            r = requests.get(url, params=params, headers=h, timeout=30)
            self._last_call = time.time()
            if r.status_code == 404:
                return None
            # 429 (rate-limit) / 403 (UA throttle) / 5xx are transient — back off & retry
            if r.status_code in (429, 403) or r.status_code >= 500:
                ra = r.headers.get("Retry-After")
                time.sleep(float(ra) if (ra and ra.isdigit()) else 1.0 * (attempt + 1))
                last_exc = requests.HTTPError(f"{r.status_code} for {r.url}")
                continue
            r.raise_for_status()
            return r.json()
        raise last_exc

    # ── ticker -> CIK (cached daily) ─────────────────────────────────────────
    def _load_tickers(self):
        if self._tickers is not None:
            return self._tickers
        path = os.path.join(self.cache_dir, "sec_company_tickers.json")
        fresh = (os.path.exists(path) and
                 time.time() - os.path.getmtime(path) < 86400)
        if fresh:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
        else:
            data = self._get("https://www.sec.gov/files/company_tickers.json",
                             host="www.sec.gov")
            with open(path, "w", encoding="utf-8") as f:
                json.dump(data, f)
        # data is {idx: {cik_str, ticker, title}}
        self._tickers = {row["ticker"].upper(): row for row in data.values()}
        return self._tickers

    def _ticker_row(self, ticker):
        """Look up a ticker row, normalizing class-share separators.
        SEC stores class tickers with a hyphen (BRK-B); traders/Polygon use the
        dot form (BRK.B) or none. Try the common variants."""
        m = self._load_tickers()
        t = ticker.upper()
        for cand in (t, t.replace('.', '-'), t.replace('.', ''), t.replace('-', '')):
            if cand in m:
                return m[cand]
        return None

    def ticker_to_cik(self, ticker):
        """Return zero-padded 10-digit CIK string, or None if not found."""
        row = self._ticker_row(ticker)
        return f"{int(row['cik_str']):010d}" if row else None

    def company_name(self, ticker):
        row = self._ticker_row(ticker)
        return row["title"] if row else None

    # ── submissions / filings ────────────────────────────────────────────────
    def submissions(self, cik):
        return self._get(f"https://data.sec.gov/submissions/CIK{cik}.json")

    _FILING_COLS = ["form", "filingDate", "reportDate", "accessionNumber",
                    "primaryDocument", "primaryDocDescription"]

    def recent_filings(self, cik, forms=None, since=None, until=None):
        """
        DataFrame of filings (form, filingDate, reportDate, accessionNumber, primaryDocument, primaryDocDescription).
        forms : optional list of form types. EXACT form + amendment match (anchored regex),
                so 'S-1' no longer matches 'S-11'/'S-1MEF' and 'S-3' no longer matches
                'S-3D'/'S-3DPOS'. List ASR variants (S-3ASR/F-3ASR) explicitly if wanted.
        since : optional 'YYYY-MM-DD' lower bound on filingDate.
        until : optional 'YYYY-MM-DD' upper bound on filingDate (point-in-time runs).
        Pulls older paged shard files when `since` reaches before the inline 'recent' block.
        """
        sub = self.submissions(cik)
        if not sub:
            return pd.DataFrame(columns=self._FILING_COLS)
        filings = sub.get("filings", {})
        blocks = [filings.get("recent", {})]
        if since:
            rec_dates = filings.get("recent", {}).get("filingDate", [])
            oldest = rec_dates[-1] if rec_dates else None
            if oldest and pd.Timestamp(oldest) > pd.Timestamp(since):
                for shard in (filings.get("files") or []):
                    nm = shard.get("name")
                    fto = shard.get("filingTo")
                    if nm and not (fto and pd.Timestamp(fto) < pd.Timestamp(since)):
                        data = self._get(f"https://data.sec.gov/submissions/{nm}")
                        if data:
                            blocks.append(data)
        frames = []
        for b in blocks:
            n = len(b.get("form", []))
            if not n:
                continue
            frames.append(pd.DataFrame({c: (b.get(c) if len(b.get(c, [])) == n else [None] * n)
                                        for c in self._FILING_COLS}))
        if not frames:
            return pd.DataFrame(columns=self._FILING_COLS)
        df = pd.concat(frames, ignore_index=True)
        df["filingDate"] = pd.to_datetime(df["filingDate"], errors="coerce")
        if forms:
            pat = r'^(?:' + '|'.join(re.escape(x) for x in forms) + r')(?:/A.*)?$'
            df = df[df["form"].astype(str).str.match(pat)]
        if since:
            df = df[df["filingDate"] >= pd.Timestamp(since)]
        if until:
            df = df[df["filingDate"] <= pd.Timestamp(until)]
        return df.sort_values("filingDate", ascending=False).reset_index(drop=True)

    def filing_url(self, cik, accession, doc=None):
        acc = accession.replace("-", "")
        base = f"https://www.sec.gov/Archives/edgar/data/{int(cik)}/{acc}"
        return f"{base}/{doc}" if doc else base

    def document_text(self, url, max_chars=2_000_000):
        """Fetch a filing document and return tag-stripped plain text (rate-limited)."""
        wait = RATE_SLEEP - (time.time() - self._last_call)
        if wait > 0:
            time.sleep(wait)
        try:
            r = requests.get(url, headers=self._headers(), timeout=45)
            self._last_call = time.time()
            if r.status_code != 200:
                return ""
            html = r.text
        except Exception:
            return ""
        text = re.sub(r"<[^>]+>", " ", html)
        text = re.sub(r"&#?\w+;", " ", text)
        return re.sub(r"\s+", " ", text)[:max_chars]

    # ── XBRL company facts ───────────────────────────────────────────────────
    def companyfacts(self, cik, use_cache=True, max_age=43200):
        path = os.path.join(self.cache_dir, f"sec_facts_{cik}.json")
        if use_cache and os.path.exists(path) and time.time() - os.path.getmtime(path) < max_age:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        data = self._get(f"https://data.sec.gov/api/xbrl/companyfacts/CIK{cik}.json")
        if data:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(data, f)
        return data

    _CONCEPT_COLS = ["end", "val", "start", "form", "filed", "fy", "fp", "unit", "frame"]

    @classmethod
    def concept(cls, facts, tag, taxonomies=("us-gaap", "dei"), unit=None, positive=False):
        """All datapoints for an XBRL tag as a DataFrame
        (end, val, start, form, filed, fy, fp, unit, frame), sorted by (end, filed) STABLY.
        unit     : if set, keep only that unit (e.g. 'shares','USD') — avoids mixing currencies.
        positive : if True, drop val<=0 placeholder rows (avoids false 0-share reads).
        Returns an empty frame WITH columns when the tag is absent, so callers can
        safely dropna/access columns (a bare DataFrame() would KeyError)."""
        empty = pd.DataFrame(columns=cls._CONCEPT_COLS)
        if not facts:
            return empty
        for tax in taxonomies:
            node = facts.get("facts", {}).get(tax, {}).get(tag)
            if not node:
                continue
            rows = []
            for u, points in node.get("units", {}).items():
                if unit and u != unit:
                    continue
                for p in points:
                    rows.append({"end": p.get("end"), "val": p.get("val"),
                                 "start": p.get("start"), "form": p.get("form"),
                                 "filed": p.get("filed"), "fy": p.get("fy"),
                                 "fp": p.get("fp"), "unit": u, "frame": p.get("frame")})
            if rows:
                df = pd.DataFrame(rows)
                df["end"] = pd.to_datetime(df["end"], errors="coerce")
                df["start"] = pd.to_datetime(df["start"], errors="coerce")
                df["filed"] = pd.to_datetime(df["filed"], errors="coerce")
                if positive:
                    df = df[df["val"].notna() & (df["val"] > 0)]
                # stable sort so per-end restatements keep deterministic order
                return df.sort_values(["end", "filed"], kind="mergesort").reset_index(drop=True)
        return empty

    def latest(self, facts, tags, taxonomies=("us-gaap", "dei")):
        """Value for the most-recent REPORTING PERIOD among candidate tags (not just
        most-recently-filed — a late 10-K/A for an old period must NOT clobber the
        current count). Ranks by (end, filed); ties prefer earlier tags in `tags`
        (so dei entity-total beats a us-gaap per-class row). Returns (value, asof_end, tag)."""
        best = (None, None, None)
        best_key = None
        for i, tag in enumerate(tags):
            df = self.concept(facts, tag, taxonomies, positive=True)
            if df.empty:
                continue
            row = df.iloc[-1]               # concept is sorted (end, filed) → latest period+restatement
            end = row["end"] if pd.notna(row["end"]) else pd.Timestamp.min
            filed = row["filed"] if pd.notna(row["filed"]) else pd.Timestamp.min
            key = (end, filed, -i)
            if best_key is None or key > best_key:
                best_key = key
                best = (row["val"], row["end"], tag)
        return best

    def latest_asof(self, facts, tags, as_of, taxonomies=("us-gaap", "dei")):
        """Point-in-time `latest()`: among datapoints actually FILED on/before `as_of`,
        return the value for the most-recent reporting period. Prevents lookahead — a
        post-`as_of` 10-Q's share count must not be used to grade a pre-`as_of` event.
        `as_of` may be a date/datetime/str. Returns (value, asof_end, tag) like latest()."""
        cutoff = pd.Timestamp(as_of)
        best = (None, None, None)
        best_key = None
        for i, tag in enumerate(tags):
            df = self.concept(facts, tag, taxonomies, positive=True)
            if df.empty:
                continue
            df = df[df["filed"].notna() & (df["filed"] <= cutoff)]   # only what was public by as_of
            if df.empty:
                continue
            row = df.iloc[-1]               # still sorted (end, filed) → latest period+restatement ≤ cutoff
            end = row["end"] if pd.notna(row["end"]) else pd.Timestamp.min
            filed = row["filed"] if pd.notna(row["filed"]) else pd.Timestamp.min
            key = (end, filed, -i)
            if best_key is None or key > best_key:
                best_key = key
                best = (row["val"], row["end"], tag)
        return best

    # ── full-text search (EFTS) ──────────────────────────────────────────────
    def full_text_search(self, q, cik=None, forms=None, startdt=None, enddt=None, size=20):
        """
        EDGAR full-text search. Returns list of hit dicts (form, filed, accession, cik, snippet-ish).
        q     : query string (phrases auto-quoted if they contain spaces).
        forms : comma string or list, e.g. '424B5' or ['8-K','424B5'].
        Note: EFTS only indexes filings from 2001-present.
        """
        # EFTS 500s on bare unquoted terms — always quote (phrase match).
        if not (q.startswith('"') and q.endswith('"')):
            q = f'"{q}"'
        params = {"q": q}
        if cik:
            params["ciks"] = cik
        if forms:
            params["forms"] = forms if isinstance(forms, str) else ",".join(forms)
        # EFTS needs startdt+enddt AND dateRange=custom together, else it 500s.
        if startdt or enddt:
            params["dateRange"] = "custom"
            params["startdt"] = startdt or "2001-01-01"
            params["enddt"] = enddt or dt.date.today().strftime("%Y-%m-%d")
        try:
            data = self._get("https://efts.sec.gov/LATEST/search-index", params=params,
                             host="efts.sec.gov")
        except Exception:
            return []
        if not data:
            return []
        out = []
        for h in data.get("hits", {}).get("hits", [])[:size]:
            src = h.get("_source", {})
            adsh = (h.get("_id", "") or "").split(":")[0]
            out.append({
                "form": src.get("file_type") or src.get("root_form"),
                "filed": src.get("file_date"),
                "accession": adsh,
                "cik": (src.get("ciks") or [None])[0],
                "display_names": src.get("display_names"),
            })
        return out

    def full_text_count(self, q, cik=None, forms=None, startdt=None, enddt=None):
        """Total number of matching filings (cheap relevance probe)."""
        # EFTS 500s on bare unquoted terms — always quote (phrase match).
        if not (q.startswith('"') and q.endswith('"')):
            q = f'"{q}"'
        params = {"q": q}
        if cik:
            params["ciks"] = cik
        if forms:
            params["forms"] = forms if isinstance(forms, str) else ",".join(forms)
        # EFTS needs startdt+enddt AND dateRange=custom together, else it 500s.
        if startdt or enddt:
            params["dateRange"] = "custom"
            params["startdt"] = startdt or "2001-01-01"
            params["enddt"] = enddt or dt.date.today().strftime("%Y-%m-%d")
        try:
            data = self._get("https://efts.sec.gov/LATEST/search-index", params=params,
                             host="efts.sec.gov")
        except Exception:
            return 0
        if not data:
            return 0
        total = data.get("hits", {}).get("total", {})
        return total.get("value", 0) if isinstance(total, dict) else (total or 0)


if __name__ == "__main__":
    import sys
    t = sys.argv[1].upper() if len(sys.argv) > 1 else "AAPL"
    ec = EdgarClient()
    cik = ec.ticker_to_cik(t)
    print(f"{t} -> CIK {cik} ({ec.company_name(t)})")
    if cik:
        facts = ec.companyfacts(cik)
        so = ec.latest(facts, ["EntityCommonStockSharesOutstanding",
                               "CommonStockSharesOutstanding"])
        pf = ec.latest(facts, ["EntityPublicFloat"])
        print(f"  shares outstanding: {so[0]:,} (as of {so[1].date() if so[1] is not None else '?'})" if so[0] else "  shares outstanding: n/a")
        print(f"  public float ($):   {pf[0]:,} (as of {pf[1].date() if pf[1] is not None else '?'})" if pf[0] else "  public float: n/a")
        recent = ec.recent_filings(cik, forms=["S-3", "424B5", "8-K"], since="2025-01-01")
        print(f"  recent S-3/424B5/8-K filings: {len(recent)}")
        print(f"  ATM mentions (full-text): {ec.full_text_count('at-the-market', cik=cik)}")
