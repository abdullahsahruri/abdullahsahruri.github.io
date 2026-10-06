#!/usr/bin/env python3
"""Discover conference deadlines from keyword web searches.

Pipeline (one run):
  1. read keywords from _data/conference_keywords.yml;
  2. search the web for "<keyword> <year> call for papers" (Google Custom
     Search when GOOGLE_API_KEY + GOOGLE_CSE_ID are set, otherwise the
     DuckDuckGo HTML endpoint, no key needed);
  3. fetch each result page, pull out the conference name+year, the paper
     deadline and the conference date with regex heuristics;
  4. write every finding to _data/conference_candidates.yml (never rendered
     on the site) and merge the high-confidence, future-dated ones into
     _data/conferences.yml with source: search.

Run `python scripts/discover_conferences.py --dry-run` to see what it would
do without writing anything; `--review-only` writes candidates but never
touches the public list.
"""
import argparse
import html
import json
import os
import re
import sys
import time
import urllib.parse
import urllib.request
from datetime import date
from html.parser import HTMLParser
from pathlib import Path

import yaml

import conflib

ROOT = Path(__file__).resolve().parent.parent
KEYWORDS = ROOT / "_data" / "conference_keywords.yml"
CANDIDATES = ROOT / "_data" / "conference_candidates.yml"
UA = "Mozilla/5.0 (compatible; conference-deadline-discovery; +https://abdullahsahruri.github.io/)"

# Domains that aggregate or mirror CFPs; they rarely give a clean single-conference page.
SKIP_DOMAINS = ("wikicfp.com", "myhuiban.com", "github.com", "linkedin.com", "researchgate.net",
                "x.com", "twitter.com", "facebook.com", "reddit.com", "youtube.com", "easychair.org",
                "conferencelists.org", "10times.com", "semiconductorcalendar.com", "ourglocal.com",
                "dl.acm.org", "ieeexplore.ieee.org", "scholar.google", "ieee.org/conferences")

MONTHS = "jan|feb|mar|apr|may|jun|jul|aug|sep|sept|oct|nov|dec"
MONTH_NUM = {m: i + 1 for i, m in enumerate(["jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep", "oct", "nov", "dec"])}
_M = rf"(?:{MONTHS})[a-z]*\.?"
# "16 November 2026" | "November 16, 2026" | "Nov. 16 2026" | "2026-11-16" | "April 18 – 22, 2027" | "22 - 24 March 2027"
DATE_PATTERNS = [
    re.compile(rf"\b(\d{{1,2}})(?:st|nd|rd|th)?\s*(?:[–-]\s*\d{{1,2}}(?:st|nd|rd|th)?\s*)?({_M})[,.]?\s*(20\d\d)\b", re.I),      # D [– D] Month YYYY
    re.compile(rf"\b({_M})\s*(\d{{1,2}})(?:st|nd|rd|th)?(?:\s*[–-]\s*(?:{_M}\s*)?\d{{1,2}}(?:st|nd|rd|th)?)?,?\s*(20\d\d)\b", re.I),  # Month D [– D], YYYY
    re.compile(r"\b(20\d\d)-(\d{2})-(\d{2})\b"),                                                                    # ISO
]
DEADLINE_CUES = [  # (regex, weight) — matched against the label text just before a date
    (r"(?:firm|final|hard)\s+(?:paper\s+)?(?:submission\s+)?deadline", 6),
    (r"full[\s-]+papers?\s+(?:submission\s+)?(?:deadline|due)", 6),
    (r"(?:final|full)\s+submission\s+of\s+the\s+paper", 6),
    (r"full[\s-]*papers?\s*(?:submission)?\s*:", 5),
    (r"papers?\s+submission\s+(?:deadline|due)", 5),
    (r"submissions?\s+(?:deadline|due)", 4),
    (r"papers?\s+(?:deadline|due)", 4),
    (r"(?:submitted|submission)\s+(?:by|before|no later than)", 4),
    (r"full[\s-]*papers?\s+submission\s*[:\-—]?\s*$", 5),
    (r"papers?\s+submission\s*[:\-—]?\s*$", 3),
    (r"papers?\s*:", 3),
    (r"deadline", 2),
    (r"\bdue\b", 1),
]
NEGATIVE_CUES = r"abstract|regist|notification|notif|camera[\s-]*ready|registration|acceptance|rebuttal|workshop|tutorial|poster|demo|special session|late[\s-]*breaking|wip\b|work[\s-]in[\s-]progress|journal|revision|opens?\b|early[\s-]bird|hotel|travel|visa|award|student"
# "FPGA 2027", "DATE 2027", "FPT'26", "Hot Chips 2026", and the reversed "2027 IEEE CICC"
NAME_RE = re.compile(r"\b(?:IEEE\s+|ACM\s+|IEEE/ACM\s+)?([A-Z][A-Za-z]*(?:[-+/&][A-Za-z]+)*(?:\s(?:[A-Z][A-Za-z]+|[A-Z]{2,}))?)(?:\s*(20\d\d)|\s?[’'](\d\d))\b")
NAME_REV_RE = re.compile(r"\b(20\d\d)\s+(?:IEEE\s+|ACM\s+|IEEE/ACM\s+)?([A-Z][A-Z0-9+/&-]{2,}(?:\s[A-Z][A-Z0-9+/&-]{2,})?)\b")
NOISE_NAMES = {"call", "cfp", "ieee", "acm", "the", "copyright", "all", "home", "conference", "symposium", "workshop",
               "international", "important", "dates", "deadline", "papers", "paper", "for", "sunday", "monday", "tuesday",
               "wednesday", "thursday", "friday", "saturday", "january", "february", "march", "april", "may", "june", "july",
               "august", "september", "october", "november", "december", "jan", "feb", "mar", "apr", "jun", "jul", "aug",
               "sep", "sept", "oct", "nov", "dec", "fall", "spring", "summer", "winter", "university", "volume", "vol"}


