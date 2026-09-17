#!/usr/bin/env python3
"""sources/ の SHA-256 マニフェスト作成と照合。

正本の不変性を担保する最終防衛線。guard.py は難読化されたシェルを捕捉できないため、
セッション開始時と CI の両方で本照合を実行する。

  python3 tools/manifest.py build     # sources/MANIFEST.sha256 を作る（人間が実行）
  python3 tools/manifest.py verify    # 照合する（CI / SessionStart）
"""
import argparse
import hashlib
import os
import sys

ROOT = os.path.realpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
SOURCES = os.path.join(ROOT, "sources")
MANIFEST = os.path.join(SOURCES, "MANIFEST.sha256")
SKIP = {"MANIFEST.sha256", "README.md", ".gitkeep"}


def digest(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def listing():
    out = []
    for dirpath, dirnames, filenames in os.walk(SOURCES):
        dirnames[:] = sorted(d for d in dirnames if not d.startswith("."))
        for name in sorted(filenames):
            if name in SKIP or name.startswith("."):
                continue
            ap = os.path.join(dirpath, name)
            out.append((os.path.relpath(ap, ROOT).replace(os.sep, "/"), ap))
    return out


def cmd_build(_a):
    files = listing()
    if not files:
        print("BUILD: FAIL — sources/ に原文がない。原文を投入してから実行すること。")
        return 1
    lines = ["%s  %s" % (digest(ap), rel) for rel, ap in files]
    with open(MANIFEST, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    print("BUILD: PASS — %d files -> sources/MANIFEST.sha256" % len(files))
    print("次の操作（人間が実行）: chmod a-w sources/SRC-*")
    return 0


def cmd_verify(_a):
    if not os.path.exists(MANIFEST):
        print("VERIFY: NOT_IDENTIFIABLE — sources/MANIFEST.sha256 が無い（原文未投入）")
        return 2
    recorded, bad = {}, []
    for line in open(MANIFEST, encoding="utf-8"):
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        h, _, rel = line.partition(" ")
        rel = rel.strip().lstrip("*")
        recorded[rel] = h.strip()
        ap = os.path.join(ROOT, rel)
        try:
            got = digest(ap)
        except OSError:
            bad.append("%s: MISSING" % rel)
            continue
        if got != h.strip():
            bad.append("%s: MODIFIED" % rel)
    extra = [rel for rel, _ in listing() if rel not in recorded]
    for rel in extra:
        bad.append("%s: UNTRACKED" % rel)
    if bad:
        print("VERIFY: FAIL\n  " + "\n  ".join(bad))
        return 1
    print("VERIFY: PASS (%d files)" % len(recorded))
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser(description="NEXORA sources manifest")
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("build").set_defaults(fn=cmd_build)
    sub.add_parser("verify").set_defaults(fn=cmd_verify)
    a = ap.parse_args(argv)
    return a.fn(a)


if __name__ == "__main__":
    sys.exit(main())
