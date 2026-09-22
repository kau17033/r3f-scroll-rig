import copy
import unittest

from _common import ROOT  # noqa: F401
from capability_gate import evaluate


def valid_contract():
    return {
        "capability_id":"cap.test",
        "version":"1.0",
        "scope":"held-out coding tasks",
        "policy_version":"p1",
        "evidence_refs":["run:1","run:2"],
        "baseline":{"metric":"success_rate","value":0.5,"evaluation_distribution":"D_eval"},
        "effect":{"metric":"delta_success","estimate":0.1,"decision_threshold":0.05,"status":"PASS"},
        "retention":{"status":"PASS","metric":"delta_after_delay","value":0.08},
        "generalization":{"status":"PASS","metric":"heldout_delta","value":0.06},
        "interference":{"status":"PASS","metric":"protected_noninferiority_margin","value":0.0},
        "cost":{"production":1.0,"selection":1.0,"verification":1.0,"transfer":1.0,
                "application":1.0,"human":0.0,"compute":2.0,"recovery":0.0,"unit":"USD"},
        "limitations":["single benchmark family"],
        "validity":{"status":"VALID","evaluated_at":"2026-09-23T00:00:00Z","expires_at":None},
        "provenance":{"source_experience_ids":["exp1"],"lineage_hashes":["a"*64]},
    }


class CapabilityGate(unittest.TestCase):
    def test_full_contract_is_promotable(self):
        r=evaluate(valid_contract())
        self.assertEqual("PROMOTABLE",r["status"])
        self.assertEqual([],r["blockers"])

    def test_effect_only_cannot_promote(self):
        c=valid_contract()
        c["retention"]["status"]="UNKNOWN"
        c["generalization"]["status"]="UNKNOWN"
        r=evaluate(c)
        self.assertEqual("BLOCKED",r["status"])
        codes={x["code"] for x in r["blockers"]}
        self.assertIn("RETENTION_NOT_PASS",codes)
        self.assertIn("GENERALIZATION_NOT_PASS",codes)

    def test_artifact_count_never_promotes(self):
        c=valid_contract()
        c["artifact_count"]=999999
        r=evaluate(c)
        self.assertEqual("BLOCKED",r["status"])
        self.assertIn("ARTIFACT_COUNT_PROXY_FORBIDDEN",{x["code"] for x in r["blockers"]})

    def test_missing_interference_and_cost_fail_closed(self):
        c=valid_contract()
        c["interference"]["value"]=None
        c["cost"]["verification"]=None
        r=evaluate(c)
        codes={x["code"] for x in r["blockers"]}
        self.assertIn("INTERFERENCE_VALUE",codes)
        self.assertIn("COST_FIELD",codes)

    def test_invalid_or_unproven_provenance_blocks(self):
        c=valid_contract()
        c["validity"]["status"]="HOLD"
        c["provenance"]["lineage_hashes"]=[]
        r=evaluate(c)
        codes={x["code"] for x in r["blockers"]}
        self.assertIn("VALIDITY_NOT_VALID",codes)
        self.assertIn("PROVENANCE_LINEAGE",codes)


if __name__=="__main__":
    unittest.main()
