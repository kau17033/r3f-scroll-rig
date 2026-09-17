#!/usr/bin/env python3
"""NEXORA SessionStart hook.

標準出力はセッション文脈に追加される。ここでは「実装を開始してよいか」を
毎回機械的に判定して先頭に出す。SOURCES_INTEGRITY が PASS 以外なら、
CLAUDE.md §0 により変更は禁止される。
"""
import csv
import hashlib
import os
import re
import sys

ROOT = os.environ.get("CLAUDE_PROJECT_DIR") or os.getcwd()
out = []


def read_text(path):
    with open(path, encoding="utf-8") as f:
        return f.read()


# 1) 正本の完全性
manifest = os.path.join(ROOT, "sources", "MANIFEST.sha256")
try:
    bad, total = [], 0
    for line in read_text(manifest).splitlines():
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        h, _, p = line.partition(" ")
        p = p.strip().lstrip("*")
        total += 1
        try:
            with open(os.path.join(ROOT, p), "rb") as fh:
                dg = hashlib.sha256(fh.read()).hexdigest()
        except OSError:
            dg = "MISSING"
        if dg != h.strip():
            bad.append(p)
    if total == 0:
        out.append("SOURCES_INTEGRITY: NOT_IDENTIFIABLE (MANIFEST.sha256 が空)")
    else:
        out.append("SOURCES_INTEGRITY: " + ("PASS (%d files)" % total if not bad
                                            else "FAIL " + ", ".join(bad)))
except OSError:
    out.append("SOURCES_INTEGRITY: NOT_IDENTIFIABLE (MANIFEST.sha256 missing) "
               "— 原文未投入。T-000 と T-010 のみ実行可。")

# 1b) 外部保持の正本（複製せず blob SHA で固定しているもの）
ext = os.path.join(ROOT, "sources", "EXTERNAL.csv")
if os.path.exists(ext):
    try:
        import subprocess
        r = subprocess.run([sys.executable, os.path.join(ROOT, "tools", "external_sources.py"),
                            "verify"], capture_output=True, text=True, timeout=25)
        out.append((r.stdout or r.stderr).strip().splitlines()[0])
    except Exception as e:
        out.append("EXTERNAL_SOURCES: NOT_IDENTIFIABLE (%r)" % (e,))

# 2) 現在状態
st = os.path.join(ROOT, "control", "STATE.md")
if os.path.exists(st):
    out.append("STATE(head):\n" + "".join(read_text(st).splitlines(True)[:25]).rstrip())
else:
    out.append("STATE: MISSING (control/STATE.md 未作成)")

# 3) 人間判断待ち
dc = os.path.join(ROOT, "control", "decisions.md")
if os.path.exists(dc):
    body = read_text(dc)
    pend = re.findall(r"^\|\s*(DEC-\d{3})\s*\|[^\n]*?\|\s*PENDING\s*\|", body, re.M)
    pend += re.findall(r"^-\s*(DEC-\d{3})\b[^\n]*Status:\s*PENDING", body, re.M)
    out.append("PENDING_DECISIONS: %d %s" % (len(pend), sorted(set(pend))))

# 4) 全節処置の進捗
dp = os.path.join(ROOT, "control", "disposition.csv")
if os.path.exists(dp):
    try:
        with open(dp, encoding="utf-8", newline="") as f:
            rows = list(csv.DictReader(f))
        pending = sum(1 for r in rows if (r.get("disposition") or "").strip().upper() == "PENDING")
        out.append("DISPOSITION: %d rows, PENDING=%d (実装解禁条件: PENDING=0)" % (len(rows), pending))
    except Exception as e:
        out.append("DISPOSITION: NOT_IDENTIFIABLE (%r)" % (e,))

out.append("RULE_REF: CLAUDE.md §0 — SOURCES_INTEGRITY が PASS 以外の場合は変更禁止。"
           " §3 の順序を越えない。§6 の人間判断事項は自律実行しない。")

sys.stdout.write("\n".join(out) + "\n")
sys.exit(0)
