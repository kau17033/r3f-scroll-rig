#!/usr/bin/env python3
"""Attempt a network upgrade of frozen CP-001 OpenTimestamps proof.

Uses the pinned upstream python-opentimestamps implementation. This script does not
modify repository files. If a Bitcoin attestation is available it prints the fully
upgraded detached proof as base64 so it can be frozen only after observed success.
"""
from __future__ import annotations
import base64, json, os, sys

from opentimestamps.calendar import RemoteCalendar
from opentimestamps.core.notary import BitcoinBlockHeaderAttestation, PendingAttestation
from opentimestamps.core.serialize import BytesDeserializationContext, BytesSerializationContext
from opentimestamps.core.timestamp import DetachedTimestampFile

ROOT=os.path.realpath(os.path.join(os.path.dirname(os.path.abspath(__file__)),".."))
B64=os.path.join(ROOT,"evidence","orp","ORP-RECEIPT-CP-001.ots.b64")
META=os.path.join(ROOT,"evidence","orp","ORP-RECEIPT-CP-001-OTS.json")

def walk(stamp):
    yield stamp
    for child in stamp.ops.values():
        yield from walk(child)

def main():
    proof=base64.b64decode(open(B64,encoding="ascii").read().strip(),validate=True)
    meta=json.load(open(META,encoding="utf-8"))
    detached=DetachedTimestampFile.deserialize(BytesDeserializationContext(proof))

    attempts=[]
    changed=False
    for node in list(walk(detached.timestamp)):
        pending=[a for a in node.attestations if isinstance(a,PendingAttestation)]
        for att in pending:
            uri=att.uri
            row={"uri":uri,"commitment":node.msg.hex()}
            try:
                upgraded=RemoteCalendar(uri,user_agent="NEXORA-ORP-upgrade/1.0").get_timestamp(node.msg,timeout=20)
                before={(type(a).__name__,repr(a)) for _,a in detached.timestamp.all_attestations()}
                node.merge(upgraded)
                after={(type(a).__name__,repr(a)) for _,a in detached.timestamp.all_attestations()}
                row["new_attestations"]=len(after-before)
                changed=changed or bool(after-before)
                row["status"]="OK"
            except Exception as exc:
                row["status"]="ERROR"
                row["error"]=type(exc).__name__+":"+str(exc)[:240]
            attempts.append(row)

    atts=[]
    heights=[]
    pending_count=0
    for msg,att in detached.timestamp.all_attestations():
        item={"type":type(att).__name__,"message_hex":msg.hex()}
        if isinstance(att,BitcoinBlockHeaderAttestation):
            item["height"]=att.height
            heights.append(att.height)
        elif isinstance(att,PendingAttestation):
            item["uri"]=att.uri
            pending_count+=1
        atts.append(item)

    outctx=BytesSerializationContext()
    detached.serialize(outctx)
    upgraded_bytes=outctx.getbytes()

    result={
        "schema":"orp-receipt-ots-upgrade-attempt/1.0",
        "checkpoint_id":meta["checkpoint_id"],
        "input_proof_bytes":len(proof),
        "output_proof_bytes":len(upgraded_bytes),
        "changed":changed,
        "bitcoin_attestation_count":len(heights),
        "bitcoin_heights":sorted(heights),
        "pending_attestation_count":pending_count,
        "attempts":attempts,
        "status":"BITCOIN_CONFIRMED" if heights else "PENDING",
    }
    print(json.dumps(result,sort_keys=True,indent=2))
    if heights:
        print("UPGRADED_PROOF_B64="+base64.b64encode(upgraded_bytes).decode("ascii"))
    return 0

if __name__=="__main__":
    sys.exit(main())
