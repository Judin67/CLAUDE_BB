"""
vault_index.py — PQN Strategy Vault: one page per strategy + a generated index.

The vault = 66 PyQuant News strategy write-ups (Google Docs in the Drive folder
`PQN strategy vault`), triaged 2026-09-14 in `workflows/pqn_strategy_vault.md`.
This tool gives every strategy the SAME page shape and keeps one index of all 66.

Commands
--------
  python tools/vault_index.py split            one-time: catalog -> 66 pages (refuses if pages exist; --force to redo)
  python tools/vault_index.py index            rebuild strategies/pqn_vault/README.md from the pages' front matter
  python tools/vault_index.py check            sanity: 66 pages, 66 unique doc ids, front matter complete

Page shape (identical for all 66)
---------------------------------
  front matter: id, name, tier, strength, difficulty, source, doc, data_status, build_status, verdict
  # <ID> · <Name>
  ## At a glance · ## Thesis · ## Rules as written · ## Data map · ## Open questions
  ## Risk · ## Backtest · ## Notes

After `split`, the PAGES are the source of truth for rules, status and decisions.
The README is generated — never hand-edit it; run `index` after editing any page.
Status vocabulary (front matter):
  data_status  = buildable | partial | blocked      (set by tier: A-H / P / X)
  build_status = not started | built | backtested
  verdict      = (blank) | keep | dead | indicator only

Results convention: strategies/pqn_vault/results/<ID>/{returns.csv, trades.csv, eda.png, report.md}
(produced by whatever tool runs the strategy, ending in tools/backtest_eda.py). The index links the
folder when it exists.
"""
from __future__ import annotations

import argparse
import re
import sys
from collections import OrderedDict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CATALOG = ROOT / "workflows" / "pqn_strategy_vault.md"
VAULT = ROOT / "strategies" / "pqn_vault"
RESULTS = VAULT / "results"
README = VAULT / "README.md"

DRIVE_FOLDER = "https://drive.google.com/drive/folders/1Fm8yz5CU-pXE9F3OgR_MmOqr4qOhbrpM"

TIER_ORDER = list("ABCDEFGHPX")
DATA_STATUS = {**{t: "buildable" for t in "ABCDEFGH"}, "P": "partial", "X": "blocked"}

# which catalog bullet fields land in which page section (everything else = "Rules as written")
THESIS_FIELDS = {"thesis"}
DATA_FIELDS = {"data", "data note", "blocker", "needs", "live gap", "substitution (no futures in stack)"}
QUESTION_FIELDS = {"⚠ resolve before build"}
RISK_FIELDS = {"risk", "risk (per doc)", "doc's own caveat"}
NOTE_FIELDS = {"note"}

FM_KEYS = ["id", "name", "tier", "strength", "difficulty", "source", "doc",
           "data_status", "build_status", "verdict"]

RE_TIER = re.compile(r"^## [✅🟡❌] ([A-Z]) — (.+?) \((\d+)\)\s*$")
RE_ENTRY = re.compile(r"^### ([A-Z]\d+)\. (.+?)\s*$")
RE_HEAD = re.compile(
    r"^\[doc\]\((https://[^)]+)\)\s*·\s*(?:Strength:\s*)?\**(\w+)\**\s*·\s*(?:Difficulty:\s*)?\**(\w+)\**\s*·\s*Source:\s*(.*)$"
)
RE_FIELD = re.compile(r"^- \*\*(.+?):\*\*\s?(.*)$")
RE_XROW = re.compile(r"^\|\s*(X\d+)\s*\|\s*(.+?)\s*\|\s*\[doc\]\((https://[^)]+)\)\s*\|\s*(.+?)\s*\|\s*(.+?)\s*\|\s*$")
RE_DOCID = re.compile(r"docs\.google\.com/document/d/([A-Za-z0-9_-]+)")


def _utf8_stdout():
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass


# ----------------------------------------------------------------------------- parse the catalog

