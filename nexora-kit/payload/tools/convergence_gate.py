#!/usr/bin/env python3
"""T-070 cross-repository convergence gate.

This gate answers only whether the canonical control plane is structurally converged.
It MUST NOT claim C2-C8 scientific/operational completion and MUST NOT satisfy HG-* gates.
"""
import json
import os
import subprocess
import sys

ROOT = os.path.realpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

CHECKS = [
    ("source_registry", "source_registry_check.py", []),
    ("disposition", "disposition_check.py", []),
    ("requirements", "requirements_check.py", []),
    ("conflicts", "conflict_check.py", []),
    ("traceability", "traceability_check.py", []),
    ("human_gate_registry", "human_gate_check.py", ["--validate"]),
    ("state_projection", "state_reduce.py", ["--check"]),
]


def run_tool(name, args):
    path = os.path.join(ROOT, "tools", name)
    r = subprocess.run([sys.executable, path] + args, capture_output=True, text=True)
    line = (r.stdout or r.stderr).strip().splitlines()
    return r.returncode == 0, (line[0] if line else "no output")


def final_host():
    path = os.path.join(ROOT, "control", "STATE.generated.json")
    with open(path, encoding="utf-8") as f:
        state = json.load(f)
    row = state.get("subjects", {}).get("NEXORA:FINAL_HOST")
    if not row:
        return False, "NEXORA:FINAL_HOST missing"
    ok = row.get("state") in ("VERIFIED", "PASS", "CLOSED")
    return ok, "state=%s evidence=%s" % (row.get("state"), row.get("evidence_ref"))


def main():
    ok_all = True
    print("NEXORA CONVERGENCE GATE")
    for label, tool, args in CHECKS:
        try:
            ok, detail = run_tool(tool, args)
        except Exception as e:
            ok, detail = False, "checker error: %r" % (e,)
        ok_all &= ok
        print("  [%s] %-22s %s" % ("PASS" if ok else "BLOCK", label, detail))

    ok, detail = final_host()
    ok_all &= ok
    print("  [%s] %-22s %s" % ("PASS" if ok else "BLOCK", "final_host", detail))

    print("SCIENTIFIC_HUMAN_GATES: OUT_OF_SCOPE (remain fail-closed per control/human_gates.csv)")
    print("RESULT: %s" % ("CONVERGED" if ok_all else "BLOCKED"))
    return 0 if ok_all else 1


if __name__ == "__main__":
    sys.exit(main())
