"""外部保持の正本レジストリに対する回帰。

ネットワークに触れない。到達性は環境依存であり、テストの合否に混ぜると
「取得できなかった」と「改変された」の区別が失われる。
"""
import csv
import os
import re
import unittest

from _common import ROOT  # noqa: E402
import external_sources as ex  # noqa: E402

SHA40 = re.compile(r"^[0-9a-f]{40}$")


def rows():
    with open(os.path.join(ROOT, "sources", "EXTERNAL.csv"), encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


class ExternalRegistry(unittest.TestCase):
    def test_registry_is_well_formed(self):
        rs = rows()
        self.assertGreater(len(rs), 0)
        for r in rs:
            self.assertRegex(r["blob_sha"], SHA40, r["path"])
            self.assertRegex(r["repo"], r"^[\w.-]+/[\w.-]+$", r["path"])
            self.assertTrue(r["path"].strip())
            self.assertFalse(r["path"].startswith("/"), "パスは相対であること: %s" % r["path"])
            self.assertIn(r["src_id"], ("SRC-01", "SRC-02", "SRC-03", "SRC-04",
                                        "SRC-05", "SRC-06", "SRC-07", "SRC-08"))
            self.assertRegex(r["observed_at"], r"^\d{4}-\d{2}-\d{2}$", r["path"])

    def test_no_duplicate_entries(self):
        keys = [(r["repo"], r["path"]) for r in rows()]
        self.assertEqual(len(keys), len(set(keys)), "同一 (repo, path) が重複している")

    def test_authoritative_documents_are_registered(self):
        """SSOT と LOCK は必ず登録されていること。落とすと固定が意味を失う。"""
        paths = {(r["repo"], r["path"]) for r in rows()}
        for must in (("kau17033/vea-g3", "SSOT.md"),
                     ("kau17033/vea-g3", "SPEC.md"),
                     ("kau17033/vea-g3", "PROTOCOL_LOCK.md"),
                     ("kau17033/loopcell", "experiments/loopcell_phase0/spec/SPEC_v1.1.md"),
                     ("kau17033/loopcell", "experiments/loopcell_phase0/spec/FREEZE_MANIFEST.json")):
            self.assertIn(must, paths, "正本が未登録: %s" % (must,))

    def test_load_matches_file(self):
        self.assertEqual(len(rows()), len(ex.load()))

    def test_partial_is_not_a_pass(self):
        """検証が不完全な状態をゲート合格にしない。ソースに終了コードの分離が残っているか。"""
        src = open(os.path.join(ROOT, "tools", "external_sources.py"), encoding="utf-8").read()
        self.assertIn('"PARTIAL": 3', src, "PARTIAL が 0 に戻されている（不完全な検証を合格にしている）")
        self.assertIn('"NOT_IDENTIFIABLE": 2', src)
        self.assertIn('"FAIL": 1', src)

    def test_no_local_copy_of_external_sources(self):
        """外部正本を sources/ へ複製していないこと。複製は SSOT の分岐である。"""
        entries = [e for e in os.listdir(os.path.join(ROOT, "sources"))
                   if e not in (".gitkeep", "README.md", "MANIFEST.sha256", "EXTERNAL.csv")]
        self.assertEqual([], entries, "sources/ に複製がある: %s" % entries)


if __name__ == "__main__":
    unittest.main()
