"""Shared helpers for the conference list in _data/conferences.yml.

The data file is kept as one flow-style mapping per line so diffs stay
readable and the file can be edited by hand. Only these keys are used:
name, url, deadline, date, note, pin, source.
"""
import re
from pathlib import Path

import yaml

DATA = Path(__file__).resolve().parent.parent / "_data" / "conferences.yml"
KEYS = ["name", "url", "deadline", "date", "note", "pin", "source"]
DATE_RE = re.compile(r"\b(\d{4}-\d{2}-\d{2})\b")


def load():
    with DATA.open(encoding="utf-8") as f:
        text = f.read()
    header = [ln for ln in text.splitlines() if ln.startswith("#")]
    rows = yaml.safe_load(text) or []
    for r in rows:
        for k in ("deadline", "date", "url", "name"):
            r[k] = str(r.get(k) or "").strip()
    return header, rows


def _q(v):
    return '"' + str(v).replace('"', '\\"') + '"'


def dump(header, rows):
    rows = sorted(rows, key=lambda r: (r["deadline"] or "9999-99-99", r["name"]), reverse=True)
    width = max(len(_q(r["name"])) for r in rows) + 1
    out = list(header) + []
    for r in rows:
        parts = [f"name: {_q(r['name']) + ',':<{width}} url: {_q(r['url'])}",
                 f"deadline: {_q(r['deadline'])}", f"date: {_q(r['date'])}"]
        for k in ("note", "source"):
            if r.get(k):
                parts.append(f"{k}: {_q(r[k])}")
        if r.get("pin"):
            parts.append("pin: true")
        out.append("- {" + ", ".join(parts) + "}")
    DATA.write_text("\n".join(out) + "\n", encoding="utf-8")


def key(name):
    """Normalise a conference name for matching: case/punctuation-insensitive."""
    n = name.lower().replace("symposium", "symp").replace("conference", "conf")
    n = re.sub(r"[^a-z0-9]+", " ", n)
    n = re.sub(r"\b(ieee|acm|international|intl|the)\b", "", n)
    return " ".join(n.split())


def valid_date(s):
    return bool(DATE_RE.fullmatch(s or ""))
