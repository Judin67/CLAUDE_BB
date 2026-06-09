#!/usr/bin/env python
# coding: utf-8
"""
lowfloat_db.py — the low-float gap-event store (queue item #1b).

One table, `gap_events`, in the existing data/financier.duckdb. It is BOTH:
  - the growing, point-in-time-validated research set (every gapper, scored as-of
    its gap date, with the realized outcome), and
  - the morning watchlist generator ("today's dirty + tiny-float names, fade-first").

Built on the validated scored table from #1 (DILUTION_CARD_VALIDATION.md). Lean
slice-one columns — the broken-out 8 flags / profile / squeeze get backfilled later.

Commands:
    python tools/lowfloat_db.py load  data/gapper_universe_Q2pilot_scored_pit.csv [--source backtest]
    python tools/lowfloat_db.py watch [--date YYYY-MM-DD]      # fade-first read for a date (default: latest in DB)
    python tools/lowfloat_db.py stats                          # grade-vs-fade, straight from the DB

Data source for scoring stays EDGAR/Polygon via the existing tools — this only stores/queries.
"""
import os, sys, argparse
import duckdb
import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB   = os.path.join(ROOT, "data", "financier.duckdb")

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

# table column order — INSERT relies on this matching exactly
COLS = ["date", "ticker", "prev_close", "open", "high", "close", "day_vol",
        "gap_open", "pm_gap", "pm_high", "pm_vol", "float_sh", "rotation",
        "n_flags", "serial", "grade", "band",
        "open_to_close", "high_to_close", "faded", "scored_asof", "source"]

DDL = """
CREATE TABLE IF NOT EXISTS gap_events (
    date          DATE,
    ticker        VARCHAR,
    prev_close    DOUBLE,
    open          DOUBLE,
    high          DOUBLE,
    close         DOUBLE,
    day_vol       BIGINT,
    gap_open      DOUBLE,
    pm_gap        DOUBLE,
    pm_high       DOUBLE,
    pm_vol        BIGINT,
    float_sh      BIGINT,
    rotation      DOUBLE,   -- pm_vol / float_sh  (premarket float turnover)
    n_flags       INTEGER,
    serial        BOOLEAN,
    grade         VARCHAR,  -- CLEAN / MODERATE / HIGH RISK / SERIAL DILUTER  (direction)
    band          VARCHAR,  -- RELATIVELY SAFE … DO NOT TRADE                 (energy)
    open_to_close DOUBLE,
    high_to_close DOUBLE,
    faded         BOOLEAN,
    scored_asof   DATE,     -- point-in-time cutoff used to grade the card
    source        VARCHAR,  -- 'backtest' | 'live'
    PRIMARY KEY (date, ticker)
);
"""

# severity ranks for fade-first ordering (SQL CASE built from these)
GRADE_RANK = {"SERIAL DILUTER": 0, "HIGH RISK": 1, "MODERATE": 2, "CLEAN": 3, "UNKNOWN": 4}
BAND_RANK  = {"DO NOT TRADE": 0, "EXTREME": 1, "HIGH SQUEEZE": 2, "CAUTION": 3,
              "RELATIVELY SAFE": 4, "UNKNOWN": 5}
DIRTY = ("HIGH RISK", "SERIAL DILUTER")


def _case(col, ranks):
    whens = " ".join(f"WHEN '{k}' THEN {v}" for k, v in ranks.items())
    return f"CASE {col} {whens} ELSE 99 END"


