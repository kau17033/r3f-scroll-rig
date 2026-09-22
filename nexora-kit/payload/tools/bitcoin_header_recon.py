#!/usr/bin/env python3
"""TASK-007 Bitcoin header validation reconnaissance.

Fetches a small historical window from mempool.space, validates the known
OpenTimestamps attestation block 358391, and prints a JSON observation record.
No scientific or legal claim is promoted by this tool.
"""
from __future__ import annotations
import hashlib, json, statistics, struct, sys, time
from urllib.request import Request, urlopen

BASE = "https://mempool.space/api"
HEIGHT = 358391
WINDOW_MIN = 358380
WINDOW_MAX = 358402
EXPECTED_OTS_ROOT_INTERNAL = "007ee445d23ad061af4a36b809501fab1ac4f2d7e7a739817dd0cbb7ec661b8a"

def get_text(url: str) -> str:
    last = None
    for i in range(4):
        try:
            req = Request(url, headers={"User-Agent":"NEXORA-ORP-recon/1.0"})
            with urlopen(req, timeout=20) as r:
                return r.read().decode("utf-8").strip()
        except Exception as exc:
            last = exc
            time.sleep(1 + i)
    raise RuntimeError("network fetch failed: %s: %r" % (url, last))

def get_json(url: str):
    return json.loads(get_text(url))

def dsha256(b: bytes) -> bytes:
    return hashlib.sha256(hashlib.sha256(b).digest()).digest()

def compact_target(bits: int) -> int:
    exp = bits >> 24
    mant = bits & 0x007fffff
    if bits & 0x00800000:
        raise ValueError("negative compact target")
    if exp <= 3:
        return mant >> (8 * (3 - exp))
    return mant << (8 * (exp - 3))

def parse_header(raw: bytes):
    if len(raw) != 80:
        raise ValueError("header must be 80 bytes")
    return {
        "version": struct.unpack("<I", raw[:4])[0],
        "previousblockhash": raw[4:36][::-1].hex(),
        "merkle_root_display": raw[36:68][::-1].hex(),
        "merkle_root_internal": raw[36:68].hex(),
        "timestamp": struct.unpack("<I", raw[68:72])[0],
        "bits": struct.unpack("<I", raw[72:76])[0],
        "nonce": struct.unpack("<I", raw[76:80])[0],
        "hash": dsha256(raw)[::-1].hex(),
    }

def main():
    # Three 10-block calls cover the required historical window with margin.
    by_height = {}
    for start in (358402, 358392, 358382):
        for row in get_json("%s/blocks/%d" % (BASE, start)):
            by_height[int(row["height"])] = row

    missing = [h for h in range(WINDOW_MIN, WINDOW_MAX + 1) if h not in by_height]
    if missing:
        raise RuntimeError("missing block heights: %r" % missing)

    # Live identity + raw header.
    block_hash = get_text("%s/block-height/%d" % (BASE, HEIGHT))
    header_hex = get_text("%s/block/%s/header" % (BASE, block_hash))
    raw = bytes.fromhex(header_hex)
    header = parse_header(raw)
    block = get_json("%s/block/%s" % (BASE, block_hash))

    if header["hash"] != block_hash:
        raise AssertionError("double-SHA256 header hash mismatch")
    if header["previousblockhash"] != block["previousblockhash"]:
        raise AssertionError("previous block hash mismatch")
    if header["timestamp"] != int(block["timestamp"]):
        raise AssertionError("header timestamp mismatch")
    if header["bits"] != int(block["bits"]):
        raise AssertionError("bits mismatch")
    if header["nonce"] != int(block["nonce"]):
        raise AssertionError("nonce mismatch")

    # OTS proof reaches the block merkle root in internal byte order.
    if header["merkle_root_internal"] != EXPECTED_OTS_ROOT_INTERNAL:
        raise AssertionError("OTS attestation root != header merkle root internal order")

    # PoW and compact target.
    target = compact_target(header["bits"])
    hash_num = int.from_bytes(dsha256(raw), "little")
    if hash_num > target:
        raise AssertionError("PoW target check failed")

    # Chain linkage across the whole observed window.
    for h in range(WINDOW_MIN + 1, WINDOW_MAX + 1):
        cur = by_height[h]
        prev = by_height[h-1]
        if cur["previousblockhash"] != prev["id"]:
            raise AssertionError("chain linkage failed at height %d" % h)

    # Bitcoin Core's MTP check for block N uses the prior 11 block timestamps.
    prev11 = [int(by_height[h]["timestamp"]) for h in range(HEIGHT - 11, HEIGHT)]
    mtp_prev11 = int(statistics.median(prev11))
    api_mtp = int(block["mediantime"])
    if mtp_prev11 != api_mtp:
        raise AssertionError("computed MTP != API mediantime")
    if not header["timestamp"] > mtp_prev11:
        raise AssertionError("time-too-old consensus rule would fail")

    # MTP observable eleven blocks later (diagnostic only; not claimed as strict creation-time upper bound).
    nplus11 = by_height[HEIGHT + 11]
    mtp_nplus11 = int(nplus11["mediantime"])

    # Bitcoin difficulty 1 target from 0x1d00ffff.
    diff1 = compact_target(0x1d00ffff)
    difficulty_from_bits = diff1 / target
    api_difficulty = float(block["difficulty"])
    rel_err = abs(difficulty_from_bits - api_difficulty) / api_difficulty
    if rel_err > 1e-12:
        raise AssertionError("difficulty mismatch")

    result = {
        "schema": "orp-bitcoin-recon/1.0",
        "source": "mempool.space public REST API",
        "height": HEIGHT,
        "block_hash": block_hash,
        "header_hex": header_hex,
        "header": header,
        "pow": {
            "target_hex": "%064x" % target,
            "hash_as_target_integer_hex": "%064x" % hash_num,
            "valid": True,
            "difficulty_from_bits": difficulty_from_bits,
            "api_difficulty": api_difficulty,
        },
        "chain_window": {
            "min_height": WINDOW_MIN,
            "max_height": WINDOW_MAX,
            "linked": True,
        },
        "time": {
            "header_timestamp": header["timestamp"],
            "prev11_timestamps": prev11,
            "mtp_prev11": mtp_prev11,
            "header_minus_mtp_seconds": header["timestamp"] - mtp_prev11,
            "height_n_plus_11": HEIGHT + 11,
            "mtp_n_plus_11": mtp_nplus11,
            "consensus_observation": "header timestamp must be strictly greater than previous-11 MTP",
            "future_time_rule": "Bitcoin Core also rejects a header more than 2h ahead of node clock at validation time; that node clock is not committed in this historical header.",
            "strict_historical_upper_bound_from_header_alone": None,
        },
        "claim_ceiling": "Header/PoW/chain/MTP facts are reproducible. No strict wall-clock upper bound is inferred from header bytes alone.",
    }
    print(json.dumps(result, sort_keys=True, indent=2))
    return 0

if __name__ == "__main__":
    sys.exit(main())
