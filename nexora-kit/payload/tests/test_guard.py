"""guard.py の期待挙動。期待値は tools/guard_fixtures.py に 1 か所だけ置く。"""
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest

from _common import ROOT, HOOKS  # noqa: E402
from guard_fixtures import CASES  # noqa: E402

GUARD = os.path.join(HOOKS, "guard.py")


def run_guard(tool, tool_input, sandbox):
    payload = json.dumps({"tool_name": tool, "tool_input": tool_input, "cwd": sandbox})
    return subprocess.run([sys.executable, GUARD], input=payload, capture_output=True,
                          text=True, cwd=sandbox,
                          env=dict(os.environ, CLAUDE_PROJECT_DIR=sandbox))


class GuardCase(unittest.TestCase):
    def setUp(self):
        self.sandbox = tempfile.mkdtemp(prefix="nexora-guard-test-")
        for d in ("sources", "evidence", "control", "tasks", ".claude"):
            os.makedirs(os.path.join(self.sandbox, d), exist_ok=True)
        for rel in ("evidence/existing.md", "CLAUDE.md"):
            with open(os.path.join(self.sandbox, rel), "w") as f:
                f.write("x")

    def tearDown(self):
        shutil.rmtree(self.sandbox, ignore_errors=True)

    def test_fixture_cases(self):
        failures = []
        for cid, want, tool, ti in CASES:
            ti = {k: (v.replace("{ROOT}", self.sandbox) if isinstance(v, str) else v)
                  for k, v in ti.items()}
            r = run_guard(tool, ti, self.sandbox)
            if r.returncode != want:
                failures.append("%s: want %d got %d (%s)" % (cid, want, r.returncode,
                                                             r.stderr.strip()[:90]))
        self.assertEqual([], failures)

    def test_fail_closed_on_broken_stdin(self):
        r = subprocess.run([sys.executable, GUARD], input="{not json", capture_output=True,
                           text=True, env=dict(os.environ, CLAUDE_PROJECT_DIR=self.sandbox))
        self.assertEqual(2, r.returncode, "内部エラーは exit 2 でなければならない（exit 1 は非ブロッキング）")

    def test_never_exits_one(self):
        """exit 1 は Claude Code が非ブロッキングとして扱う。guard は 0 か 2 のみを返す。"""
        for cid, _want, tool, ti in CASES:
            ti = {k: (v.replace("{ROOT}", self.sandbox) if isinstance(v, str) else v)
                  for k, v in ti.items()}
            r = run_guard(tool, ti, self.sandbox)
            self.assertIn(r.returncode, (0, 2), "%s が exit %d を返した" % (cid, r.returncode))

    def test_blocked_cases_explain_themselves(self):
        for cid, want, tool, ti in CASES:
            if want != 2:
                continue
            ti = {k: (v.replace("{ROOT}", self.sandbox) if isinstance(v, str) else v)
                  for k, v in ti.items()}
            r = run_guard(tool, ti, self.sandbox)
            self.assertIn("[NEXORA-GUARD] BLOCKED", r.stderr, "%s に理由が無い" % cid)


if __name__ == "__main__":
    unittest.main()
