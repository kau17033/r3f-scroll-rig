import os
import subprocess
import sys
import unittest

from _common import ROOT  # noqa: E402


class VeaComplianceReconciliation(unittest.TestCase):
    def test_compliance_reconciliation_is_fail_closed(self):
        r = subprocess.run(
            [sys.executable, os.path.join(ROOT, "tools", "vea_compliance_check.py")],
            capture_output=True, text=True,
        )
        self.assertEqual(0, r.returncode, r.stdout + r.stderr)
        self.assertIn("42 rows reconciled", r.stdout)
        self.assertIn("G4=BLOCKED/closure-null", r.stdout)


if __name__ == "__main__":
    unittest.main()