def parse_catalog(text: str):
    """Return (tiers, entries). tiers = {letter: {"desc", "count", "note"}}; entries = list of dicts."""
    tiers: "OrderedDict[str, dict]" = OrderedDict()
    entries: list[dict] = []
    tier = None
    cur = None
    in_x_table = False

    def close():
        nonlocal cur
        if cur is not None:
            entries.append(cur)
            cur = None

    for raw in text.splitlines():
        line = raw.rstrip()
        m = RE_TIER.match(line)
        if m:
            close()
            tier = m.group(1)
            tiers[tier] = {"desc": m.group(2), "count": int(m.group(3)), "note": []}
            in_x_table = tier == "X"
            continue
        if line.startswith("## "):          # any other H2 ends the tier sections
            close()
            tier = None
            in_x_table = False
            continue
        if tier is None:
            continue
        if line.startswith("> ") and cur is None:
            tiers[tier]["note"].append(line[2:].strip())
            continue
        if in_x_table:
            m = RE_XROW.match(line)
            if m:
                xid, name, doc, missing, unblock = m.groups()
                entries.append({
                    "id": xid, "tier": tier, "name": name.strip(), "doc": doc,
                    "strength": "", "difficulty": "", "source": "",
                    "fields": [("Missing data", missing.strip()), ("What would unblock it", unblock.strip())],
                })
            continue
        m = RE_ENTRY.match(line)
        if m:
            close()
            cur = {"id": m.group(1), "tier": tier, "name": m.group(2).strip(), "doc": "",
                   "strength": "", "difficulty": "", "source": "", "fields": []}
            continue
        if cur is None:
            continue
        m = RE_HEAD.match(line)
        if m and not cur["doc"]:
            cur["doc"], cur["strength"], cur["difficulty"], cur["source"] = m.groups()
            cur["source"] = cur["source"].strip()
            continue
        m = RE_FIELD.match(line)
        if m:
            cur["fields"].append((m.group(1).strip(), m.group(2).strip()))
            continue
        if line.strip() == "---" or not line.strip():
            continue
        # continuation line -> append to the last field
        if cur["fields"]:
            k, v = cur["fields"][-1]
            cur["fields"][-1] = (k, (v + " " + line.strip()).strip())
    close()
    return tiers, entries


# ----------------------------------------------------------------------------- page writing

def slug(name: str, limit: int = 48) -> str:
    s = re.sub(r"[^a-z0-9]+", "_", name.lower()).strip("_")
    return s[:limit].rstrip("_")


def padded(sid: str) -> str:
    return f"{sid[0]}{int(sid[1:]):02d}"


def page_path(sid: str, name: str) -> Path:
    return VAULT / f"{padded(sid)}_{slug(name)}.md"


def _bullets(pairs):
    return "\n".join(f"- **{k}:** {v}" for k, v in pairs) if pairs else "—"


def render_page(e: dict, tiers: dict) -> str:
    t = e["tier"]
    tier_label = f"{t} — {tiers[t]['desc']}"
    fields = e["fields"]
    low = lambda k: k.lower()
    thesis = [(k, v) for k, v in fields if low(k) in THESIS_FIELDS]
    data = [(k, v) for k, v in fields if low(k) in DATA_FIELDS]
    questions = [(k, v) for k, v in fields if low(k) in QUESTION_FIELDS]
    risk = [(k, v) for k, v in fields if low(k) in RISK_FIELDS]
    notes = [(k, v) for k, v in fields if low(k) in NOTE_FIELDS]
    used = THESIS_FIELDS | DATA_FIELDS | QUESTION_FIELDS | RISK_FIELDS | NOTE_FIELDS
    rules = [(k, v) for k, v in fields if low(k) not in used]

    fm = OrderedDict([
        ("id", e["id"]), ("name", e["name"]), ("tier", tier_label),
        ("strength", e["strength"] or "—"), ("difficulty", e["difficulty"] or "—"),
        ("source", e["source"] or "—"), ("doc", e["doc"]),
        ("data_status", DATA_STATUS[t]), ("build_status", "not started"), ("verdict", ""),
    ])

    glance = [
        f"- **Tier:** {tier_label}",
        f"- **Strength (PQN):** {fm['strength']} · **Difficulty (PQN):** {fm['difficulty']}",
        f"- **Source:** {fm['source']}",
        f"- **PQN doc:** [{e['id']} on Drive]({e['doc']})",
        f"- **Data status:** {fm['data_status']} · **Build status:** {fm['build_status']} · **Verdict:** —",
    ]

    if t == "X":
        rules_md = "Not triaged in detail — blocked on data (see Data map). The PQN doc has the full rules and pseudo-code."
        data_md = _bullets(fields)
    else:
        rules_md = _bullets(rules)
        data_md = _bullets(data)
    tier_note = tiers[t]["note"]
    if tier_note:
        data_md += "\n\n> **Tier note:** " + " ".join(tier_note)

    q_md = _bullets(questions) if questions else "None flagged in the triage."
    q_md += "\n\n**Decisions:** none yet. (Resolve each line with Judin before building — never pick a definition silently.)"

    body = f"""---
{chr(10).join(f'{k}: {v}' for k, v in fm.items())}
---
# {e['id']} · {e['name']}

## At a glance
{chr(10).join(glance)}

## Thesis
{_bullets(thesis) if thesis else "—"}

## Rules as written
{rules_md}

## Data map
{data_md}

## Open questions
{q_md}

## Risk
{_bullets(risk) if risk else "—"}

## Backtest
Not run. When it is, results live in `results/{e['id']}/` (returns.csv · trades.csv · eda.png · report.md), ending in `tools/backtest_eda.py`.

## Notes
{_bullets(notes) if notes else "—"}
"""
    return body


