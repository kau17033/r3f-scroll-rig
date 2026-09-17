"""ゲートは初期状態で BLOCKED、条件を全て満たしたときのみ UNLOCKED。"""
import os
import shutil
import subprocess
import sys
import tempfile
import unittest

from _common import ROOT  # noqa: E402

AUDIT_ITEMS = "\n".join("A%02d,item%02d,0," % (i, i) for i in range(1, 12))


class GateCheck(unittest.TestCase):
    def test_blocked_in_initial_state(self):
        r = subprocess.run([sys.executable, os.path.join(ROOT, "tools", "gate_check.py")],
                           capture_output=True, text=True)
        self.assertEqual(1, r.returncode)
        self.assertIn("BLOCKED", r.stdout)
        for gid in ("G1", "G2", "G3", "G4", "G5"):
            self.assertIn(gid, r.stdout)

    def test_unlocks_only_when_every_condition_holds(self):
        d = tempfile.mkdtemp(prefix="nexora-gate-")
        try:
            os.makedirs(os.path.join(d, "tools"))
            os.makedirs(os.path.join(d, "sources"))
            os.makedirs(os.path.join(d, "control"))
            for f in ("gate_check.py", "manifest.py"):
                shutil.copy(os.path.join(ROOT, "tools", f), os.path.join(d, "tools", f))
            with open(os.path.join(d, "sources", "SRC-01.md"), "w") as f:
                f.write("§1\n")
            subprocess.run([sys.executable, os.path.join(d, "tools", "manifest.py"), "build"],
                           capture_output=True, text=True)
            c = os.path.join(d, "control")
            with open(os.path.join(c, "disposition.csv"), "w") as f:
                f.write("section_id,source_id,disposition,rationale,req_ids,task_ids,decided_by,decided_at\n")
                f.write("SRC-01:B1§1,SRC-01,REQUIREMENT,x,REQ-1,T-1,human,2026-01-01\n")
            with open(os.path.join(c, "decisions.md"), "w") as f:
                f.write("| DEC-001 | x | — | T-1 | APPROVED |\n")
            with open(os.path.join(c, "traceability.csv"), "w") as f:
                f.write("req_id,source_ref,requirement,task_ids,test_ids,evidence_paths,status\n")
                f.write("REQ-1,SRC-01 §1,x,T-1,TEST-1,evidence/a.md,SATISFIED\n")
            with open(os.path.join(c, "audit70.csv"), "w") as f:
                f.write("item_id,item,count,evidence\n" + AUDIT_ITEMS + "\n")

            r = subprocess.run([sys.executable, os.path.join(d, "tools", "gate_check.py")],
                               capture_output=True, text=True)
            self.assertEqual(0, r.returncode, r.stdout)
            self.assertIn("UNLOCKED", r.stdout)

            # 1 条件を崩すと必ず BLOCKED に戻る
            with open(os.path.join(c, "decisions.md"), "a") as f:
                f.write("| DEC-002 | y | — | T-2 | PENDING |\n")
            r2 = subprocess.run([sys.executable, os.path.join(d, "tools", "gate_check.py")],
                                capture_output=True, text=True)
            self.assertEqual(1, r2.returncode)
            self.assertIn("BLOCKED", r2.stdout)
        finally:
            shutil.rmtree(d, ignore_errors=True)
