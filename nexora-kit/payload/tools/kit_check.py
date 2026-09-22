#!/usr/bin/env python3
"""T-000 キット自己検証。

「ゲートが黙って無効化されていないこと」を毎回、実測で確認する。
フックのパス誤り・終了コードの取り違え・権限規則の欠落は、いずれも
静かにゲートを外すため、宣言ではなく実行結果で確かめる。

  python3 tools/kit_check.py               # 検証のみ
  python3 tools/kit_check.py --evidence    # evidence/T-000/<UTC>.md に実測を保存
"""
import argparse
import datetime
import json
import os
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.realpath(os.path.join(HERE, ".."))
sys.path.insert(0, HERE)
from guard_fixtures import CASES  # noqa: E402

GUARD = os.path.join(ROOT, ".claude", "hooks", "guard.py")
SESSION_START = os.path.join(ROOT, ".claude", "hooks", "session_start.py")
SETTINGS = os.path.join(ROOT, ".claude", "settings.json")

REQUIRED = [
    "CLAUDE.md", ".claude/settings.json", ".claude/hooks/guard.py",
    ".claude/hooks/session_start.py", "control/AUTHORITY.md", "control/STATE.md",
    "control/conflicts.md", "control/decisions.md", "control/open_questions.md",
    "control/deviations.md", "control/glossary.md", "control/disposition.csv",
    "control/requirements.csv", "control/traceability.csv", "control/section_index.csv",
    "sources/README.md", "tasks/INDEX.md",
    "tools/manifest.py", "tools/index_sections.py", "tools/seed_derive.py",
    "tools/gate_check.py", "tools/kit_check.py", "tools/guard_fixtures.py",
    "tests/golden/seed_vectors.json", "tests/test_pipeline_e2e.py",
    "tools/verify_evalue.py", "control/EXTERNAL-001-evidence-kernel.md",
    "control/REPO-001-vea-g3.md", "control/REPO-002-protocol-lock.md", "control/REPO-003-loopcell.md", "control/REPO-004-gate-status.md",
    "control/REPO-005-source-selection-root-cause.md",
    "control/INDEX-cross-repo.md", "control/REPO-006-r5-640-result.md", "control/REPO-007-loopcell-gaps.md",
    "control/PROPOSAL-001-compliance-manifest.md",
    "control/STANDING-ORDER-001.md", "control/readiness.csv", "tools/readiness_check.py",
    "control/human_gates.csv", "tools/human_gate_check.py",
    "sources/EXTERNAL.csv", "tools/external_sources.py",
    "tools/requirements_check.py",
    "control/CONVERGED-SSOT.md", "control/source_registry.csv",
    "control/state_events.csv", "control/completion_gates.csv", "control/transitions.csv",
    "control/STATE.generated.json", "control/capability_contract.schema.json",
    "control/DREAM-RSI-ADAPTER.md", "control/replay_worlds/bootstrap_convergence_20260922.json",
    "control/EXTERNAL-VALIDATION-20260922.json",
    "tools/state_reduce.py", "tools/source_registry_check.py", "tools/dream_replay.py",
    "tests/test_state_reduce.py", "tests/test_source_registry_check.py", "tests/test_dream_replay.py",
    "tools/disposition_check.py", "tests/test_disposition_check.py", "control/CORPUS-DISPOSITION.md",
]

log = []


def say(line):
    log.append(line)
    print(line)


def run(cmd, **kw):
    return subprocess.run(cmd, capture_output=True, text=True, **kw)


def check_required():
    missing = [p for p in REQUIRED if not os.path.exists(os.path.join(ROOT, p))]
    say("[%s] required files: %d/%d%s" % ("PASS" if not missing else "FAIL",
                                          len(REQUIRED) - len(missing), len(REQUIRED),
                                          "" if not missing else " missing=%s" % missing))
    return not missing


def check_settings():
    try:
        cfg = json.load(open(SETTINGS, encoding="utf-8"))
    except Exception as e:
        say("[FAIL] settings.json: 読み込み不能 %r" % (e,))
        return False
    problems = []
    if cfg.get("autoMemoryEnabled") is not False:
        problems.append("autoMemoryEnabled が false でない（SRC-02 ISO§2 と衝突）")
    deny = cfg.get("permissions", {}).get("deny", [])
    for needle in ("sources/", ".claude/", "CLAUDE.md", "AUTHORITY.md"):
        if not any(needle in d for d in deny):
            problems.append("deny に %s が無い" % needle)
    hooks = cfg.get("hooks", {})
    pre = hooks.get("PreToolUse") or []
    if not any("guard.py" in h.get("command", "")
               for entry in pre for h in entry.get("hooks", [])):
        problems.append("PreToolUse に guard.py が登録されていない")
    for entry in pre:
        m = entry.get("matcher", "")
        for tool in ("Edit", "Write", "Bash"):
            if tool not in m:
                problems.append("PreToolUse matcher に %s が無い" % tool)
    if not any("session_start.py" in h.get("command", "")
               for entry in (hooks.get("SessionStart") or []) for h in entry.get("hooks", [])):
        problems.append("SessionStart に session_start.py が登録されていない")
    say("[%s] settings.json: %s" % ("PASS" if not problems else "FAIL",
                                    "構造 OK" if not problems else "; ".join(problems)))
    return not problems