def cmd_split(force: bool):
    text = CATALOG.read_text(encoding="utf-8")
    tiers, entries = parse_catalog(text)
    VAULT.mkdir(parents=True, exist_ok=True)
    existing = [p for p in VAULT.glob("*.md") if p.name != "README.md"]
    if existing and not force:
        sys.exit(f"{len(existing)} pages already exist in {VAULT}. Use --force to overwrite.")
    for p in existing:
        p.unlink()
    n = 0
    for e in entries:
        page_path(e["id"], e["name"]).write_text(render_page(e, tiers), encoding="utf-8", newline="\n")
        n += 1
    by_tier = {t: sum(1 for e in entries if e["tier"] == t) for t in tiers}
    print(f"wrote {n} pages to {VAULT}")
    for t, c in by_tier.items():
        flag = "" if c == tiers[t]["count"] else f"  <-- header says {tiers[t]['count']}"
        print(f"  {t}: {c}{flag}")
    missing = [e["id"] for e in entries if not e["doc"]]
    if missing:
        print("  entries without a doc link:", missing)


# ----------------------------------------------------------------------------- index

def read_front_matter(p: Path) -> dict:
    txt = p.read_text(encoding="utf-8")
    if not txt.startswith("---\n"):
        raise ValueError(f"{p.name}: no front matter")
    end = txt.index("\n---", 4)
    fm = {}
    for line in txt[4:end].splitlines():
        k, _, v = line.partition(":")
        fm[k.strip()] = v.strip()
    fm["_path"] = p
    return fm


def load_pages() -> list[dict]:
    pages = [read_front_matter(p) for p in sorted(VAULT.glob("*.md")) if p.name != "README.md"]

    def key(fm):
        return (TIER_ORDER.index(fm["id"][0]), int(fm["id"][1:]))

    return sorted(pages, key=key)


