#!/usr/bin/env python3
"""Deterministic reducer for the NEXORA cross-repository convergence state."""
import argparse
import csv
import json
import os
import re
import sys

ROOT = os.path.realpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

EVENT_STATES = {
    "VERIFIED", "RECOVERED", "CLOSED_NOT_DETERMINABLE", "PENDING_HUMAN",
    "NOT_EXECUTED", "FORMAL_ESTABLISHED", "PARTIAL_PASS", "FORMAL_ONLY",
    "AUTHORIZED", "PARTIAL", "BLOCKED_EVIDENCE", "BLOCKED", "SUPPORTING_ONLY",
    "PASS", "CLOSED", "FAIL", "HOLD", "UNKNOWN", "NOT_IDENTIFIABLE",
    "PENDING_CONFIRMATION", "VERIFIED_DRAFT",
}
SOURCE_STATES = {
    "VERIFIED_IMMUTABLE", "RECEIVED_UNHASHED", "CONTENT_HASH_FIXED",
    "VERIFIED_EXTERNAL_REFERENCE", "FORMAL_ESTABLISHED",
    "RECOVERED", "PARTIAL_PASS",
}


def read_csv(rel):
    path = os.path.join(ROOT, rel)
    with open(path, encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def unique(rows, key, rel):
    seen = set()
    for row in rows:
        value = (row.get(key) or "").strip()
        if not value:
            raise ValueError("%s: empty %s" % (rel, key))
        if value in seen:
            raise ValueError("%s: duplicate %s=%s" % (rel, key, value))
        seen.add(value)


def latest_events(events):
    latest = {}
    for row in events:
        if row["state"] not in EVENT_STATES:
            raise ValueError("invalid event state: %s" % row["state"])
        key = "%s:%s" % (row["scope"], row["subject"])
        rank = (row["observed_at"], row["event_id"])
        if key not in latest or rank > latest[key][0]:
            latest[key] = (rank, row)
    return latest


def build():
    sources = read_csv("control/source_registry.csv")
    events = read_csv("control/state_events.csv")
    gates = read_csv("control/completion_gates.csv")
    transitions = read_csv("control/transitions.csv")

    unique(sources, "source_id", "source_registry.csv")
    unique(events, "event_id", "state_events.csv")
    unique(gates, "gate_id", "completion_gates.csv")
    unique(transitions, "transition_id", "transitions.csv")

    for row in sources:
        state = row["status"]
        if state not in SOURCE_STATES:
            raise ValueError("invalid source state: %s" % state)
        immutable = (row.get("immutable_ref") or "").strip()
        if state == "VERIFIED_IMMUTABLE" and not re.fullmatch(r"[0-9a-f]{40}", immutable):
            raise ValueError("%s: VERIFIED_IMMUTABLE requires 40-hex immutable_ref" % row["source_id"])
        if state == "CONTENT_HASH_FIXED" and not re.fullmatch(r"sha256:[0-9a-f]{64}", immutable):
            raise ValueError("%s: CONTENT_HASH_FIXED requires sha256:<64-hex>" % row["source_id"])
        if state == "VERIFIED_EXTERNAL_REFERENCE" and not immutable:
            raise ValueError("%s: VERIFIED_EXTERNAL_REFERENCE requires immutable_ref" % row["source_id"])

    latest = latest_events(events)

    source_map = {}
    for row in sorted(sources, key=lambda r: r["source_id"]):
        source_map[row["source_id"]] = {
            "scope": row["scope"],
            "artifact": row["artifact"],
            "authority_class": row["authority_class"],
            "status": row["status"],
            "immutable_ref": row["immutable_ref"],
            "locator": row["locator"],
        }

    subjects = {}
    for key in sorted(latest):
        row = latest[key][1]
        if row["scope"] in ("GATE", "TRANSITION"):
            continue
        subjects[key] = {
            "state": row["state"],
            "observed_at": row["observed_at"],
            "evidence_class": row["evidence_class"],
            "evidence_ref": row["evidence_ref"],
        }

    expected_gates = ["C%d" % i for i in range(9)]
    actual_gates = [row["gate_id"] for row in gates]
    if actual_gates != expected_gates:
        raise ValueError("completion gates must be exactly C0..C8 in order: %r" % actual_gates)

    gate_map = {}
    for row in gates:
        event_key = "GATE:%s" % row["gate_id"]
        if event_key not in latest:
            raise ValueError("missing current event for %s" % event_key)
        ev = latest[event_key][1]
        gate_map[row["gate_id"]] = {
            "name": row["name"],
            "status": ev["state"],
            "predicate": row["predicate"],
            "evidence_ref": ev["evidence_ref"],
            "notes": ev["notes"],
        }

    expected_transitions = ["TR-%02d" % i for i in range(1, 5)]
    actual_transitions = [row["transition_id"] for row in transitions]
    if actual_transitions != expected_transitions:
        raise ValueError("transitions must be exactly TR-01..TR-04 in order: %r" % actual_transitions)

    transition_map = {}
    for row in transitions:
        event_key = "TRANSITION:%s" % row["transition_id"]
        if event_key not in latest:
            raise ValueError("missing current event for %s" % event_key)
        ev = latest[event_key][1]
        transition_map[row["transition_id"]] = {
            "from": row["from_layer"],
            "to": row["to_layer"],
            "status": ev["state"],
            "promotion_predicate": row["promotion_predicate"],
            "evidence_ref": ev["evidence_ref"],
            "notes": ev["notes"],
        }

    as_of = max(row["observed_at"] for row in events)
    return {
        "schema_version": "1.0",
        "as_of": as_of,
        "sources": source_map,
        "subjects": subjects,
        "completion_gates": gate_map,
        "transitions": transition_map,
    }


def main(argv=None):
    ap = argparse.ArgumentParser()
    mode = ap.add_mutually_exclusive_group()
    mode.add_argument("--check", action="store_true")
    mode.add_argument("--write", action="store_true")
    args = ap.parse_args(argv)

    actual = build()
    path = os.path.join(ROOT, "control", "STATE.generated.json")

    if args.write:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(actual, f, ensure_ascii=False, sort_keys=True, indent=2)
            f.write("\n")
        print("CONVERGENCE_STATE: WROTE %s" % path)
        return 0

    if args.check:
        with open(path, encoding="utf-8") as f:
            expected = json.load(f)
        if actual != expected:
            print("CONVERGENCE_STATE: FAIL (snapshot drift)")
            return 1
        print("CONVERGENCE_STATE: PASS (sources=%d subjects=%d gates=%d transitions=%d)" %
              (len(actual["sources"]), len(actual["subjects"]),
               len(actual["completion_gates"]), len(actual["transitions"])))
        return 0

    print(json.dumps(actual, ensure_ascii=False, sort_keys=True, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
