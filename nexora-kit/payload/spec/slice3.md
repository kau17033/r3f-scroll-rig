# ORP/Receipt Slice 3 — Bitcoin header validation / observed historical window

Status: **IMPLEMENTED-THEN-SPECIFIED / RECONNAISSANCE v1.0**  
Implementation: `tools/bitcoin_header_recon.py`  
Evidence: `evidence/orp/TASK-007-bitcoin-358391.json`  
Live CI: run `35747066563`

## 1. Scope

Slice 3 validates the Bitcoin-side facts needed by the observed Slice 2 proof. It does not
replace Bitcoin Core consensus validation and does not claim a complete genesis-to-tip SPV node.

The verified historical window is heights **358380–358402**, centered on the OpenTimestamps
attestation at height **358391**.

## 2. Observed block identity

For height 358391:

- header hash: `000000000000000003e892881a8cdcdc117c06d444057c98b6f04a9ee75a2319`
- previous block: `0000000000000000040238cb61fda1452649edc9d18f435f7e1b285a589463b9`
- Merkle root, internal byte order:
  `007ee445d23ad061af4a36b809501fab1ac4f2d7e7a739817dd0cbb7ec661b8a`
- Merkle root, display order:
  `8a1b66ecb7cbd07d8139a7e7d7f2c41aab1f5009b8364aaf61d03ad245e47e00`
- nTime: `1432827678`
- bits: `0x181686f5`
- nonce: `4141773410`

The internal Merkle root is byte-identical to the terminal message reached by the observed
OpenTimestamps proof in Slice 2.

## 3. Header hash and proof of work

The verifier constructs the 80-byte header and computes:

```
block_hash = reverse(SHA256(SHA256(header)))
```

The observed result equals the height-358391 block hash above.

Compact `bits=0x181686f5` expands to:

`00000000000000001686f5000000000000000000000000000000000000000000`

The little-endian double-SHA256 integer of the header is below that target. Therefore the
observed header satisfies its encoded PoW target.

Difficulty derived from the target is **48807487244.68138**, matching the independent API
observation in the CI run.

## 4. Chain linkage

For each height N in 358381–358402:

```
header[N].previousblockhash == hash(header[N-1])
```

was verified against the fetched historical window.

This proves local linkage of the observed 23-block window. It does **not** by itself prove the
entire genesis-to-358402 chain or maximum cumulative chainwork among all possible forks.

## 5. Median Time Past

Bitcoin Core's contextual rule for a candidate block N is:

```
block[N].nTime > pindexPrev->GetMedianTimePast()
```

For block 358391, the timestamps of heights 358380–358390 were observed as:

```
1432820482
1432820586
1432820787
1432821406
1432822665
1432823346
1432824115
1432824649
1432825972
1432826241
1432826832
```

Their median is:

```
MTP_prev11 = 1432823346
```

Block 358391 has:

```
nTime = 1432827678
nTime - MTP_prev11 = 4332 seconds = 72 minutes 12 seconds
```

Thus the observed block satisfies the previous-MTP lower-bound rule.

## 6. Critical correction: the two-hour rule is not a durable historical upper-bound proof

Bitcoin Core also applies a future-time acceptance rule of the form:

```
block.Time() <= NodeClock::now() + MAX_FUTURE_BLOCK_TIME
MAX_FUTURE_BLOCK_TIME = 2 hours
```

This comparison uses the validating node's clock **at validation time**. That clock value is not
committed into the block header.

Therefore, after the fact:

```
header.nTime + 2h
```

MUST NOT be represented as a cryptographically proven upper bound on the real-world time at
which the block or receipt existed.

Similarly, MTP is a consensus-derived timestamp statistic, not exact wall-clock truth.

The correct claim boundary is:

- verified header/PoW/chain linkage can bind the receipt commitment to a valid observed Bitcoin header;
- nTime and MTP are reproducible chain data;
- exact wall-clock creation time is not identified by these bytes alone.

The earlier candidate rule that proposed a strict `when_upper_bound` from `header.timestamp`
or `header.timestamp + 2h` is rejected for this verifier.

## 7. Provider trust boundary

The HTTP provider is a byte/data transport, not the final trust root for the facts that are
independently recomputed here.

For the observed window, the verifier recomputes or cross-checks:

- double-SHA256 header identity;
- previous-header linkage;
- compact-target expansion;
- PoW threshold;
- difficulty;
- OTS terminal Merkle root equality;
- previous-11 MTP.

A production Bitcoin verifier that claims trust-minimized best-chain verification MUST additionally
validate the required consensus/difficulty transitions and sufficient cumulative chainwork from an
explicit checkpoint or genesis. This Slice 3 reconnaissance does not claim that broader closure.

## 8. No-teleportation boundary

```
valid .ots parse
  != valid Bitcoin header

valid Bitcoin header + local chain window
  != globally strongest chain proof

Bitcoin nTime / MTP
  != exact wall-clock timestamp

ORP/Receipt integrity
  != completeness / semantic truth / causal benefit
```

Slice 3 closes TASK-007 reconnaissance for this historical vector; it does not, by itself, close C6.
