#!/usr/bin/env python3
"""Independently verify the frozen CP-001 Bitcoin-confirmed OpenTimestamps proof.

Checks:
- anchor payload SHA-256 matches detached proof file digest
- proof parses to EOF with observed-subset executor
- each BitcoinBlockHeaderAttestation is bound to the Merkle root of the claimed block
- claimed block header double-SHA256 identity and encoded PoW target
- immediate prev/next main-chain linkage from independently fetched public block data

The public API is transport. Header/Merkle/PoW facts are recomputed locally.
"""
from __future__ import annotations
import base64, hashlib, json, os, sys
from urllib.request import Request, urlopen

from ots_observed import parse_detached
from bitcoin_header_recon import compact_target, dsha256, parse_header

ROOT=os.path.realpath(os.path.join(os.path.dirname(os.path.abspath(__file__)),".."))
ANCHOR=os.path.join(ROOT,"evidence","orp","ORP-RECEIPT-CP-001.anchor.txt")
PROOF=os.path.join(ROOT,"evidence","orp","ORP-RECEIPT-CP-001-upgraded.ots.b64")
META=os.path.join(ROOT,"evidence","orp","ORP-RECEIPT-CP-001-confirmed.json")
BASE="https://mempool.space/api"

def get_text(url):
    req=Request(url,headers={"User-Agent":"NEXORA-ORP-confirm/1.0","Cache-Control":"no-cache"})
    with urlopen(req,timeout=25) as r:
        return r.read().decode("utf-8").strip()

def get_json(url):
    return json.loads(get_text(url))

def main():
    anchor=open(ANCHOR,"rb").read()
    proof=base64.b64decode(open(PROOF,encoding="ascii").read().strip(),validate=True)
    meta=json.load(open(META,encoding="utf-8"))
    parsed=parse_detached(proof)

    digest=hashlib.sha256(anchor).hexdigest()
    if parsed["file_digest_hex"] != digest:
        raise RuntimeError("anchor digest != detached proof digest")
    if parsed["consumed_bytes"] != len(proof):
        raise RuntimeError("proof not fully consumed")
    if len(proof) != int(meta["upgraded_proof_bytes"]):
        raise RuntimeError("proof length drift")

    btc=[a for a in parsed["attestations"] if a["kind"]=="bitcoin-block-header"]
    if len(btc) < 1:
        raise RuntimeError("no Bitcoin attestation")
    heights=sorted(a["height"] for a in btc)
    if heights != sorted(meta["bitcoin_heights"]):
        raise RuntimeError("Bitcoin height metadata drift")

    verified=[]
    for height in sorted(set(heights)):
        block_hash=get_text(f"{BASE}/block-height/{height}")
        header_hex=get_text(f"{BASE}/block/{block_hash}/header")
        raw=bytes.fromhex(header_hex)
        hdr=parse_header(raw)
        if hdr["hash"] != block_hash:
            raise RuntimeError(f"header hash mismatch at {height}")
        target=compact_target(hdr["bits"])
        hash_num=int.from_bytes(dsha256(raw),"little")
        if hash_num > target:
            raise RuntimeError(f"PoW target failure at {height}")

        block=get_json(f"{BASE}/block/{block_hash}")
        if block["merkle_root"] != hdr["merkle_root_display"]:
            raise RuntimeError(f"API/header Merkle disagreement at {height}")

        bound=[a for a in btc if a["height"]==height]
        for a in bound:
            if a["message_hex"] != hdr["merkle_root_internal"]:
                raise RuntimeError(f"OTS Merkle binding mismatch at {height}")

        prev_hash=get_text(f"{BASE}/block-height/{height-1}")
        next_hash=get_text(f"{BASE}/block-height/{height+1}")
        prev=get_json(f"{BASE}/block/{prev_hash}")
        cur=block
        nxt=get_json(f"{BASE}/block/{next_hash}")
        if cur["previousblockhash"] != prev_hash:
            raise RuntimeError(f"prev linkage failure at {height}")
        if nxt["previousblockhash"] != block_hash:
            raise RuntimeError(f"next linkage failure at {height}")

        verified.append({
            "height":height,
            "block_hash":block_hash,
            "header_hex":header_hex,
            "merkle_root_internal":hdr["merkle_root_internal"],
            "merkle_root_display":hdr["merkle_root_display"],
            "timestamp":hdr["timestamp"],
            "bits":hdr["bits"],
            "nonce":hdr["nonce"],
            "target_hex":"%064x"%target,
            "pow_valid":True,
            "prev_height":height-1,
            "prev_hash":prev_hash,
            "next_height":height+1,
            "next_hash":next_hash,
            "local_linkage_valid":True,
            "attestation_paths":len(bound),
        })

    out={
        "schema":"orp-receipt-cp001-independent-confirmation/1.0",
        "checkpoint_id":meta["checkpoint_id"],
        "checkpoint_hash":meta["checkpoint_hash"],
        "anchor_payload_sha256":digest,
        "proof_bytes":len(proof),
        "bitcoin_attestations":len(btc),
        "bitcoin_heights":heights,
        "verified_blocks":verified,
        "status":"PASS",
        "claim_ceiling":"Confirms CP-001 anchor payload binding through the frozen OTS proof to independently rehashed PoW-valid Bitcoin header(s) with local prev/next linkage. It does not prove full genesis-to-tip best-chain validation, receipt completeness, semantic truth, or causal benefit.",
    }
    print(json.dumps(out,sort_keys=True,indent=2))
    return 0

if __name__=="__main__":
    sys.exit(main())
