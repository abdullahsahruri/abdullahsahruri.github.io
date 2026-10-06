#!/usr/bin/env python3
"""Add or update one conference in _data/conferences.yml.

  python scripts/add_conference.py --name "FCCM 2027" --url https://www.fccm.org/ \
      --deadline 2027-01-12 --date 2027-05-03 [--note "abstract 2027-01-05"] [--pin]

An existing entry with the same name is updated in place. --pin marks the
entry so the automatic updater never overwrites its dates.
"""
import argparse
import sys

import conflib


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--name", required=True)
    ap.add_argument("--url", default="")
    ap.add_argument("--deadline", default="", help="YYYY-MM-DD, or empty for TBD")
    ap.add_argument("--date", default="", help="YYYY-MM-DD, or empty for TBD")
    ap.add_argument("--note", default="")
    ap.add_argument("--pin", action="store_true")
    a = ap.parse_args()
    for f in ("deadline", "date"):
        v = getattr(a, f).strip()
        if v and not conflib.valid_date(v):
            sys.exit(f"--{f} must be YYYY-MM-DD, got {v!r}")
    header, rows = conflib.load()
    k = conflib.key(a.name)
    cur = next((r for r in rows if conflib.key(r["name"]) == k), None)
    if cur is None:
        cur = {"name": a.name.strip(), "url": "", "deadline": "", "date": "", "source": "manual"}
        rows.append(cur)
        print(f"added {cur['name']}")
    else:
        print(f"updated {cur['name']}")
    for f in ("url", "deadline", "date", "note"):
        v = getattr(a, f).strip()
        if v:
            cur[f] = v
    if a.pin:
        cur["pin"] = True
    conflib.dump(header, rows)
    return 0


if __name__ == "__main__":
    sys.exit(main())
