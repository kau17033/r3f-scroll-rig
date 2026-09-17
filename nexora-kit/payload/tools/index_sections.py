#!/usr/bin/env python3
"""NEXORA 索引器 — 原文を節単位に索引化する。

設計上の制約（過去の欠陥に対する対策）:
- 見出し判定は **緩く** する。番号を取得できたら、その後ろに何が続いても見出しとする。
  （初回索引で SOV§650–653 が欠落した原因は、見出しに「→」を含む行を
    検出器が弾いたことにある。番号以降の書式を条件にしてはならない。）
- 抽出テキストには数式変換の残骸（`# [`, `# ERS` 等）が見出しとして残る。
  除去せず `suspect` として印を付け、人間が判断する。除去は情報の破壊である。
- 欠番は「欠落」ではなく「検出器の欠陥の可能性」として報告する。

使用法:
  python3 tools/index_sections.py sources/SRC-01.md --source-id SRC-01 \
      --out control/section_index.csv --disposition control/disposition.csv
  python3 tools/index_sections.py sources/SRC-01.md --source-id SRC-01 --report
"""
import argparse
import csv
import os
import re
import sys

# 1) markdown 見出し
RE_MD = re.compile(r"^(#{1,6})\s+(?P<title>.*\S)\s*$")
# 2) 明示的な節記号つき（CONV§12, SOV§650 → ... など。後続書式を問わない）
RE_MARKED = re.compile(r"^\s*(?P<mark>[A-Z]{2,6})?§\s*(?P<num>\d+(?:\.\d+)*)\s*(?P<title>.*)$")
# 3) 先頭番号のみ（"12. 見出し" / "12 見出し" / "12.3.4 見出し"）
RE_NUM = re.compile(r"^\s*(?P<num>\d+(?:\.\d+)*)\s*[.．、)\］\]]?\s+(?P<title>\S.*)$")
# 4) 和文の章節
RE_JP = re.compile(r"^\s*第\s*(?P<num>\d+)\s*[章節条]\s*(?P<title>.*)$")

# 数式変換残骸の疑い
RE_SUSPECT = re.compile(r"^#+\s*(\[|\]|ERS\b|\\|\$)|^\s*\$\$")


def classify(line):
    """見出しなら (num, title, kind) を返す。番号が取れなければ num は None。"""
    m = RE_MARKED.match(line)
    if m:
        return m.group("num"), (m.group("mark") or "") + "§" + m.group("num") + " " + m.group("title").strip(), "marked"
    m = RE_MD.match(line)
    if m:
        inner = classify_inner(m.group("title"))
        return inner[0], m.group("title").strip(), "md"
    m = RE_JP.match(line)
    if m:
        return m.group("num"), line.strip(), "jp"
    m = RE_NUM.match(line)
    if m:
        return m.group("num"), line.strip(), "num"
    return None


def classify_inner(title):
    m = RE_MARKED.match(title) or RE_NUM.match(title) or RE_JP.match(title)
    return (m.group("num"), title) if m else (None, title)


def index_file(path, source_id):
    with open(path, encoding="utf-8") as f:
        lines = f.read().splitlines()
    heads = []
    for i, line in enumerate(lines, 1):
        got = classify(line)
        if not got:
            continue
        num, title, kind = got
        heads.append({
            "line": i,
            "num": num,
            "title": title,
            "kind": kind,
            "suspect": bool(RE_SUSPECT.match(line)),
        })
    # block 推定: 主番号が直前より減少したら新ブロック（発見的。人間が検証する）
    block, prev = 1, -1
    for h in heads:
        major = int(h["num"].split(".")[0]) if h["num"] and h["num"].split(".")[0].isdigit() else None
        if major is not None:
            if prev >= 0 and major < prev:
                block += 1
            prev = major
        h["block"] = "B%d" % block
    # 範囲
    rows = []
    for idx, h in enumerate(heads):
        end = (heads[idx + 1]["line"] - 1) if idx + 1 < len(heads) else len(lines)
        chars = sum(len(l) for l in lines[h["line"] - 1:end])
        sid = "%s:%s§%s" % (source_id, h["block"], h["num"]) if h["num"] else "%s:%s@L%d" % (source_id, h["block"], h["line"])
        rows.append({
            "section_id": sid,
            "source_id": source_id,
            "heading": h["title"],
            "line_start": h["line"],
            "line_end": end,
            "block": h["block"],
            "char_count": chars,
            "kind": h["kind"],
            "suspect": h["suspect"],
        })
    return rows, len(lines)


def gaps(rows):
    """ブロックごとに主番号の欠番を返す。欠落ではなく検出器の欠陥の可能性として扱う。"""
    per = {}
    for r in rows:
        num = r["section_id"].rsplit("§", 1)[-1]
        if "@L" in r["section_id"] or not num.split(".")[0].isdigit():
            continue
        per.setdefault(r["block"], set()).add(int(num.split(".")[0]))
    out = {}
    for b, s in per.items():
        if not s:
            continue
        missing = sorted(set(range(min(s), max(s) + 1)) - s)
        if missing:
            out[b] = missing
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(description="NEXORA section indexer")
    ap.add_argument("paths", nargs="+")
    ap.add_argument("--source-id", required=True)
    ap.add_argument("--out")
    ap.add_argument("--disposition")
    ap.add_argument("--report", action="store_true")
    a = ap.parse_args(argv)

    all_rows, total_lines = [], 0
    for p in a.paths:
        rows, n = index_file(p, a.source_id)
        all_rows += rows
        total_lines += n

    if a.out:
        with open(a.out, "w", encoding="utf-8", newline="") as f:
            w = csv.DictWriter(f, fieldnames=["section_id", "source_id", "heading",
                                              "line_start", "line_end", "block", "char_count"])
            w.writeheader()
            for r in all_rows:
                w.writerow({k: r[k] for k in w.fieldnames})
    if a.disposition:
        with open(a.disposition, "w", encoding="utf-8", newline="") as f:
            w = csv.writer(f)
            w.writerow(["section_id", "source_id", "disposition", "rationale",
                        "req_ids", "task_ids", "decided_by", "decided_at"])
            for r in all_rows:
                w.writerow([r["section_id"], r["source_id"], "PENDING", "", "", "", "", ""])

    g = gaps(all_rows)
    susp = [r["section_id"] for r in all_rows if r["suspect"]]
    print("sections: %d / lines: %d" % (len(all_rows), total_lines))
    print("blocks: %s" % sorted({r["block"] for r in all_rows}))
    print("suspect_headings: %d %s" % (len(susp), susp[:10]))
    if g:
        print("NUMBER_GAPS (検出器の欠陥の可能性。原文を人間が確認すること): %s" % g)
    else:
        print("NUMBER_GAPS: none")
    return 0


if __name__ == "__main__":
    sys.exit(main())
