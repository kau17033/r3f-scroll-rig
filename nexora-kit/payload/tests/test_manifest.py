"""マニフェストの作成・照合・改変検出。正本の不変性の最終防衛線。"""
import os
import shutil
import subprocess
import sys
import tempfile
import unittest

from _common import ROOT  # noqa: E402


class ManifestRoundTrip(unittest.TestCase):
    def setUp(self):
        self.d = tempfile.mkdtemp(prefix="nexora-mf-")
        os.makedirs(os.path.join(self.d, "tools"))
        os.makedirs(os.path.join(self.d, "sources"))
        shutil.copy(os.path.join(ROOT, "tools", "manifest.py"),
                    os.path.join(self.d, "tools", "manifest.py"))
        self.src = os.path.join(self.d, "sources", "SRC-01-x.md")
        with open(self.src, "w", encoding="utf-8") as f:
            f.write("§1 原文\n")

    def tearDown(self):
        shutil.rmtree(self.d, ignore_errors=True)

    def run_mf(self, *args):
        return subprocess.run([sys.executable, os.path.join(self.d, "tools", "manifest.py")] + list(args),
                              capture_output=True, text=True)

    def test_build_then_verify_passes(self):
        self.assertEqual(0, self.run_mf("build").returncode)
        r = self.run_mf("verify")
        self.assertEqual(0, r.returncode, r.stdout)
        self.assertIn("VERIFY: PASS", r.stdout)

    def test_modification_is_detected(self):
        self.run_mf("build")
        with open(self.src, "a", encoding="utf-8") as f:
            f.write("改変\n")
        r = self.run_mf("verify")
        self.assertEqual(1, r.returncode)
        self.assertIn("MODIFIED", r.stdout)

    def test_deletion_is_detected(self):
        self.run_mf("build")
        os.remove(self.src)
        r = self.run_mf("verify")
        self.assertEqual(1, r.returncode)
        self.assertIn("MISSING", r.stdout)

    def test_untracked_addition_is_detected(self):
        self.run_mf("build")
        with open(os.path.join(self.d, "sources", "SRC-99-new.md"), "w") as f:
            f.write("後から足した原文\n")
        r = self.run_mf("verify")
        self.assertEqual(1, r.returncode)
        self.assertIn("UNTRACKED", r.stdout)

    def test_missing_manifest_is_not_identifiable(self):
        r = self.run_mf("verify")
        self.assertEqual(2, r.returncode)
        self.assertIn("NOT_IDENTIFIABLE", r.stdout)

    def test_build_refuses_empty_sources(self):
        os.remove(self.src)
        r = self.run_mf("build")
        self.assertEqual(1, r.returncode)
        self.assertIn("FAIL", r.stdout)
