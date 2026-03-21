# Project: CLAUDE_BB — WAT Orchestration Hub

This is the orchestration layer for Judin's quant stack.
It does NOT contain research — it contains the workflows and tools that operate on the research repo.

Research repo: `C:/Users/Trader/quant-project/`

## Project Purpose
WAT hub: workflows (SOPs) and tools (Python scripts) that wrap quant-project.
Claude reads this to know how to execute recurring tasks reliably.

## Active Workflows
- `workflows/sector_internals.md` — pulls A/D, VOLD, TICK, breadth per sector via TradingView

## Tools in Use
- (none yet — `tools/fetch_polygon.py` goes here when Massive subscription is active)

## Outputs / Deliverables
- Research outputs live in `quant-project/notebooks/`
- Screener outputs → Google Sheets (when built)

## Project-Specific Notes
- Polygon/Massive subscription not yet active — skip any tool that requires POLYGON_API_KEY
- Primary conda env: `my_quant_lab_py310`
- Check with user before re-running anything that uses paid API credits

## Environment Variables Required
- `POLYGON_API_KEY` — Massive/Polygon.io (planned)
- `TVDATAFEED_USERNAME` — TradingView
- `TVDATAFEED_PASSWORD` — TradingView