def cmd_index():
    pages = load_pages()
    tiers: "OrderedDict[str, str]" = OrderedDict()
    for fm in pages:
        tiers.setdefault(fm["tier"][0], fm["tier"])
    counts = {t: sum(1 for fm in pages if fm["tier"][0] == t) for t in tiers}
    buildable = sum(1 for fm in pages if fm["data_status"] == "buildable")
    partial = sum(1 for fm in pages if fm["data_status"] == "partial")
    blocked = sum(1 for fm in pages if fm["data_status"] == "blocked")
    built = sum(1 for fm in pages if fm["build_status"] in ("built", "backtested"))
    tested = sum(1 for fm in pages if fm["build_status"] == "backtested")

    rows = []
    for fm in pages:
        rid = fm["id"]
        rdir = RESULTS / rid
        res = f"[results](results/{rid}/)" if rdir.is_dir() else "—"
        rows.append(
            f"| {rid} | {fm['name']} | {fm['tier'][0]} | {fm['data_status']} | {fm['build_status']} | "
            f"{fm['verdict'] or '—'} | [doc]({fm['doc']}) | [page]({fm['_path'].name}) | {res} |"
        )

    tier_rows = "\n".join(f"| {t} | {tiers[t][4:]} | {counts[t]} |" for t in tiers)

    md = f"""# PQN Strategy Vault — index

> 66 strategies from the PyQuant News *Alpha Strategy Vault* (pro.pyquantnews.com), saved as Google Docs in
> the Drive folder [`PQN strategy vault`]({DRIVE_FOLDER}). Triaged 2026-09-14 against Massive (Polygon) + free SEC EDGAR.
> **This file is generated** by `python tools/vault_index.py index` from each page's front matter — do not hand-edit.
> Edit the page, then rerun. One page per strategy, all the same shape. PQN's rules are kept as written and never
> blended with Judin's own models (Cascade / Dr. S / low-float stack).

**{len(pages)} strategies · {buildable} buildable · {partial} partial · {blocked} blocked · {built} built · {tested} backtested**

## How to use this folder
- **Find a strategy:** the table below. ID → page (rules, data map, open questions, status) → PQN doc (full write-up + pseudo-code).
- **Status lives on the page** (front matter): `data_status` buildable/partial/blocked · `build_status` not started/built/backtested · `verdict` keep/dead/indicator only.
- **Backtest a strategy:** put that ONE strategy on `PROJECT_QUEUE.md` first (WIP = 1), resolve its *Open questions* with Judin, run the open checks its tier needs, build as a `tools/` script, and land outputs in `results/<ID>/` ending in `tools/backtest_eda.py`. Then set `build_status` on the page and rerun `index`.
- **Data map, known traps, open checks, build checklist:** [`workflows/pqn_strategy_vault.md`](../../workflows/pqn_strategy_vault.md).

## Scoreboard
| Tier | Meaning | Count |
|---|---|---|
{tier_rows}
| **Total** | | **{len(pages)}** |

## All strategies
| ID | Name | Tier | Data | Build | Verdict | Doc | Page | Results |
|---|---|---|---|---|---|---|---|---|
{chr(10).join(rows)}
"""
    README.write_text(md, encoding="utf-8", newline="\n")
    print(f"wrote {README}  ({len(pages)} rows)")


# ----------------------------------------------------------------------------- check

def cmd_check():
    pages = load_pages()
    ok = True
    print(f"pages: {len(pages)}")
    if len(pages) != 66:
        ok = False
        print("  !! expected 66")
    for fm in pages:
        miss = [k for k in FM_KEYS if k not in fm]
        if miss:
            ok = False
            print(f"  !! {fm['_path'].name}: missing front matter keys {miss}")
    ids = [fm["id"] for fm in pages]
    if len(set(ids)) != len(ids):
        ok = False
        print("  !! duplicate ids")
    page_docs = {RE_DOCID.search(fm["doc"]).group(1) for fm in pages if RE_DOCID.search(fm["doc"])}
    cat_docs = set(RE_DOCID.findall(CATALOG.read_text(encoding="utf-8")))
    print(f"doc ids: pages {len(page_docs)} · catalog {len(cat_docs)}")
    if page_docs != cat_docs:
        ok = False
        print("  !! page docs != catalog docs")
        print("     only in catalog:", sorted(cat_docs - page_docs))
        print("     only in pages:  ", sorted(page_docs - cat_docs))
    print("OK" if ok else "FAILED")
    return ok


def main():
    _utf8_stdout()
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("split", help="catalog -> 66 pages (one-time)")
    s.add_argument("--force", action="store_true", help="overwrite existing pages")
    sub.add_parser("index", help="rebuild README.md from page front matter")
    sub.add_parser("check", help="sanity checks")
    a = ap.parse_args()
    if a.cmd == "split":
        cmd_split(a.force)
    elif a.cmd == "index":
        cmd_index()
    elif a.cmd == "check":
        sys.exit(0 if cmd_check() else 1)


if __name__ == "__main__":
    main()
