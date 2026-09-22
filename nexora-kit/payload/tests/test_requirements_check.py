import os
import subprocess
import sys
import unittest

from _common import ROOT  # noqa: E402


class RequirementsCheck(unittest.TestCase):
    def test_full_requirement_ledger(self):
        r = subprocess.run(
            [sys.executable, os.path.join(ROOT, "tools", "requirements_check.py")],
            capture_output=True, text=True,
        )
        self.assertEqual(0, r.returncode, r.stdout + r.stderr)
        self.assertIn("coverage=1652/1652", r.stdout)


if __name__ == "__main__":
    unittest.main()
