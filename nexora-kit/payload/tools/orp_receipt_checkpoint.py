#!/usr/bin/env python3
"""Build and exercise ORP/Receipt checkpoint CP-001 in the checked-out repository."""
from __future__ import annotations
import json
import os
import shutil
import tempfile

from evidence_checkpoint import build_manifest, recover_from_backup, verify_manifest, all_ok

ROOT = os.path.realpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
FILES = [
    "notes/ots-observed.md",
    "testvectors/ots-observed.json",
    "tools/ots_observed.py",
    "tests/test_ots_observed.py",
    "spec/slice2.md",
    "tools/bitcoin_header_recon.py",
    "tests/test_bitcoin_header_recon.py",
    "evidence/orp/TASK-007-bitcoin-358391.json",
    "spec/slice3.md",
    "tools/evidence_checkpoint.py",
    "tests/test_evidence_checkpoint.py",
    "control/ORP-RECEIPT-RECOVERY.md",
]

def main():
    manifest = build_manifest(ROOT, FILES, "ORP-RECEIPT-CP-001")
    baseline = verify_manifest(ROOT, manifest)
    if not all_ok(baseline):
        raise RuntimeError("checkpoint baseline verification failed")

    with tempfile.TemporaryDirectory() as td:
        primary = os.path.join(td, "primary")
        backup = os.path.join(td, "backup")
        for rel in FILES:
            for dest in (primary, backup):
                out = os.path.join(dest, rel)
                os.makedirs(os.path.dirname(out), exist_ok=True)
                shutil.copyfile(os.path.join(ROOT, rel), out)

        # Corrupt one byte without changing length.
        victim = os.path.join(primary, "testvectors", "ots-observed.json")
        with open(victim, "rb") as f:
            data = bytearray(f.read())
        if not data:
            raise RuntimeError("victim file unexpectedly empty")
        data[len(data)//2] ^= 1
        with open(victim, "wb") as f:
            f.write(data)

        detected = verify_manifest(primary, manifest)
        if all_ok(detected):
            raise RuntimeError("corruption was not detected")
        if not any(r["status"] == "HASH_MISMATCH" for r in detected):
            raise RuntimeError("expected same-size HASH_MISMATCH")

        recovered = recover_from_backup(primary, backup, manifest)
        if not all_ok(recovered):
            raise RuntimeError("recovery did not restore manifest")

    result = {
        "schema": "orp-receipt-checkpoint-evidence/1.0",
        "checkpoint": manifest,
        "baseline_verified": True,
        "corruption_injected": "testvectors/ots-observed.json one-bit same-size mutation",
        "corruption_detected": True,
        "recovery_source": "independent temporary backup copy populated before corruption",
        "atomic_restore": True,
        "post_recovery_verified": True,
        "files": len(FILES),
        "claim_ceiling": "Proves deterministic identity and tested hash-verified recovery for this checkpoint file set; does not prove history completeness, semantic truth, or independent failure-domain durability.",
    }
    print(json.dumps(result, sort_keys=True, indent=2))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
