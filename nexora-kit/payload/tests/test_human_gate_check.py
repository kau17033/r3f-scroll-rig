import os
import subprocess
import sys
import unittest

from _common import ROOT  # noqa: E402


class HumanGateCheck(unittest.TestCase):
    def run_gate(self, *args):
        return subprocess.run(
            [sys.executable, os.path.join(ROOT, "tools", "human_gate_check.py"), *args],
            capture_output=True, text=True
        )

    def test_registry_is_structurally_valid(self):
        r = self.run_gate("--validate")
        self.assertEqual(0, r.returncode, r.stdout + r.stderr)
        self.assertIn("HUMAN_GATES: VALID", r.stdout)

    def test_pending_human_gate_blocks_required_execution(self):
        r = self.run_gate("--require", "HG-VEA-ESTIMAND")
        self.assertEqual(2, r.returncode, r.stdout + r.stderr)
        self.assertIn("PENDING_HUMAN", r.stdout)

    def test_missing_gate_fails_closed(self):
        r = self.run_gate("--require", "HG-NOT-REAL")
        self.assertEqual(2, r.returncode, r.stdout + r.stderr)
        self.assertIn("MISSING", r.stdout)


if __name__ == "__main__":
    unittest.main()
