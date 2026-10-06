#!/usr/bin/env bash
# Run after editing _data/conferences.csv: commits the change and pushes it.
cd "$(dirname "$0")"
git add _data/conferences.csv
git commit -m "Update conference list" || echo "Nothing changed."
git push
