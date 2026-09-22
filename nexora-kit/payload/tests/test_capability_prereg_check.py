import unittest

from _common import ROOT  # noqa: F401
from capability_prereg_check import validate, expected_hash


def plan():
    p={
      "schema":"nexora-capability-evaluation-plan/1.0",
      "plan_id":"C5-test-v1",
      "status":"FROZEN",
      "frozen_at":"2026-09-23T00:00:00Z",
      "capability_candidate_id":"cap.test",
      "baseline_policy":"baseline-v1",
      "candidate_policy":"candidate-v1",
      "primary_scope":"coding.patch",
      "effect":{"metric":"success_rate_delta","evaluation_distribution":"D_primary",
                "estimator":"paired_difference","direction":"HIGHER_IS_BETTER",
                "decision_threshold":0.05},
      "repeat":{"independent_runs":2,"units_per_run":100,"independence_unit":"task_instance"},
      "retention":{"metric":"retained_delta","evaluation_distribution":"D_retention",
                   "lag":7,"lag_unit":"days","direction":"HIGHER_IS_BETTER",
                   "decision_threshold":0.03},
      "generalization":{"metric":"heldout_delta","heldout_distribution":"D_heldout",
                        "direction":"HIGHER_IS_BETTER","decision_threshold":0.02},
      "interference":{"metric":"protected_delta","protected_distribution":"D_protected",
                      "direction":"NONINFERIORITY","noninferiority_margin":-0.02},
      "cost":{"unit":"USD","budget_ceiling":100.0,
              "required_categories":["production","selection","verification","transfer",
                                     "application","human","compute","recovery"]},
      "missing_data_rule":"fail closed; no imputation unless separately preregistered",
      "stopping_rule":"fixed completed-unit counts; no outcome-dependent extension",
      "claim_ceiling":"scope-limited capability evidence only",
      "plan_sha256":""
    }
    p["plan_sha256"]=expected_hash(p)
    return p


class CapabilityPrereg(unittest.TestCase):
    def test_valid_frozen_plan(self):
        self.assertEqual([],validate(plan()))

    def test_repeat_must_really_repeat(self):
        p=plan();p["repeat"]["independent_runs"]=1;p["plan_sha256"]=expected_hash(p)
        self.assertIn("REPEAT_RUNS",{e["code"] for e in validate(p)})

    def test_generalization_must_be_heldout(self):
        p=plan();p["generalization"]["heldout_distribution"]="D_primary";p["plan_sha256"]=expected_hash(p)
        self.assertIn("GENERALIZATION_NOT_HELDOUT",{e["code"] for e in validate(p)})

    def test_interference_margin_is_predeclared(self):
        p=plan();p["interference"]["noninferiority_margin"]=None;p["plan_sha256"]=expected_hash(p)
        self.assertIn("INTERFERENCE_MARGIN",{e["code"] for e in validate(p)})

    def test_tamper_breaks_plan_hash(self):
        p=plan();p["effect"]["decision_threshold"]=0.99
        self.assertIn("PLAN_HASH",{e["code"] for e in validate(p)})

    def test_placeholders_are_not_freeze(self):
        p=plan();p["claim_ceiling"]="TBD";p["plan_sha256"]=expected_hash(p)
        self.assertIn("TEXT",{e["code"] for e in validate(p)})


if __name__=="__main__":
    unittest.main()
