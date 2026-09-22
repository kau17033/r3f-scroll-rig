#!/usr/bin/env python3
"""VEA-G3 frozen seed derivation mirror.

Source of truth:
  kau17033/VEA-G3 src/veag3_dk/derive.py
  git blob 4b529381a26b9e70a6d7e32fbe9e75d029fc00af

This module mirrors the frozen implementation for cross-repo verification only.
Changing these formulas or constants requires a new VEA protocol/version; NEXORA
must not reinterpret them.
"""
import argparse
import hashlib
import json
import os
import sys

PREFIX = "VEA-G3"
MASTER_SEED_EVAL = 2082073855474150835
MASTER_SEED_SRC = 7681503877328397875
FROZEN_DERIVE_BLOB = "4b529381a26b9e70a6d7e32fbe9e75d029fc00af"


def _u32(material: str) -> int:
    return int.from_bytes(hashlib.sha256(material.encode("utf-8")).digest()[:4], "big")


def _index(i, name="i"):
    if not isinstance(i, int) or isinstance(i, bool) or i < 0:
        raise ValueError("%s must be a non-negative integer: %r" % (name, i))
    return i


def env_seed(i: int, s_eval: int = MASTER_SEED_EVAL) -> int:
    i = _index(i)
    return _u32("%s|eval|%d|%d" % (PREFIX, s_eval, i))


def eval_seed(i: int, s_eval: int = MASTER_SEED_EVAL) -> int:
    """Compatibility alias: VEA names this derived value env_seed."""
    return env_seed(i, s_eval)


def order(i: int, s_eval: int = MASTER_SEED_EVAL) -> int:
    i = _index(i)
    es = env_seed(i, s_eval)
    return _u32("%s|order|%d" % (PREFIX, es)) % 2


def source_seed(j: int, s_src: int = MASTER_SEED_SRC) -> int:
    j = _index(j, "j")
    return _u32("%s|src|%d|%d" % (PREFIX, s_src, j))


def main(argv=None):
    ap = argparse.ArgumentParser(description="Mirror VEA-G3 frozen seed derivation")
    ap.add_argument("--index", type=int)
    ap.add_argument("--source-index", type=int)
    ap.add_argument("--selftest", metavar="GOLDEN_JSON", nargs="?",
                    const=os.path.join(os.path.dirname(__file__), "..", "tests",
                                       "golden", "seed_vectors.json"))
    args = ap.parse_args(argv)

    if args.selftest:
        with open(args.selftest, encoding="utf-8") as f:
            g = json.load(f)
        bad = []
        if g.get("frozen_derive_blob") != FROZEN_DERIVE_BLOB:
            bad.append("derive blob identity")
        if g.get("master_seed_eval") != MASTER_SEED_EVAL:
            bad.append("MASTER_SEED_EVAL")
        if g.get("master_seed_src") != MASTER_SEED_SRC:
            bad.append("MASTER_SEED_SRC")
        for case in g["eval_reference_vectors"]:
            i = case["i"]
            if env_seed(i) != case["env_seed"]:
                bad.append("env_seed(%d)" % i)
            if order(i) != case["order"]:
                bad.append("order(%d)" % i)
        for j, want in g["source_reference_vectors"].items():
            if source_seed(int(j)) != want:
                bad.append("source_seed(%s)" % j)
        if bad:
            print("SEED_SELFTEST: FAIL\n  " + "\n  ".join(bad))
            return 1
        n = len(g["eval_reference_vectors"]) * 2 + len(g["source_reference_vectors"])
        print("SEED_SELFTEST: PASS (%d frozen checks; source verified)" % n)
        return 0

    if args.index is not None:
        print(json.dumps({"i": args.index, "env_seed": env_seed(args.index),
                          "order": order(args.index)}, sort_keys=True))
        return 0
    if args.source_index is not None:
        print(json.dumps({"j": args.source_index, "source_seed": source_seed(args.source_index)},
                         sort_keys=True))
        return 0
    ap.error("--index, --source-index, or --selftest is required")


if __name__ == "__main__":
    sys.exit(main())
