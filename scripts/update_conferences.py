#!/usr/bin/env python3
"""Pull the Chalmers VLSI conference table and merge it into _data/conferences.yml.

Rules:
  * a conference not yet in the file is added (source: chalmers);
  * an existing conference gets its deadline/date refreshed when Chalmers
    shows a different value, unless the entry carries `pin: true`;
  * nothing is ever deleted, and `note`/`url` edits made by hand are kept
    (the url is only filled in when the entry has none).
Prints a change report; exits 0 whether or not anything changed.
"""
import sys
import urllib.request
from html.parser import HTMLParser

import conflib

SOURCE = "https://www.cse.chalmers.se/research/group/vlsi/conference/"


class TableParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.rows, self.row, self.cell, self.href, self.in_cell = [], None, None, None, False

    def handle_starttag(self, tag, attrs):
        if tag == "tr":
            self.row = []
        elif tag in ("td", "th") and self.row is not None:
            self.cell, self.href, self.in_cell = [], None, True
        elif tag == "a" and self.in_cell:
            self.href = dict(attrs).get("href") or self.href

    def handle_data(self, data):
        if self.in_cell:
            self.cell.append(data)

    def handle_endtag(self, tag):
        if tag in ("td", "th") and self.in_cell:
            self.row.append((" ".join("".join(self.cell).split()), self.href))
            self.in_cell = False
        elif tag == "tr" and self.row is not None:
            if len(self.row) >= 4:
                self.rows.append(self.row)
            self.row = None


def fetch_rows():
    req = urllib.request.Request(SOURCE, headers={"User-Agent": "conference-list-updater (github pages)"})
    with urllib.request.urlopen(req, timeout=60) as resp:
        html = resp.read().decode("utf-8", "replace")
    p = TableParser()
    p.feed(html)
    out = []
    for cells in p.rows:
        name = cells[0][0]
        url = cells[1][1] or cells[1][0].strip("<> ")
        dl = conflib.DATE_RE.search(cells[2][0])
        cd = conflib.DATE_RE.search(cells[3][0])
        if not name or not dl or name.lower() == "conference":
            continue
        out.append({"name": name, "url": url, "deadline": dl.group(1), "date": cd.group(1) if cd else ""})
    return out


def main():
    remote = fetch_rows()
    if len(remote) < 10:
        print(f"Only {len(remote)} rows parsed from {SOURCE}; page layout may have changed. No changes made.")
        return 0
    header, rows = conflib.load()
    by_key = {conflib.key(r["name"]): r for r in rows}
    added, updated = [], []
    for rr in remote:
        k = conflib.key(rr["name"])
        cur = by_key.get(k)
        if cur is None:
            rr["source"] = "chalmers"
            rows.append(rr)
            by_key[k] = rr
            added.append(rr["name"])
            continue
        if cur.get("pin"):
            continue
        changes = []
        for f in ("deadline", "date"):
            if rr[f] and rr[f] != cur[f]:
                changes.append(f"{f} {cur[f] or 'TBD'} -> {rr[f]}")
                cur[f] = rr[f]
        if not cur["url"] and rr["url"]:
            cur["url"] = rr["url"]
            changes.append("url filled")
        if changes:
            updated.append(f"{cur['name']}: " + ", ".join(changes))
    if not added and not updated:
        print("No changes.")
        return 0
    conflib.dump(header, rows)
    for n in added:
        print(f"added   {n}")
    for u in updated:
        print(f"updated {u}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
