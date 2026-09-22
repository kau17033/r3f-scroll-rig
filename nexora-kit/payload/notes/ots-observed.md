# TASK-006 — OTS Proof Reconnaissance / observed facts only

Status: **OBSERVED / ACCEPT**  
Observed: 2026-09-22  
Scope: format reconnaissance only. This file is **not** a new OTS specification and does not close ORP/Receipt C6 by itself.

## 1. Network-acquired primary proof

The observed proof is an existing OpenTimestamps upstream example, read directly from GitHub by immutable commit:

- repository: `opentimestamps/opentimestamps-client`
- commit: `cd71c7609421bed2a07b9642a3c02a58c9fd2cdf`
- path: `examples/hello-world.txt.ots`
- Git blob: `d8357eb50f9f26136a367bcc7e8365b2ddd7e0f5`
- proof bytes: **688**
- paired message path: `examples/hello-world.txt`
- paired message Git blob: `980a0d5f19a64b4b30a87d4206aade58726b60e3`
- paired message bytes: **13**
- paired message UTF-8: `Hello World!\\n`
- independently recomputed SHA-256 of the 13-byte message: `03ba204e50d126e4674c005e04d82e84c21366780af1f43bd54a37816b6ab340`

The digest above is exactly the 32-byte file digest encoded in the proof.

## 2. Parser authority actually inspected

Byte semantics below were derived by reading the consensus-critical Python implementation at immutable commit
`3af46432efc4a4c4e7bba439c1f49bce808eb3e5` in `opentimestamps/python-opentimestamps`:

- `opentimestamps/core/serialize.py`: unsigned LEB128 varuint and varbytes framing.
- `opentimestamps/core/op.py`: operation tags observed here: `03=RIPEMD160`, `08=SHA256`, `f0=append`, `f1=prepend`.
- `opentimestamps/core/timestamp.py`: detached-file header/version/hash/digest and recursive Timestamp grammar; `00` enters an attestation and `ff` denotes an additional sibling item.
- `opentimestamps/core/notary.py`: Bitcoin attestation tag `0588960d73d71901`; its payload is a varuint block height.

No opcode table was supplied from memory. Only tags encountered in this proof and observed in the pinned parser are recorded here.

## 3. Full byte coverage

Ranges are zero-based and inclusive. Every byte from 0 through 687 appears exactly once below.

