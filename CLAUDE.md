# Project: CLAUDE_BB — WAT Orchestration Hub

This is the orchestration layer for Judin's quant stack.
It does NOT contain research — it contains the workflows and tools that operate on the research repo.

Research repo: `C:/Users/Trader/quant-project/`

## Project Purpose
WAT hub: workflows (SOPs) and tools (Python scripts) that wrap quant-project.
Claude reads this to know how to execute recurring tasks reliably.

## Active Workflows
- `workflows/cascade_core_rules.md` — Cascade strategy rules reference
- `workflows/cascade_pretrade_checklist.md` — morning pre-trade checklist
- `workflows/earnings_trend.md` — earnings cycle model (built, tool ready)
- `workflows/low_float_master_filter.md` — pre-market + real-time low float grading
- `workflows/parabolic_exhaustion_grading.md` — parabolic exhaustion trade grading
- `workflows/spread_scalp_on_core.md` — spread scalp on directional core position
- `workflows/dr_s.md` — Dr. S indicator (opening participation/displacement)
- `workflows/dilution_bias.md` — low-float quick-read: float size (SMB bands) + rotation + dilution risk from SEC EDGAR

## On Ice (resume after trade grader)
- `workflows/sector_internals.md` — A/D, VOLD, TICK, breadth per sector (file removed, rebuild when ready)
- `workflows/twitter_trader_monitor.md` — scrape trader tweets, extract tickers, store in DuckDB

## Tools in Use

**Data**
- `tools/fetch_polygon.py` — all OHLCV fetching via Polygon/Massive (paid real-time tier; 10s + extended hours supported)

**Cascade (the MTF-slope strategy — see `workflows/cascade_core_rules.md`)**
- `tools/cascade_live.py` — live stack read: Weekly→Daily→4h→65m→30m→5m→1m→10s, with slope/gate alignment/cycle phase. `PULLBACK` = pre-entry alert, `FIRED` = entry. Manual snapshot.
- `tools/chart_intraday.py` — intraday candlestick + VWAP + volume charts
- `tools/legacy/` — superseded Gen-1 "MTF slope" chart scripts (`mtf_candles.py`, `mtf_stop_viz.py`). Reference only, **not current** — use `cascade_live.py` instead.

**Indicators / screeners**
- `tools/dr_s_indicator.py` — Dr. S opening participation/displacement (`dr_s` workflow)
- `tools/fetch_volume_mtf.py` — multi-timeframe volume
- `tools/premarket_avol.py` — premarket average volume
- `tools/fetch_earnings_trend.py` — earnings cycle model

**Low-float / dilution (see `workflows/dilution_bias.md`)**
- `tools/fetch_dilution.py` — full PRE-OPEN low-float card: profile (sector/mkt-cap/🇨🇳 foreign-domicile flag) · catalyst (news) · float size (SMB bands) · premarket rotation (PM vol÷float) · squeeze (short interest %float / days-to-cover / short-vol) · dilution risk (shelf/ATM/warrants w/ strike+%float+moneyness/cash/reverse-split age → Clean→Serial grade + max size). Color-coded 🔴/🟠/🟡/🟢, plain-language. Single or batch (`--tickers`/`--watchlist`, `--float` override, `--date`). EDGAR (free) + Polygon.
- `tools/edgar_client.py` — reusable raw-requests SEC EDGAR data layer (CIK, submissions, XBRL companyfacts, full-text search, document_text). Needs `SEC_EDGAR_USER_AGENT` in `.env`. MCP-wrappable later.
- `tools/polygon_ref.py` — Polygon REST reference layer (ticker overview/sector, news/catalyst, short-interest, short-volume). Standalone — does NOT use the Massive MCP (tools must run from CLI/cron).
- `tools/financier_db.py` + `tools/ingest_deals.py` — financier (underwriter/placement-agent) fingerprint DB (DuckDB at `data/financier.duckdb`). `ingest_deals.py TICKER` scans EDGAR offerings → parses financier/deal-type/warrant terms → stores (dedup by accession). Phase 1 done; Phase 2 (post-deal fade) + Phase 3 (fingerprint report) pending.

**Apps**
- `webapp/app.py` — **WAT Command Center** (Flask, http://127.0.0.1:5057). Visual dashboard that shells out to the CLI tools (dilution / cascade / financier) and renders the cards. Run: `python webapp/app.py`. AI brain = Claude Code for now; in-app Claude-API chat is a later phase.

**Twitter pipeline (on ice)**
- `tools/get_twitter_cookies.py`, `tools/fetch_twitter_mentions.py`, `tools/run_twitter_pipeline.py`

**Endpoint tests**
- `tools/test_polygon_options.py`, `tools/test_polygon_earnings.py`

## Outputs / Deliverables
- Research outputs live in `quant-project/notebooks/`
- Screener outputs → Google Sheets (when built)

## Data Access — Two Methods

### 1. Massive MCP Server (installed, connected)
- Registered in Claude Code — I can call Massive endpoints directly mid-conversation, no script needed
- Use for: ad-hoc data questions, one-off pulls, exploring endpoints, answering questions about a ticker
- Examples: "what was NVDA revenue last quarter", "show me RBLX's last 8Q EPS", "does Massive have an options flow endpoint"

### 2. Python Tools (WAT architecture)
- Use for: repeatable workflows, chart output, multi-ticker runs, anything that produces a saved deliverable
- Examples: `fetch_earnings_trend.py`, `fetch_polygon.py`
- These stay as scripts — MCP does not replace them

**Rule:** exploring or asking a data question → MCP. Building something repeatable → Python tool.

## Project-Specific Notes
- **Data source: Polygon/Massive ONLY. Never use TradingView or yfinance.**
- **Tier: PAID real-time (active).** Same-day intraday works; 10-second bars + extended hours (04:00–20:00 ET) available. No "delayed plan" workaround — that constraint is gone.
- Primary conda env: `my_quant_lab_py310`
- Check with user before re-running anything that uses paid API credits

## Environment Variables Required
- `POLYGON_API_KEY` — Massive/Polygon.io (active)
