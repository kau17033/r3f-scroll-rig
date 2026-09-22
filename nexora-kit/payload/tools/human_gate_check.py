#!/usr/bin/env python3
"""Validate and enforce scoped NEXORA human gates."""
import argparse
import csv
import os
import sys

ROOT = os.path.realpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
CSV_PATH = os.path.join(ROOT, "control", "human_gates.csv")
ALLOWED = {"PENDING_HUMAN", "SATISFIED", "NOT_APPLICABLE"}
REQUIRED_FIELDS = {
    "gate_id", "scope", "type", "status", "blocks",
    "evidence_ref", "required_human_action", "notes",
}


def load_rows():
    with open(CSV_PATH, encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def validate(rows):
    errors = []
    seen = set()
    for i, row in enumerate(rows, 2):
        missing = sorted(k for k in REQUIRED_FIELDS if not (row.get(k) or "").strip())
        if missing:
            errors.append("line %d missing=%s" % (i, ",".join(missing)))
        gid = (row.get("gate_id") or "").strip()
        if gid in seen:
            errors.append("duplicate gate_id=%s" % gid)
        seen.add(gid)
        if not gid.startswith("HG-"):
            errors.append("invalid gate_id=%s" % gid)
        status = (row.get("status") or "").strip()
        if status not in ALLOWED:
            errors.append("%s invalid status=%s" % (gid, status))
    return errors


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--validate", action="store_true")
    ap.add_argument("--require", action="append", default=[])
    args = ap.parse_args(argv)

    rows = load_rows()
    errors = validate(rows)
    if errors:
        print("HUMAN_GATES: FAIL")
        for e in errors:
            print("  - %s" % e)
        return 1

    by_id = {r["gate_id"]: r for r in rows}
    if args.require:
        blocked = []
        for gid in args.require:
            row = by_id.get(gid)
            if row is None:
                blocked.append("%s:MISSING" % gid)
            elif row["status"] not in ("SATISFIED", "NOT_APPLICABLE"):
                blocked.append("%s:%s" % (gid, row["status"]))
        if blocked:
            print("HUMAN_GATES: BLOCKED " + " ".join(blocked))
            return 2
        print("HUMAN_GATES: PASS required=" + ",".join(args.require))
        return 0

    pending = [r["gate_id"] for r in rows if r["status"] == "PENDING_HUMAN"]
    print("HUMAN_GATES: VALID (total=%d pending_human=%d)" % (len(rows), len(pending)))
    if pending:
        print("PENDING_HUMAN: " + ",".join(pending))
    return 0


if __name__ == "__main__":
    sys.exit(main())