| Offset | Bytes | Field | Raw hex | Observed meaning |
|---:|---:|---|---|---|
| 0–30 | 31 | header | `004f70656e54696d657374616d7073000050726f6f6600bf89e2e884e89294` | DetachedTimestampFile.HEADER_MAGIC |
| 31–31 | 1 | version | `01` | major version = 1 |
| 32–32 | 1 | hash-op | `08` | 0x08 = SHA-256 file hash |
| 33–64 | 32 | file-digest | `03ba204e50d126e4674c005e04d82e84c21366780af1f43bd54a37816b6ab340` | declared SHA-256 digest of hello-world.txt |
| 65–65 | 1 | timestamp-tag | `03` | Timestamp item tag; RIPEMD160 |
| 66–66 | 1 | timestamp-tag | `f1` | ↳ Timestamp item tag; PREPEND |
| 67–68 | 2 | prepend-length | `c801` | ↳ PREPEND argument length; LEB128=200 |
| 69–268 | 200 | prepend-argument | `0100000001e482f9d32ecc3ba657b69d898010857b54457a90497982ff56f97c4ec58e6f98010000006b483045022100b253add1d1cf90844338a475a04ff13fc9e7bd242b07762dea07f5608b2de367022000b268ca9c3342b3769cdd062891317cdcef87aac310b6855e9d93898ebbe8ec0121020d8e4d107d2b339b0050efdd4b4a09245aa056048f125396374ea6a2ab0709c6ffffffff026533e605000000001976a9140bf057d40fbba6744862515f5b55a2310de5772f88aca0860100000000001976a914` | ↳ PREPEND raw argument bytes |
| 269–269 | 1 | timestamp-tag | `f0` | ↳ ↳ Timestamp item tag; APPEND |
| 270–270 | 1 | append-length | `06` | ↳ ↳ APPEND argument length; LEB128=6 |
| 271–276 | 6 | append-argument | `88ac00000000` | ↳ ↳ APPEND raw argument bytes |
| 277–277 | 1 | timestamp-tag | `08` | ↳ ↳ ↳ Timestamp item tag; SHA256 |
| 278–278 | 1 | timestamp-tag | `08` | ↳ ↳ ↳ ↳ Timestamp item tag; SHA256 |
| 279–279 | 1 | timestamp-tag | `f1` | ↳ ↳ ↳ ↳ ↳ Timestamp item tag; PREPEND |
| 280–280 | 1 | prepend-length | `20` | ↳ ↳ ↳ ↳ ↳ PREPEND argument length; LEB128=32 |
| 281–312 | 32 | prepend-argument | `a987f716c533913c314c78e35d35884cac943fa42cac49d2b2c69f4003f85f88` | ↳ ↳ ↳ ↳ ↳ PREPEND raw argument bytes |
| 313–313 | 1 | timestamp-tag | `08` | ↳ ↳ ↳ ↳ ↳ ↳ Timestamp item tag; SHA256 |
| 314–314 | 1 | timestamp-tag | `08` | ↳ ↳ ↳ ↳ ↳ ↳ Timestamp item tag; SHA256 |
| 315–315 | 1 | timestamp-tag | `f1` | ↳ ↳ ↳ ↳ ↳ ↳ Timestamp item tag; PREPEND |
| 316–316 | 1 | prepend-length | `20` | ↳ ↳ ↳ ↳ ↳ ↳ PREPEND argument length; LEB128=32 |
| 317–348 | 32 | prepend-argument | `dec55b3487e1e3f722a49b55a7783215862785f4a3acb392846019f71dc64a9d` | ↳ ↳ ↳ ↳ ↳ ↳ PREPEND raw argument bytes |
| 349–349 | 1 | timestamp-tag | `08` | ↳ ↳ ↳ ↳ ↳ ↳ Timestamp item tag; SHA256 |
| 350–350 | 1 | timestamp-tag | `08` | ↳ ↳ ↳ ↳ ↳ ↳ Timestamp item tag; SHA256 |
| 351–351 | 1 | timestamp-tag | `f1` | ↳ ↳ ↳ ↳ ↳ ↳ Timestamp item tag; PREPEND |
| 352–352 | 1 | prepend-length | `20` | ↳ ↳ ↳ ↳ ↳ ↳ PREPEND argument length; LEB128=32 |
| 353–384 | 32 | prepend-argument | `b2ca18f485e080478e025dab3d464b416c0e1ecb6629c9aefce8c8214d042432` | ↳ ↳ ↳ ↳ ↳ ↳ PREPEND raw argument bytes |
| 385–385 | 1 | timestamp-tag | `08` | ↳ ↳ ↳ ↳ ↳ ↳ Timestamp item tag; SHA256 |
| 386–386 | 1 | timestamp-tag | `08` | ↳ ↳ ↳ ↳ ↳ ↳ Timestamp item tag; SHA256 |
| 387–387 | 1 | timestamp-tag | `f0` | ↳ ↳ ↳ ↳ ↳ ↳ Timestamp item tag; APPEND |
| 388–388 | 1 | append-length | `20` | ↳ ↳ ↳ ↳ ↳ ↳ APPEND argument length; LEB128=32 |
| 389–420 | 32 | append-argument | `11b0e90661196ff4b0813c3eda141bab5e91604837bdf7a0c9df37db0e3a1198` | ↳ ↳ ↳ ↳ ↳ ↳ APPEND raw argument bytes |
| 421–421 | 1 | timestamp-tag | `08` | ↳ ↳ ↳ ↳ ↳ ↳ Timestamp item tag; SHA256 |
| 422–422 | 1 | timestamp-tag | `08` | ↳ ↳ ↳ ↳ ↳ ↳ Timestamp item tag; SHA256 |
| 423–423 | 1 | timestamp-tag | `f0` | ↳ ↳ ↳ ↳ ↳ ↳ Timestamp item tag; APPEND |
| 424–424 | 1 | append-length | `20` | ↳ ↳ ↳ ↳ ↳ ↳ APPEND argument length; LEB128=32 |
| 425–456 | 32 | append-argument | `c34bc1a4a1093ffd148c016b1e664742914e939efabe4d3d356515914b26d9e2` | ↳ ↳ ↳ ↳ ↳ ↳ APPEND raw argument bytes |
| 457–457 | 1 | timestamp-tag | `08` | ↳ ↳ ↳ ↳ ↳ ↳ Timestamp item tag; SHA256 |
| 458–458 | 1 | timestamp-tag | `08` | ↳ ↳ ↳ ↳ ↳ ↳ Timestamp item tag; SHA256 |
| 459–459 | 1 | timestamp-tag | `f0` | ↳ ↳ ↳ ↳ ↳ ↳ Timestamp item tag; APPEND |
| 460–460 | 1 | append-length | `20` | ↳ ↳ ↳ ↳ ↳ ↳ APPEND argument length; LEB128=32 |
| 461–492 | 32 | append-argument | `c3e6e7c38c69f6af24c2be34ebac48257ede61ec0a21b9535e4443277be30646` | ↳ ↳ ↳ ↳ ↳ ↳ APPEND raw argument bytes |
| 493–493 | 1 | timestamp-tag | `08` | ↳ ↳ ↳ ↳ ↳ ↳ Timestamp item tag; SHA256 |
| 494–494 | 1 | timestamp-tag | `08` | ↳ ↳ ↳ ↳ ↳ ↳ Timestamp item tag; SHA256 |
| 495–495 | 1 | timestamp-tag | `f1` | ↳ ↳ ↳ ↳ ↳ ↳ Timestamp item tag; PREPEND |
| 496–496 | 1 | prepend-length | `20` | ↳ ↳ ↳ ↳ ↳ ↳ PREPEND argument length; LEB128=32 |
| 497–528 | 32 | prepend-argument | `0798bf8606e00024e5d5d54bf0c960f629dfb9dad69157455b6f2652c0e8de81` | ↳ ↳ ↳ ↳ ↳ ↳ PREPEND raw argument bytes |
| 529–529 | 1 | timestamp-tag | `08` | ↳ ↳ ↳ ↳ ↳ ↳ Timestamp item tag; SHA256 |
| 530–530 | 1 | timestamp-tag | `08` | ↳ ↳ ↳ ↳ ↳ ↳ Timestamp item tag; SHA256 |
| 531–531 | 1 | timestamp-tag | `f0` | ↳ ↳ ↳ ↳ ↳ ↳ Timestamp item tag; APPEND |
| 532–532 | 1 | append-length | `20` | ↳ ↳ ↳ ↳ ↳ ↳ APPEND argument length; LEB128=32 |
| 533–564 | 32 | append-argument | `3f9ada6d60baa244006bb0aad51448ad2fafb9d4b6487a0999cff26b91f0f536` | ↳ ↳ ↳ ↳ ↳ ↳ APPEND raw argument bytes |
| 565–565 | 1 | timestamp-tag | `08` | ↳ ↳ ↳ ↳ ↳ ↳ Timestamp item tag; SHA256 |
| 566–566 | 1 | timestamp-tag | `08` | ↳ ↳ ↳ ↳ ↳ ↳ Timestamp item tag; SHA256 |
| 567–567 | 1 | timestamp-tag | `f1` | ↳ ↳ ↳ ↳ ↳ ↳ Timestamp item tag; PREPEND |
| 568–568 | 1 | prepend-length | `20` | ↳ ↳ ↳ ↳ ↳ ↳ PREPEND argument length; LEB128=32 |
| 569–600 | 32 | prepend-argument | `c703019e959a8dd3faef7489bb328ba485574758e7091f01464eb65872c975c8` | ↳ ↳ ↳ ↳ ↳ ↳ PREPEND raw argument bytes |
| 601–601 | 1 | timestamp-tag | `08` | ↳ ↳ ↳ ↳ ↳ ↳ Timestamp item tag; SHA256 |
| 602–602 | 1 | timestamp-tag | `08` | ↳ ↳ ↳ ↳ ↳ ↳ Timestamp item tag; SHA256 |
| 603–603 | 1 | timestamp-tag | `f0` | ↳ ↳ ↳ ↳ ↳ ↳ Timestamp item tag; APPEND |
| 604–604 | 1 | append-length | `20` | ↳ ↳ ↳ ↳ ↳ ↳ APPEND argument length; LEB128=32 |
| 605–636 | 32 | append-argument | `cbfefff513ff84b915e3fed6f9d799676630f8364ea2a6c7557fad94a5b5d788` | ↳ ↳ ↳ ↳ ↳ ↳ APPEND raw argument bytes |
| 637–637 | 1 | timestamp-tag | `08` | ↳ ↳ ↳ ↳ ↳ ↳ Timestamp item tag; SHA256 |
| 638–638 | 1 | timestamp-tag | `08` | ↳ ↳ ↳ ↳ ↳ ↳ Timestamp item tag; SHA256 |
| 639–639 | 1 | timestamp-tag | `f1` | ↳ ↳ ↳ ↳ ↳ ↳ Timestamp item tag; PREPEND |
| 640–640 | 1 | prepend-length | `20` | ↳ ↳ ↳ ↳ ↳ ↳ PREPEND argument length; LEB128=32 |
| 641–672 | 32 | prepend-argument | `0be23709859913babd4460bbddf8ed213e7c8773a4b1face30f8acfdf093b705` | ↳ ↳ ↳ ↳ ↳ ↳ PREPEND raw argument bytes |
| 673–673 | 1 | timestamp-tag | `08` | ↳ ↳ ↳ ↳ ↳ ↳ Timestamp item tag; SHA256 |
| 674–674 | 1 | timestamp-tag | `08` | ↳ ↳ ↳ ↳ ↳ ↳ Timestamp item tag; SHA256 |
| 675–675 | 1 | timestamp-tag | `00` | ↳ ↳ ↳ ↳ ↳ ↳ Timestamp item tag; attestation |
| 676–683 | 8 | attestation-tag | `0588960d73d71901` | ↳ ↳ ↳ ↳ ↳ ↳ TimeAttestation 8-byte tag |
| 684–684 | 1 | attestation-length | `03` | ↳ ↳ ↳ ↳ ↳ ↳ attestation payload length; LEB128=3 |
| 685–687 | 3 | attestation-payload | `f7ef15` | ↳ ↳ ↳ ↳ ↳ ↳ BitcoinBlockHeaderAttestation payload (block height varuint); height=358391 |

