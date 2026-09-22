import os
import subprocess
import sys
import unittest

from _common import ROOT  # noqa: E402


class ConflictCheck(unittest.TestCase):
    def test_conflicts_are_resolved_or_human_gated(self):
        r = subprocess.run(
            [sys.executable, os.path.join(ROOT, "tools", "conflict_check.py")],
            capture_output=True, text=True,
        )
        self.assertEqual(0, r.returncode, r.stdout + r.stderr)
        self.assertIn("18/18 classified", r.stdout)
        self.assertIn("human_gated=3", r.stdout)


if __name__ == "__main__":
    unittest.main()
