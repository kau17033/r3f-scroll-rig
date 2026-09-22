# ORP/Receipt checkpoint and recovery boundary

Status: **ENGINEERING CONTROL**

This control implements the recovery requirements used by NEXORA without broadening the
scientific claim ceiling.

A checkpoint binds a sorted file set by SHA-256 and optionally binds the preceding checkpoint
hash. A committed checkpoint is written atomically. Recovery is allowed only from backup bytes
whose size and SHA-256 match the checkpoint manifest; restoration is followed by full verification.

This establishes:
- deterministic file identity relative to a manifest;
- corruption/missing-file detection;
- parent-checkpoint linkage;
- hash-verified restoration from a second copy;
- fail-closed refusal of a corrupt backup.

It does **not** establish:
- completeness of the recorded history;
- truth of the recorded action;
- semantic correctness;
- causal improvement;
- external timestamping of the checkpoint.

External anchoring and Bitcoin/header validation are separate evidence layers. C6 MUST remain
PARTIAL until the external checkpoint evidence and recovery evidence are both bound to an actual
ORP/Receipt checkpoint and independently verified.
