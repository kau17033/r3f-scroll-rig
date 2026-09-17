"""索引器の回帰。見出し判定は緩くなければならない。"""
import os
import shutil
import tempfile
import unittest

from _common import ROOT  # noqa: E402
import index_sections as ix  # noqa: E402

FIXTURE = (
    "SOV§649 通常の見出し\n本文A\n"
    "SOV§650 状態復元 → 再検証\n本文B\n"
    "SOV§651 → 矢印で始まる\n本文C\n"
    "# [\n数式変換の残骸\n"
    "652. 番号のみ\n本文D\n"
    "第3章 和文の章\n本文E\n"
)


class Indexer(unittest.TestCase):
    def setUp(self):
        self.d = tempfile.mkdtemp(prefix="nexora-ix-")
        self.p = os.path.join(self.d, "f.md")
        with open(self.p, "w", encoding="utf-8") as f:
            f.write(FIXTURE)

    def tearDown(self):
        shutil.rmtree(self.d, ignore_errors=True)

    def test_arrow_headings_are_not_dropped(self):
        rows, _ = ix.index_file(self.p, "SRC-T")
        ids = [r["section_id"] for r in rows]
        self.assertTrue(any(i.endswith("§650") for i in ids), ids)
        self.assertTrue(any(i.endswith("§651") for i in ids), ids)

    def test_artifact_heading_is_flagged_not_removed(self):
        rows, _ = ix.index_file(self.p, "SRC-T")
        susp = [r for r in rows if r["suspect"]]
        self.assertEqual(1, len(susp))
        self.assertEqual(6, len(rows), "残骸を削らず、節として保持すること")

    def test_line_ranges_cover_the_file(self):
        rows, total = ix.index_file(self.p, "SRC-T")
        self.assertEqual(rows[-1]["line_end"], total)
        for a, b in zip(rows, rows[1:]):
            self.assertEqual(a["line_end"] + 1, b["line_start"])

    def test_gap_reporting(self):
        rows, _ = ix.index_file(self.p, "SRC-T")
        g = ix.gaps(rows)
        self.assertTrue(all(isinstance(v, list) for v in g.values()))

    def test_csv_output(self):
        out = os.path.join(self.d, "s.csv")
        disp = os.path.join(self.d, "d.csv")
        rc = ix.main([self.p, "--source-id", "SRC-T", "--out", out, "--disposition", disp])
        self.assertEqual(0, rc)
        with open(disp, encoding="utf-8") as f:
            body = f.read().strip().splitlines()
        self.assertEqual(7, len(body), "ヘッダ + 6 節")
        self.assertTrue(all("PENDING" in l for l in body[1:]))


if __name__ == "__main__":
    unittest.main()
