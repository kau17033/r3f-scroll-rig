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

Current convergence state: **PARTIAL_PASS**.

Verified engineering evidence now includes:
- recovered Slice 1 cross-language signature/canonical-byte conformance;
- one real upstream OpenTimestamps proof accounted byte-for-byte and executed by the observed-subset parser;
- Bitcoin block 358391 header/PoW/local-chain/MTP reconnaissance bound to that proof's Merkle root;
- deterministic CP-001 manifest and CI-tested corruption detection + atomic hash-verified recovery.

Still outside C6 closure:
- CP-001 itself is not yet anchored by an independent external timestamp/checkpoint;
- the OTS parser is intentionally an observed subset, not a claim of universal OTS-format coverage;
- the Bitcoin reconnaissance validates a historical local window, not a complete production best-chain verifier from genesis/checkpoint.

## ORP/Controller

Purpose: choose the next research/engineering action that reduces valid uncertainty under
budget, risk, authority and reversibility constraints.

Allowed decision modes:
1. Probabilistic information gain only when prior and likelihood are explicitly defined.
2. Deterministic finite-hypothesis minimax elimination (ECD T7) when they are not.

It MUST record predicted information gain, actual information gain, uncertainty before/after,
cost, risk, reversibility and decision quality. It MUST NOT invent a prior to make an objective computable.

Current convergence state: **FORMAL_ONLY**.

## Interaction invariant

ORP/Controller may request ORP/Receipt records.
ORP/Receipt may provide evidence references to the controller.
Neither namespace may silently upgrade the other's result.
