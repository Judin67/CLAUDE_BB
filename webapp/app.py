#!/usr/bin/env python
# coding: utf-8
"""
WAT Command Center — local Flask dashboard.

A visual, click-driven front-end over the WAT tools. It shells out to the
existing CLI tools (so it always runs the exact tested code) and renders their
output. No AI key needed — this is the dashboard layer. The Claude-API chat
("AI brain in-app") is a later phase; for now Claude Code is the brain.

Run:
    python webapp/app.py
    -> open http://127.0.0.1:5057

Tools wired:
    dilution  -> tools/fetch_dilution.py   (float band + premarket rotation + dilution risk)
    cascade   -> tools/cascade_premarket.py (premarket Cascade stack read)
    financier -> tools/financier_db.py      (financier DB overview)
"""
import os, re, sys, subprocess
from flask import Flask, request, jsonify, render_template

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PY = sys.executable

app = Flask(__name__)

# tool -> (script, takes_tickers, render_as)
TOOLS = {
    "dilution":  ("tools/fetch_dilution.py",   True,  "markdown"),
    "cascade":   ("tools/cascade_premarket.py", True,  "pre"),
    "financier": ("tools/financier_db.py",      False, "pre"),
}

TICKER_RE = re.compile(r'^[A-Za-z][A-Za-z.\-]{0,7}$')


def clean_tickers(raw):
    out = []
    for t in re.split(r'[\s,]+', (raw or "").strip()):
        if t and TICKER_RE.match(t):
            out.append(t.upper())
    return out


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/run")
def run_tool():
    tool = request.args.get("tool", "")
    if tool not in TOOLS:
        return jsonify(ok=False, error=f"unknown tool '{tool}'"), 400
    script, takes_tickers, render_as = TOOLS[tool]

    args = [PY, os.path.join(ROOT, *script.split("/"))]
    if takes_tickers:
        tickers = clean_tickers(request.args.get("tickers", ""))
        if not tickers:
            return jsonify(ok=False, error="enter a valid ticker"), 400
        if tool == "cascade":
            args.append(tickers[0])          # cascade is single-ticker
        else:
            args += tickers

    env = dict(os.environ, PYTHONUTF8="1", PYTHONIOENCODING="utf-8")
    try:
        r = subprocess.run(args, cwd=ROOT, capture_output=True, text=True,
                           encoding="utf-8", errors="replace", timeout=240, env=env)
    except subprocess.TimeoutExpired:
        return jsonify(ok=False, error="tool timed out (240s)"), 504

    output = (r.stdout or "") + (("\n[stderr]\n" + r.stderr) if r.returncode != 0 and r.stderr else "")
    return jsonify(ok=(r.returncode == 0), output=output.strip(), render=render_as)


if __name__ == "__main__":
    print("WAT Command Center -> http://127.0.0.1:5057")
    app.run(host="127.0.0.1", port=5057, debug=False)
