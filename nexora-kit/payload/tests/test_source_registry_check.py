import json
import os
import subprocess
import sys
import unittest

from _common import ROOT  # noqa: E402
from source_registry_check import validate_external_report, validate_registry


class SourceRegistryCheck(unittest.TestCase):
    def test_repo_registry_passes(self):
        r = subprocess.run(
            [sys.executable, os.path.join(ROOT, "tools", "source_registry_check.py")],
            capture_output=True, text=True
        )
        self.assertEqual(0, r.returncode, r.stdout + r.stderr)
        self.assertIn("SOURCE_REGISTRY: PASS", r.stdout)

    def test_bad_content_hash_fails(self):
        rows = [{
            "source_id": sid,
            "status": "CONTENT_HASH_FIXED",
            "immutable_ref": "sha256:" + "0" * 64,
            "authority_class": "X",
        } for sid in ("SRC-01", "SRC-03", "SRC-05", "SRC-06", "SRC-07", "SRC-14")]
        rows += [{
            "source_id": sid,
            "status": "VERIFIED_IMMUTABLE",
            "immutable_ref": "a" * 40,
            "authority_class": "X",
        } for sid in ("SRC-02A", "SRC-02B", "SRC-04A", "SRC-04B")]
        rows.append({
            "source_id": "SRC-15",
            "status": "VERIFIED_EXTERNAL_REFERENCE",
            "immutable_ref": "arxiv:2609.14858",
            "authority_class": "EXTERNAL_RESEARCH_REFERENCE",
        })
        rows[0]["immutable_ref"] = "sha256:bad"
        self.assertTrue(validate_registry(rows))

    def test_external_report_requires_all_match(self):
        report = {
            "total": 34, "match": 33, "mismatch": 1, "missing": 0,
            "entries": [{"status": "MATCH"}] * 33 + [{"status": "MISMATCH"}],
        }
        self.assertTrue(validate_external_report(report))


if __name__ == "__main__":
    unittest.main()
