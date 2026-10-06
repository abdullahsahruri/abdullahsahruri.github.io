#!/usr/bin/env python3
"""Add a conference to _data/conferences.csv from its web page.

    python addconf.py https://www.isfpga.org/call-for-papers/
    python addconf.py https://www.isfpga.org/call-for-papers/ https://www.ieee-cicc.org/2027-call-for-papers/
    python addconf.py <url> --name "FPGA 2027" --deadline 2026-10-08     # override anything it got wrong
    python addconf.py <url> -y --publish                                  # no questions, then commit + push

For each URL it reads the page, pulls out the conference name + year, the paper
deadline and the conference start date, shows the row, and appends it to the CSV
(an existing entry with the same name is replaced). Standard library only.
"""
import argparse
import csv
import html
import re
import subprocess
import sys
import urllib.request
from datetime import date
from html.parser import HTMLParser
from pathlib import Path

CSV = Path(__file__).resolve().parent / "_data" / "conferences.csv"
FIELDS = ["name", "url", "deadline", "date", "note"]
UA = "Mozilla/5.0 (compatible; addconf/1.0)"

MONTHS = "jan|feb|mar|apr|may|jun|jul|aug|sep|sept|oct|nov|dec"
MONTH_NUM = {m: i + 1 for i, m in enumerate(["jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep", "oct", "nov", "dec"])}
_M = rf"(?:{MONTHS})[a-z]*\.?"
DATE_PATTERNS = [  # "16 November 2026" / "22 - 24 March 2027"
    re.compile(rf"\b(\d{{1,2}})(?:st|nd|rd|th)?\s*(?:[–-]\s*\d{{1,2}}(?:st|nd|rd|th)?\s*)?({_M})[,.]?\s*(20\d\d)\b", re.I),
    # "November 16, 2026" / "April 18 – 22, 2027" / "March 14 – March 16, 2027"
    re.compile(rf"\b({_M})\s*(\d{{1,2}})(?:st|nd|rd|th)?(?:\s*[–-]\s*(?:{_M}\s*)?\d{{1,2}}(?:st|nd|rd|th)?)?,?\s*(20\d\d)\b", re.I),
    re.compile(r"\b(20\d\d)-(\d{2})-(\d{2})\b"),  # ISO
]
DEADLINE_CUES = [  # (regex on the label just before a date, weight)
    (r"(?:firm|final|hard)\s+(?:paper\s+)?(?:submission\s+)?deadline", 6),
    (r"full[\s-]+papers?\s+(?:submission\s+)?(?:deadline|due)", 6),
    (r"(?:final|full)\s+submission\s+of\s+the\s+paper", 6),
    (r"full[\s-]*papers?\s*(?:submission)?\s*:", 5),
    (r"full[\s-]*papers?\s+submission\s*[:\-—]?\s*$", 5),
    (r"papers?\s+submission\s+(?:deadline|due)", 5),
    (r"submissions?\s+(?:deadline|due)", 4),
    (r"papers?\s+(?:deadline|due)", 4),
    (r"(?:submitted|submission)\s+(?:by|before|no later than)", 4),
    (r"papers?\s+submission\s*[:\-—]?\s*$", 3),
    (r"papers?\s*:", 3),
    (r"deadline", 2),
    (r"\bdue\b", 1),
]
NEGATIVE = r"abstract|regist|notification|notif|camera[\s-]*ready|acceptance|rebuttal|workshop|tutorial|poster|demo|special session|late[\s-]*breaking|wip\b|work[\s-]in[\s-]progress|journal|revision|opens?\b|early[\s-]bird|hotel|travel|visa|award|student"
NAME_RE = re.compile(r"\b(?:IEEE\s+|ACM\s+|IEEE/ACM\s+)?([A-Z][A-Za-z]*(?:[-+/&][A-Za-z]+)*(?:\s(?:[A-Z][A-Za-z]+|[A-Z]{2,}))?)(?:\s*(20\d\d)|\s?[’'](\d\d))\b")
NAME_REV_RE = re.compile(r"\b(20\d\d)\s+(?:IEEE\s+|ACM\s+|IEEE/ACM\s+)?([A-Z][A-Z0-9+/&-]{2,}(?:\s[A-Z][A-Z0-9+/&-]{2,})?)\b")
NOISE = {"call", "cfp", "ieee", "acm", "the", "copyright", "all", "home", "conference", "symposium", "workshop", "international",
         "important", "dates", "deadline", "papers", "paper", "for", "sunday", "monday", "tuesday", "wednesday", "thursday", "friday",
         "saturday", "january", "february", "march", "april", "may", "june", "july", "august", "september", "october", "november",
         "december", "jan", "feb", "mar", "apr", "jun", "jul", "aug", "sep", "sept", "oct", "nov", "dec", "fall", "spring", "summer",
         "winter", "university", "volume", "vol", "round", "track"}


class Text(HTMLParser):
    def __init__(self):
        super().__init__()
        self.parts, self.title, self._t, self._skip = [], "", False, 0

    def handle_starttag(self, tag, attrs):
        if tag in ("script", "style", "noscript", "svg"):
            self._skip += 1
        elif tag == "title":
            self._t = True
        elif tag in ("br", "p", "div", "li", "tr", "td", "th", "h1", "h2", "h3", "h4", "dt", "dd", "section", "body", "span", "a", "b", "strong"):
            self.parts.append("\n")

    def handle_endtag(self, tag):
        if tag in ("script", "style", "noscript", "svg") and self._skip:
            self._skip -= 1
        elif tag == "title":
            self._t = False
            self.parts.append("\n")

    def handle_data(self, d):
        if self._skip:
            return
        if self._t:
            self.title += d
        self.parts.append(d)


