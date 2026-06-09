# PROJECT QUEUE — WIP = 1

**Rule:** One project active at a time. No new project starts until the active one is DONE.
Write the active number on the whiteboard. Check it off only when its "DONE =" line is true.

Goal filter: does finishing this make me more hireable at SMB Capital (by 2026-09-18)?

---

## FINISH-NOW TIER (closest to done, daily/high value)

1. ✅ **Dilution validation re-run** — DONE 2026-06-09. Point-in-time back-test, 365 events / 265 tickers.
   Answer: **YES, grade predicts the fade** (clean-vs-dirty cut: dirty fades 62% / −7.4% o2c vs clean 47% / flat).
   Writeup: `DILUTION_CARD_VALIDATION.md`. Scored table: `data/gapper_universe_Q2pilot_scored_pit.csv`.

1b. **Low-float database** ← NEW (Judin 6/9), the complement to #1. Persist the point-in-time card snapshot per
   gap event into `data/financier.duckdb` + charts + surface in Command Center. **Inherits #1's scored table as
   table one** (columns that earned their place: `grade`, `band`, outcome fields). Build on validated signal, not guesses.
   DONE = DuckDB-backed low-float store queryable + charted in the webapp for a watchlist.

## LIVE-TRADING EDGE TIER (bigger, core to how I trade)

2. **Cascade alert app / realtime scanner** — Flask dashboard, 1m polling, DEVELOPING→ARMED→GO state machine.
   DONE = app runs, alerts on a real watchlist in observe mode for a full session.

3. **Locate exhaustion screener** — iborrowdesk + FINRA SHO + Polygon, 0–100 squeeze score.
   DONE = outputs a ranked squeeze-score list for the day's low-floats.

4. **Fade Cascade build** — the overextension-short mirror of Trend Cascade.
   DONE = rules coded into a live read like cascade_live.py, flags valid fade setups.

## SUPPLY-SIDE INTELLIGENCE TIER (the master-plan modules)

5. **Pre-short detector + financier DB Phase 2/3** — SI spike around 424B date; post-deal fade; fingerprint report.
   DONE = given a ticker, outputs financier fingerprint + pre-short flag.

6. **Real-time absorption detector** — capped-tape absorption, VWAP posture, stop-hunt zones (Polygon 1m/10s).
   DONE = live read that flags distribution/absorption on a name in play.

7. **Borrow regime classifier** — SQUEEZE_PRONE / CROWDED / DILUTION_RISK / COLLAPSE_UNWIND.
   DONE = classifies any low-float into one regime with the inputs behind it.

## INFRA / EXECUTION TIER

8. **LULD spread scalp infra** — Massive WS + IBKR TWS execution stack.
   DONE = hotkey script places/cancels a scalp order against live L1.

9. **IPO pre-open auction indicator** — reference price + paired volume + imbalance, Massive NOI feed.
   DONE = panel renders the auction picture for an IPO/NOI name pre-open.

## MODELS / ANALYSIS TIER

10. **Sector rotation model** — 3-layer stack (pctabovevwap + internals + sector internals).
    DONE = daily readout of which sectors are leading/lagging with trade expressions.

11. **Dr S 4-phase cycle + 10yr earnings backtest** — validate the premarket→open→midday→close cycle.
    DONE = backtest confirms (or rejects) the cycle, with stats.

12. **Lucci 0DTE mean-reversion decode** — sell options at cycle exhaustion + VIX filter.
    DONE = documented rule set, mapped onto Cascade exhaustion signal.

## APPS / META TIER

13. **Trade grader** — setup tag library, research/grading modes, session history.
    DONE = grade a session end-to-end, export the result.

14. **Playbook grader** — multi-ticker, multi-playbook morning grading + risk allocation.
    DONE = morning input → graded playbooks + risk allocation per name.

15. **Multi-agent trading infra** — stateless agents, MCP shared layer, session handoff.
    DONE = (long horizon — keep parked until the above prove out.)

16. **Market Intelligence Report (MIR) generator** — Gmail newsletters + news/Massive → LLM-synthesized cited report (Environment/Tone + Top Stories w/ sector tags + source links), time-of-day editions (Pre-Market/Intraday/Post-Market). Modeled on the "Trading OS" MIR screen (seen 2026-06-09). Gated on: (a) #1 done, (b) premium news feeds (TradeTheNews-grade) Judin doesn't have yet ("maybe soon"). MVP buildable on web + Massive + existing inbox.
    DONE = given an edition + watchlist, outputs a cited MIR from available sources.

---

### Parked / manual (not on the build queue)
- **EOD recap docs (DRC / Journal / Trade Review)** — doing all manually by choice (2026-06-07). Reflection is the point; Tradervue already handles trades/PnL/charts. No tool to build.
- **Premarket Prep doc** — doing this manually by choice.
- **Sector internals + Twitter monitor** — on ice.

### Done / Resolved log
- ✅ 2026-06-09 — **Dilution validation re-run (#1)** — DONE. Point-in-time back-test, 365 events. Grade predicts the fade (clean-vs-dirty). Fixed 3 leaks (crash, `until=as_of`, as-of float via new `latest_asof`); 47% of tickers re-graded once lookahead removed. Writeup `DILUTION_CARD_VALIDATION.md`. SECOND build check-off. 🎉
- ✅ 2026-06-07 — **Dr S TradingView Pine port** — DONE. Built + backed up at `pine/dr_s_indicator.pine`, validated live (matches Python output). FIRST real build check-off. 🎉
- 2026-06-07 — **EOD recap automation** → resolved as MANUAL (descoped, not built). Daily docs done by hand.
