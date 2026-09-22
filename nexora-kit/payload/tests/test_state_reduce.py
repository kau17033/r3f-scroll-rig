import json
import os
import subprocess
import sys
import unittest

from _common import ROOT  # noqa: E402


class ConvergenceState(unittest.TestCase):
    def run_reducer(self, *args):
        return subprocess.run(
            [sys.executable, os.path.join(ROOT, "tools", "state_reduce.py"), *args],
            capture_output=True, text=True
        )

    def load_state(self):
        r = self.run_reducer()
        self.assertEqual(0, r.returncode, r.stderr)
        return json.loads(r.stdout)

    def test_snapshot_is_exact_projection(self):
        r = self.run_reducer("--check")
        self.assertEqual(0, r.returncode, r.stdout + r.stderr)
        self.assertIn("CONVERGENCE_STATE: PASS", r.stdout)

    def test_completion_gate_namespace_is_exact(self):
        state = self.load_state()
        self.assertEqual(["C%d" % i for i in range(9)], list(state["completion_gates"].keys()))
        self.assertEqual("BLOCKED_EVIDENCE", state["completion_gates"]["C3"]["status"])
        self.assertEqual("NOT_EXECUTED", state["completion_gates"]["C4"]["status"])
        self.assertEqual("FORMAL_ONLY", state["completion_gates"]["C5"]["status"])
        self.assertEqual("PASS", state["completion_gates"]["C6"]["status"])
        self.assertEqual("PASS", state["completion_gates"]["C7"]["status"])
        self.assertEqual("VERIFIED", state["subjects"]["ORP/Receipt:EXTERNAL_CHECKPOINT"]["state"])

    def test_no_teleportation_states_are_preserved(self):
        state = self.load_state()
        self.assertEqual("BLOCKED_EVIDENCE", state["transitions"]["TR-01"]["status"])
        self.assertEqual("NOT_EXECUTED", state["transitions"]["TR-02"]["status"])
        self.assertEqual("FORMAL_ONLY", state["transitions"]["TR-03"]["status"])
        self.assertEqual("SUPPORTING_ONLY", state["transitions"]["TR-04"]["status"])

    def test_receipt_and_controller_are_separate_subjects(self):
        state = self.load_state()
        self.assertIn("ORP/Receipt:SLICE1", state["subjects"])
        self.assertIn("ORP/Controller:ACTION_SELECTION", state["subjects"])
        self.assertNotEqual(
            state["subjects"]["ORP/Receipt:SLICE1"]["state"],
            state["subjects"]["ORP/Controller:ACTION_SELECTION"]["state"],
        )

    def test_verified_t000_overrides_stale_prose(self):
        state = self.load_state()
        self.assertEqual("VERIFIED", state["subjects"]["NEXORA:T-000"]["state"])

    def test_verified_immutable_sources_have_blob_sha(self):
        state = self.load_state()
        for source_id, source in state["sources"].items():
            if source["status"] == "VERIFIED_IMMUTABLE":
                self.assertRegex(source["immutable_ref"], r"^[0-9a-f]{40}$", source_id)

    def test_capability_contract_has_no_artifact_count_proxy(self):
        with open(os.path.join(ROOT, "control", "capability_contract.schema.json"), encoding="utf-8") as f:
            schema = json.load(f)
        required = set(schema["required"])
        for name in ("baseline", "effect", "retention", "generalization", "interference", "cost", "validity", "provenance"):
            self.assertIn(name, required)
        self.assertNotIn("artifact_count", schema.get("properties", {}))


if __name__ == "__main__":
    unittest.main()
