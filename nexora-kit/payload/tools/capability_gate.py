#!/usr/bin/env python3
"""Deterministic NEXORA Capability promotion gate.

This gate does not create empirical evidence. It only prevents promotion until
the v1 capability contract carries explicit PASS/VALID evidence for every
required empirical dimension. Artifact/storage counts are never accepted as a
capability proxy.
"""
from __future__ import annotations
import argparse
import json
import math
import os
import sys

REQUIRED_TOP = {
    "capability_id","version","scope","policy_version","evidence_refs","baseline",
    "effect","retention","generalization","interference","cost","limitations",
    "validity","provenance",
}
ASSESSMENTS = ("retention","generalization","interference")
COST_FIELDS = ("production","selection","verification","transfer","application",
               "human","compute","recovery")


def _finite_number(x):
    return isinstance(x, (int,float)) and not isinstance(x,bool) and math.isfinite(float(x))


def evaluate(contract: dict) -> dict:
    blockers=[]
    unknown=set(contract)-REQUIRED_TOP
    missing=REQUIRED_TOP-set(contract)
    if missing:
        blockers.append({"code":"MISSING_TOP_LEVEL","fields":sorted(missing)})
    if unknown:
        blockers.append({"code":"UNKNOWN_TOP_LEVEL","fields":sorted(unknown)})
    if "artifact_count" in contract:
        blockers.append({"code":"ARTIFACT_COUNT_PROXY_FORBIDDEN"})

    if contract.get("version") != "1.0":
        blockers.append({"code":"VERSION","expected":"1.0","actual":contract.get("version")})

    refs=contract.get("evidence_refs")
    if not isinstance(refs,list) or not refs or not all(isinstance(x,str) and x for x in refs):
        blockers.append({"code":"EVIDENCE_REFS"})

    baseline=contract.get("baseline",{})
    if not _finite_number(baseline.get("value")):
        blockers.append({"code":"BASELINE_VALUE"})
    if not baseline.get("metric") or not baseline.get("evaluation_distribution"):
        blockers.append({"code":"BASELINE_IDENTITY"})

    effect=contract.get("effect",{})
    if effect.get("status") != "PASS":
        blockers.append({"code":"EFFECT_NOT_PASS","status":effect.get("status")})
    if not _finite_number(effect.get("estimate")):
        blockers.append({"code":"EFFECT_ESTIMATE"})
    if not _finite_number(effect.get("decision_threshold")):
        blockers.append({"code":"EFFECT_THRESHOLD"})

    for name in ASSESSMENTS:
        a=contract.get(name,{})
        if a.get("status") != "PASS":
            blockers.append({"code":f"{name.upper()}_NOT_PASS","status":a.get("status")})
        if not a.get("metric"):
            blockers.append({"code":f"{name.upper()}_METRIC"})
        if not _finite_number(a.get("value")):
            blockers.append({"code":f"{name.upper()}_VALUE"})

    cost=contract.get("cost",{})
    for field in COST_FIELDS:
        value=cost.get(field)
        if not _finite_number(value) or float(value) < 0:
            blockers.append({"code":"COST_FIELD","field":field,"value":value})
    if not isinstance(cost.get("unit"),str) or not cost.get("unit"):
        blockers.append({"code":"COST_UNIT"})

    validity=contract.get("validity",{})
    if validity.get("status") != "VALID":
        blockers.append({"code":"VALIDITY_NOT_VALID","status":validity.get("status")})
    if not isinstance(validity.get("evaluated_at"),str) or not validity.get("evaluated_at"):
        blockers.append({"code":"VALIDITY_TIME"})

    prov=contract.get("provenance",{})
    ids=prov.get("source_experience_ids")
    hashes=prov.get("lineage_hashes")
    if not isinstance(ids,list) or not ids or not all(isinstance(x,str) and x for x in ids):
        blockers.append({"code":"PROVENANCE_SOURCE_IDS"})
    if not isinstance(hashes,list) or not hashes or not all(
        isinstance(x,str) and len(x)>=32 for x in hashes
    ):
        blockers.append({"code":"PROVENANCE_LINEAGE"})

    return {
        "schema":"nexora-capability-promotion/1.0",
        "capability_id":contract.get("capability_id"),
        "status":"PROMOTABLE" if not blockers else "BLOCKED",
        "blockers":blockers,
        "no_teleportation":{
            "artifact_count_is_capability":False,
            "effect_only_is_capability":False,
            "formal_contract_is_empirical_capability":False,
        },
    }


def main(argv=None):
    ap=argparse.ArgumentParser()
    ap.add_argument("contract")
    args=ap.parse_args(argv)
    with open(args.contract,encoding="utf-8") as f:
        c=json.load(f)
    result=evaluate(c)
    print(json.dumps(result,ensure_ascii=False,sort_keys=True,indent=2))
    return 0 if result["status"]=="PROMOTABLE" else 1


if __name__=="__main__":
    sys.exit(main())