def load(csv_path, source):
    df = pd.read_csv(csv_path)
    df["date"] = pd.to_datetime(df["date"]).dt.date
    df["rotation"] = df.apply(
        lambda r: (r["pm_vol"] / r["float_sh"]) if r.get("float_sh") and r["float_sh"] > 0 else None, axis=1)
    df["scored_asof"] = df["date"]          # backtest scored as-of the gap date
    df["source"] = source
    # nullable ints: float_sh/n_flags may be blank for UNKNOWN reads
    for c in ("day_vol", "pm_vol", "float_sh", "n_flags"):
        df[c] = pd.to_numeric(df.get(c), errors="coerce").astype("Int64")
    df["serial"] = df.get("serial").astype("boolean")
    df["faded"]  = df.get("faded").astype("boolean")
    incoming = df[COLS]

    con = duckdb.connect(DB)
    con.execute(DDL)
    con.register("incoming", incoming)
    n_before = con.execute("SELECT COUNT(*) FROM gap_events").fetchone()[0]
    con.execute("DELETE FROM gap_events WHERE (date, ticker) IN (SELECT date, ticker FROM incoming)")
    con.execute(f"INSERT INTO gap_events ({','.join(COLS)}) SELECT {','.join(COLS)} FROM incoming")
    n_after = con.execute("SELECT COUNT(*) FROM gap_events").fetchone()[0]
    rng = con.execute("SELECT MIN(date), MAX(date) FROM gap_events").fetchone()
    con.close()
    print(f"Loaded {len(incoming)} events from {os.path.basename(csv_path)} (source={source}).")
    print(f"gap_events: {n_before} → {n_after} rows · date range {rng[0]} … {rng[1]}")


def watch(date):
    con = duckdb.connect(DB, read_only=True)
    if not date:
        date = con.execute("SELECT MAX(date) FROM gap_events").fetchone()[0]
    q = f"""
        SELECT ticker, grade, band, float_sh, ROUND(rotation,1) AS rot,
               n_flags, ROUND(pm_gap*100) AS pm_gap_pct,
               ROUND(open_to_close*100,1) AS o2c_pct, faded
        FROM gap_events WHERE date = ?
        ORDER BY {_case('grade', GRADE_RANK)}, {_case('band', BAND_RANK)}, rotation DESC NULLS LAST
    """
    df = con.execute(q, [date]).df()
    con.close()
    if df.empty:
        print(f"No gap events stored for {date}.")
        return
    dirty = df[df["grade"].isin(DIRTY)]
    print(f"\n=== LOW-FLOAT WATCH · {date} · {len(df)} gappers ({len(dirty)} dirty) ===")
    print("Fade-first. Dirty grade + tiny float = lean short; pair with structure (off the PM high).\n")
    print(df.to_string(index=False))
    print("\nLegend: grade=direction · band=energy · rot=PM float turnover · o2c_pct=open→close")
    print("FADE the dirty/tiny-float names; SKIP clean. Card = filter, not entry timer.")


def stats():
    con = duckdb.connect(DB, read_only=True)
    q = f"""
        SELECT grade,
               COUNT(*) AS n,
               ROUND(100.0*AVG(CASE WHEN faded THEN 1 ELSE 0 END)) AS pct_red,
               ROUND(100*MEDIAN(open_to_close),1) AS med_o2c,
               ROUND(100*MEDIAN(high_to_close),1) AS med_giveback
        FROM gap_events GROUP BY grade ORDER BY {_case('grade', GRADE_RANK)}
    """
    df = con.execute(q).df()
    total = con.execute("SELECT COUNT(*), ROUND(100.0*AVG(CASE WHEN faded THEN 1 ELSE 0 END)) FROM gap_events").fetchone()
    con.close()
    print(f"\n=== gap_events: {total[0]} events · base fade rate {total[1]:.0f}% ===")
    print("Does a worse grade => harder fade?  (the validated edge, live from the DB)\n")
    print(df.to_string(index=False))


def main():
    ap = argparse.ArgumentParser(description="Low-float gap-event store (DuckDB).")
    sub = ap.add_subparsers(dest="cmd", required=True)
    p_load = sub.add_parser("load"); p_load.add_argument("csv"); p_load.add_argument("--source", default="backtest")
    p_watch = sub.add_parser("watch"); p_watch.add_argument("--date", default=None)
    sub.add_parser("stats")
    args = ap.parse_args()
    if args.cmd == "load":  load(args.csv, args.source)
    elif args.cmd == "watch": watch(args.date)
    elif args.cmd == "stats": stats()


if __name__ == "__main__":
    main()
