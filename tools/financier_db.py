#!/usr/bin/env python
# coding: utf-8
"""
financier_db.py
---------------
DuckDB layer for the financier (underwriter / placement agent) fingerprint DB.

The idea: low-float offerings are run by a small set of recurring financiers,
and the funds they place to have repeatable post-deal supply behavior (warrant
hedging, registered-share bleed, ATM drip). If you know WHO is on a deal, you
can anticipate the supply. This DB accumulates every deal you ingest so each
financier's fingerprint sharpens over time.

Two tables (data/financier.duckdb):
  deals      — one row per offering (financier, type, warrant terms, proceeds)
  deal_perf  — post-deal price behavior per deal (filled from Polygon, Phase 2)

Reusable:
    from tools.financier_db import connect, init_db, upsert_deal, get_deals, fingerprint
"""
import os
import datetime as dt

import duckdb
import pandas as pd

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'data', 'financier.duckdb')

DDL_DEALS = """
CREATE TABLE IF NOT EXISTS deals (
    cik            VARCHAR,
    accession      VARCHAR,
    ticker         VARCHAR,
    company        VARCHAR,
    filing_date    DATE,
    form           VARCHAR,
    deal_type      VARCHAR,     -- ATM / registered_direct / PIPE / public_offering / shelf / resale / unknown
    financier      VARCHAR,     -- normalized agent/underwriter name
    financier_raw  VARCHAR,     -- as extracted from the filing
    gross_proceeds DOUBLE,
    warrant_strike DOUBLE,
    warrant_shares BIGINT,
    url            VARCHAR,
    ingested_at    TIMESTAMP,
    PRIMARY KEY (cik, accession)
);
"""

DDL_PERF = """
CREATE TABLE IF NOT EXISTS deal_perf (
    cik           VARCHAR,
    accession     VARCHAR,
    ticker        VARCHAR,
    deal_date     DATE,
    price_at_deal DOUBLE,
    ret_1d        DOUBLE,
    ret_5d        DOUBLE,
    ret_10d       DOUBLE,
    ret_20d       DOUBLE,
    max_dd_20d    DOUBLE,       -- worst close-to-close drawdown over 20 trading days (%)
    computed_at   TIMESTAMP,
    PRIMARY KEY (cik, accession)
);
"""


def connect(db_path=DB_PATH):
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    con = duckdb.connect(db_path)
    init_db(con)
    return con


def init_db(con):
    con.execute(DDL_DEALS)
    con.execute(DDL_PERF)


def upsert_deal(con, d):
    """d = dict with the deals columns (cik, accession required)."""
    con.execute("""
        INSERT OR REPLACE INTO deals
        (cik, accession, ticker, company, filing_date, form, deal_type,
         financier, financier_raw, gross_proceeds, warrant_strike, warrant_shares, url, ingested_at)
        VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)
    """, [d.get('cik'), d.get('accession'), d.get('ticker'), d.get('company'),
          d.get('filing_date'), d.get('form'), d.get('deal_type'),
          d.get('financier'), d.get('financier_raw'), d.get('gross_proceeds'),
          d.get('warrant_strike'), d.get('warrant_shares'), d.get('url'),
          dt.datetime.now()])


def upsert_perf(con, p):
    con.execute("""
        INSERT OR REPLACE INTO deal_perf
        (cik, accession, ticker, deal_date, price_at_deal, ret_1d, ret_5d, ret_10d, ret_20d, max_dd_20d, computed_at)
        VALUES (?,?,?,?,?,?,?,?,?,?,?)
    """, [p.get('cik'), p.get('accession'), p.get('ticker'), p.get('deal_date'),
          p.get('price_at_deal'), p.get('ret_1d'), p.get('ret_5d'), p.get('ret_10d'),
          p.get('ret_20d'), p.get('max_dd_20d'), dt.datetime.now()])


def get_deals(con, financier=None, ticker=None):
    q = "SELECT * FROM deals"
    where, params = [], []
    if financier:
        where.append("lower(financier) LIKE ?"); params.append(f"%{financier.lower()}%")
    if ticker:
        where.append("ticker = ?"); params.append(ticker.upper())
    if where:
        q += " WHERE " + " AND ".join(where)
    q += " ORDER BY filing_date DESC"
    return con.execute(q, params).df()


def fingerprint(con, financier):
    """Aggregate a financier's track record by joining deals -> deal_perf."""
    q = """
        SELECT d.financier,
               COUNT(*)                              AS deals,
               COUNT(DISTINCT d.ticker)              AS tickers,
               MEDIAN(p.ret_10d)                     AS median_ret_10d,
               MEDIAN(p.ret_20d)                     AS median_ret_20d,
               MEDIAN(p.max_dd_20d)                  AS median_maxdd_20d,
               AVG(CASE WHEN d.warrant_strike IS NOT NULL THEN 1 ELSE 0 END) AS pct_with_warrants
        FROM deals d
        LEFT JOIN deal_perf p USING (cik, accession)
        WHERE lower(d.financier) LIKE ?
        GROUP BY d.financier
    """
    return con.execute(q, [f"%{financier.lower()}%"]).df()


def summary(con):
    n_deals = con.execute("SELECT COUNT(*) FROM deals").fetchone()[0]
    n_fin = con.execute("SELECT COUNT(DISTINCT financier) FROM deals WHERE financier IS NOT NULL").fetchone()[0]
    n_tkr = con.execute("SELECT COUNT(DISTINCT ticker) FROM deals").fetchone()[0]
    return {"deals": n_deals, "financiers": n_fin, "tickers": n_tkr}


if __name__ == "__main__":
    con = connect()
    print(f"DB: {DB_PATH}")
    print("Summary:", summary(con))
    top = con.execute("""
        SELECT financier, COUNT(*) deals, COUNT(DISTINCT ticker) tickers
        FROM deals WHERE financier IS NOT NULL
        GROUP BY financier ORDER BY deals DESC LIMIT 15
    """).df()
    if len(top):
        print("\nTop financiers by deal count:")
        print(top.to_string(index=False))
    else:
        print("(empty — run tools/ingest_deals.py TICKER to populate)")
