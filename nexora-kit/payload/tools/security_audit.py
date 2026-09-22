#!/usr/bin/env python3
"""Conservative control-plane security audit.

This proves only the listed critical controls, not universal absence of vulnerabilities.
"""
import json
import os
import re
import sys

ROOT = os.path.realpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
SETTINGS = os.path.join(ROOT, ".claude", "settings.json")
WORKFLOW = os.path.realpath(os.path.join(ROOT, "..", "..", ".github", "workflows", "nexora-kit.yml"))

SECRET_PATTERNS = [
    re.compile(r"\bsk-[A-Za-z0-9_-]{20,}\b"),
    re.compile(r"\bghp_[A-Za-z0-9]{20,}\b"),
    re.compile(r"\bgithub_pat_[A-Za-z0-9_]{20,}\b"),
    re.compile(r"(?i)api[_-]?key\s*[:=]\s*['\"][A-Za-z0-9_\-]{20,}['\"]"),
]


def main():
    errors = []
    with open(SETTINGS, encoding="utf-8") as f:
        cfg = json.load(f)
    deny = cfg.get("permissions", {}).get("deny", [])
    for needle in ("sources/", ".claude/", "CLAUDE.md", "AUTHORITY.md"):
        if not any(needle in x for x in deny):
            errors.append("protected-path deny missing: %s" % needle)

    if os.path.exists(WORKFLOW):
        body = open(WORKFLOW, encoding="utf-8").read()
        if "contents: read" not in body:
            errors.append("workflow contents permission is not explicitly read-only")

    hits = []
    for dirpath, dirnames, filenames in os.walk(ROOT):
        dirnames[:] = [d for d in dirnames if d not in (".git", "__pycache__")]
        for name in filenames:
            if name.endswith((".pyc", ".png", ".jpg", ".jpeg", ".pdf", ".docx")):
                continue
            path = os.path.join(dirpath, name)
            try:
                text = open(path, encoding="utf-8").read()
            except (UnicodeDecodeError, OSError):
                continue
            for pat in SECRET_PATTERNS:
                if pat.search(text):
                    hits.append(os.path.relpath(path, ROOT))
                    break
    if hits:
        errors.append("credential-like literal(s): %s" % sorted(set(hits))[:10])

    if errors:
        print("SECURITY: FAIL")
        for e in errors:
            print("  - " + e)
        return 1
    print("SECURITY: PASS (critical_control_gaps=0; scope=control-plane static checks)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
