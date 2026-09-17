"""seed 導出の決定性とゴールデン一致。"""
import hashlib
import json
import os
import unittest

from _common import ROOT  # noqa: E402
import seed_derive as sd  # noqa: E402

GOLDEN = os.path.join(ROOT, "tests", "golden", "seed_vectors.json")


class SeedDerive(unittest.TestCase):
    def test_golden_vectors(self):
        with open(GOLDEN, encoding="utf-8") as f:
            g = json.load(f)
        for case in g["cases"]:
            self.assertEqual(case["order"], sd.order(case["env_seed"]))
            for i, want in case["eval_seeds"].items():
                self.assertEqual(want, sd.eval_seed(case["env_seed"], int(i)),
                                 "env=%s i=%s" % (case["env_seed"], i))

    def test_matches_spec_expression(self):
        """独立に式を書き下しても一致すること（実装の言い換えではなく定義の再現）。"""
        env, i = "spec-check", 42
        want = int.from_bytes(
            hashlib.sha256(("VEA-G3|eval|%s|%d" % (env, i)).encode("utf-8")).digest()[:4], "big")
        self.assertEqual(want, sd.eval_seed(env, i))

    def test_deterministic_and_uint32(self):
        for i in (0, 1, 2, 10, 183, 100000):
            a, b = sd.eval_seed("x", i), sd.eval_seed("x", i)
            self.assertEqual(a, b)
            self.assertTrue(0 <= a < 2 ** 32)

    def test_order_is_binary(self):
        self.assertIn(sd.order("any"), (0, 1))

    def test_index_must_be_nonnegative_int(self):
        for bad in (-1, 1.5, "3", True):
            with self.assertRaises(ValueError):
                sd.eval_seed("x", bad)

    def test_distinct_indices_differ(self):
        seen = {sd.eval_seed("x", i) for i in range(200)}
        self.assertGreater(len(seen), 190, "衝突が多すぎる。導出式を疑う")

    def test_golden_status_is_declared(self):
        """原文照合前にゴールデンを VERIFIED と書かない（T-100 まで UNVERIFIED）。"""
        with open(GOLDEN, encoding="utf-8") as f:
            g = json.load(f)
        self.assertIn(g["status"], ("UNVERIFIED_AGAINST_SOURCE", "VERIFIED_AGAINST_SOURCE"))


if __name__ == "__main__":
    unittest.main()