# ---------------------------------------------------------------- HTML -> text
class TextExtractor(HTMLParser):
    def __init__(self):
        super().__init__()
        self.parts, self.title, self._in_title, self._skip = [], "", False, 0

    def handle_starttag(self, tag, attrs):
        if tag in ("script", "style", "noscript", "svg"):
            self._skip += 1
        elif tag == "title":
            self._in_title = True
        elif tag in ("br", "p", "div", "li", "tr", "td", "th", "h1", "h2", "h3", "h4", "dt", "dd", "section", "body", "span", "a", "b", "strong"):
            self.parts.append("\n")

    def handle_endtag(self, tag):
        if tag in ("script", "style", "noscript", "svg") and self._skip:
            self._skip -= 1
        elif tag == "title":
            self._in_title = False
            self.parts.append("\n")

    def handle_data(self, data):
        if self._skip:
            return
        if self._in_title:
            self.title += data
        self.parts.append(data)


def html_to_text(raw):
    p = TextExtractor()
    p.feed(raw)
    text = html.unescape("".join(p.parts))
    text = re.sub(r"[ \t\xa0]+", " ", text)
    text = re.sub(r"\n\s*\n+", "\n", text)
    return " ".join(p.title.split()), text


# ---------------------------------------------------------------- dates
def parse_date(m, pat_idx):
    g = m.groups()
    try:
        if pat_idx == 0:
            d, mon, y = int(g[0]), MONTH_NUM[g[1][:3].lower()], int(g[2])
        elif pat_idx == 1:
            mon, d, y = MONTH_NUM[g[0][:3].lower()], int(g[1]), int(g[2])
        else:
            y, mon, d = int(g[0]), int(g[1]), int(g[2])
        return date(y, mon, d)
    except (ValueError, KeyError):
        return None


def find_dates(text):
    """Yield (date, start, end, is_range) for every date mention in text."""
    out = []
    for i, pat in enumerate(DATE_PATTERNS):
        for m in pat.finditer(text):
            d = parse_date(m, i)
            if d and 2024 <= d.year <= 2032:
                out.append((d, m.start(), m.end(), "–" in m.group(0) or "-" in m.group(0)[1:-1] and i != 2))
    out.sort(key=lambda t: t[1])
    return out


