#!/usr/bin/env python3
"""Fail-closed preregistration validator for NEXORA Capability evaluation.

This validator locks measurement semantics before empirical outcomes are read.
It is independent of frozen VEA-G3 and LoopCell Phase 0 protocols.
"""
from __future__ import annotations
import argparse, hashlib, json, math, sys

REQUIRED = (
    "schema","plan_id","status","frozen_at","capability_candidate_id",
    "baseline_policy","candidate_policy","primary_scope","effect","repeat",
    "retention","generalization","interference","cost","missing_data_rule",
    "stopping_rule","claim_ceiling","plan_sha256",
)
BAD_STRINGS={"","TBD","PENDING","UNKNOWN","TO_BE_DECIDED","PLACEHOLDER"}
DIRECTIONS={"HIGHER_IS_BETTER","LOWER_IS_BETTER","NONINFERIORITY"}


def canonical_without_hash(plan: dict) -> bytes:
    core={k:v for k,v in plan.items() if k!="plan_sha256"}
    return json.dumps(core,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode("utf-8")


def expected_hash(plan: dict) -> str:
    return hashlib.sha256(canonical_without_hash(plan)).hexdigest()


def _finite(v):
    return isinstance(v,(int,float)) and not isinstance(v,bool) and math.isfinite(float(v))


def _text(v):
    return isinstance(v,str) and v.strip().upper() not in BAD_STRINGS


def validate(plan: dict) -> list[dict]:
    errors=[]
    for key in REQUIRED:
        if key not in plan:
            errors.append({"code":"MISSING","field":key})
    if errors:
        return errors
    if plan["schema"]!="nexora-capability-evaluation-plan/1.0":
        errors.append({"code":"SCHEMA"})
    if plan["status"]!="FROZEN":
        errors.append({"code":"NOT_FROZEN"})
    for key in ("plan_id","frozen_at","capability_candidate_id","baseline_policy",
                "candidate_policy","primary_scope","missing_data_rule","stopping_rule",
                "claim_ceiling"):
        if not _text(plan.get(key)):
            errors.append({"code":"TEXT","field":key})
    if plan.get("baseline_policy")==plan.get("candidate_policy"):
        errors.append({"code":"POLICY_IDENTITY"})

    e=plan.get("effect",{})
    for key in ("metric","evaluation_distribution","estimator"):
        if not _text(e.get(key)):
            errors.append({"code":"EFFECT_FIELD","field":key})
    if e.get("direction") not in DIRECTIONS:
        errors.append({"code":"EFFECT_DIRECTION"})
    if not _finite(e.get("decision_threshold")):
        errors.append({"code":"EFFECT_THRESHOLD"})

    rep=plan.get("repeat",{})
    if not isinstance(rep.get("independent_runs"),int) or rep["independent_runs"]<2:
        errors.append({"code":"REPEAT_RUNS","minimum":2})
    if not isinstance(rep.get("units_per_run"),int) or rep["units_per_run"]<1:
        errors.append({"code":"REPEAT_UNITS"})
    if not _text(rep.get("independence_unit")):
        errors.append({"code":"REPEAT_INDEPENDENCE_UNIT"})

    ret=plan.get("retention",{})
    for key in ("metric","evaluation_distribution","lag_unit"):
        if not _text(ret.get(key)):
            errors.append({"code":"RETENTION_FIELD","field":key})
    if not _finite(ret.get("lag")) or float(ret["lag"])<=0:
        errors.append({"code":"RETENTION_LAG"})
    if ret.get("direction") not in DIRECTIONS or not _finite(ret.get("decision_threshold")):
        errors.append({"code":"RETENTION_DECISION"})

    gen=plan.get("generalization",{})
    for key in ("metric","heldout_distribution"):
        if not _text(gen.get(key)):
            errors.append({"code":"GENERALIZATION_FIELD","field":key})
    if gen.get("heldout_distribution")==e.get("evaluation_distribution"):
        errors.append({"code":"GENERALIZATION_NOT_HELDOUT"})
    if gen.get("direction") not in DIRECTIONS or not _finite(gen.get("decision_threshold")):
        errors.append({"code":"GENERALIZATION_DECISION"})

    inter=plan.get("interference",{})
    for key in ("metric","protected_distribution"):
        if not _text(inter.get(key)):
            errors.append({"code":"INTERFERENCE_FIELD","field":key})
    if inter.get("direction")!="NONINFERIORITY":
        errors.append({"code":"INTERFERENCE_DIRECTION"})
    if not _finite(inter.get("noninferiority_margin")):
        errors.append({"code":"INTERFERENCE_MARGIN"})

    cost=plan.get("cost",{})
    if not _text(cost.get("unit")):
        errors.append({"code":"COST_UNIT"})
    if not _finite(cost.get("budget_ceiling")) or float(cost["budget_ceiling"])<0:
        errors.append({"code":"COST_BUDGET"})
    cats=cost.get("required_categories")
    expected={"production","selection","verification","transfer","application","human","compute","recovery"}
    if not isinstance(cats,list) or set(cats)!=expected:
        errors.append({"code":"COST_CATEGORIES","expected":sorted(expected)})

    if plan.get("plan_sha256") != expected_hash(plan):
        errors.append({"code":"PLAN_HASH","expected":expected_hash(plan)})
    return errors


def main(argv=None):
    ap=argparse.ArgumentParser()
    ap.add_argument("plan")
    a=ap.parse_args(argv)
    with open(a.plan,encoding="utf-8") as f:
        p=json.load(f)
    errors=validate(p)
    print(json.dumps({"status":"PASS" if not errors else "BLOCKED","errors":errors},
                     ensure_ascii=False,sort_keys=True,indent=2))
    return 0 if not errors else 1


if __name__=="__main__":
    sys.exit(main())
