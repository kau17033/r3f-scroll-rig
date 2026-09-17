#!/usr/bin/env python3
"""VEA-G3 seed 導出（決定論）。

解釈（SRC-03 §9.5 の再実装。SRC-03 投入後に T-100 で原文と再照合すること）:
  eval seed  : sha256(UTF-8 "VEA-G3|eval|{env_seed}|{i}") の先頭 4 バイトをビッグエンディアンで読む
  order      : sha256(UTF-8 "VEA-G3|order|{env_seed}") を同様に読み、mod 2

断定不可: `master_seed_source`（env_seed 自体の作り方）は原文に無い → OQ-001。
本モジュールは env_seed を **引数として受け取るだけ** であり、生成しない。

統計・乱数に関わる決定は本スクリプトのような決定論コードだけが行う。
LLM に導出させてはならない（SRC-02 SPEC§39, §73）。
"""
import argparse
import hashlib
import json
import os
import sys

PREFIX = "VEA-G3"


def _u32(material: str) -> int:
    return int.from_bytes(hashlib.sha256(material.encode("utf-8")).digest()[:4], "big")


def eval_seed(env_seed: str, i: int) -> int:
    """評価 i 番目の seed（uint32）。"""
    if not isinstance(i, int) or isinstance(i, bool) or i < 0:
        raise ValueError("i は 0 以上の整数でなければならない: %r" % (i,))
    return _u32("%s|eval|%s|%d" % (PREFIX, env_seed, i))


def order(env_seed: str) -> int:
    """割付順序 0/1。"""
    return _u32("%s|order|%s" % (PREFIX, env_seed)) % 2


def vectors(env_seed: str, indices):
    return {
        "prefix": PREFIX,
        "env_seed": env_seed,
        "order": order(env_seed),
        "eval_seeds": {str(i): eval_seed(env_seed, i) for i in indices},
    }


def main(argv=None):
    ap = argparse.ArgumentParser(description="VEA-G3 seed derivation")
    ap.add_argument("--env-seed", help="環境 seed 文字列（生成はしない。人間が決めた値を渡す）")
    ap.add_argument("--indices", default="0,1,2,10,183")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--selftest", metavar="GOLDEN_JSON", nargs="?",
                    const=os.path.join(os.path.dirname(__file__), "..", "tests",
                                       "golden", "seed_vectors.json"))
    a = ap.parse_args(argv)

    if a.selftest:
        with open(a.selftest, encoding="utf-8") as f:
            g = json.load(f)
        bad = []
        for case in g["cases"]:
            if order(case["env_seed"]) != case["order"]:
                bad.append("order(%s)" % case["env_seed"])
            for i, want in case["eval_seeds"].items():
                got = eval_seed(case["env_seed"], int(i))
                if got != want:
                    bad.append("eval(%s,%s): got %d want %d" % (case["env_seed"], i, got, want))
        if bad:
            print("SEED_SELFTEST: FAIL\n  " + "\n  ".join(bad))
            return 1
        n = sum(len(c["eval_seeds"]) + 1 for c in g["cases"])
        print("SEED_SELFTEST: PASS (%d vectors)" % n)
        return 0

    if not a.env_seed:
        ap.error("--env-seed か --selftest のいずれかが必要")
    idx = [int(x) for x in a.indices.split(",") if x.strip()]
    v = vectors(a.env_seed, idx)
    if a.json:
        print(json.dumps(v, ensure_ascii=False, indent=2))
    else:
        print("env_seed=%s  order=%d" % (v["env_seed"], v["order"]))
        for i in idx:
            print("  i=%-5d seed=%d" % (i, v["eval_seeds"][str(i)]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