def extract_deadline(text):
    """Pick the paper-submission deadline. Each date is scored on the label text that
    immediately precedes it (from the previous date mention, at most 110 chars), so a
    date only inherits the cue written for it, not its neighbours'."""
    best, best_score, prev_end = None, 0, 0
    for d, s, e, is_range in find_dates(text):
        seg_start = max(prev_end, s - 110)
        label = text[seg_start:s].lower()
        prev_end = e
        if is_range:
            continue
        score = 0
        for cue, w in DEADLINE_CUES:
            if re.search(cue, label):
                score = max(score, w)
        if not score:
            continue
        tail = text[e:e + 40].lower()
        if re.search(NEGATIVE_CUES, label[-70:]):
            score -= 4
        if re.search(r"extended|new deadline", label) or "extended" in tail:
            score += 1
        if score > best_score or (score == best_score and best and d > best):
            best, best_score = d, score
    return best, best_score


def extract_event_date(text, deadline):
    """First date *range* on the page that is after the deadline (conference dates are ranges)."""
    cands = [d for d, s, e, is_range in find_dates(text) if is_range]
    if deadline:
        cands = [d for d in cands if d > deadline]
    return min(cands) if cands else None


def _clean_name(name, year):
    name = " ".join(name.split())
    words = [w.lower() for w in name.split()]
    if words[0] in NOISE_NAMES or words[-1] in NOISE_NAMES or len(name) < 3:
        return None
    if len(year) == 2:
        year = "20" + year
    return f"{name} {year}", int(year)


def extract_name(title, text):
    for src in (title, text[:1500]):
        for m in NAME_RE.finditer(src):
            r = _clean_name(m.group(1), m.group(2) or m.group(3))
            if r:
                return r
        for m in NAME_REV_RE.finditer(src):
            r = _clean_name(m.group(2), m.group(1))
            if r:
                return r
    return None, None


# ---------------------------------------------------------------- search backends
def http_get(url, timeout=25):
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept-Language": "en"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read().decode(r.headers.get_content_charset() or "utf-8", "replace")


def search_google(query, n=8):
    key, cx = os.environ.get("GOOGLE_API_KEY"), os.environ.get("GOOGLE_CSE_ID")
    q = urllib.parse.urlencode({"key": key, "cx": cx, "q": query, "num": n})
    data = json.loads(http_get("https://www.googleapis.com/customsearch/v1?" + q))
    return [(it["link"], it.get("title", "")) for it in data.get("items", [])]


def search_ddg(query, n=8):
    raw = http_get("https://html.duckduckgo.com/html/?" + urllib.parse.urlencode({"q": query}))
    out = []
    for m in re.finditer(r'<a[^>]+class="result__a"[^>]+href="([^"]+)"[^>]*>(.*?)</a>', raw, re.S):
        href = html.unescape(m.group(1))
        if "uddg=" in href:  # DDG redirect wrapper
            href = urllib.parse.unquote(href.split("uddg=")[1].split("&")[0])
        out.append((href, re.sub("<[^>]+>", "", m.group(2))))
        if len(out) >= n:
            break
    return out


def search(query):
    if os.environ.get("GOOGLE_API_KEY") and os.environ.get("GOOGLE_CSE_ID"):
        return search_google(query)
    return search_ddg(query)


