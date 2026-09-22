#!/usr/bin/env python3
"""Section-70 claim classification audit over the canonical generated state."""
import json
import os
import sys

ROOT = os.path.realpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
STATE = os.path.join(ROOT, "control", "STATE.generated.json")

ALLOWED = {
    "VERIFIED", "RECOVERED", "CLOSED_NOT_DETERMINABLE", "PENDING_HUMAN",
    "NOT_EXECUTED", "FORMAL_ESTABLISHED", "PARTIAL_PASS", "FORMAL_ONLY",
    "AUTHORIZED", "PARTIAL", "BLOCKED_EVIDENCE", "BLOCKED", "SUPPORTING_ONLY",
    "PASS", "CLOSED", "FAIL", "HOLD", "UNKNOWN", "NOT_IDENTIFIABLE",
}


def main():
    with open(STATE, encoding="utf-8") as f:
        s = json.load(f)
    errors = []
    n = 0
    for namespace in ("subjects", "completion_gates", "transitions"):
        for key, row in (s.get(namespace) or {}).items():
            n += 1
            status = row.get("state", row.get("status"))
            if status not in ALLOWED:
                errors.append("%s:%s unclassified status=%r" % (namespace, key, status))
            if not (row.get("evidence_ref") or "").strip():
                errors.append("%s:%s missing evidence_ref" % (namespace, key))
    if n == 0:
        errors.append("no classified state claims")
    if errors:
        print("CLAIMS: FAIL")
        for e in errors:
            print("  - " + e)
        return 1
    print("CLAIMS: PASS (classified=%d unclassified=0; UNKNOWN remains an explicit class)" % n)
    return 0


if __name__ == "__main__":
    sys.exit(main())
