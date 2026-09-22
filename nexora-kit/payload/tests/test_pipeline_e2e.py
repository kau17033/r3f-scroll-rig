"""投入 → 索引 → 処置 → ゲート解除 → 改変検出 までの通し検査。

単体検査は各部品が仕様どおりであることしか示さない。本検査は、
「原文を入れてから実装が解禁されるまで」が実際に通ること、および
「正本が改変されたら即座に閉じること」を、通しで確認する。

合成原文は SRC-01 の構造を模す: CONV§0-34 / AUDIT§0-73 / SOV§0-1313 = 1,423 節。
見出しに `→` を含む節と、数式変換の残骸を意図的に混ぜる。
"""
import csv
import os
import random
import shutil
import subprocess
import sys
import tempfile
import unittest

from _common import ROOT  # noqa: E402

BLOCKS = (("CONV", 35), ("AUDIT", 74), ("SOV", 1314))
NUMBERED = sum(n for _, n in BLOCKS)          # 1423
RESIDUE_EVERY = 97                            # i % 97 == 0 の節の直後に残骸を 2 行入れる
KIT_FILES = ["tools/manifest.py", "tools/index_sections.py", "tools/gate_check.py",
             "tools/source_registry_check.py"]
HOOKS = [".claude/hooks/session_start.py"]


def synthesize():
    random.seed(0)
    lines = ["ULTRACODE 指令群（抽出テキスト）", ""]
    residue = 0
    for mark, n in BLOCKS:
        for i in range(n):
            if mark == "SOV" and i == 650:
                lines.append("%s§%d 状態復元 → 再検証 → 人間承認" % (mark, i))
            elif mark == "SOV" and i == 651:
                lines.append("%s§%d → 矢印で始まる見出し" % (mark, i))
            else:
                lines.append("%s§%d 見出し%d" % (mark, i, i))
            for _ in range(random.randint(1, 4)):
                lines.append("本文。" * random.randint(1, 20))
            if i % RESIDUE_EVERY == 0:
                lines.extend(["# [", "数式変換の残骸 \\alpha", "# ERS"])
                residue += 2
    return "\n".join(lines) + "\n", residue