def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept-Language": "en"})
    with urllib.request.urlopen(req, timeout=30) as r:
        raw = r.read().decode(r.headers.get_content_charset() or "utf-8", "replace")
    p = Text()
    p.feed(raw)
    text = re.sub(r"[ \t\xa0]+", " ", html.unescape("".join(p.parts)))
    text = re.sub(r"\n\s*\n+", "\n", text)
    return " ".join(p.title.split()), text


def _date(m, i):
    g = m.groups()
    try:
        if i == 0:
            return date(int(g[2]), MONTH_NUM[g[1][:3].lower()], int(g[0]))
        if i == 1:
            return date(int(g[2]), MONTH_NUM[g[0][:3].lower()], int(g[1]))
        return date(int(g[0]), int(g[1]), int(g[2]))
    except (ValueError, KeyError):
        return None


def dates(text):
    out = []
    for i, pat in enumerate(DATE_PATTERNS):
        for m in pat.finditer(text):
            d = _date(m, i)
            if d and 2024 <= d.year <= 2032:
                is_range = i != 2 and bool(re.search(r"[–-]", m.group(0)[1:-1]))
                out.append((d, m.start(), m.end(), is_range))
    return sorted(out, key=lambda t: t[1])


def deadline(text):
    """The date whose immediately preceding label looks most like 'paper deadline'."""
    best, best_score, prev_end = None, 0, 0
    for d, s, e, is_range in dates(text):
        label = text[max(prev_end, s - 110):s].lower()
        prev_end = e
        if is_range:
            continue
        score = max((w for cue, w in DEADLINE_CUES if re.search(cue, label)), default=0)
        if not score:
            continue
        if re.search(NEGATIVE, label[-70:]):
            score -= 4
        if re.search(r"extended|new deadline", label) or "extended" in text[e:e + 40].lower():
            score += 1
        if score > best_score or (score == best_score and best and d > best):
            best, best_score = d, score
    return best


def event_date(text, dl):
    """First date *range* on the page after the deadline: conference dates are ranges."""
    c = [d for d, s, e, r in dates(text) if r and (not dl or d > dl)]
    return min(c) if c else None


def name(title, text):
    def clean(n, y):
        w = [x.lower() for x in n.split()]
        if w[0] in NOISE or w[-1] in NOISE or len(n) < 3:
            return None
        return f"{' '.join(n.split())} {y if len(y) == 4 else '20' + y}"
    for src in (title, text[:1500]):
        for m in NAME_RE.finditer(src):
            r = clean(m.group(1), m.group(2) or m.group(3))
            if r:
                return r
        for m in NAME_REV_RE.finditer(src):
            r = clean(m.group(2), m.group(1))
            if r:
                return r
    return ""


def extract(url):
    title, text = fetch(url)
    dl = deadline(text)
    ev = event_date(text, dl)
    return {"name": name(title, text), "url": url, "deadline": dl.isoformat() if dl else "",
            "date": ev.isoformat() if ev else "", "note": ""}


def key(n):
    return " ".join(re.sub(r"\b(ieee|acm|international|symposium|symp|conference|conf)\b", "", re.sub(r"[^a-z0-9]+", " ", n.lower())).split())


def load():
    with CSV.open(encoding="utf-8", newline="") as f:
        return [{k: (r.get(k) or "").strip() for k in FIELDS} for r in csv.DictReader(f)]


def save(rows):
    rows.sort(key=lambda r: (r["deadline"] or "9999", r["name"]), reverse=True)
    with CSV.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, FIELDS, lineterminator="\n")
        w.writeheader()
        w.writerows(rows)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("urls", nargs="+", help="conference or call-for-papers page(s)")
    ap.add_argument("--name"), ap.add_argument("--deadline"), ap.add_argument("--date"), ap.add_argument("--note")
    ap.add_argument("-y", "--yes", action="store_true", help="add without asking")
    ap.add_argument("--publish", action="store_true", help="git commit + push afterwards")
    a = ap.parse_args()

    rows = load()
    changed = 0
    for url in a.urls:
        try:
            row = extract(url)
        except Exception as ex:  # noqa: BLE001
            print(f"could not read {url}: {ex}")
            continue
        for f in ("name", "deadline", "date", "note"):
            if getattr(a, f):
                row[f] = getattr(a, f)
        for f in ("deadline", "date"):
            if row[f] and not re.fullmatch(r"\d{4}-\d{2}-\d{2}", row[f]):
                sys.exit(f"--{f} must be YYYY-MM-DD")
        print(f"\n  name      {row['name'] or '?'}\n  deadline  {row['deadline'] or 'TBD'}\n  date      {row['date'] or 'TBD'}\n  url       {url}")
        if not row["name"]:
            row["name"] = input("  name not found; type it (blank to skip): ").strip()
            if not row["name"]:
                continue
        if not a.yes and input("  add this? [Y/n] ").strip().lower() in ("n", "no"):
            continue
        k = key(row["name"])
        old = next((r for r in rows if key(r["name"]) == k), None)
        if old:
            rows.remove(old)
            print(f"  replaced {old['name']}")
        rows.append(row)
        changed += 1
    if not changed:
        print("nothing added")
        return
    save(rows)
    print(f"\n{changed} added to {CSV.name}")
    if a.publish or (not a.yes and input("publish now (git commit + push)? [y/N] ").strip().lower() in ("y", "yes")):
        subprocess.run(["git", "-C", str(CSV.parent.parent), "add", str(CSV)], check=True)
        subprocess.run(["git", "-C", str(CSV.parent.parent), "commit", "-m", "Update conference list"], check=False)
        subprocess.run(["git", "-C", str(CSV.parent.parent), "push"], check=False)


if __name__ == "__main__":
    main()
