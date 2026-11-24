#!/usr/bin/env bash
# Run every repro with each given Python interpreter and print one line per
# script and interpreter. Usage: ./run_all.sh /path/to/python [/path/to/python ...]
set -u
cd "$(dirname "$0")"
for py in "$@"; do
  ver=$("$py" -c 'import jsonargparse; print(jsonargparse.__version__)')
  for f in J*.py; do
    res=$(PYTHONDONTWRITEBYTECODE=1 timeout 300 "$py" "$f" 2>&1 | grep '^RESULT:' | tail -1)
    printf '%-10s %-48s %s\n' "$ver" "$f" "${res:-RESULT: ERROR (no result line)}"
  done
done