Coverage check: **0..687, 688/688 bytes, no trailing bytes**.

## 4. Observed path semantics

The proof is a **single linear Timestamp path**; this instance contains no `ff` sibling marker.

Observed operation sequence:

1. The detached file declares SHA-256 and embeds file digest `03ba204e...b6ab340`.
2. Apply RIPEMD160 to that digest.
3. PREPEND a 200-byte serialized Bitcoin transaction prefix and APPEND `88ac00000000`; the commitment becomes embedded in the transaction bytes.
4. Apply SHA256 twice to obtain the transaction-hash stage.
5. Traverse the recorded Bitcoin Merkle path using 11 32-byte sibling values. Each sibling is PREPEND or APPEND followed by SHA256 twice.
6. The final internal-byte-order value is `007ee445d23ad061af4a36b809501fab1ac4f2d7e7a739817dd0cbb7ec661b8a`.
7. Displayed in Bitcoin's conventional reversed hash notation, this is `8a1b66ecb7cbd07d8139a7e7d7f2c41aab1f5009b8364aaf61d03ad245e47e00`.
8. The final attestation is `BitcoinBlockHeaderAttestation`; payload bytes `f7ef15` decode as unsigned LEB128 height **358391**.

OpenTimestamps' own upstream documentation reports the same example as verified by Bitcoin block 358391. This reconnaissance establishes the serialization path and byte accountability; it does not independently re-validate Bitcoin proof-of-work or the full header chain.

