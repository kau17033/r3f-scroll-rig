#!/usr/bin/env python3
"""Section-70 audit: every registered critical failure mode must have a handler."""
import csv
import os
import sys

ROOT = os.path.realpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
PATH = os.path.join(ROOT, "control", "failure_modes.csv")
ALLOWED = {"CONTROLLED", "BLOCKED_BY_CONTROL", "BLOCKED_EVIDENCE"}


def main():
    with open(PATH, encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))
    errors = []
    seen = set()
    for r in rows:
        fid = r.get("failure_id") or ""
        if not fid or fid in seen:
            errors.append("duplicate/empty failure_id=%r" % fid)
        seen.add(fid)
        for key in ("critical_failure_mode", "control", "status", "evidence"):
            if not (r.get(key) or "").strip():
                errors.append("%s missing %s" % (fid, key))
        if r.get("status") not in ALLOWED:
            errors.append("%s unhandled status=%s" % (fid, r.get("status")))
    if len(rows) < 15:
        errors.append("critical failure registry unexpectedly small=%d" % len(rows))
    if errors:
        print("FAILURE_MODES: FAIL")
        for e in errors:
            print("  - " + e)
        return 1
    print("FAILURE_MODES: PASS (registered=%d unhandled=0)" % len(rows))
    return 0


if __name__ == "__main__":
    sys.exit(main())
