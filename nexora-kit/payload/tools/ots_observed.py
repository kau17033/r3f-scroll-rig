#!/usr/bin/env python3
"""Observed-subset OpenTimestamps parser/executor for ORP/Receipt Slice 2.

This implementation is intentionally limited to structures observed in the pinned
upstream proof recorded in notes/ots-observed.md. Unknown tags fail closed.
"""
from __future__ import annotations
import hashlib
from dataclasses import dataclass, asdict

MAGIC = b"\x00OpenTimestamps\x00\x00Proof\x00\xbf\x89\xe2\xe8\x84\xe8\x92\x94"
BITCOIN_ATTESTATION_TAG = bytes.fromhex("0588960d73d71901")

class OTSError(ValueError):
    pass

@dataclass
class Attestation:
    kind: str
    tag_hex: str
    payload_hex: str
    height: int | None
    message_hex: str
    start: int
    end: int

class Reader:
    def __init__(self, data: bytes):
        self.data = data
        self.pos = 0
    def take(self, n: int) -> bytes:
        if n < 0 or self.pos + n > len(self.data):
            raise OTSError("E_OTS_TRUNCATED")
        out = self.data[self.pos:self.pos+n]
        self.pos += n
        return out
    def varuint(self) -> int:
        value = 0
        shift = 0
        while True:
            if shift > 63:
                raise OTSError("E_OTS_VARUINT")
            b = self.take(1)[0]
            value |= (b & 0x7f) << shift
            if not (b & 0x80):
                return value
            shift += 7
    def varbytes(self, max_len: int = 4096) -> bytes:
        n = self.varuint()
        if n < 1 or n > max_len:
            raise OTSError("E_OTS_VARBYTES")
        return self.take(n)

def _ripemd160(msg: bytes) -> bytes:
    try:
        h = hashlib.new("ripemd160")
    except ValueError as exc:
        raise OTSError("E_OTS_RIPEMD160_UNAVAILABLE") from exc
    h.update(msg)
    return h.digest()

def _apply_op(tag: int, r: Reader, msg: bytes) -> tuple[bytes, str]:
    if tag == 0x03:
        return _ripemd160(msg), "ripemd160"
    if tag == 0x08:
        return hashlib.sha256(msg).digest(), "sha256"
    if tag == 0xF0:
        arg = r.varbytes()
        return msg + arg, "append:" + arg.hex()
    if tag == 0xF1:
        arg = r.varbytes()
        return arg + msg, "prepend:" + arg.hex()
    raise OTSError("E_OTS_UNKNOWN_OP_%02x" % tag)

def _parse_attestation(r: Reader, msg: bytes, start: int) -> Attestation:
    tag = r.take(8)
    payload = r.varbytes(max_len=8192)
    if tag == BITCOIN_ATTESTATION_TAG:
        pr = Reader(payload)
        height = pr.varuint()
        if pr.pos != len(payload):
            raise OTSError("E_OTS_ATTESTATION_TRAILING")
        kind = "bitcoin-block-header"
    else:
        height = None
        kind = "unknown"
    return Attestation(kind, tag.hex(), payload.hex(), height, msg.hex(), start, r.pos)

def _parse_item(tag: int, r: Reader, msg: bytes, depth: int, attestations: list[Attestation], trace: list[dict]) -> None:
    if depth > 256:
        raise OTSError("E_OTS_RECURSION")
    if tag == 0x00:
        start = r.pos - 1
        att = _parse_attestation(r, msg, start)
        attestations.append(att)
        trace.append({"depth": depth, "kind": "attestation", **asdict(att)})
        return
    before = msg
    result, op = _apply_op(tag, r, msg)
    trace.append({
        "depth": depth,
        "kind": "operation",
        "tag": "%02x" % tag,
        "op": op,
        "input_hex": before.hex(),
        "output_hex": result.hex(),
    })
    _parse_timestamp(r, result, depth + 1, attestations, trace)

def _parse_timestamp(r: Reader, msg: bytes, depth: int, attestations: list[Attestation], trace: list[dict]) -> None:
    tag = r.take(1)[0]
    while tag == 0xFF:
        sibling = r.take(1)[0]
        _parse_item(sibling, r, msg, depth, attestations, trace)
        tag = r.take(1)[0]
    _parse_item(tag, r, msg, depth, attestations, trace)

def parse_detached(proof: bytes) -> dict:
    r = Reader(proof)
    if r.take(len(MAGIC)) != MAGIC:
        raise OTSError("E_OTS_MAGIC")
    version = r.take(1)[0]
    if version != 1:
        raise OTSError("E_OTS_VERSION")
    hash_tag = r.take(1)[0]
    if hash_tag != 0x08:
        raise OTSError("E_OTS_FILE_HASH_OP")
    file_digest = r.take(32)
    attestations: list[Attestation] = []
    trace: list[dict] = []
    _parse_timestamp(r, file_digest, 0, attestations, trace)
    if r.pos != len(proof):
        raise OTSError("E_OTS_TRAILING")
    return {
        "version": version,
        "file_hash_op": "sha256",
        "file_digest_hex": file_digest.hex(),
        "proof_bytes": len(proof),
        "consumed_bytes": r.pos,
        "attestations": [asdict(x) for x in attestations],
        "trace": trace,
    }

def verify_detached(proof: bytes, message: bytes) -> dict:
    out = parse_detached(proof)
    actual = hashlib.sha256(message).hexdigest()
    if actual != out["file_digest_hex"]:
        raise OTSError("E_OTS_FILE_DIGEST_MISMATCH")
    out["message_sha256"] = actual
    return out
