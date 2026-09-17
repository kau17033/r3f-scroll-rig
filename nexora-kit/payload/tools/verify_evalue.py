#!/usr/bin/env python3
"""外部提出された anytime-valid 検定の主張を、独立に検証する。

**本モジュールは NEXORA の判定に使わない。** e-value を採用するか否かは
DEC-004（人間判断）である。ここで行うのは監査だけであり、採用ではない。

検証する主張は 3 つ。
  M1 E_n は H0 (p=1/2) のもとで test martingale である（E_0 = 1、条件付期待値が保存）。
     これが成り立つときに限り Ville の不等式 P_H0(∃n: E_n >= 1/α) <= α が使える。
  M2 閉形式が混合 e-value の定義 E = 2^n ∫ p^b (1-p)^c dπ(p) と一致する。
  M3 H0 で「固定n検定 + のぞき見」は α を超え、「e-value + のぞき見」は超えない。

再実装であり引き写しではない。M2 は数値積分で定義そのものと突き合わせる。

  python3 tools/verify_evalue.py --martingale
  python3 tools/verify_evalue.py --benchmark
  python3 tools/verify_evalue.py --selftest
"""
import argparse
import random
import sys
from fractions import Fraction
from math import comb, factorial

ALPHA = Fraction(1, 20)


# ------------------------------------------------------------------ e-values
def e_two_sided(b: int, c: int) -> Fraction:
    """Beta(1,1) 混合。π = [0,1] 上の一様分布。"""
    n = b + c
    return Fraction(2 ** n) * Fraction(factorial(b) * factorial(c), factorial(n + 1))


def e_one_sided(b: int, c: int) -> Fraction:
    """π = [1/2,1] 上の一様分布（H1: 改善が優勢）。"""
    n = b + c
    return Fraction(factorial(b) * factorial(c), factorial(n + 1)) * sum(
        comb(n + 1, j) for j in range(b + 1))


def mcnemar_exact_two_sided(b: int, c: int) -> Fraction:
    n = b + c
    if n == 0:
        return Fraction(1)
    k = max(b, c)
    return min(Fraction(1), Fraction(2 * sum(comb(n, j) for j in range(k, n + 1)), 2 ** n))


# ------------------------------------------------------------------- M1 / M2
def check_martingale(fn, n_max=40):
    """H0 のもとで 0.5*E(b+1,c) + 0.5*E(b,c+1) == E(b,c) を厳密有理数で検査する。"""
    bad = []
    for n in range(n_max + 1):
        for b in range(n + 1):
            c = n - b
            if Fraction(1, 2) * fn(b + 1, c) + Fraction(1, 2) * fn(b, c + 1) != fn(b, c):
                bad.append((b, c))
    return bad, (n_max + 1) * (n_max + 2) // 2


def mixture_numeric(b, c, lo, hi, dens, steps=200000):
    """定義そのものを台形則で数値積分する（閉形式を使わない）。"""
    n = b + c
    h = (hi - lo) / steps
    s = 0.0
    for i in range(steps + 1):
        p = lo + i * h
        s += (0.5 if i in (0, steps) else 1.0) * (p ** b) * ((1 - p) ** c)
    return (2 ** n) * dens * s * h


