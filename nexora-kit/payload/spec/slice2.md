# ORP/Receipt Slice 2 — OpenTimestamps observed-subset specification

Status: **IMPLEMENTED-THEN-SPECIFIED / OBSERVED SUBSET v1.0**  
Implementation: `tools/ots_observed.py`  
Canonical observed vector: `testvectors/ots-observed.json`  
Reconnaissance record: `notes/ots-observed.md`

## 1. Scope and authority

This specification was written **after** a real upstream OpenTimestamps proof was acquired,
byte-accounted, implemented, and exercised. It MUST NOT be read as a complete redefinition of
the OpenTimestamps format.

Evidence classes are kept separate:

- **OBSERVED+EXECUTED**: bytes/tags/operations exercised by the pinned 688-byte upstream proof.
- **UPSTREAM-SOURCE-DERIVED**: behavior read from the pinned consensus-critical Python parser but
  not necessarily exercised by the single observed proof.
- **UNSUPPORTED**: anything else; the implementation fails closed.

If this prose conflicts with `testvectors/ots-observed.json` for the observed proof, the vector wins.

## 2. Pinned upstream observation

Observed upstream proof:

- repository: `opentimestamps/opentimestamps-client`
- commit: `cd71c7609421bed2a07b9642a3c02a58c9fd2cdf`
- proof: `examples/hello-world.txt.ots`
- proof Git blob: `d8357eb50f9f26136a367bcc7e8365b2ddd7e0f5`
- size: **688 bytes**
- paired message: `Hello World!\n`
- message SHA-256: `03ba204e50d126e4674c005e04d82e84c21366780af1f43bd54a37816b6ab340`

Pinned parser source inspected:

- repository: `opentimestamps/python-opentimestamps`
- commit: `3af46432efc4a4c4e7bba439c1f49bce808eb3e5`

## 3. Detached proof framing

For the observed proof, the parser MUST read in this order:

1. 31-byte magic
   `00 4f70656e54696d657374616d7073 0000 50726f6f66 00 bf89e2e884e89294`;
2. one-byte major version, observed value `01`;
3. one-byte file hash operation, observed value `08` = SHA-256;
4. exactly 32 bytes of file digest;
5. one recursively serialized Timestamp;
6. end-of-file, with no trailing bytes.

The implementation MUST reject wrong magic, unsupported major version, non-SHA256 detached-file
hash tags in this observed-subset implementation, truncation, and trailing bytes.

## 4. Integer and byte-string encoding

Unsigned integers and variable byte lengths are unsigned little-endian base-128 (LEB128), as read
from the pinned upstream serializer.

For a variable byte string:

```
length := varuint
payload := exactly length bytes
```

The implementation MUST fail closed on truncation and configured length overflow.

## 5. Timestamp grammar

A timestamp starts from a current message value.

The pinned upstream grammar uses:

- `ff`: another sibling item follows; then read that item's tag;
- a final item tag without a preceding `ff`;
- `00`: TimeAttestation;
- any supported operation tag: execute the operation against the current message and recurse on
  the resulting message.

The observed 688-byte vector is a **single linear path** and contains no `ff` sibling marker.
Branch handling is therefore **UPSTREAM-SOURCE-DERIVED / NOT VECTOR-EXERCISED** and MUST NOT be
advertised as independently interoperability-tested until a branching real proof is added.

## 6. Operations exercised by the observed proof

Only the following operation tags are accepted by the observed-subset executor:

| Tag | Operation | Argument |
|---|---|---|
| `03` | RIPEMD-160 | none |
| `08` | SHA-256 | none |
| `f0` | append | varbytes |
| `f1` | prepend | varbytes |

Execution semantics:

- `RIPEMD160(m)`
- `SHA256(m)`
- `APPEND(x,m) := m || x`
- `PREPEND(x,m) := x || m`

Unknown operation tags MUST fail closed. The implementation does not claim support for unobserved
OpenTimestamps operations merely because they may exist upstream.

## 7. Attestation exercised by the observed proof

Tag `00` enters a TimeAttestation.

The attestation encoding inspected upstream is:

```
8-byte attestation tag
varbytes payload
```

Observed Bitcoin attestation tag:

`05 88 96 0d 73 d7 19 01`

The payload is a varuint block height. In the observed proof:

- payload: `f7 ef 15`
- decoded height: **358391**
- message arriving at the attestation:
  `007ee445d23ad061af4a36b809501fab1ac4f2d7e7a739817dd0cbb7ec661b8a`

That 32-byte value is the Bitcoin block Merkle root in internal byte order.

Unknown attestation tags may be structurally recorded, but they MUST NOT be promoted to a verified
Bitcoin attestation.

## 8. File binding

When a candidate original message is supplied, the executor MUST:

```
SHA256(message) == detached proof file digest
```

or fail with `E_OTS_FILE_DIGEST_MISMATCH`.

This establishes binding between the supplied file bytes and the starting digest only.

## 9. Error boundary

The implementation uses fail-closed errors for:

- `E_OTS_TRUNCATED`
- `E_OTS_VARUINT`
- `E_OTS_VARBYTES`
- `E_OTS_MAGIC`
- `E_OTS_VERSION`
- `E_OTS_FILE_HASH_OP`
- `E_OTS_UNKNOWN_OP_<tag>`
- `E_OTS_ATTESTATION_TRAILING`
- `E_OTS_RECURSION`
- `E_OTS_TRAILING`
- `E_OTS_FILE_DIGEST_MISMATCH`
- `E_OTS_RIPEMD160_UNAVAILABLE`

No parse error may be reclassified as a valid attestation.

## 10. Acceptance evidence

The observed vector must satisfy all of:

- 688 input proof bytes;
- 688 consumed bytes;
- zero unexplained trailing bytes;
- supplied message SHA-256 equals embedded digest;
- exactly one observed Bitcoin attestation;
- height = 358391;
- final attestation message equals the pinned Merkle root.

Mutation tests MUST show fail-closed behavior for truncation, trailing bytes, unknown operation,
and wrong message binding.

## 11. Slice boundary

Slice 2 establishes **proof parsing and operation execution** for the observed subset.

It does **not** establish:

- that block 358391 exists in the best Bitcoin chain;
- header hash validity;
- PoW validity;
- difficulty-transition validity;
- Merkle-root equality against an independently validated block header;
- trustworthy wall-clock time;
- a strict timestamp upper bound.

Those are Slice 3 / TASK-007 responsibilities.

Therefore:

```
OTS parse success != Bitcoin attestation verification
Bitcoin attestation verification != exact wall-clock truth
Receipt authenticity != completeness / semantic truth / causal benefit
```