class PipelineEndToEnd(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.d = tempfile.mkdtemp(prefix="nexora-e2e-")
        for rel in KIT_FILES + HOOKS:
            dst = os.path.join(cls.d, rel)
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            shutil.copy(os.path.join(ROOT, rel), dst)
        for sub in ("sources", "control"):
            os.makedirs(os.path.join(cls.d, sub), exist_ok=True)
        shutil.copy(os.path.join(ROOT, "control", "decisions.md"),
                    os.path.join(cls.d, "control", "decisions.md"))
        # G6 validates the committed immutable observation of external sources.
        # The synthetic E2E corpus tests G1 independently; copy the real registry/report
        # so this fixture is not coupled to live GitHub/network access.
        for name in ("source_registry.csv", "EXTERNAL-VALIDATION-20260922.json"):
            shutil.copy(os.path.join(ROOT, "control", name),
                        os.path.join(cls.d, "control", name))
        cls.src = os.path.join(cls.d, "sources", "SRC-01-ultracode.md")
        body, cls.residue = synthesize()
        with open(cls.src, "w", encoding="utf-8") as f:
            f.write(body)

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.d, ignore_errors=True)

    def tool(self, name, *args, **kw):
        return subprocess.run([sys.executable, os.path.join(self.d, "tools", name)] + list(args),
                              capture_output=True, text=True, **kw)

    def rows(self, rel):
        with open(os.path.join(self.d, rel), encoding="utf-8", newline="") as f:
            return list(csv.DictReader(f))

    # 順序に意味があるため、名前で実行順を固定する。
    def test_01_manifest_build_and_verify(self):
        self.assertEqual(0, self.tool("manifest.py", "build").returncode)
        r = self.tool("manifest.py", "verify")
        self.assertEqual(0, r.returncode, r.stdout)

    def test_02_index_keeps_every_numbered_section(self):
        r = self.tool("index_sections.py", self.src, "--source-id", "SRC-01",
                      "--out", os.path.join(self.d, "control", "section_index.csv"),
                      "--disposition", os.path.join(self.d, "control", "disposition.csv"))
        self.assertEqual(0, r.returncode, r.stderr)
        self.assertIn("NUMBER_GAPS: none", r.stdout)

        rows = self.rows("control/section_index.csv")
        numbered = [x for x in rows if "@L" not in x["section_id"]]
        self.assertEqual(NUMBERED, len(numbered), "番号付き節が 1,423 でない")
        self.assertEqual(self.residue, len(rows) - len(numbered), "残骸を落としている")

        per = {}
        for x in numbered:
            per[x["block"]] = per.get(x["block"], 0) + 1
        self.assertEqual({"B1": 35, "B2": 74, "B3": 1314}, per, "ブロック分割が一致しない")

        ids = {x["section_id"] for x in rows}
        for want in ("SRC-01:B3§650", "SRC-01:B3§651"):
            self.assertIn(want, ids, "→ を含む見出しを落とした")

    def test_03_gate_blocked_before_disposition(self):
        r = self.tool("gate_check.py")
        self.assertEqual(1, r.returncode)
        self.assertIn("[PASS] G1", r.stdout)      # 正本は健全
        self.assertIn("PENDING=%d" % (NUMBERED + self.residue), r.stdout)

    def test_04_gate_unlocks_only_when_all_ledgers_are_complete(self):
        rows = self.rows("control/disposition.csv")
        reqs = []
        with open(os.path.join(self.d, "control", "disposition.csv"), "w",
                  encoding="utf-8", newline="") as f:
            w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
            w.writeheader()
            for i, x in enumerate(rows):
                if "@L" in x["section_id"]:
                    x["disposition"] = "ARTIFACT"
                else:
                    x["disposition"] = "REQUIREMENT" if i % 3 == 0 else "CONTEXT"
                if x["disposition"] == "REQUIREMENT":
                    rid = "REQ-%04d" % len(reqs)
                    x["req_ids"], x["task_ids"] = rid, "T-040"
                    reqs.append((rid, x["section_id"]))
                x["rationale"], x["decided_by"], x["decided_at"] = "e2e", "test", "2026-09-17"
                w.writerow(x)
        with open(os.path.join(self.d, "control", "traceability.csv"), "w",
                  encoding="utf-8", newline="") as f:
            w = csv.writer(f)
            w.writerow(["req_id", "source_ref", "requirement", "task_ids",
                        "test_ids", "evidence_paths", "status"])
            for rid, sid in reqs:
                w.writerow([rid, sid, "e2e", "T-040", "TEST-" + rid,
                            "evidence/T-040/%s.md" % rid, "SATISFIED"])
        with open(os.path.join(self.d, "control", "audit70.csv"), "w", encoding="utf-8") as f:
            f.write("item_id,item,count,evidence\n")
            for i in range(1, 12):
                f.write("A%02d,item%02d,0,evidence/T-070/a%02d.md\n" % (i, i, i))

        # 実リポジトリの DEC 状態に依存せず、fixture に PENDING を注入して
        # G3 が fail-closed であることを検証する。
        p = os.path.join(self.d, "control", "decisions.md")
        with open(p, encoding="utf-8") as f:
            body = f.read()
        injected = (
            body
            + "\n| DEC-999 | e2e pending decision | — | T-040 | PENDING |\n"
        )
        with open(p, "w", encoding="utf-8") as f:
            f.write(injected)

        self.assertEqual(1, self.tool("gate_check.py").returncode,
                         "fixture の DEC が未決のまま解除された")

        with open(p, "w", encoding="utf-8") as f:
            f.write(injected.replace(
                "| DEC-999 | e2e pending decision | — | T-040 | PENDING |",
                "| DEC-999 | e2e pending decision | — | T-040 | APPROVED |",
            ))

        r = self.tool("gate_check.py")
        self.assertEqual(0, r.returncode, r.stdout)
        self.assertIn("UNLOCKED", r.stdout)

    def test_05_tampering_relocks_the_gate(self):
        with open(self.src, "a", encoding="utf-8") as f:
            f.write("改変\n")
        try:
            r = self.tool("gate_check.py")
            self.assertEqual(1, r.returncode, "正本が改変されたのに解除されたまま")
            self.assertIn("[BLOCK] G1", r.stdout)

            s = subprocess.run([sys.executable, os.path.join(self.d, ".claude", "hooks",
                                                             "session_start.py")],
                               capture_output=True, text=True,
                               env=dict(os.environ, CLAUDE_PROJECT_DIR=self.d))
            self.assertIn("SOURCES_INTEGRITY: FAIL", s.stdout)
        finally:
            with open(self.src, encoding="utf-8") as f:
                body = f.read()
            with open(self.src, "w", encoding="utf-8") as f:
                f.write(body[: -len("改変\n")])
        self.assertEqual(0, self.tool("manifest.py", "verify").returncode, "復元できていない")


if __name__ == "__main__":
    unittest.main()
