#!/usr/bin/env python3
"""Deterministic evidence checkpoint + recovery primitives for ORP/Receipt.

This module proves file identity and recoverability relative to a manifest.
It does not prove that recorded actions happened or that evidence is complete.
"""
from __future__ import annotations
import hashlib
import json
import os
import shutil
import tempfile

SCHEMA = "nexora-evidence-checkpoint/1.0"

def sha256_file(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while True:
            chunk = f.read(1024 * 1024)
            if not chunk:
                break
            h.update(chunk)
    return h.hexdigest()

def _canonical(obj) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")

def build_manifest(root: str, relpaths: list[str], checkpoint_id: str, previous_checkpoint: str | None = None) -> dict:
    if not checkpoint_id:
        raise ValueError("checkpoint_id required")
    entries = []
    for rel in sorted(set(relpaths)):
        if os.path.isabs(rel) or ".." in rel.split("/"):
            raise ValueError("unsafe relative path: %r" % rel)
        path = os.path.join(root, rel)
        if not os.path.isfile(path):
            raise FileNotFoundError(path)
        entries.append({
            "path": rel,
            "size": os.path.getsize(path),
            "sha256": sha256_file(path),
        })
    core = {
        "schema": SCHEMA,
        "checkpoint_id": checkpoint_id,
        "previous_checkpoint": previous_checkpoint,
        "entries": entries,
    }
    return {**core, "checkpoint_hash": hashlib.sha256(_canonical(core)).hexdigest()}

def validate_manifest_shape(manifest: dict) -> None:
    if manifest.get("schema") != SCHEMA:
        raise ValueError("E_CHECKPOINT_SCHEMA")
    cp = manifest.get("checkpoint_hash")
    if not isinstance(cp, str) or len(cp) != 64:
        raise ValueError("E_CHECKPOINT_HASH")
    core = {k: manifest[k] for k in ("schema","checkpoint_id","previous_checkpoint","entries")}
    expected = hashlib.sha256(_canonical(core)).hexdigest()
    if cp != expected:
        raise ValueError("E_CHECKPOINT_HASH")
    paths = [e.get("path") for e in manifest.get("entries", [])]
    if paths != sorted(set(paths)):
        raise ValueError("E_CHECKPOINT_ENTRIES_ORDER")
    for e in manifest["entries"]:
        if not isinstance(e.get("size"), int) or e["size"] < 0:
            raise ValueError("E_CHECKPOINT_SIZE")
        digest = e.get("sha256") or ""
        if len(digest) != 64 or any(c not in "0123456789abcdef" for c in digest):
            raise ValueError("E_CHECKPOINT_ENTRY_HASH")

def verify_manifest(root: str, manifest: dict) -> list[dict]:
    validate_manifest_shape(manifest)
    result = []
    for e in manifest["entries"]:
        p = os.path.join(root, e["path"])
        if not os.path.isfile(p):
            result.append({"path":e["path"],"status":"MISSING"})
            continue
        size = os.path.getsize(p)
        digest = sha256_file(p)
        if size != e["size"]:
            result.append({"path":e["path"],"status":"SIZE_MISMATCH","actual_size":size})
        elif digest != e["sha256"]:
            result.append({"path":e["path"],"status":"HASH_MISMATCH","actual_sha256":digest})
        else:
            result.append({"path":e["path"],"status":"OK"})
    return result

def all_ok(results: list[dict]) -> bool:
    return bool(results) and all(r["status"] == "OK" for r in results)

def _atomic_copy(src: str, dst: str) -> None:
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    fd, tmp = tempfile.mkstemp(prefix=".recover-", dir=os.path.dirname(dst))
    os.close(fd)
    try:
        shutil.copyfile(src, tmp)
        with open(tmp, "rb") as f:
            os.fsync(f.fileno())
        os.replace(tmp, dst)
    finally:
        if os.path.exists(tmp):
            os.unlink(tmp)

def recover_from_backup(primary_root: str, backup_root: str, manifest: dict) -> list[dict]:
    """Restore only missing/corrupt files, but only from backup bytes matching manifest."""
    validate_manifest_shape(manifest)
    before = verify_manifest(primary_root, manifest)
    for state, e in zip(before, manifest["entries"]):
        if state["status"] == "OK":
            continue
        src = os.path.join(backup_root, e["path"])
        if not os.path.isfile(src):
            raise RuntimeError("E_BACKUP_MISSING:%s" % e["path"])
        if os.path.getsize(src) != e["size"] or sha256_file(src) != e["sha256"]:
            raise RuntimeError("E_BACKUP_INVALID:%s" % e["path"])
        _atomic_copy(src, os.path.join(primary_root, e["path"]))
    after = verify_manifest(primary_root, manifest)
    if not all_ok(after):
        raise RuntimeError("E_RECOVERY_VERIFY")
    return after

def atomic_write_manifest(path: str, manifest: dict) -> None:
    validate_manifest_shape(manifest)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    payload = json.dumps(manifest, sort_keys=True, indent=2, ensure_ascii=False).encode("utf-8") + b"\n"
    fd, tmp = tempfile.mkstemp(prefix=".checkpoint-", dir=os.path.dirname(path))
    try:
        with os.fdopen(fd, "wb") as f:
            f.write(payload)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp, path)
    finally:
        if os.path.exists(tmp):
            os.unlink(tmp)

def load_manifest(path: str) -> dict:
    with open(path, encoding="utf-8") as f:
        m = json.load(f)
    validate_manifest_shape(m)
    return m
