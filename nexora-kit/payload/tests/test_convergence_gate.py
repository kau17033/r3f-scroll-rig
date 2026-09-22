import os
import subprocess
import sys
import unittest

from _common import ROOT  # noqa: E402


class ConvergenceGate(unittest.TestCase):
    def test_current_gate_fails_only_as_a_gate_not_as_a_crash(self):
        r = subprocess.run(
            [sys.executable, os.path.join(ROOT, "tools", "convergence_gate.py")],
            capture_output=True, text=True
        )
        self.assertIn(r.returncode, (0, 1), r.stdout + r.stderr)
        self.assertIn("NEXORA CONVERGENCE GATE", r.stdout)
        self.assertIn("final_host", r.stdout)
        self.assertIn("SCIENTIFIC_HUMAN_GATES: OUT_OF_SCOPE", r.stdout)

    def test_current_known_blocker_is_final_host(self):
        r = subprocess.run(
            [sys.executable, os.path.join(ROOT, "tools", "convergence_gate.py")],
            capture_output=True, text=True
        )
        self.assertEqual(1, r.returncode, r.stdout + r.stderr)
        self.assertIn("[BLOCK] final_host", r.stdout)
        for label in ("source_registry", "disposition", "requirements", "conflicts",
                      "traceability", "human_gate_registry", "state_projection"):
            self.assertIn("[PASS] " + label, r.stdout)


if __name__ == "__main__":
    unittest.main()
