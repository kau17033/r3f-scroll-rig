#!/usr/bin/env python3
"""NEXORA PreToolUse guard (fail-closed).

exit 0 = allow, exit 2 = block (Claude Code はこの終了コードのみをブロッキングとして扱う).
exit 1 は非ブロッキング扱いになるため、内部例外も exit 2 に統一する。

限界（既知・意図的に文書化する）:
- 完全なサンドボックスではない。難読化されたシェル、未知のインタプリタ、
  ネットワーク経由の書き込みは検出できない。
- 最終防衛線は sources/MANIFEST.sha256 の照合（SessionStart と CI）である。
- Windows の PowerShell ツールは対象外。
"""
import json
import os
import re
import sys

IMM_DIRS = ("sources/", ".claude/", ".git/")
IMM_FILES = ("CLAUDE.md", "control/AUTHORITY.md")
APP_DIRS = ("evidence/", "historical/", "protocol/")

IMM_RE = r"(\./)?(sources/|\.claude/|\.git/|CLAUDE\.md\b|control/AUTHORITY\.md\b)"
APP_RE = r"(\./)?(evidence|historical|protocol)/"
PROTECTED_RE = "(%s|%s)" % (IMM_RE, APP_RE)

INTERPRETERS = ("python", "python3", "node", "nodejs", "ruby", "perl", "php", "deno", "bun")
PREFIX_WORDS = ("sudo", "env", "command", "builtin", "nohup", "time", "timeout", "xargs", "exec")

RE_INLINE = re.compile(r"(?:^|\s)(?:--eval|-[a-zA-Z]{0,4}[ce])(?:\s|$)")


def block(msg):
    sys.stderr.write("[NEXORA-GUARD] BLOCKED: %s\n" % msg)
    sys.exit(2)


def check_path(tool, path, root):
    ap = os.path.realpath(path if os.path.isabs(path) else os.path.join(root, path))
    rp = os.path.relpath(ap, root).replace(os.sep, "/")
    if rp.startswith(".."):
        if not ap.startswith("/tmp/"):
            block("project 外への書込: %s" % ap)
        return
    if rp in IMM_FILES or rp.startswith(IMM_DIRS):
        block("不変パス: %s（control/decisions.md に起案）" % rp)
    if rp.startswith(APP_DIRS) and (tool != "Write" or os.path.exists(ap)):
        block("追記専用パス: %s（新規作成のみ。訂正は correction record）" % rp)


def check_bash(cmd, depth=0):
    if depth > 4:
        block("シェル入れ子が深すぎる（解析不能、fail-closed）")
    for seg in re.split(r"&&|\|\||;|\||\n", cmd):
        toks = seg.strip().split()
        while toks and ("=" in toks[0].split("/")[0]
                        or re.fullmatch(r"\d+[smhd]?", toks[0])
                        or toks[0] in PREFIX_WORDS):
            toks.pop(0)
        if not toks:
            continue
        s = " ".join(toks)
        head = os.path.basename(toks[0])

        if head in ("bash", "sh", "zsh", "dash", "ksh") and "-c" in toks:
            check_bash(s.split("-c", 1)[1].strip().strip("'\""), depth + 1)

        # インタプリタのインライン実行で保護パスに触れるものは一律ブロック
        # RE_INLINE は -c / -e / -ne / --eval のみを拾う。--verbose 等を誤検知しない。
        if head in INTERPRETERS and RE_INLINE.search(s) and re.search(PROTECTED_RE, s):
            block("インタプリタ経由の保護パス操作: %s" % s[:120])

        # リダイレクト
        if re.search(r">{1,2}\|?\s*['\"]?" + IMM_RE, s):
            block("不変パスへの出力: %s" % s[:120])
        if re.search(r"(^|[^>])>\|?\s*['\"]?" + APP_RE, s):
            block("追記専用パスの上書き: %s" % s[:120])

        if head == "git":
            if re.search(r"\bpush\b", s) and re.search(r"(\s--force(-with-lease)?\b|\s-f\b|\s\+\S)", s):
                block("force push（人間が実行）")
            if re.search(r"\breset\b.*--hard|\bclean\b.*\s-\w*f|\b(filter-branch|filter-repo)\b"
                         r"|\btag\s+-d\b|\bbranch\s+-D\b|\bupdate-ref\s+-d\b", s):
                block("履歴/証拠を失う git 操作: %s" % s[:120])
            if re.search(r"\b(checkout|restore|stash)\b", s) and re.search(APP_RE, s):
                block("追記専用パスに対する git 復元操作: %s" % s[:120])

        if head == "rm" and re.search(r"\s(-\w*[rR]\w*|--recursive)\b", s):
            block("再帰削除（人間が実行）: %s" % s[:120])
        if head == "find" and re.search(r"-delete\b|-exec\s+rm\b", s):
            block("find 経由の削除: %s" % s[:120])
        if head == "dd" and re.search(r"\bof=['\"]?" + PROTECTED_RE, s):
            block("dd による保護パス書込: %s" % s[:120])

        if head in ("rm", "mv", "truncate", "chmod", "chown", "ln", "unlink", "shred", "tee") \
                and re.search(r"(^|\s|['\"])" + IMM_RE, s):
            block("不変パスの変更: %s" % s[:120])
        if head in ("rm", "mv", "truncate", "unlink", "shred") and re.search(r"(^|\s|['\"])" + APP_RE, s):
            block("追記専用パスの削除/移動: %s" % s[:120])
        if head in ("sed", "perl") and re.search(r"\s-\w*i", s) and re.search(PROTECTED_RE, s):
            block("インプレース編集: %s" % s[:120])
        if head in ("cp", "rsync", "install") and re.match(IMM_RE, toks[-1]):
            block("不変パスへのコピー: %s" % s[:120])


def main():
    raw = sys.stdin.read()
    d = json.loads(raw) if raw.strip() else {}
    root = os.path.realpath(os.environ.get("CLAUDE_PROJECT_DIR") or d.get("cwd") or os.getcwd())
    tool = d.get("tool_name", "")
    ti = d.get("tool_input") or {}
    if tool in ("Edit", "Write", "MultiEdit", "NotebookEdit"):
        p = ti.get("file_path") or ti.get("notebook_path")
        if not p:
            block("対象パス不明")
        check_path(tool, p, root)
    elif tool == "Bash":
        check_bash(ti.get("command", ""))
    sys.exit(0)


try:
    main()
except SystemExit:
    raise
except Exception as e:  # exit 1 は非ブロッキングのため exit 2 に統一する
    block("guard 内部エラー（fail-closed）: %r" % (e,))
