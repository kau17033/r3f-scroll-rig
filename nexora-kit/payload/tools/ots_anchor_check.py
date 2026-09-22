#!/usr/bin/env python3
"""Verify the single frozen CP-001 OpenTimestamps pending proof."""
from __future__ import annotations
import base64, hashlib, json, os, sys
from ots_observed import parse_detached

ROOT=os.path.realpath(os.path.join(os.path.dirname(os.path.abspath(__file__)),".."))
ANCHOR=os.path.join(ROOT,"evidence","orp","ORP-RECEIPT-CP-001.anchor.txt")
B64=os.path.join(ROOT,"evidence","orp","ORP-RECEIPT-CP-001.ots.b64")
META=os.path.join(ROOT,"evidence","orp","ORP-RECEIPT-CP-001-OTS.json")
PENDING_TAG="83dfe30d2ef90c8e"

def main():
    anchor=open(ANCHOR,"rb").read()
    proof=base64.b64decode(open(B64,encoding="ascii").read(),validate=True)
    meta=json.load(open(META,encoding="utf-8"))
    parsed=parse_detached(proof)
    digest=hashlib.sha256(anchor).hexdigest()

    errors=[]
    if digest != meta["anchor_payload_sha256"]:
        errors.append("anchor sha256 mismatch")
    if parsed["file_digest_hex"] != digest:
        errors.append("proof file digest mismatch")
    if len(proof) != meta["proof_bytes"]:
        errors.append("proof byte length mismatch")
    if parsed["consumed_bytes"] != len(proof):
        errors.append("proof not fully consumed")
    atts=parsed["attestations"]
    pending=sum(1 for a in atts if a["tag_hex"]==PENDING_TAG)
    bitcoin=sum(1 for a in atts if a["tag_hex"]=="0588960d73d71901")
    if pending != 4 or bitcoin != 0:
        errors.append("unexpected attestation state pending=%d bitcoin=%d" % (pending,bitcoin))
    if meta["bitcoin_confirmation"] != "PENDING":
        errors.append("metadata confirmation state mismatch")
    if errors:
        print("OTS_EXTERNAL_ANCHOR: FAIL")
        for e in errors: print("  - "+e)
        return 1
    print("OTS_EXTERNAL_ANCHOR: PASS (bytes=%d pending=%d bitcoin=%d)" % (len(proof),pending,bitcoin))
    return 0

if __name__=="__main__":
    sys.exit(main())
