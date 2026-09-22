#!/usr/bin/env python3
"""Validate the additive VEA compliance-manifest reconciliation."""
import json
import os
import sys

ROOT = os.path.realpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
PATH = os.path.join(ROOT, "control", "VEA-COMPLIANCE-RECONCILIATION-20260922.json")
EXPECTED_STALE = [7, 8, 9, 18, 31, 39, 42]


def validate():
    errors = []
    with open(PATH, encoding="utf-8") as f:
        d = json.load(f)
    ms = d.get("manifest_structure") or {}
    if ms.get("numbered_rows") != 42:
        errors.append("manifest numbered_rows != 42")
    if ms.get("addendum_rows") != 3:
        errors.append("manifest addendum_rows != 3")
    stale = [x.get("row") for x in d.get("proven_stale_rows", [])]
    if stale != EXPECTED_STALE:
        errors.append("stale rows drift: %r" % stale)
    if len(d.get("protocol_lock_internal_stale_prose", [])) != 2:
        errors.append("internal stale-prose audit != 2")
    ts = d.get("current_truth_state") or {}
    if ts.get("truth_state") != "NOT_DETERMINABLE":
        errors.append("truth_state drift")
    if ts.get("scientific_promotion") != "NONE":
        errors.append("scientific_promotion drift")
    if ts.get("g4_state") != "BLOCKED" or ts.get("g4_closure") is not None:
        errors.append("G4 must remain BLOCKED with closure=null")
    if "does not establish VEA efficacy" not in (d.get("claim_ceiling") or ""):
        errors.append("claim ceiling missing")
    refs = d.get("authority_boundary") or {}
    frozen = {x.get("blob_sha") for x in refs.get("frozen_experiment_sources", [])}
    if "e535476b4f981f3ca1f8dff9efb92253797c0a39" not in frozen:
        errors.append("PROTOCOL_LOCK immutable ref missing")
    return errors


def main():
    errors = validate()
    if errors:
        print("VEA_COMPLIANCE: FAIL")
        for e in errors:
            print("  - %s" % e)
        return 1
    print("VEA_COMPLIANCE: PASS (42 rows reconciled; stale=7; G4=BLOCKED/closure-null)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
