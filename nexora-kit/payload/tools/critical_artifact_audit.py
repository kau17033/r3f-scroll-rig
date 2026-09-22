#!/usr/bin/env python3
"""Section-70 critical artifact integrity-protection audit."""
import csv
import os
import sys

ROOT = os.path.realpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
PATH = os.path.join(ROOT, "control", "critical_artifacts.csv")


def main():
    with open(PATH, encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))
    errors = []
    seen = set()
    for r in rows:
        aid = r.get("artifact_id") or ""
        if not aid or aid in seen:
            errors.append("duplicate/empty artifact_id=%r" % aid)
        seen.add(aid)
        for key in ("critical_artifact", "protection", "verification", "evidence"):
            if not (r.get(key) or "").strip():
                errors.append("%s missing %s" % (aid, key))
        ev = r.get("evidence") or ""
        if ev.startswith(("control/", "tests/", "tools/")):
            if not os.path.exists(os.path.join(ROOT, ev)):
                errors.append("%s evidence path missing: %s" % (aid, ev))
    if len(rows) < 12:
        errors.append("critical artifact registry unexpectedly small=%d" % len(rows))
    if errors:
        print("CRITICAL_ARTIFACTS: FAIL")
        for e in errors:
            print("  - " + e)
        return 1
    print("CRITICAL_ARTIFACTS: PASS (registered=%d unprotected=0)" % len(rows))
    return 0


if __name__ == "__main__":
    sys.exit(main())
