import os
import subprocess
import sys
import unittest

from _common import ROOT  # noqa: E402


class DependencyAudit(unittest.TestCase):
    def test_no_dangling_dependency_reference(self):
        r = subprocess.run(
            [sys.executable, os.path.join(ROOT, "tools", "dependency_audit.py")],
            capture_output=True, text=True,
        )
        self.assertEqual(0, r.returncode, r.stdout + r.stderr)
        self.assertIn("dangling=0", r.stdout)


if __name__ == "__main__":
    unittest.main()
