# ORP namespace split

Bare `ORP` is ambiguous and MUST NOT be used as a scientific state transition.

## ORP/Receipt

Purpose: bind an observed/reported action and its evidence references to canonical bytes,
identity, signatures and externally verifiable history/checkpoints.

Can establish:
- byte identity;
- signer identity under the selected key model;
- tamper evidence relative to a trusted checkpoint;
- provenance links actually bound into the signed payload.

Cannot establish by itself:
- that every action was recorded;
- that the recorded action really occurred as claimed;
- that inputs/outputs were semantically correct;
- that the action caused an improvement;
- that a capability is reusable/generalizable.

Current convergence state: **PASS (implemented verification boundary; scope-limited)**.

Verified engineering evidence now includes:
- recovered Slice 1 cross-language signature/canonical-byte conformance;
- one real upstream OpenTimestamps proof accounted byte-for-byte and executed by the observed-subset parser;
- Bitcoin block 358391 header/PoW/local-chain/MTP reconnaissance bound to that proof's Merkle root;
- deterministic CP-001 manifest and CI-tested corruption detection + atomic hash-verified recovery.

C6 closure evidence now additionally includes:
- CP-001 externally submitted to OpenTimestamps calendars and upgraded to two BitcoinBlockHeaderAttestations at block 968161;
- the frozen upgraded proof independently re-executed from anchor digest through OTS operations to the attested Merkle root;
- Bitcoin block 968161 independently rehashed, checked against its compact PoW target, and locally linked to heights 968160 and 968162.

The PASS is deliberately bounded. It does not claim universal OpenTimestamps-format coverage, a full genesis-to-tip best-chain verifier, history completeness, semantic truth of recorded actions, or causal benefit. These are explicit verification boundaries rather than silently assumed properties.

## ORP/Controller

Purpose: choose the next research/engineering action that reduces valid uncertainty under
budget, risk, authority and reversibility constraints.

Allowed decision modes:
1. Probabilistic information gain only when prior and likelihood are explicitly defined.
2. Deterministic finite-hypothesis minimax elimination (ECD T7) when they are not.

It MUST record predicted information gain, actual information gain, uncertainty before/after,
cost, risk, reversibility and decision quality. It MUST NOT invent a prior to make an objective computable.

C7 v2 prospective evidence: the preregistered controller evaluation ran 8/8 held-out live public-code tasks against the locked fixed-exploration baseline. Both policies resolved all tasks; Dream-Replay used 26 probes vs 32 and improved mean frozen utility by 0.1740222739. This closes the C7 gate predicate for that engineering benchmark family only; it does not establish C5 capability, VEA transfer, LoopCell accumulation, or general ORP superiority.

Current convergence state: **PASS (prospective engineering benchmark; scope-limited)**.

## Interaction invariant

ORP/Controller may request ORP/Receipt records.
ORP/Receipt may provide evidence references to the controller.
Neither namespace may silently upgrade the other's result.
