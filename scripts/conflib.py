"""Helpers for the conference list in _data/conferences.yml.

One flow-style mapping per line so the file stays readable and hand-editable.
Keys: name, url, deadline, date, note (all strings; empty deadline/date = TBD).
"""
import re
from pathlib import Path

import yaml

DATA = Path(__file__).resolve().parent.parent / "_data" / "conferences.yml"
DATE_RE = re.compile(r"\d{4}-\d{2}-\d{2}")


def load():
    text = DATA.read_text(encoding="utf-8")
    header = [ln for ln in text.splitlines() if ln.startswith("#")]
    rows = yaml.safe_load(text) or []
    for r in rows:
        for k in ("name", "url", "deadline", "date", "note"):
            r[k] = str(r.get(k) or "").strip()
    return header, rows


def _q(v):
    return '"' + str(v).replace('"', '\\"') + '"'


def dump(header, rows):
    rows = sorted(rows, key=lambda r: (r["deadline"] or "9999-99-99", r["name"]), reverse=True)
    width = max(len(_q(r["name"])) for r in rows) + 1
    out = list(header)
    for r in rows:
        line = f"- {{name: {_q(r['name']) + ',':<{width}} url: {_q(r['url'])}, deadline: {_q(r['deadline'])}, date: {_q(r['date'])}"
        if r["note"]:
            line += f", note: {_q(r['note'])}"
        out.append(line + "}")
    DATA.write_text("\n".join(out) + "\n", encoding="utf-8")


def key(name):
    """Case/punctuation-insensitive name for matching ("IEEE ISCAS 2027" == "iscas 2027")."""
    n = re.sub(r"[^a-z0-9]+", " ", name.lower())
    n = re.sub(r"\b(ieee|acm|international|intl|the|symposium|symp|conference|conf)\b", "", n)
    return " ".join(n.split())


def valid_date(s):
    return bool(DATE_RE.fullmatch(s or ""))
