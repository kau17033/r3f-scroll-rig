#!/usr/bin/env python3
"""Validate NEXORA source registry and the latest frozen external-source observation."""
import csv
import json
import os
import re
import sys

ROOT = os.path.realpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
REGISTRY = os.path.join(ROOT, "control", "source_registry.csv")
EXTERNAL_REPORT = os.path.join(ROOT, "control", "EXTERNAL-VALIDATION-20260922-35.json")
EXTERNAL_REGISTRY = os.path.join(ROOT, "sources", "EXTERNAL.csv")

REQUIRED_LOCAL_FIXED = {"SRC-01", "SRC-03", "SRC-05", "SRC-06", "SRC-07", "SRC-14"}
REQUIRED_WORK_FIXED = {"SRC-08", "SRC-09", "SRC-10", "SRC-11", "SRC-12", "SRC-13", "SRC-16", "SRC-17", "SRC-18"}
REQUIRED_GIT_IMMUTABLE = {"SRC-02A", "SRC-02B", "SRC-02C", "SRC-04A", "SRC-04B"}


def load_registry(path=REGISTRY):
    with open(path, encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def validate_registry(rows):
    errors = []
    by_id = {}
    for row in rows:
        sid = (row.get("source_id") or "").strip()
        if not sid:
            errors.append("empty source_id")
            continue
        if sid in by_id:
            errors.append("duplicate source_id=%s" % sid)
        by_id[sid] = row

    for sid in sorted(REQUIRED_LOCAL_FIXED):
        row = by_id.get(sid)
        if not row:
            errors.append("%s missing" % sid)
            continue
        if row.get("status") != "CONTENT_HASH_FIXED":
            errors.append("%s status=%s" % (sid, row.get("status")))
        if not re.fullmatch(r"sha256:[0-9a-f]{64}", row.get("immutable_ref") or ""):
            errors.append("%s invalid sha256 ref" % sid)

    for sid in sorted(REQUIRED_WORK_FIXED):
        row = by_id.get(sid)
        if not row:
            errors.append("%s missing" % sid)
            continue
        if row.get("status") != "CONTENT_HASH_FIXED":
            errors.append("%s status=%s" % (sid, row.get("status")))
        if not re.fullmatch(r"sha256:[0-9a-f]{64}", row.get("immutable_ref") or ""):
            errors.append("%s invalid sha256 ref" % sid)

    for sid in sorted(REQUIRED_GIT_IMMUTABLE):
        row = by_id.get(sid)
        if not row:
            errors.append("%s missing" % sid)
            continue
        if row.get("status") != "VERIFIED_IMMUTABLE":
            errors.append("%s status=%s" % (sid, row.get("status")))
        if not re.fullmatch(r"[0-9a-f]{40}", row.get("immutable_ref") or ""):
            errors.append("%s invalid git blob ref" % sid)

    local_dream = by_id.get("SRC-14")
    public_dream = by_id.get("SRC-15")
    if not public_dream or public_dream.get("immutable_ref") != "arxiv:2609.14858":
        errors.append("SRC-15 Dream-RSI arXiv identity missing")
    if local_dream and public_dream and local_dream.get("authority_class") == "FROZEN_EXPERIMENTAL_SSOT":
        errors.append("Dream-RSI must not become experimental SSOT authority")

    return errors


def validate_external_report(report, expected_rows=None):
    errors = []
    if report.get("total") != 35:
        errors.append("external total != 35")
    if report.get("match") != 35:
        errors.append("external match != 35")
    if report.get("mismatch") != 0:
        errors.append("external mismatch != 0")
    if report.get("missing") != 0:
        errors.append("external missing != 0")
    entries = report.get("entries") or []
    if len(entries) != 35:
        errors.append("external entries != 35")
    if any(e.get("status") != "MATCH" for e in entries):
        errors.append("non-MATCH external entry exists")
    if expected_rows is not None:
        expected = {(r["repo"], r["path"]): r["blob_sha"] for r in expected_rows}
        observed = {(e.get("repo"), e.get("path")): e for e in entries}
        if set(expected) != set(observed):
            errors.append("external registry/report identity mismatch")
        for key, sha in expected.items():
            e = observed.get(key)
            if not e:
                continue
            if e.get("expected_blob_sha") != sha or e.get("actual_blob_sha") != sha:
                errors.append("external blob mismatch in report: %s:%s" % key)
    return errors


def main():
    rows = load_registry()
    with open(EXTERNAL_REPORT, encoding="utf-8") as f:
        report = json.load(f)
    with open(EXTERNAL_REGISTRY, encoding="utf-8", newline="") as f:
        external_rows = list(csv.DictReader(f))
    errors = validate_registry(rows) + validate_external_report(report, external_rows)
    if errors:
        print("SOURCE_REGISTRY: FAIL")
        for e in errors:
            print("  - %s" % e)
        return 1
    print("SOURCE_REGISTRY: PASS (registry=%d hash_fixed=%d external=35/35)"
          % (len(rows), len(REQUIRED_LOCAL_FIXED | REQUIRED_WORK_FIXED)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
