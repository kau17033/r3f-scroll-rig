#!/usr/bin/env python3
"""外部リポジトリが保持する正本を、複製せずに固定する。

SRC-02（VEA-G3）と SRC-04（LoopCell）は、それぞれ自前の凍結機構
（`PROTOCOL_LOCK.md` / `FREEZE_MANIFEST.json`）を持つリポジトリに既に存在する。
本キットへ複製すると SSOT が 2 つに分岐し、キットの目的と正面から矛盾する。

代わりに **git blob SHA** で参照を固定する。blob SHA は内容アドレスであるため、
1 バイトでも変われば一致しなくなる。複製せずに不変性を検証できる。

  python3 tools/external_sources.py list
  python3 tools/external_sources.py verify        # GitHub API で現在値と照合

private リポジトリの照合には `GITHUB_TOKEN` が要る。無い場合の判定は
**NOT_IDENTIFIABLE**（FAIL ではない）。取得できないことと改変されたことは別事象である。
"""
import argparse
import csv
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request

ROOT = os.path.realpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
REGISTRY = os.path.join(ROOT, "sources", "EXTERNAL.csv")
API = "https://api.github.com/repos/%s/contents/%s"


def load():
    with open(REGISTRY, encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def fetch_sha(repo, path, token, timeout=20):
    """現在の blob SHA を返す。(sha, err) の組。"""
    req = urllib.request.Request(API % (repo, urllib.parse.quote(path)))
    req.add_header("Accept", "application/vnd.github+json")
    req.add_header("User-Agent", "nexora-external-sources")
    if token:
        req.add_header("Authorization", "Bearer %s" % token)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return json.loads(r.read().decode("utf-8")).get("sha"), None
    except urllib.error.HTTPError as e:
        return None, "HTTP %s" % e.code
    except Exception as e:  # ネットワーク不通・DNS・TLS
        return None, type(e).__name__


def cmd_list(_a):
    rows = load()
    by = {}
    for r in rows:
        by.setdefault(r["src_id"], []).append(r)
    print("EXTERNAL SOURCES — %d 件 / %d SRC" % (len(rows), len(by)))
    for sid in sorted(by):
        print("\n[%s] %s" % (sid, by[sid][0]["repo"]))
        for r in sorted(by[sid], key=lambda x: x["path"]):
            print("  %-8s %-12s %s  %s" % (r["blob_sha"][:8], r["role"], r["path"], r["observed_at"]))
    return 0


def cmd_verify(a):
    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    rows = load()
    match = mismatch = unknown = 0
    bad, unk = [], []
    for r in rows:
        sha, err = fetch_sha(r["repo"], r["path"], token)
        if err or not sha:
            unknown += 1
            unk.append("%s:%s (%s)" % (r["repo"], r["path"], err or "no sha"))
            continue
        if sha == r["blob_sha"]:
            match += 1
        else:
            mismatch += 1
            bad.append("%s:%s  registered=%s current=%s" % (r["repo"], r["path"],
                                                            r["blob_sha"][:12], sha[:12]))
    if mismatch:
        state = "FAIL"
    elif unknown == len(rows):
        state = "NOT_IDENTIFIABLE"
    elif unknown:
        state = "PARTIAL"
    else:
        state = "PASS"
    print("EXTERNAL_SOURCES: %s (match=%d mismatch=%d unknown=%d / %d)"
          % (state, match, mismatch, unknown, len(rows)))
    for b in bad:
        print("  CHANGED  %s" % b)
    if unknown and a.verbose:
        for u in unk[:10]:
            print("  UNKNOWN  %s" % u)
    if state == "NOT_IDENTIFIABLE":
        print("  → GITHUB_TOKEN 未設定か、private リポジトリへ到達できない。"
              "取得不能であって改変ではない。")
    # ゲート用途では PASS のみを 0 とする。PARTIAL は「検証が不完全」であり合格ではない。
    return {"PASS": 0, "PARTIAL": 3, "NOT_IDENTIFIABLE": 2, "FAIL": 1}[state]


def main(argv=None):
    ap = argparse.ArgumentParser(description="外部保持の正本を blob SHA で固定・照合する")
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("list").set_defaults(fn=cmd_list)
    v = sub.add_parser("verify")
    v.add_argument("--verbose", action="store_true")
    v.set_defaults(fn=cmd_verify)
    a = ap.parse_args(argv)
    return a.fn(a)


if __name__ == "__main__":
    try:
        sys.exit(main())
    except BrokenPipeError:  # `| head` 等でのパイプ切断は異常ではない
        try:
            sys.stdout.close()
        finally:
            os._exit(0)
