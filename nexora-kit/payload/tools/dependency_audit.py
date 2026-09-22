#!/usr/bin/env python3
"""Audit dependency references across NEXORA task/decision/human-gate ledgers."""
import csv
import os
import re
import sys

ROOT = os.path.realpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
TASKS = os.path.join(ROOT, "tasks", "INDEX.md")
DECISIONS = os.path.join(ROOT, "control", "decisions.md")
HUMAN = os.path.join(ROOT, "control", "human_gates.csv")
GATES = os.path.join(ROOT, "control", "completion_gates.csv")
TRANSITIONS = os.path.join(ROOT, "control", "transitions.csv")
TRACE = os.path.join(ROOT, "control", "traceability.csv")

ALIASES = {
    "T-1xx": "VEA-G3 experimental task family (T-110)",
    "T-2xx": "LoopCell experimental task family (T-200)",
    "T-3xx": "Outlier/public-release task family (T-300)",
    "VEA-confirmatory": "VEA confirmatory execution scope",
    "public-release": "public release scope",
}
TOKEN_RE = re.compile(r"\b(?:T-\d{3}|DEC-\d{3}|HG-[A-Z0-9-]+|C\d|TR-\d{2}|T-[123]xx)\b")


def table_ids(path, prefix):
    out = set()
    with open(path, encoding="utf-8") as f:
        for line in f:
            if line.startswith("| " + prefix):
                parts = [x.strip() for x in line.strip().strip("|").split("|")]
                if parts:
                    out.add(parts[0])
    return out


def csv_ids(path, field):
    with open(path, encoding="utf-8", newline="") as f:
        return {r[field] for r in csv.DictReader(f)}


def validate():
    tasks = table_ids(TASKS, "T-")
    decisions = table_ids(DECISIONS, "DEC-")
    humans = csv_ids(HUMAN, "gate_id")
    gates = csv_ids(GATES, "gate_id")
    transitions = csv_ids(TRANSITIONS, "transition_id")
    known = tasks | decisions | humans | gates | transitions | set(ALIASES)
    errors = []
    refs = set()

    # Task blocked_by cells.
    with open(TASKS, encoding="utf-8") as f:
        for line in f:
            if not line.startswith("| T-"):
                continue
            parts = [x.strip() for x in line.strip().strip("|").split("|")]
            if len(parts) < 5:
                continue
            owner = parts[0]
            for tok in TOKEN_RE.findall(parts[2]):
                refs.add(tok)
                if tok not in known:
                    errors.append("%s blocked_by unknown %s" % (owner, tok))

    # Human gate blocks.
    with open(HUMAN, encoding="utf-8", newline="") as f:
        for r in csv.DictReader(f):
            owner = r["gate_id"]
            for tok in TOKEN_RE.findall(r["blocks"]):
                refs.add(tok)
                if tok not in known:
                    errors.append("%s blocks unknown %s" % (owner, tok))

    # Requirement trace task IDs.
    with open(TRACE, encoding="utf-8", newline="") as f:
        for r in csv.DictReader(f):
            for tok in TOKEN_RE.findall(r.get("task_ids") or ""):
                refs.add(tok)
                if tok not in known:
                    errors.append("%s traces to unknown %s" % (r["req_id"], tok))

    return errors, refs, known


def main():
    errors, refs, known = validate()
    if errors:
        print("DEPENDENCIES: FAIL")
        for e in errors[:50]:
            print("  - " + e)
        return 1
    print("DEPENDENCIES: PASS (refs=%d known_nodes=%d dangling=0)" % (len(refs), len(known)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
