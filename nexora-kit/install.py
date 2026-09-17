#!/usr/bin/env python3
"""NEXORA キットを対象リポジトリのルートへ配置する。

キットはリポジトリ **ルート** に置かれたときにだけ強制力を持つ。
Claude Code はルートの `CLAUDE.md` と `.claude/` しか読まないため、
`nexora-kit/payload/` に置いたままでは規約は一切効かない。

  python3 nexora-kit/install.py --target /path/to/repo --dry-run
  python3 nexora-kit/install.py --target /path/to/repo

既存ファイルは既定で上書きしない（--force で明示的に上書きする）。
"""
import argparse
import os
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PAYLOAD = os.path.join(HERE, "payload")
EXECUTABLE = (".claude/hooks/guard.py", ".claude/hooks/session_start.py")


def walk_payload():
    for dirpath, dirnames, filenames in os.walk(PAYLOAD):
        dirnames[:] = sorted(d for d in dirnames if d != "__pycache__")
        for name in sorted(filenames):
            if name.endswith(".pyc"):
                continue
            ap = os.path.join(dirpath, name)
            yield os.path.relpath(ap, PAYLOAD).replace(os.sep, "/"), ap


def main(argv=None):
    ap = argparse.ArgumentParser(description="NEXORA kit installer")
    ap.add_argument("--target", required=True, help="対象リポジトリのルート")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--force", action="store_true", help="既存ファイルを上書きする")
    a = ap.parse_args(argv)

    target = os.path.realpath(a.target)
    if not a.dry_run and not os.path.isdir(target):
        os.makedirs(target, exist_ok=True)

    files = list(walk_payload())
    if not files:
        print("FAIL: payload/ が空である")
        return 1

    clashes = [rel for rel, _ in files if os.path.exists(os.path.join(target, rel))]
    if clashes and not a.force and not a.dry_run:
        print("FAIL: 既存ファイルがある。内容を確認してから --force を付けること。")
        for rel in clashes:
            print("  既存: %s" % rel)
        return 1

    for rel, src in files:
        dst = os.path.join(target, rel)
        mark = "SKIP(既存)" if rel in clashes and not a.force else "COPY"
        if a.dry_run:
            print("%-11s %s" % (mark, rel))
            continue
        if rel in clashes and not a.force:
            continue
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        shutil.copy2(src, dst)
        if rel in EXECUTABLE:
            os.chmod(dst, 0o755)
        print("%-11s %s" % (mark, rel))

    print("\n%d files -> %s%s" % (len(files), target, "（dry-run。書き込みなし）" if a.dry_run else ""))
    if a.dry_run:
        return 0

    print("""
次の手順（順に実行する）:
  1) cd %s
  2) python3 tools/kit_check.py --evidence        # T-000。exit 0 を確認する
  3) sources/README.md に従い原文 SRC-01..07 を投入する（人間が実行）
  4) python3 tools/manifest.py build && chmod a-w sources/SRC-*
  5) python3 tools/manifest.py verify             # PASS を確認する
  6) git add -A && git commit && git push
  7) Claude Code で開き、/hooks と /context でフックと CLAUDE.md の読込を確認する
  8) 実際に sources/ への Edit を試み、ブロックされることを確認する
     ※ ブロックされない場合、キットは無効である。フックのパスと終了コードを疑う。
""" % target)
    return 0


if __name__ == "__main__":
    sys.exit(main())