## 5. Raw proof bytes

```text
004f70656e54696d657374616d7073000050726f6f6600bf89e2e884e89294010803ba204e50d126e4674c005e04d82e
84c21366780af1f43bd54a37816b6ab34003f1c8010100000001e482f9d32ecc3ba657b69d898010857b54457a904979
82ff56f97c4ec58e6f98010000006b483045022100b253add1d1cf90844338a475a04ff13fc9e7bd242b07762dea07f5
608b2de367022000b268ca9c3342b3769cdd062891317cdcef87aac310b6855e9d93898ebbe8ec0121020d8e4d107d2b
339b0050efdd4b4a09245aa056048f125396374ea6a2ab0709c6ffffffff026533e605000000001976a9140bf057d40f
bba6744862515f5b55a2310de5772f88aca0860100000000001976a914f00688ac000000000808f120a987f716c53391
3c314c78e35d35884cac943fa42cac49d2b2c69f4003f85f880808f120dec55b3487e1e3f722a49b55a7783215862785
f4a3acb392846019f71dc64a9d0808f120b2ca18f485e080478e025dab3d464b416c0e1ecb6629c9aefce8c8214d0424
320808f02011b0e90661196ff4b0813c3eda141bab5e91604837bdf7a0c9df37db0e3a11980808f020c34bc1a4a1093f
fd148c016b1e664742914e939efabe4d3d356515914b26d9e20808f020c3e6e7c38c69f6af24c2be34ebac48257ede61
ec0a21b9535e4443277be306460808f1200798bf8606e00024e5d5d54bf0c960f629dfb9dad69157455b6f2652c0e8de
810808f0203f9ada6d60baa244006bb0aad51448ad2fafb9d4b6487a0999cff26b91f0f5360808f120c703019e959a8d
d3faef7489bb328ba485574758e7091f01464eb65872c975c80808f020cbfefff513ff84b915e3fed6f9d799676630f8
364ea2a6c7557fad94a5b5d7880808f1200be23709859913babd4460bbddf8ed213e7c8773a4b1face30f8acfdf093b7
050808000588960d73d7190103f7ef15
```

## 6. Acceptance decision

TASK-006 acceptance criterion:

> proof の全バイトが観測結果で説明できる

**PASS** for this observed upstream proof:

- actual upstream `.ots` acquired by immutable repository/commit/path;
- exact Git blob identity recorded;
- 688/688 bytes assigned to parser-observed fields;
- file digest cross-checked against the paired 13-byte message;
- attestation payload decoded to block height 358391;
- parser reached end-of-file with no unexplained trailing bytes.

This is reconnaissance evidence only. The next permitted step is to derive Slice 2 from this observation. It MUST NOT retroactively change Slice 1, frozen VEA-G3, frozen LoopCell, or promote ORP/Receipt to C6 PASS without checkpoint/recovery implementation and validation.
