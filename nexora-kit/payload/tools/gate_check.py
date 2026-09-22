#!/usr/bin/env python3
"""実装解禁ゲート。「完遂」宣言の断定条件を機械判定する。

条件（いずれか 1 つでも満たさなければ BLOCKED）:
  G1 SOURCES_INTEGRITY = PASS
  G2 control/disposition.csv が 1 行以上あり、PENDING = 0
  G3 control/decisions.md の PENDING = 0
  G4 control/traceability.csv の全要求に task_ids / test_ids / evidence_paths が埋まっている
  G5 control/audit70.csv の 11 項目がすべて 0
  G6 外部保持の正本について、最新の durable live-validation record が EXTERNAL.csv と完全一致

exit 0 = 解禁、exit 1 = BLOCKED。判定は本スクリプトのみが行う。会話で上書きしない。
"""
import csv
import os
import re
import subprocess
import sys

ROOT = os.path.realpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))


def _rows(rel):
    p = os.path.join(ROOT, rel)
    if not os.path.exists(p):
        return None
    with open(p, encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def g1():
    # Converged control plane: source bodies may remain in their canonical stores.
    # Use registry/content-address validation when installed; retain manifest.py as
    # a backward-compatible fallback for isolated legacy fixtures.
    check = os.path.join(ROOT, "tools", "source_registry_check.py")
    if os.path.exists(check) and os.path.exists(os.path.join(ROOT, "control", "source_registry.csv")):
        r = subprocess.run([sys.executable, check], capture_output=True, text=True)
    else:
        r = subprocess.run([sys.executable, os.path.join(ROOT, "tools", "manifest.py"), "verify"],
                           capture_output=True, text=True)
    head = (r.stdout or r.stderr).strip().splitlines()
    return (r.returncode == 0, head[0] if head else "出力なし")


def g2():
    check = os.path.join(ROOT, "tools", "disposition_check.py")
    if os.path.exists(check) and os.path.isdir(os.path.join(ROOT, "control", "corpus_sections")):
        r = subprocess.run([sys.executable, check], capture_output=True, text=True)
        head = (r.stdout or r.stderr).strip().splitlines()
        return (r.returncode == 0, head[0] if head else "出力なし")
    rows = _rows("control/disposition.csv")
    if rows is None:
        return False, "disposition.csv が無い"
    if not rows:
        return False, "disposition.csv が 0 行（全節索引が未実行）"
    pend = [r["section_id"] for r in rows if (r.get("disposition") or "").strip().upper() == "PENDING"]
    return (not pend), "%d rows, PENDING=%d" % (len(rows), len(pend))


def g3():
    p = os.path.join(ROOT, "control", "decisions.md")
    if not os.path.exists(p):
        return False, "decisions.md が無い"
    body = open(p, encoding="utf-8").read()
    pend = sorted(set(re.findall(r"^\|\s*(DEC-\d{3})\s*\|[^\n]*?\|\s*PENDING\s*\|", body, re.M)))
    return (not pend), "PENDING=%d %s" % (len(pend), pend)


def g4():
    rows = _rows("control/traceability.csv")
    if rows is None:
        return False, "traceability.csv が無い"
    if not rows:
        return False, "traceability.csv が 0 行（要求正規化 T-040 が未実行）"
    holes = [r.get("req_id") for r in rows
             if not all((r.get(k) or "").strip() for k in ("task_ids", "test_ids", "evidence_paths"))]
    return (not holes), "%d rows, 未追跡 %d %s" % (len(rows), len(holes), holes[:5])


def g5():
    rows = _rows("control/audit70.csv")
    if rows is None:
        return False, "audit70.csv が無い（SRC-01 AUDIT§70 未投入 → NOT_IDENTIFIABLE）"
    if len(rows) != 11:
        return False, "行数が 11 でない: %d" % len(rows)
    nz = [r.get("item_id") for r in rows if (r.get("count") or "").strip() not in ("0",)]
    return (not nz), "非ゼロ %d %s" % (len(nz), nz)


def g6():
    """Verify durable cross-repo validation evidence without depending on CI token reachability."""
    check = os.path.join(ROOT, "tools", "source_registry_check.py")
    r = subprocess.run([sys.executable, check], capture_output=True, text=True)
    head = (r.stdout or r.stderr).strip().splitlines()
    return r.returncode == 0, head[0] if head else "出力なし"

CHECKS = [("G1 sources integrity", g1), ("G2 disposition PENDING=0", g2),
          ("G3 decisions PENDING=0", g3), ("G4 traceability 完備", g4),
          ("G5 AUDIT§70 = 0", g5), ("G6 外部正本の一致", g6)]


def main():
    ok_all = True
    print("NEXORA IMPLEMENTATION GATE")
    for name, fn in CHECKS:
        try:
            ok, detail = fn()
        except Exception as e:  # 判定不能は解禁しない
            ok, detail = False, "判定不能: %r" % (e,)
        ok_all &= ok
        print("  [%s] %-26s %s" % ("PASS" if ok else "BLOCK", name, detail))
    print("RESULT: %s" % ("UNLOCKED" if ok_all else "BLOCKED — 実装を開始しない"))
    return 0 if ok_all else 1


if __name__ == "__main__":
    sys.exit(main())
