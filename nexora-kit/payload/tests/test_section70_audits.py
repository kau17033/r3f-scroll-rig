import os
import subprocess
import sys
import unittest
from _common import ROOT  # noqa: E402

class Section70Audits(unittest.TestCase):
    def run_tool(self, name):
        return subprocess.run([sys.executable, os.path.join(ROOT, "tools", name)],
                              capture_output=True, text=True)

    def test_dependencies(self):
        r=self.run_tool("dependency_audit.py")
        self.assertEqual(0,r.returncode,r.stdout+r.stderr)
        self.assertIn("dangling=0",r.stdout)

    def test_claims(self):
        r=self.run_tool("claim_audit.py")
        self.assertEqual(0,r.returncode,r.stdout+r.stderr)
        self.assertIn("unclassified=0",r.stdout)

    def test_failure_modes(self):
        r=self.run_tool("failure_mode_audit.py")
        self.assertEqual(0,r.returncode,r.stdout+r.stderr)
        self.assertIn("unhandled=0",r.stdout)

    def test_critical_artifacts(self):
        r=self.run_tool("critical_artifact_audit.py")
        self.assertEqual(0,r.returncode,r.stdout+r.stderr)
        self.assertIn("unprotected=0",r.stdout)

    def test_security(self):
        r=self.run_tool("security_audit.py")
        self.assertEqual(0,r.returncode,r.stdout+r.stderr)
        self.assertIn("critical_control_gaps=0",r.stdout)

if __name__=="__main__":
    unittest.main()
