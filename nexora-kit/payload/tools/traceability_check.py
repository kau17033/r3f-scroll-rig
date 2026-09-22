#!/usr/bin/env python3
"""Verify complete requirement -> task/test/evidence trace coverage."""
import csv
import os
import sys

ROOT = os.path.realpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
REQ = os.path.join(ROOT, "control", "requirements.csv")
TRACE = os.path.join(ROOT, "control", "traceability.csv")
EXPECTED = 1652
ALLOWED = {
    "TRACE_BOUND_NOT_CLAIMED_SATISFIED",
    "FROZEN_REQUIREMENT_TRACE_BOUND",
    "REFERENCE_ONLY",
    "FROZEN_REQUIREMENT_TRACE_BOUND_NOT_EXECUTED",
}


def load(path):
    with open(path, encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def validate():
    errors = []
    reqs = load(REQ)
    traces = load(TRACE)
    if len(reqs) != EXPECTED:
        errors.append("requirements=%d expected=%d" % (len(reqs), EXPECTED))
    if len(traces) != EXPECTED:
        errors.append("traceability=%d expected=%d" % (len(traces), EXPECTED))

    req_by_id = {r["req_id"]: r for r in reqs}
    if len(req_by_id) != len(reqs):
        errors.append("duplicate requirement ids")

    seen = set()
    for tr in traces:
        rid = tr.get("req_id") or ""
        if rid in seen:
            errors.append("duplicate trace req_id=%s" % rid)
        seen.add(rid)
        req = req_by_id.get(rid)
        if req is None:
            errors.append("unknown trace req_id=%s" % rid)
            continue
        for key in ("source_ref", "requirement", "task_ids", "test_ids", "evidence_paths", "status"):
            if not (tr.get(key) or "").strip():
                errors.append("%s missing %s" % (rid, key))
        if tr.get("source_ref") != req.get("source_ref"):
            errors.append("%s source_ref drift" % rid)
        if tr.get("requirement") != req.get("normalized_requirement"):
            errors.append("%s requirement text drift" % rid)
        if tr.get("status") not in ALLOWED:
            errors.append("%s invalid status=%s" % (rid, tr.get("status")))
        if tr.get("status") == "SATISFIED":
            errors.append("%s improperly claims satisfaction" % rid)

    missing = set(req_by_id) - seen
    if missing:
        errors.append("missing traces=%d" % len(missing))
    return errors


def main():
    errors = validate()
    if errors:
        print("TRACEABILITY: FAIL")
        for e in errors[:40]:
            print("  - %s" % e)
        if len(errors) > 40:
            print("  ... %d more" % (len(errors) - 40))
        return 1
    print("TRACEABILITY: PASS (requirements=1652 traced=1652 satisfaction_not_implied=true)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