# ---------------------------------------------------------------- main
def analyse_page(url, title, text, today):
    name, year = extract_name(title, text)
    deadline, score = extract_deadline(text)
    event = extract_event_date(text, deadline)
    conf = 0
    if name:
        conf += 2
    if deadline:
        conf += min(score, 6)
        if deadline >= today:
            conf += 2
        if year and deadline.year in (year - 1, year):
            conf += 2
    if event:
        conf += 1
    return {
        "name": name or "", "url": url, "deadline": deadline.isoformat() if deadline else "",
        "date": event.isoformat() if event else "", "confidence": conf,
        "title": title[:120], "found": today.isoformat(),
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true", help="print findings, write nothing")
    ap.add_argument("--review-only", action="store_true", help="write candidates only, never the public list")
    ap.add_argument("--min-confidence", type=int, default=11)
    ap.add_argument("--max-pages", type=int, default=60)
    a = ap.parse_args()

    cfg = yaml.safe_load(KEYWORDS.read_text(encoding="utf-8")) or {}
    keywords = cfg.get("keywords") or []
    exclude = [e.lower() for e in cfg.get("exclude_domains") or []]
    years = cfg.get("years") or [date.today().year, date.today().year + 1]
    templates = cfg.get("query_templates") or ["{keyword} {year} call for papers", "{keyword} conference {year} paper deadline"]
    today = date.today()

    seen, pages = set(), []
    for kw in keywords:
        for y in years:
            for t in templates:
                q = t.format(keyword=kw, year=y)
                try:
                    results = search(q)
                except Exception as ex:  # noqa: BLE001
                    print(f"search failed for {q!r}: {ex}", file=sys.stderr)
                    continue
                for url, title in results:
                    host = urllib.parse.urlparse(url).netloc.lower()
                    if url in seen or any(s in url.lower() for s in SKIP_DOMAINS) or any(e in host for e in exclude):
                        continue
                    seen.add(url)
                    pages.append((url, kw, q))
                time.sleep(1.0)
                if len(pages) >= a.max_pages:
                    break

    findings = []
    for url, kw, q in pages[: a.max_pages]:
        try:
            title, text = html_to_text(http_get(url))
        except Exception as ex:  # noqa: BLE001
            print(f"fetch failed {url}: {ex}", file=sys.stderr)
            continue
        f = analyse_page(url, title, text, today)
        f["keyword"], f["query"] = kw, q
        findings.append(f)
        time.sleep(0.5)

    findings.sort(key=lambda f: -f["confidence"])
    for f in findings:
        print(f"{f['confidence']:>2}  {f['name'] or '?':<28} {f['deadline'] or 'TBD':<11} {f['date'] or 'TBD':<11} {f['url']}")
    if a.dry_run:
        return 0

    # candidates file: keep history, newest first, de-duplicated by url
    old = yaml.safe_load(CANDIDATES.read_text(encoding="utf-8")) if CANDIDATES.exists() else []
    merged = {f["url"]: f for f in (old or [])}
    merged.update({f["url"]: f for f in findings})
    CANDIDATES.write_text(
        "# Written by scripts/discover_conferences.py. Not rendered on the site.\n"
        + yaml.safe_dump(sorted(merged.values(), key=lambda f: (-f["confidence"], f["name"])), sort_keys=False, allow_unicode=True),
        encoding="utf-8")

    if a.review_only:
        return 0
    header, rows = conflib.load()
    by_key = {conflib.key(r["name"]): r for r in rows}
    added, updated = [], []
    for f in findings:
        if f["confidence"] < a.min_confidence or not f["name"] or not f["deadline"] or f["deadline"] < today.isoformat():
            continue
        k = conflib.key(f["name"])
        cur = by_key.get(k)
        if cur is None:
            row = {"name": f["name"], "url": f["url"], "deadline": f["deadline"], "date": f["date"], "source": "search"}
            rows.append(row)
            by_key[k] = row
            added.append(f["name"])
        elif not cur.get("pin") and cur.get("source") == "search":
            ch = []
            for fld in ("deadline", "date"):
                if f[fld] and f[fld] != cur[fld]:
                    ch.append(f"{fld} {cur[fld] or 'TBD'} -> {f[fld]}")
                    cur[fld] = f[fld]
            if ch:
                updated.append(f"{cur['name']}: " + ", ".join(ch))
    if added or updated:
        conflib.dump(header, rows)
    for n in added:
        print(f"added   {n}")
    for u in updated:
        print(f"updated {u}")
    if not added and not updated:
        print("No changes to the public list.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
