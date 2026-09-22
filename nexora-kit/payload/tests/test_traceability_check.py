import os
import subprocess
import sys
import unittest

from _common import ROOT  # noqa: E402


class TraceabilityCheck(unittest.TestCase):
    def test_all_requirements_are_traced_without_false_satisfaction(self):
        r = subprocess.run(
            [sys.executable, os.path.join(ROOT, "tools", "traceability_check.py")],
            capture_output=True, text=True,
        )
        self.assertEqual(0, r.returncode, r.stdout + r.stderr)
        self.assertIn("traced=1652", r.stdout)
        self.assertIn("satisfaction_not_implied=true", r.stdout)


if __name__ == "__main__":
    unittest.main()
