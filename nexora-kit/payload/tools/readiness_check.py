#!/usr/bin/env python3
"""STANDING-ORDER-001 の発動条件を機械判定する。

「準備が整い次第」を述語に変換する。曖昧なままでは、着手すべき時点も
着手してはならない時点も決まらない。

AUTO  行: 本スクリプトが実測で判定する。
HUMAN 行: 人間しか報告できない。`control/readiness.csv` の status 列を
          人間が PENDING 以外に書き換えるまで未達として扱う。**推測で埋めない。**

  python3 tools/readiness_check.py          # 判定
  python3 tools/readiness_check.py --json   # 機械可読
"""
import argparse
import csv
import json
import os
import subprocess
import sys

ROOT = os.path.realpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
CSV = os.path.join(ROOT, "control", "readiness.csv")
SCOPES = {
    "W1": "本キット（nexora-core）",
    "W2": "VEA-G3",
    "W3": "LoopCell Phase 0",
}


def auto_check(cid):
    """AUTO 行の実測。判定不能は未達として扱う（fail-closed）。"""
    if cid == "R-01":
        # 対象リポジトリの **ルート** に配置されているか。
        # `nexora-kit/payload/` に置かれたままの staging 状態を READY と誤認しない
        # （偽陽性は恒常命令を早発させる）。
        files_ok = all(os.path.exists(os.path.join(ROOT, p))
                       for p in ("CLAUDE.md", ".claude/hooks/guard.py", "control/STATE.md"))
        staging = os.path.basename(os.path.dirname(ROOT)) == "nexora-kit"
        if staging:
            return False, "staging（nexora-kit/payload/）。install.py で対象リポジトリのルートへ配置すること"
        return files_ok, "ルート配置 %s" % ("あり" if files_ok else "なし")
    if cid == "R-02":
        r = subprocess.run([sys.executable, os.path.join(ROOT, "tools", "manifest.py"), "verify"],
                           capture_output=True, text=True)
        line = (r.stdout or r.stderr).strip().splitlines()
        return r.returncode == 0, line[0] if line else "出力なし"
    if cid == "R-03":
        p = os.path.join(ROOT, "control", "disposition.csv")
        if not os.path.exists(p):
            return False, "disposition.csv なし"
        with open(p, encoding="utf-8", newline="") as f:
            n = len(list(csv.DictReader(f)))
        return n > 0, "%d 行" % n
    return False, "未知の AUTO 条件（fail-closed）"


def main(argv=None):
    ap = argparse.ArgumentParser(description="STANDING-ORDER-001 発動条件の判定")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args(argv)

    with open(CSV, encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))

    result = {}
    for r in rows:
        cid, kind = r["id"], (r["check_type"] or "").strip().upper()
        if kind == "AUTO":
            ok, detail = auto_check(cid)
        else:
            st = (r["status"] or "").strip().upper()
            ok = st not in ("", "PENDING")
            detail = "status=%s" % (st or "PENDING")
        r["_ok"], r["_detail"] = ok, detail
        result.setdefault(r["scope"], []).append(r)

    ready = {}
    print("STANDING-ORDER-001 READINESS")
    for scope in sorted(result):
        rs = result[scope]
        ok_all = all(x["_ok"] for x in rs)
        ready[scope] = ok_all
        print("\n[%s] %s — %s" % (scope, SCOPES.get(scope, scope),
                                  "READY" if ok_all else "NOT_READY"))
        for x in rs:
            print("   [%s] %-5s %-6s %s  (%s)" % ("OK " if x["_ok"] else "   ",
                                                  x["id"], x["check_type"],
                                                  x["condition"], x["_detail"]))
        if not ok_all:
            blockers = [x["id"] for x in rs if not x["_ok"]]
            print("   → 未達 %d 件: %s" % (len(blockers), ", ".join(blockers)))

    print("\nRESULT: %s" % (", ".join("%s=%s" % (k, "READY" if v else "NOT_READY")
                                      for k, v in sorted(ready.items()))))
    if not any(ready.values()):
        print("着手条件を満たすワークストリームは無い。待機は設計どおりである。")
    if a.json:
        print(json.dumps({"ready": ready,
                          "conditions": [{k: v for k, v in r.items() if not k.startswith("_")}
                                         | {"ok": r["_ok"], "detail": r["_detail"]} for r in rows]},
                         ensure_ascii=False, indent=2))
    return 0 if all(ready.values()) else 1


if __name__ == "__main__":
    sys.exit(main())
