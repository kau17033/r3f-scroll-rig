#!/usr/bin/env python3
"""guard.py の期待挙動を 1 か所に固定する。

tools/kit_check.py（T-000）と tests/test_guard.py の双方がこれを読む。
期待値を 2 か所に書かない（不一致は検証の無効化に直結する）。
"""

# (id, expect_exit, tool_name, tool_input)
CASES = [
    # --- ブロックされなければならない (exit 2) ---
    ("imm-edit-source",      2, "Edit",  {"file_path": "sources/SRC-01.md"}),
    ("imm-edit-claudemd",    2, "Edit",  {"file_path": "CLAUDE.md"}),
    ("imm-edit-settings",    2, "Edit",  {"file_path": ".claude/settings.json"}),
    ("imm-write-authority",  2, "Write", {"file_path": "control/AUTHORITY.md"}),
    ("imm-edit-abs",         2, "Edit",  {"file_path": "{ROOT}/sources/SRC-02.md"}),
    ("app-edit-existing",    2, "Edit",  {"file_path": "evidence/existing.md"}),
    ("app-write-existing",   2, "Write", {"file_path": "evidence/existing.md"}),
    ("outside-write",        2, "Write", {"file_path": "/etc/nexora-test"}),
    ("bash-force-push",      2, "Bash",  {"command": "git -C . push --force origin main"}),
    ("bash-force-push-f",    2, "Bash",  {"command": "git push -f"}),
    ("bash-nested-rm",       2, "Bash",  {"command": "bash -c 'rm -rf x'"}),
    ("bash-rm-recursive",    2, "Bash",  {"command": "rm -rf evidence"}),
    ("bash-redirect-imm",    2, "Bash",  {"command": "echo x > sources/SRC-01.md"}),
    ("bash-append-imm",      2, "Bash",  {"command": "echo x >> CLAUDE.md"}),
    ("bash-overwrite-app",   2, "Bash",  {"command": "echo x > evidence/existing.md"}),
    ("bash-sed-inplace",     2, "Bash",  {"command": "sed -i 's/a/b/' CLAUDE.md"}),
    ("bash-python-inline",   2, "Bash",  {"command": "python3 -c \"open('sources/SRC-01.md','w').write('')\""}),
    ("bash-reset-hard",      2, "Bash",  {"command": "git reset --hard HEAD~1"}),
    ("bash-mv-evidence",     2, "Bash",  {"command": "mv evidence/existing.md /tmp/"}),
    ("bash-find-delete",     2, "Bash",  {"command": "find . -name '*.md' -delete"}),
    ("bash-env-prefix-rm",   2, "Bash",  {"command": "FOO=1 sudo rm -rf /"}),
    ("bash-chained",         2, "Bash",  {"command": "git status && echo x > CLAUDE.md"}),
    ("bash-tee-imm",         2, "Bash",  {"command": "echo x | tee sources/SRC-01.md"}),
    ("bash-git-restore-app", 2, "Bash",  {"command": "git checkout -- evidence/existing.md"}),
    ("no-path",              2, "Edit",  {}),

    # --- 通らなければならない (exit 0) ---
    ("app-write-new",        0, "Write", {"file_path": "evidence/new-record.md"}),
    ("control-edit",         0, "Edit",  {"file_path": "control/STATE.md"}),
    ("tasks-write",          0, "Write", {"file_path": "tasks/T-000-kit-selfcheck.md"}),
    ("bash-status",          0, "Bash",  {"command": "git status"}),
    ("bash-echo",            0, "Bash",  {"command": "echo hello"}),
    ("bash-pytest-like",     0, "Bash",  {"command": "python3 -m unittest discover -s tests"}),
    ("bash-push-plain",      0, "Bash",  {"command": "git push -u origin work"}),
    ("bash-read-source",     0, "Bash",  {"command": "sed -n '1,40p' sources/SRC-01.md"}),
    ("tmp-write",            0, "Write", {"file_path": "/tmp/nexora-scratch.txt"}),
    ("read-tool-passthru",   0, "Read",  {"file_path": "sources/SRC-01.md"}),
]
