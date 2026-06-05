# Dilution & Float Quick-Read

> Full PRE-OPEN low-float card for any name you pull up. A pre-open bias call:
> assess everything before 9:30, decide long / short / avoid going into the open.
>
> **SSOT note:** the SMB float bands and the dilution grading come from
> `workflows/low_float_master_filter.md` **Section 6 + Section 8** — this workflow
> *applies* them automatically from SEC EDGAR; it does not redefine them.

---

## The card (sections, top to bottom)

1. **PROFILE** — sector/industry · market cap · 🇨🇳/🌐 foreign-domicile flag (files 20-F/F-1/6-K, or non-US locale).
2. **CATALYST** — latest news headline (why it's moving).
3. **FLOAT SIZE** — SMB band 🔴/🟠/🟡/🟢 (uses shares outstanding; `--float N` to override with true free float).
4. **PREMARKET ROTATION** — PM volume (04:00–09:29) ÷ float; >1x full rotation, >2x extreme.
5. **SQUEEZE (shorts)** — short interest %float · days-to-cover · daily short-vol ratio → 🔴/🟠/🟢. *Distinguishes a real short-squeeze from a dilution/retail move.*
6. **DILUTION RISK** — Clean→Serial grade + max long size, color-coded plain-language flags (live shelf, ATM, low cash, frequent/recent offerings, reverse-split **age**, share doubling), warrants line (strike · % of float · ITM/OTM vs price).

Squeeze thresholds (standard defaults): SI >20% high / >30% extreme · days-to-cover >3 notable / >5 strong.

It's a *screening* read. For the deep dossier (exact warrant strikes, underwriter patterns, management behavior) read the filing prose — see "What needs a prose read."

---

## Tool

`tools/fetch_dilution.py` (orchestrator) + `tools/edgar_client.py` (EDGAR layer) + `tools/polygon_ref.py` (overview/news/shorts).
Also surfaced in the **WAT Command Center** dashboard (`webapp/app.py`, http://127.0.0.1:5057).

```
python tools/fetch_dilution.py STI                 # one name
python tools/fetch_dilution.py STI LULU NXTT       # several
python tools/fetch_dilution.py --tickers STI,LULU  # comma list
python tools/fetch_dilution.py --watchlist names.txt   # one ticker per line
python tools/fetch_dilution.py STI --float 2500000 # override float if you know the real number
python tools/fetch_dilution.py STI --date 2026-06-04    # historical run
```

Cards print to stdout and save to `.tmp/dilution_<TICKER>_<date>.md`.

---

## Data sources

| Field | Source | Cost |
|---|---|---|
| Shares outstanding, public float, filings, XBRL | **SEC EDGAR** (`data.sec.gov`, `efts.sec.gov`) | free |
| Price + volume (for rotation) | **Polygon/Massive** | paid tier |

EDGAR needs only a contact User-Agent (`SEC_EDGAR_USER_AGENT` in `.env`) and a ~10 req/sec cap (handled in the client). No paid credits for the EDGAR side.

---

## SMB float bands (from the slide — verbatim)

| Float (shares) | Band | Behavior |
|---|---|---|
| > 30M | RELATIVELY SAFE | normal action |
| 15–30M | CAUTION | start to use caution |
| 5–15M | HIGH SQUEEZE | very high chance of squeezes + manipulation |
| 1–5M | EXTREME | $1 → $100 moves become possible |
| < 1M | DO NOT TRADE | unless very experienced |

**Float number used = shares outstanding** (EDGAR's reliable recent figure). True free
float can be lower (insider/restricted); pass `--float N` when you have the real number.
Public float is reported in **dollars** and is usually stale (annual) — shown for reference, never converted to shares with the current price.

## Premarket rotation (from low_float_master_filter SSOT)

`rotation = premarket volume (04:00–09:29 ET) ÷ float`. **>1x** = more volume than shares exist (full rotation); **>2x** = extreme supply pressure.

Float rotation — and this whole card — is a **pre-open read**: you assess float / dilution / rotation **before 9:30** to set your directional bias going into the open (per the cascade pretrade checklist and low-float Section 1/Step 6). Run it during premarket; if run after the open it uses the completed 04:00–09:29 premarket session.

## Dilution flags (Section 6, auto-filled)

Counted risk flags → classification (Section 6 table):

| Risk flags | Class | Max long size |
|---|---|---|
| 0–1 | Clean | 100% |
| 2 | Moderate | 50% |
| 3–4 | High Risk | 25% |
| 5+ / serial pattern | Serial Diluter | 0% |

Flags computed deterministically from EDGAR:
- **Live shelf** — recent S-3/F-3/S-1 + an EFFECT notice (S-3ASR/F-3ASR are auto-effective).
- **Active ATM** — full-text "at-the-market" in recent filings.
- **Cash runway < 2 quarters** — cash ÷ (annual operating burn / 4).
- **3+ offerings in 12 months** — count of 424B-type prospectuses.
- **Diluted in last 30 days** — most recent offering date.
- **Reverse split (5y)** — detected as a >40% step-down in the share-count series (not text mentions).
- **Shares +100% in 6 months** — XBRL share-count growth.

Serial-pattern path = any 4 of the Section-6 serial list (offerings, ATM, 2+ reverse splits, <1Q cash, float doubling).

---

## What needs a prose read (not auto-filled)

The tool flags presence; these need you (or a later EDGAR MCP) to read the filing text:
- **Warrant strike vs current price** (near-money?) and whether warrants were repriced/restructured.
- **Same underwriter across 3+ deals** (institutional dilution machine).
- Qualitative bias rows (business substance, earnings-quality games) — the SMB
  "Determining Bias" card layer, deferred to v2.

---

## WAT loop / hand-off

- **Tool (deterministic):** float band, rotation, all EDGAR-derivable dilution flags, classification, max size.
- **Claude (qualitative):** read the saved filing prose for warrant strikes / underwriter patterns; combine with borrow (borrow_regime) and price-action (Polygon) for the full directional bias.

---

## Edge cases / known limits

- **Stale public float** — annual figure; only shares-outstanding drives the band.
- **Foreign private issuers** — file 20-F/6-K/F-3 instead of 10-K/8-K/S-3; some flags thin out.
- **Recent deSPAC / IPO** — share-count history can jump at the merger (may look like a split); verify the step-down date.
- **No XBRL / shell companies** — facts may be missing; fields show n/a rather than guessing.
- **True free float** — EDGAR can't give exact tradable float; use `--float` for names where it matters.

---

## Roadmap

- v2: SMB "Determining Bias" two-column card (short vs avoid-short) layered on top — see `RECOVERED_edgar_session.md` for the full design.
- Later: wire warrant-strike + underwriter prose via an EDGAR MCP; push cards to Google Sheets.
