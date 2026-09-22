"""VEA-G3 frozen seed derivation mirror tests."""
import hashlib
import json
import os
import unittest

from _common import ROOT  # noqa: E402
import seed_derive as sd  # noqa: E402

GOLDEN = os.path.join(ROOT, "tests", "golden", "seed_vectors.json")


def u32(s):
    return int.from_bytes(hashlib.sha256(s.encode("utf-8")).digest()[:4], "big")


class SeedDerive(unittest.TestCase):
    def test_golden_vectors(self):
        with open(GOLDEN, encoding="utf-8") as f:
            g = json.load(f)
        self.assertEqual("VERIFIED_AGAINST_SOURCE", g["status"])
        self.assertEqual(sd.FROZEN_DERIVE_BLOB, g["frozen_derive_blob"])
        self.assertEqual(sd.MASTER_SEED_EVAL, int(g["master_seed_eval"]))
        self.assertEqual(sd.MASTER_SEED_SRC, int(g["master_seed_src"]))
        for case in g["eval_reference_vectors"]:
            self.assertEqual(case["env_seed"], sd.env_seed(case["i"]))
            self.assertEqual(case["order"], sd.order(case["i"]))
        for j, want in g["source_reference_vectors"].items():
            self.assertEqual(want, sd.source_seed(int(j)))

    def test_independent_formula_expansion(self):
        i = 42
        env = u32("VEA-G3|eval|%d|%d" % (sd.MASTER_SEED_EVAL, i))
        self.assertEqual(env, sd.env_seed(i))
        want_order = u32("VEA-G3|order|%d" % env) % 2
        self.assertEqual(want_order, sd.order(i))
        j = 2
        want_src = u32("VEA-G3|src|%d|%d" % (sd.MASTER_SEED_SRC, j))
        self.assertEqual(want_src, sd.source_seed(j))

    def test_alias_is_exact(self):
        for i in (0, 1, 2, 10, 183):
            self.assertEqual(sd.env_seed(i), sd.eval_seed(i))

    def test_deterministic_uint32(self):
        for i in (0, 1, 2, 10, 183, 100000):
            a, b = sd.env_seed(i), sd.env_seed(i)
            self.assertEqual(a, b)
            self.assertTrue(0 <= a < 2 ** 32)

    def test_indices_must_be_nonnegative_int(self):
        for bad in (-1, 1.5, "3", True):
            with self.assertRaises(ValueError):
                sd.env_seed(bad)
            with self.assertRaises(ValueError):
                sd.source_seed(bad)


if __name__ == "__main__":
    unittest.main()
