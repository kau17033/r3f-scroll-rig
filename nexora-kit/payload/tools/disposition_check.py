#!/usr/bin/env python3
"""Validate section-level corpus disposition without copying canonical source bodies."""
import csv
import glob
import os
import re
import sys

ROOT = os.path.realpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
PART_DIR = os.path.join(ROOT, "control", "corpus_sections")
REGISTRY = os.path.join(ROOT, "control", "source_registry.csv")

EXPECTED = {
    "SRC-01": 1395,
    "SRC-02A": 55,
    "SRC-02B": 67,
    "SRC-03": 63,
    "SRC-04A": 71,
    "SRC-04B": 1,
}
ALLOWED = {"KEEP_GOVERNANCE", "SCOPE_AUTHORITY", "REFERENCE_ONLY",
           "CONFLICT_RECORDED", "DEFER_HUMAN", "SUPERSEDED", "NOT_APPLICABLE"}


def read_registry():
    with open(REGISTRY, encoding="utf-8", newline="") as f:
        return {r["source_id"]: r for r in csv.DictReader(f)}


def validate():
    errors = []
    registry = read_registry()
    files = sorted(glob.glob(os.path.join(PART_DIR, "*.csv")))
    if not files:
        return ["no corpus section shards"]

    seen = set()
    counts = {}
    for path in files:
        with open(path, encoding="utf-8", newline="") as f:
            rows = list(csv.DictReader(f))
        if not rows:
            errors.append("%s empty" % os.path.basename(path))
            continue
        for row in rows:
            sid = row.get("source_id") or ""
            sec = row.get("section_id") or ""
            disp = (row.get("disposition") or "").strip().upper()
            fp = row.get("section_sha256") or ""
            if sec in seen:
                errors.append("duplicate section_id=%s" % sec)
            seen.add(sec)
            counts[sid] = counts.get(sid, 0) + 1
            if disp == "PENDING" or not disp:
                errors.append("%s unresolved disposition" % sec)
            elif disp not in ALLOWED:
                errors.append("%s invalid disposition=%s" % (sec, disp))
            if sid in ("SRC-01", "SRC-03"):
                if not re.fullmatch(r"[0-9a-f]{64}", fp):
                    errors.append("%s invalid section sha256" % sec)
            else:
                source_ref = (registry.get(sid) or {}).get("immutable_ref") or ""
                if fp != "source_blob:" + source_ref:
                    errors.append("%s not bound to source blob" % sec)

    if counts != EXPECTED:
        errors.append("section counts mismatch got=%r expected=%r" % (counts, EXPECTED))
    return errors


def main():
    errors = validate()
    if errors:
        print("DISPOSITION: FAIL")
        for e in errors[:30]:
            print("  - %s" % e)
        if len(errors) > 30:
            print("  ... %d more" % (len(errors) - 30))
        return 1
    print("DISPOSITION: PASS (sources=%d sections=%d PENDING=0)" %
          (len(EXPECTED), sum(EXPECTED.values())))
    return 0


if __name__ == "__main__":
    sys.exit(main())
