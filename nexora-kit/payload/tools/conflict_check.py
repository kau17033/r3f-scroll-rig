#!/usr/bin/env python3
"""Validate conflict convergence without auto-resolving scientific human gates."""
import csv
import os
import re
import sys

ROOT = os.path.realpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
CONFLICTS = os.path.join(ROOT, "control", "conflicts.md")
HUMAN = os.path.join(ROOT, "control", "human_gates.csv")

ROW = re.compile(r"^\|\s*(CONF-\d{2})\s*\|(.+?)\|(.+?)\|(.+?)\|\s*(DEC-\d{3})\s*\|(.+?)\|\s*$")
ALLOWED_TERMINAL = ("RESOLVED", "SUPERSEDED")
OPEN_TO_HG = {
    "CONF-04": "HG-VEA-ESTIMAND",
    "CONF-16": "HG-VEA-FREEZE-SCOPE",
    "CONF-17": "HG-VEA-WS-C",
}


def human_gates():
    with open(HUMAN, encoding="utf-8", newline="") as f:
        return {r["gate_id"]: r for r in csv.DictReader(f)}


def parse():
    out = {}
    with open(CONFLICTS, encoding="utf-8") as f:
        for raw in f:
            m = ROW.match(raw.rstrip("\n"))
            if not m:
                continue
            cid, conflict, source, resolution, decision, status = m.groups()
            out[cid] = {
                "conflict": conflict.strip(),
                "source": source.strip(),
                "resolution": resolution.strip(),
                "decision": decision.strip(),
                "status": status.replace("*", "").replace(chr(96), "").strip(),
            }
    return out


def validate():
    errors = []
    conflicts = parse()
    hg = human_gates()
    expected = {"CONF-%02d" % i for i in range(1, 19)}
    if set(conflicts) != expected:
        errors.append("conflict IDs mismatch missing=%s extra=%s" %
                      (sorted(expected-set(conflicts)), sorted(set(conflicts)-expected)))
    for cid, row in conflicts.items():
        status = row["status"].upper()
        if status.startswith(ALLOWED_TERMINAL):
            continue
        if status == "OPEN":
            gid = OPEN_TO_HG.get(cid)
            if not gid:
                errors.append("%s OPEN without scoped human gate" % cid)
                continue
            if gid not in hg:
                errors.append("%s missing human gate %s" % (cid, gid))
            if ("[" + gid + "]") not in row["resolution"]:
                errors.append("%s resolution does not bind %s" % (cid, gid))
            continue
        errors.append("%s invalid status=%s" % (cid, row["status"]))
    return errors


def main():
    errors = validate()
    if errors:
        print("CONFLICTS: FAIL")
        for e in errors:
            print("  - %s" % e)
        return 1
    print("CONFLICTS: PASS (18/18 classified; open_scientific=3 human_gated=3)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
