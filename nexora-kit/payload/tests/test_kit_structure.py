"""キットの構造不変条件。ゲートが黙って外れる形の変更を落とす。"""
import json
import os
import re
import unittest

from _common import ROOT  # noqa: E402

SETTINGS = os.path.join(ROOT, ".claude", "settings.json")


def read(rel):
    with open(os.path.join(ROOT, rel), encoding="utf-8") as f:
        return f.read()


class KitStructure(unittest.TestCase):
    def test_settings_disables_auto_memory(self):
        cfg = json.loads(read(".claude/settings.json"))
        self.assertIs(False, cfg.get("autoMemoryEnabled"),
                      "auto memory は SRC-02 ISO§2（過去文脈の隔離）と衝突する")

    def test_settings_denies_protected_paths(self):
        deny = json.loads(read(".claude/settings.json"))["permissions"]["deny"]
        joined = " ".join(deny)
        for needle in ("sources/", ".claude/", "CLAUDE.md", "AUTHORITY.md"):
            self.assertIn(needle, joined)

    def test_settings_registers_both_hooks(self):
        hooks = json.loads(read(".claude/settings.json"))["hooks"]
        pre = [h["command"] for e in hooks["PreToolUse"] for h in e["hooks"]]
        start = [h["command"] for e in hooks["SessionStart"] for h in e["hooks"]]
        self.assertTrue(any("guard.py" in c for c in pre))
        self.assertTrue(any("session_start.py" in c for c in start))
        for e in hooks["PreToolUse"]:
            for tool in ("Edit", "Write", "Bash"):
                self.assertIn(tool, e["matcher"])

    def test_hook_scripts_are_executable_and_shebanged(self):
        for rel in (".claude/hooks/guard.py", ".claude/hooks/session_start.py"):
            p = os.path.join(ROOT, rel)
            self.assertTrue(os.access(p, os.X_OK), "%s に実行権限が無い" % rel)
            self.assertTrue(read(rel).startswith("#!"), "%s に shebang が無い" % rel)

    def test_claude_md_stays_short(self):
        n = len(read("CLAUDE.md").splitlines())
        self.assertLess(n, 200, "CLAUDE.md が長すぎる（目安 200 行未満）: %d 行" % n)

    def test_no_skill_named_verify(self):
        d = os.path.join(ROOT, ".claude", "skills")
        self.assertNotIn("verify", os.listdir(d), "同梱スキル /verify と名前が衝突する")

    def test_every_skill_and_agent_has_frontmatter(self):
        for base, pattern in ((os.path.join(ROOT, ".claude", "skills"), "SKILL.md"),
                              (os.path.join(ROOT, ".claude", "agents"), None)):
            for entry in sorted(os.listdir(base)):
                p = os.path.join(base, entry, pattern) if pattern else os.path.join(base, entry)
                if not os.path.isfile(p):
                    continue
                with open(p, encoding="utf-8") as f:
                    head = f.read(400)
                self.assertTrue(head.startswith("---\n"), "%s に frontmatter が無い" % p)
                self.assertRegex(head, r"\nname:\s*\S+")
                self.assertRegex(head, r"\ndescription:\s*\S+")

    def test_decisions_are_all_pending_until_a_human_approves(self):
        body = read("control/decisions.md")
        ids = set(re.findall(r"^\|\s*(DEC-\d{3})\s*\|", body, re.M))
        self.assertEqual(9, len(ids), "DEC-001..009 が揃っていない: %s" % sorted(ids))

    def test_authority_is_marked_unapproved(self):
        self.assertIn("PROPOSED", read("control/AUTHORITY.md"))

    def test_state_declares_implementation_locked(self):
        self.assertIn("実装解禁", read("control/STATE.md"))

    def test_every_task_declares_blocked_by(self):
        d = os.path.join(ROOT, "tasks")
        for name in sorted(os.listdir(d)):
            if not name.startswith("T-"):
                continue
            with open(os.path.join(d, name), encoding="utf-8") as f:
                self.assertIn("blocked_by", f.read(), "%s に blocked_by が無い" % name)

    def test_sources_holds_no_original_yet(self):
        """原文を勝手に生成していないこと。要約を正本に昇格させない。"""
        entries = [e for e in os.listdir(os.path.join(ROOT, "sources"))
                   if e not in (".gitkeep", "README.md", "MANIFEST.sha256")]
        self.assertEqual([], entries, "sources/ に未検証の生成物がある: %s" % entries)
