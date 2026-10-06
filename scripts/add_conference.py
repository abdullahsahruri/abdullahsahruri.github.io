#!/usr/bin/env python3
"""Add, update or remove one conference in _data/conferences.yml.

  python scripts/add_conference.py --name "FCCM 2027" --url https://www.fccm.org/ --deadline 2027-01-12 --date 2027-05-03
  python scripts/add_conference.py --name "FCCM 2027" --remove

An existing entry with the same name is updated in place; only the fields you pass change.
"""
import argparse
import sys

import conflib


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--name", required=True, help="conference name with year, e.g. FCCM 2027")
    ap.add_argument("--url", default="")
    ap.add_argument("--deadline", default="", help="YYYY-MM-DD; leave empty for TBD")
    ap.add_argument("--date", default="", help="YYYY-MM-DD; leave empty for TBD")
    ap.add_argument("--note", default="", help="short note, e.g. 'abstract 2027-01-05'")
    ap.add_argument("--remove", action="store_true", help="delete the entry instead")
    a = ap.parse_args()
    for f in ("deadline", "date"):
        v = getattr(a, f).strip()
        if v and not conflib.valid_date(v):
            sys.exit(f"--{f} must be YYYY-MM-DD, got {v!r}")

    header, rows = conflib.load()
    k = conflib.key(a.name)
    cur = next((r for r in rows if conflib.key(r["name"]) == k), None)

    if a.remove:
        if cur is None:
            sys.exit(f"not found: {a.name}")
        rows.remove(cur)
        print(f"removed {cur['name']}")
    else:
        if cur is None:
            cur = {"name": a.name.strip(), "url": "", "deadline": "", "date": "", "note": ""}
            rows.append(cur)
            print(f"added {cur['name']}")
        else:
            print(f"updated {cur['name']}")
        for f in ("url", "deadline", "date", "note"):
            v = getattr(a, f).strip()
            if v:
                cur[f] = v
        if a.deadline and not a.note and "not posted" in cur["note"].lower():
            cur["note"] = ""  # the placeholder note is obsolete once a real deadline is known
    conflib.dump(header, rows)
    return 0


if __name__ == "__main__":
    sys.exit(main())