def check_guard():
    sandbox = tempfile.mkdtemp(prefix="nexora-guard-")
    try:
        for d in ("sources", "evidence", "control", "tasks", ".claude"):
            os.makedirs(os.path.join(sandbox, d), exist_ok=True)
        open(os.path.join(sandbox, "evidence", "existing.md"), "w").write("x")
        open(os.path.join(sandbox, "CLAUDE.md"), "w").write("x")
        env = dict(os.environ, CLAUDE_PROJECT_DIR=sandbox)
        bad = []
        for cid, want, tool, ti in CASES:
            ti = {k: (v.replace("{ROOT}", sandbox) if isinstance(v, str) else v)
                  for k, v in ti.items()}
            payload = json.dumps({"tool_name": tool, "tool_input": ti, "cwd": sandbox})
            r = subprocess.run([sys.executable, GUARD], input=payload,
                               capture_output=True, text=True, env=env, cwd=sandbox)
            if r.returncode != want:
                bad.append("%s: want exit %d got %d %s" % (cid, want, r.returncode,
                                                           (r.stderr or "").strip()[:80]))
        say("[%s] guard.py: %d/%d cases" % ("PASS" if not bad else "FAIL",
                                            len(CASES) - len(bad), len(CASES)))
        for b in bad:
            say("        %s" % b)
        return not bad
    finally:
        shutil.rmtree(sandbox, ignore_errors=True)


def check_guard_failclosed():
    """壊れた入力でも exit 2（非ブロッキングの exit 1 にならない）ことを確認する。"""
    r = subprocess.run([sys.executable, GUARD], input="{ this is not json",
                       capture_output=True, text=True,
                       env=dict(os.environ, CLAUDE_PROJECT_DIR=ROOT))
    ok = r.returncode == 2
    say("[%s] guard.py fail-closed: 不正入力で exit %d (期待 2)" % ("PASS" if ok else "FAIL",
                                                                r.returncode))
    return ok


def check_session_start():
    r = run([sys.executable, SESSION_START], env=dict(os.environ, CLAUDE_PROJECT_DIR=ROOT))
    ok = r.returncode == 0 and "SOURCES_INTEGRITY" in r.stdout
    say("[%s] session_start.py: exit %d" % ("PASS" if ok else "FAIL", r.returncode))
    for line in r.stdout.strip().splitlines():
        say("        %s" % line)
    return ok


def check_seed():
    r = run([sys.executable, os.path.join(HERE, "seed_derive.py"), "--selftest"])
    say("[%s] seed_derive: %s" % ("PASS" if r.returncode == 0 else "FAIL", r.stdout.strip()))
    return r.returncode == 0


def check_indexer():
    """見出しに「→」を含む節を落とさないこと（過去の欠陥に対する回帰検査）。"""
    d = tempfile.mkdtemp(prefix="nexora-index-")
    try:
        p = os.path.join(d, "fixture.md")
        open(p, "w", encoding="utf-8").write(
            "SOV§649 通常の見出し\n本文\n"
            "SOV§650 状態復元 → 再検証\n本文\n"
            "SOV§651 → 矢印始まり\n本文\n"
            "# [\n数式変換の残骸\n"
            "652. 番号のみ\n本文\n"
        )
        r = run([sys.executable, os.path.join(HERE, "index_sections.py"), p,
                 "--source-id", "SRC-TEST", "--report"])
        ok = r.returncode == 0 and "sections: 5" in r.stdout and "suspect_headings: 1" in r.stdout
        say("[%s] index_sections 回帰（→ を含む見出し）: %s"
            % ("PASS" if ok else "FAIL", r.stdout.strip().splitlines()[0] if r.stdout else r.stderr[:100]))
        return ok
    finally:
        shutil.rmtree(d, ignore_errors=True)


def check_tests():
    r = run([sys.executable, "-m", "unittest", "discover", "-s", "tests", "-t", "tests"],
            cwd=ROOT)
    tail = (r.stderr or r.stdout).strip().splitlines()
    say("[%s] unittest: %s" % ("PASS" if r.returncode == 0 else "FAIL",
                               tail[-1] if tail else "出力なし"))
    if r.returncode != 0:
        for line in tail[-25:]:
            say("        %s" % line)
    return r.returncode == 0


def report_only():
    for name, script, args in (("manifest", "manifest.py", ["verify"]),
                               ("gate", "gate_check.py", [])):
        r = run([sys.executable, os.path.join(HERE, script)] + args)
        say("[INFO] %s (exit %d):" % (name, r.returncode))
        for line in (r.stdout or r.stderr).strip().splitlines():
            say("        %s" % line)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--evidence", action="store_true", help="evidence/T-000/ に実測を保存する")
    a = ap.parse_args()

    say("NEXORA T-000 KIT SELF-CHECK")
    say("root: %s" % ROOT)
    say("python: %s" % sys.version.split()[0])
    results = [check_required(), check_settings(), check_guard(),
               check_guard_failclosed(), check_session_start(), check_seed(),
               check_indexer(), check_tests()]
    report_only()
    ok = all(results)
    say("RESULT: %s" % ("PASS — キットは機能している" if ok else "FAIL — キットが無効化されている"))
    say("NOTE: 本検査はキットの健全性のみを判定する。実装解禁の判定は tools/gate_check.py が行う。")

    if a.evidence:
        stamp = datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        d = os.path.join(ROOT, "evidence", "T-000")
        os.makedirs(d, exist_ok=True)
        p = os.path.join(d, "%s.md" % stamp)
        if os.path.exists(p):
            print("evidence: 既存ファイルを上書きしない。中止する: %s" % p)
            return 1
        with open(p, "w", encoding="utf-8") as f:
            f.write("# T-000 実測 (%s UTC)\n\n```\n%s\n```\n" % (stamp, "\n".join(log)))
        print("evidence: %s" % os.path.relpath(p, ROOT))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
