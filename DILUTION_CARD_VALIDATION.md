# Dilution Card Validation — does the grade predict the fade?

**Run:** 2026-06-09 · point-in-time back-test · 365 gap events / 265 unique tickers (Mar–May 2026)
**Universe:** `data/gapper_universe_Q2pilot.csv` → scored `data/gapper_universe_Q2pilot_scored_pit.csv`
**Method:** one structural card read per ticker, as-of its first gap date. Float (`latest_asof`) and every
dilution window (`until=as_of`) are bounded to the gap date — **no post-gap filing leaks into a pre-gap grade.**
EDGAR-only (Polygon float/free-float are real-time, so they'd reintroduce lookahead).

---

## Answer: YES — the dilution grade predicts the fade. The cut is clean-vs-dirty.

| Bucket | n | faded (closed < open) | median open→close |
|---|---|---|---|
| **CLEAN + MODERATE** (clean half) | 98 | **47%** | **+0.4%** (≈ flat) |
| **HIGH RISK + SERIAL DILUTER** (dirty half) | 261 | **62%** | **−7.4%** |

A "dirty" grade fades **15 percentage points more often** and gives up **~8 more points** open→close.
That is the edge: **grade = directional bias.** A clean-graded gapper is roughly a coin-flip that holds its open;
a dilutive-graded one fades into the close most of the time.

Full grade table (per event):

```
grade            n   pct_red  med_open→close  med_giveback_from_high
CLEAN           45     51        -1.9            -17.9
MODERATE        53     43        +2.3            -19.7
HIGH RISK      178     62        -7.4            -23.3
SERIAL DILUTER  83     61        -6.2            -23.4
```

**Honest nuance:** it's a **binary** signal (clean vs dilutive), not a smooth 4-level gradient — CLEAN vs
MODERATE is noise (small n, they swap on pct_red). The real, repeatable separation is the clean half vs the dirty half.

---

## Float band = energy, not direction (confirms "supply = direction, float = energy")

```
band              n   pct_red  med_open→close
HIGH SQUEEZE     79     49        +0.0      <- tiny floats that SQUEEZE / hold
DO NOT TRADE     18     78       -20.0      <- tiny floats that COLLAPSE
RELATIVELY SAFE 106     60        -4.3
CAUTION          59     58        -2.7
EXTREME          64     56        -4.9
```

Float band is **not monotonic** — the extremes bifurcate. The smallest floats either squeeze (HIGH SQUEEZE holds,
+0.0% o2c) or crater (DO NOT TRADE, −20% o2c, 78% red). Float tells you how *violent* the move is, not which way.
Give-back from the intraday high is large across **every** band (−18% to −30%) — these gappers nearly all fade
from the high; the grade tells you whether they close red.

---

## The point-in-time fix was material (not cosmetic)

Diffing the prior (leaky) scores against this run:
- **124 of 265 tickers (47%) changed grade** — almost all toward *less* severe.
- The old lookahead was **systematically over-grading**: BATL, TURB, ADVB, WFF, MTEK all went `HIGH RISK → CLEAN`
  once future offerings/splits were excluded; `UNKNOWN` collapsed 31 → 6.
- Float leak example: **TPET** read 31.9M shares (a 3/16 filing) for a **3/02** gap; point-in-time is **12.3M** — a
  2.6× error that mis-banded the name. Validating on the leaky scores would have answered the wrong question.

---

## Bottom line

- **Trade read:** dilutive grade (HIGH/SERIAL) = lean short/fade bias into the close; clean grade = no edge from the
  card alone (it holds ~half the time). Pair the grade (direction) with the float band (energy) — not either alone.
- **For the database (next):** store the **point-in-time** card snapshot per gap event. The columns that earned their
  place are `grade` (clean-vs-dirty) and `band` (energy/bifurcation) + the outcome fields. This scored table is table one.

**Caveat:** one read per ticker as-of *first* gap (leak-free but conservative — undercounts dilution that accrued later
in the quarter). A per-event re-score is the obvious next refinement if the database wants it.
