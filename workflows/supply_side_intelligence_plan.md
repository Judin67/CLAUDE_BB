# Supply-Side Intelligence System — Master Plan

> The unifying blueprint for the low-float work. Synthesizes the insider/MM view
> (JJ VwapTrader1 + "Reaper"), the short-seller view (The Friendly Bear / David),
> and the squeeze-data view (Ortex) into one system. See `jj_market_maker_playbook.md`
> for the source mechanics and `dilution_bias.md` for the pre-open card spec.

---

## Thesis
**A low-float move is engineered supply meeting manufactured demand.** Insiders/financiers hold cheap stock; a market maker creates liquidity so they can distribute into a catalyst-driven retail chase; whoever buys the manufactured demand is the exit. **Edge = read the *seller's* side** — before the open (what *can* hit) and in real time (what *is* hitting, and is it almost gone).

## Three perspectives, one system
- **Insider / MM (JJ + Reaper)** — *how* supply is created & distributed (morning knee-jerk, pull-bids-to-stop-hunt, capped-tape absorption, backdooring, pre-shorting offerings, PFOF).
- **Short-seller (David / Friendly Bear)** — *how to trade against it* (float<1M avoid, PM rotation, borrow fee, inst-ownership, lockups, cash/ATM).
- **Squeeze data (Ortex)** — *how to measure it* (daily est. SI, CTB avg, utilization, short score).

## The 5 supply questions → the 5 modules
| # | Question | Module | Status |
|---|---|---|---|
| 1 | How much structural supply can hit? | Pre-open dilution/supply card | ✅ built |
| 2 | Who's the distributor & how do their deals behave? | Financier fingerprint DB | 🟡 Phase 1 |
| 3 | Is distribution happening *now*? | Real-time absorption/distribution detector | ❌ |
| 4 | Is the supply almost *gone* (trigger)? | Supply-exhaustion + squeeze (Ortex/locate) | ❌ |
| 5 | Who's on the tape (the chessboard)? | Level 2 / MMID watch + execution | ❌ |

---

## Architecture (WAT)
- **Data layers (tools):** `edgar_client.py` (filings) · `polygon_ref.py` (overview/news/shorts) · `fetch_polygon.py` (bars) · `financier_db.py` (DuckDB). **Add:** Ortex API (squeeze data) · Massive WS + IBKR (real-time L2 + execution).
- **Intelligence modules:** dilution/supply card · financier DB + fingerprints · distribution detector · exhaustion/squeeze trigger · MMID/tape.
- **Surface:** WAT Command Center dashboard (`webapp/`) + later in-app Claude-API chat.

## Phased build (each ships standalone value)
**Phase 0 — Foundation** ✅ — card · EDGAR/Polygon-ref/DuckDB layers · financier DB P1 · dashboard.

**Phase 1 — Distributor intelligence** *(who's selling)*
- Financier DB Phase 2 (post-deal fade) + Phase 3 (fingerprint report)
- EDGAR firehose auto-ingest (populate market-wide)
- **Pre-short detector** (JJ's GME insight): SI spike around a 424B/offering date = funds pre-shorting the deal.

**Phase 2 — Movers scanner** *(surface the names)* — premarket gappers/% movers → auto-runs the card + auto-ingests the financier. (Ties into `project_realtime_scanner`.)

**Phase 3 — Real-time distribution detector (the JJ/Reaper layer)** *(is it happening now)*
- **Capped-tape absorption** (vol↑, price flat at a ceiling = diluter)
- **VWAP posture** (reclaim vs loss after a run)
- **Morning knee-jerk pattern** (9:30 spike → back-and-fill)
- **Stop-hunt zones** (clustered obvious levels)
- Pure Polygon (1m/10s). Add **AVWAP** (Brian Shannon) anchored to the catalyst/offering.

**Phase 4 — Supply-exhaustion + squeeze trigger** *(the entry)*
- Cap clears / absorption flips = supply gone → entry. Fuse **Cascade** entry + **Ortex** (utilization, CTB, short score, % free float on loan) + `locate_exhaustion` + `borrow_regime`.

**Phase 5 — Level 2 / MMID layer + execution** *(the chessboard)*
- Real-time L2 via Massive WS + IBKR (`luld_scalp_infra`) → **MMID dilution watch** (VFIN/NITE/PUMA…), **hidden-size/iceberg** detection, then **execution** (LULD scalp).

**Phase 6 — Decision surface / AI** — unified Command Center + in-app Claude-API chat (`multiagent_infra`): "is STI being distributed right now?" → runs the whole stack.

---

## Card spec additions (from the new inputs)
Add to `fetch_dilution.py` card:
- **Institutional ownership %** (avoid >40% — David) — EDGAR 13F / Polygon.
- **Insider lockup expiration** (EDGAR S-1/424 prose).
- **Ortex squeeze block** (daily est. SI, CTB avg, utilization, short score, % free float on loan) — upgrade over FINRA bi-weekly.
- **Short-seller lean** — auto-grade from the David checklist (float-tier + PM-rotation + borrow + inst-own + lockup + cash/ATM → long/short/avoid).

## Design principles
- **Supply-first** in every module (JJ's doctrine).
- **Two halves:** pre-open card = "what *can* happen"; real-time detectors = "what *is* happening."
- Build on what exists; free EDGAR + paid Polygon; **Ortex (paid API)** and **L2/execution** are the heavier later layers.
- This **unifies** the scattered projects: [[project_dilution_bias]], financier DB, [[project_realtime_scanner]], [[project_locate_exhaustion]], [[project_borrow_regime]], [[project_luld_scalp_infra]], [[project_multiagent_infra]].

## Data-source decisions
- **Squeeze data:** start with Massive short-interest/volume (free, FINRA bi-weekly) → **upgrade to Ortex API** (daily est. SI, CTB avg, utilization, short score). **Judin is likely subscribing to Ortex** (host notes this data is genuinely hard to find) — so **Ortex = the chosen squeeze-data layer for Phase 4**; build that integration when the subscription is active.
- **Real-time L2:** Massive WS + IBKR (already the `luld_scalp_infra` stack).
- **AI brain:** Claude Code now → in-app Claude API later.