# ------------------------------------------------------------------- M3
def thresholds(n_max):
    """各 n における棄却閾値。シミュレーションを閾値比較に落として高速化する。"""
    t_fixed, t_e = [], []
    for n in range(n_max + 1):
        k = n + 1
        for j in range((n + 1) // 2, n + 1):
            if mcnemar_exact_two_sided(j, n - j) <= ALPHA:
                k = j
                break
        t_fixed.append(k)
        k = n + 1
        for b in range(n + 1):
            if e_one_sided(b, n - b) >= 1 / ALPHA:
                k = b
                break
        t_e.append(k)
    return t_fixed, t_e


def benchmark(p, n_max, seeds, trials):
    """A: 固定n・のぞき見なし / B: 固定n・のぞき見 / C: e-value・のぞき見。
    いずれも改善方向の棄却のみを数える（3 手続きを同一の向きで比較するため）。"""
    t_fixed, t_e = thresholds(n_max)
    out = {"A": [], "B": [], "C": []}
    for s in seeds:
        rng = random.Random(s)
        a = b_ = c_ = 0
        for _ in range(trials):
            b = 0
            hit_fixed = None
            hit_e = False
            for n in range(1, n_max + 1):
                if rng.random() < p:
                    b += 1
                c = n - b
                if hit_fixed is None and (b >= t_fixed[n] or c >= t_fixed[n]):
                    hit_fixed = b > c
                if not hit_e and b >= t_e[n]:
                    hit_e = True
            c = n_max - b
            if (b >= t_fixed[n_max] or c >= t_fixed[n_max]) and b > c:
                a += 1
            if hit_fixed:
                b_ += 1
            if hit_e:
                c_ += 1
        out["A"].append(a / trials)
        out["B"].append(b_ / trials)
        out["C"].append(c_ / trials)
    return {k: (sum(v) / len(v), min(v), max(v)) for k, v in out.items()}


# ------------------------------------------------------------------- CLI
def main(argv=None):
    ap = argparse.ArgumentParser(description="anytime-valid 検定の外部主張を監査する")
    ap.add_argument("--martingale", action="store_true")
    ap.add_argument("--benchmark", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args(argv)
    if not (a.martingale or a.benchmark or a.selftest):
        a.selftest = True

    rc = 0
    if a.martingale or a.selftest:
        print("== M1 test martingale 性（Ville 適用の前提）==")
        for name, fn in (("two_sided", e_two_sided), ("one_sided", e_one_sided)):
            bad, total = check_martingale(fn, 40 if not a.selftest else 25)
            ok = not bad and fn(0, 0) == 1
            rc |= 0 if ok else 1
            print("  [%s] %-10s %d 点を厳密有理数で検査、不一致 %d、E_0=%s"
                  % ("PASS" if ok else "FAIL", name, total, len(bad), fn(0, 0)))

        print("== M2 閉形式と混合 e-value の定義の一致 ==")
        for bb, cc in ((3, 1), (7, 0), (5, 5), (9, 2)):
            n2 = mixture_numeric(bb, cc, 0.0, 1.0, 1.0)
            n1 = mixture_numeric(bb, cc, 0.5, 1.0, 2.0)
            d2 = abs(float(e_two_sided(bb, cc)) - n2)
            d1 = abs(float(e_one_sided(bb, cc)) - n1)
            ok = d2 < 1e-6 and d1 < 1e-6
            rc |= 0 if ok else 1
            print("  [%s] b=%d c=%d  two 差=%.2e  one 差=%.2e"
                  % ("PASS" if ok else "FAIL", bb, cc, d2, d1))

    if a.benchmark or a.selftest:
        print("== M3 のぞき見下の第一種過誤（H0: p=1/2, α=1/20）==")
        cells = ([(0.5, 30, 2000)] if a.benchmark else [(0.5, 30, 500)])
        if a.benchmark:
            cells += [(0.5, 200, 2000), (0.6, 200, 2000)]
        seeds = [20260917 + i for i in range(10 if a.benchmark else 3)]
        for p, n_max, trials in cells:
            r = benchmark(p, n_max, seeds, trials)
            print("  p=%.1f n_max=%-3d A=%.4f  B=%.4f  C=%.4f" %
                  (p, n_max, r["A"][0], r["B"][0], r["C"][0]))
            if p == 0.5:
                ok_b = r["B"][0] > float(ALPHA)
                ok_c = r["C"][0] <= float(ALPHA)
                rc |= 0 if (ok_b and ok_c) else 1
                print("     [%s] B（固定n+のぞき見）が α を超える" % ("PASS" if ok_b else "FAIL"))
                print("     [%s] C（e-value+のぞき見）が α 以下" % ("PASS" if ok_c else "FAIL"))

    print("RESULT: %s" % ("PASS" if rc == 0 else "FAIL"))
    return rc


if __name__ == "__main__":
    sys.exit(main())
