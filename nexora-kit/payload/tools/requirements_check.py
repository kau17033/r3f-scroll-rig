#!/usr/bin/env python3
"""Verify that requirements.csv is a lossless section-addressed normalization ledger."""
import csv
import glob
import os
import sys

ROOT = os.path.realpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
REQ = os.path.join(ROOT, "control", "requirements.csv")
PARTS = os.path.join(ROOT, "control", "corpus_sections", "*.csv")
EXPECTED = 1652
REQUIRED = (
    "req_id", "source_ref", "quote_ref", "normalized_requirement",
    "type", "scope", "verifiable", "notes",
)


def rows(path):
    with open(path, encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def load_sections():
    out = {}
    for path in sorted(glob.glob(PARTS)):
        for r in rows(path):
            sid = r["section_id"]
            if sid in out:
                raise ValueError("duplicate section_id=%s" % sid)
            out[sid] = r
    return out


def validate():
    errors = []
    reqs = rows(REQ)
    sections = load_sections()
    if len(reqs) != EXPECTED:
        errors.append("requirements count=%d expected=%d" % (len(reqs), EXPECTED))
    if len(sections) != EXPECTED:
        errors.append("sections count=%d expected=%d" % (len(sections), EXPECTED))

    seen_req = set()
    seen_src = set()
    for i, r in enumerate(reqs, 1):
        expected_id = "REQ-%05d" % i
        if r.get("req_id") != expected_id:
            errors.append("row %d req_id=%s expected=%s" % (i, r.get("req_id"), expected_id))
        rid = r.get("req_id") or ""
        if rid in seen_req:
            errors.append("duplicate req_id=%s" % rid)
        seen_req.add(rid)
        missing = [k for k in REQUIRED if not (r.get(k) or "").strip()]
        if missing:
            errors.append("%s missing=%s" % (rid, ",".join(missing)))
            continue

        sid = r["source_ref"]
        if sid in seen_src:
            errors.append("duplicate source_ref=%s" % sid)
        seen_src.add(sid)
        sec = sections.get(sid)
        if sec is None:
            errors.append("%s unknown source_ref=%s" % (rid, sid))
            continue
        if r["quote_ref"] != sec["section_sha256"]:
            errors.append("%s hash drift for %s" % (rid, sid))
        if sec["heading"] not in r["normalized_requirement"]:
            errors.append("%s normalization lost heading identity" % rid)

        if sec["source_id"] == "SRC-03":
            if r["type"] != "REFERENCE_ONLY" or r["verifiable"] != "NOT_EXECUTABLE":
                errors.append("%s SRC-03 authority inflation" % rid)
        elif r["verifiable"] != "TRACEABLE_BY_SECTION_HASH":
            errors.append("%s executable authority lacks traceable verification class" % rid)

    if seen_src != set(sections):
        errors.append("section coverage mismatch missing=%d extra=%d" %
                      (len(set(sections) - seen_src), len(seen_src - set(sections))))
    return errors


def main():
    errors = validate()
    if errors:
        print("REQUIREMENTS: FAIL")
        for e in errors[:40]:
            print("  - %s" % e)
        if len(errors) > 40:
            print("  ... %d more" % (len(errors) - 40))
        return 1
    print("REQUIREMENTS: PASS (rows=1652 coverage=1652/1652 PENDING=0)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
