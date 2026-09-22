#!/usr/bin/env python3
"""Final-host migration preflight for the NEXORA bootstrap carrier.

This does not create or mutate the destination repository. It proves that the
carrier payload can be frozen unambiguously and that structural convergence is
blocked only by the absent final host.
"""
from __future__ import annotations
import json
import os
import subprocess
import sys

ROOT = os.path.realpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
TARGET = "kau17033/kau17033-nexora-core"
CARRIER_SUBTREE = "nexora-kit/payload"


def run(*args, cwd=None, check=True):
    p = subprocess.run(args, cwd=cwd, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if check and p.returncode != 0:
        raise RuntimeError("%s failed (%d): %s" % (" ".join(args), p.returncode, p.stderr.strip() or p.stdout.strip()))
    return p


def git_top():
    return run("git", "rev-parse", "--show-toplevel", cwd=ROOT).stdout.strip()


def freeze_source():
    top = git_top()
    head = run("git", "rev-parse", "HEAD", cwd=top).stdout.strip()
    tree = run("git", "rev-parse", "HEAD:%s" % CARRIER_SUBTREE, cwd=top).stdout.strip()
    listing = run("git", "ls-tree", "-r", "--full-tree", "HEAD", CARRIER_SUBTREE, cwd=top).stdout.splitlines()
    files = []
    prefix = CARRIER_SUBTREE + "/"
    for line in listing:
        meta, path = line.split("\t", 1)
        mode, obj_type, sha = meta.split()
        if obj_type != "blob":
            continue
        if not path.startswith(prefix):
            raise RuntimeError("unexpected path outside payload: %s" % path)
        files.append({
            "path": path[len(prefix):],
            "mode": mode,
            "git_blob_sha1": sha,
        })
    files.sort(key=lambda x: x["path"])
    if not files:
        raise RuntimeError("payload tree has no blobs")
    return {
        "carrier_repository": "kau17033/r3f-scroll-rig",
        "carrier_head": head,
        "carrier_subtree": CARRIER_SUBTREE,
        "payload_tree_sha1": tree,
        "file_count": len(files),
        "files": files,
    }


def verify_structural_stop():
    state = run(sys.executable, "tools/state_reduce.py", "--check", cwd=ROOT, check=False)
    if state.returncode != 0:
        raise RuntimeError("state projection is not converged: " + (state.stdout + state.stderr).strip())

    gate = run(sys.executable, "tools/convergence_gate.py", cwd=ROOT, check=False)
    block_lines = [line.strip() for line in gate.stdout.splitlines() if "[BLOCK]" in line]
    if len(block_lines) != 1 or "final_host" not in block_lines[0]:
        raise RuntimeError("expected exactly one structural blocker final_host, got: %r" % block_lines)
    if "state=BLOCKED" not in block_lines[0] or TARGET not in block_lines[0]:
        raise RuntimeError("final_host blocker does not bind expected target: %s" % block_lines[0])
    return {
        "state_projection": "PASS",
        "convergence_gate_returncode": gate.returncode,
        "structural_blockers": block_lines,
        "only_structural_blocker": "final_host",
    }


def main():
    frozen = freeze_source()
    structural = verify_structural_stop()
    out = {
        "schema": "nexora-final-host-preflight/1.0",
        "target_repository": TARGET,
        "destination_requirement": "empty private repository with connector contents read/write",
        "source": frozen,
        "structural": structural,
        "migration_ready": True,
        "claim_ceiling": (
            "Preflight proves source identity and that final_host is the sole structural T-070 blocker. "
            "It does not create the destination, prove byte-equivalent migration, satisfy scientific/human gates, or close C8."
        ),
    }
    print(json.dumps(out, ensure_ascii=False, sort_keys=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
