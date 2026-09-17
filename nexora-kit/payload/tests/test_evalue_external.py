"""外部提出された anytime-valid 検定の主張に対する回帰。

採用の可否は DEC-004（人間判断）であり、本テストは監査のみを固定する。
主張が将来崩れた場合（式の変更、閾値の変更）、ここで落ちる。
"""
import unittest
from fractions import Fraction

from _common import ROOT  # noqa: E402
import verify_evalue as ve  # noqa: E402


class EValueAudit(unittest.TestCase):
    def test_m1_is_a_test_martingale(self):
        for fn in (ve.e_two_sided, ve.e_one_sided):
            bad, total = ve.check_martingale(fn, n_max=25)
            self.assertEqual([], bad, "Ville の前提が崩れている")
            self.assertGreater(total, 300)
            self.assertEqual(Fraction(1), fn(0, 0), "E_0 は 1 でなければならない")

    def test_m2_closed_form_matches_the_definition(self):
        for b, c in ((3, 1), (7, 0), (5, 5), (9, 2)):
            self.assertAlmostEqual(float(ve.e_two_sided(b, c)),
                                   ve.mixture_numeric(b, c, 0.0, 1.0, 1.0, 50000), places=4)
            self.assertAlmostEqual(float(ve.e_one_sided(b, c)),
                                   ve.mixture_numeric(b, c, 0.5, 1.0, 2.0, 50000), places=4)

    def test_m3_peeking_breaks_the_fixed_test_but_not_the_e_value(self):
        seeds = [20260917 + i for i in range(3)]
        r = ve.benchmark(0.5, 30, seeds, 500)
        self.assertGreater(r["B"][0], float(ve.ALPHA), "固定n+のぞき見が α を超えていない")
        self.assertLessEqual(r["C"][0], float(ve.ALPHA), "e-value+のぞき見が α を超えた")

    def test_readme_claim_reject_at_b7_c0(self):
        e = ve.e_one_sided(7, 0)
        self.assertEqual(Fraction(255, 8), e)
        self.assertGreaterEqual(e, 1 / ve.ALPHA)

    def test_fixed_test_is_conservative_under_h0(self):
        """A の H0 棄却率が α を大きく下回るのは離散性による。
        C の「α 以下」はこの保守的な基準との比較である点を固定する。"""
        r = ve.benchmark(0.5, 30, [20260917, 20260918, 20260919], 500)
        self.assertLess(r["A"][0], float(ve.ALPHA))


if __name__ == "__main__":
    unittest.main()
