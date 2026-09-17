"""発動条件の判定に対する回帰。

偽陽性は恒常命令（STANDING-ORDER-001）を早発させる。未達を READY と
読むことは、未投入の原文に対して実装を始めることに等しい。
"""
import csv
import os
import subprocess
import sys
import unittest

from _common import ROOT  # noqa: E402
import readiness_check as rc  # noqa: E402


class Readiness(unittest.TestCase):
    def test_staging_is_never_ready(self):
        """`nexora-kit/payload/` に置かれたままの状態を READY と判定しない。"""
        ok, detail = rc.auto_check("R-01")
        if os.path.basename(os.path.dirname(rc.ROOT)) == "nexora-kit":
            self.assertFalse(ok, "staging を READY と誤認した: %s" % detail)
            self.assertIn("staging", detail)

    def test_unknown_auto_condition_fails_closed(self):
        ok, detail = rc.auto_check("R-999")
        self.assertFalse(ok)
        self.assertIn("fail-closed", detail)

    def test_human_rows_need_explicit_status(self):
        """HUMAN 行は空欄・PENDING のいずれも未達として扱う。推測で埋めない。"""
        with open(os.path.join(ROOT, "control", "readiness.csv"), encoding="utf-8", newline="") as f:
            rows = list(csv.DictReader(f))
        human = [r for r in rows if r["check_type"].strip().upper() == "HUMAN"]
        self.assertGreater(len(human), 0)
        for r in human:
            st = (r["status"] or "").strip().upper()
            self.assertIn(st, ("", "PENDING", "DONE", "RESOLVED", "WAIVED"),
                          "未知の status: %s (%s)" % (st, r["id"]))

    def test_every_row_declares_scope_and_type(self):
        with open(os.path.join(ROOT, "control", "readiness.csv"), encoding="utf-8", newline="") as f:
            rows = list(csv.DictReader(f))
        for r in rows:
            self.assertIn(r["scope"], ("W1", "W2", "W3"), r["id"])
            self.assertIn(r["check_type"].strip().upper(), ("AUTO", "HUMAN"), r["id"])
            self.assertTrue(r["condition"].strip(), r["id"])

    def test_cli_reports_not_ready_in_staging(self):
        r = subprocess.run([sys.executable, os.path.join(ROOT, "tools", "readiness_check.py")],
                           capture_output=True, text=True)
        self.assertEqual(1, r.returncode, "未達があるのに exit 0 を返した")
        self.assertIn("NOT_READY", r.stdout)


if __name__ == "__main__":
    unittest.main()
