import os
import subprocess
import sys
import unittest

from _common import ROOT  # noqa: E402


class DispositionCheck(unittest.TestCase):
    def test_normative_corpus_is_fully_dispositioned(self):
        r = subprocess.run(
            [sys.executable, os.path.join(ROOT, "tools", "disposition_check.py")],
            capture_output=True, text=True
        )
        self.assertEqual(0, r.returncode, r.stdout + r.stderr)
        self.assertIn("sections=1652", r.stdout)
        self.assertIn("PENDING=0", r.stdout)


if __name__ == "__main__":
    unittest.main()
