# NEXORA CONVERGED SSOT v1.0

Status: **CROSS-REPO CANONICAL CONTROL PLANE**  
Effective: **2026-09-22**  
Scope: **VEA-G3 / LoopCell / Capability Accumulation / ORP / NEXORA integration**

## 0. Purpose

This document is the single cross-repository source of truth for **integration state**.
It does **not** replace a frozen experimental SSOT. It records where authoritative sources live,
what has actually been observed, which transitions are scientifically justified, and what is still blocked.

Core invariant:

```
architecture contains X  !=  system achieves X
stored experience          !=  reusable capability
formal theorem             !=  empirical effect
valid receipt              !=  truthful/complete execution
research closure           !=  hypothesis supported
```

## 1. Authority order

Within each scope, use the highest applicable authority only.

1. Explicit human approval / human-only declaration.
2. Frozen experimental SSOT and protocol lock for that experiment.
3. Immutable empirical evidence, run artifacts, manifests, signed/frozen evidence.
4. This cross-repo convergence control plane.
5. Formal addenda, recovered Work artifacts, implementation reports, audit reports.
6. Historical chat/session claims and unverified summaries.

A lower layer may index or explain a higher layer. It may not silently modify it.

## 2. Canonical state representation

Current state is not hand-authored prose.

Authoritative machine-readable inputs:

- `control/source_registry.csv`
- `control/state_events.csv` — append-only current-state evidence events
- `control/completion_gates.csv` — gate definitions, not hand-written current statuses
- `control/transitions.csv` — transition definitions, not hand-written current statuses

Derived state:

- `control/STATE.generated.json`
- generated and checked by `tools/state_reduce.py`

`control/STATE.md` is a human-readable projection only. If prose and generated state disagree,
the generated state wins for cross-repository current-state reporting.

## 2.1 Physical hosting

The logical canonical control plane is now singular, but its final physical host is not yet converged.
DEC-002 still designates `kau17033/nexora-core` as the final integration repository.
Until that repository exists and migration is hash-verified, this PR branch is the **BOOTSTRAP_CANONICAL_CARRIER**.
Migration MUST be a move-with-verification: do not leave two writable canonical copies.
C0 cannot close while final-host convergence is incomplete.

## 3. Layer model

```
Frozen Evidence / Authority
          |
          v
VEA-G3 -- experience validity / applicability
          |
      TR-01 gate
          v
LoopCell -- STORE / IDENTIFY / RETRIEVE / VERIFY / APPLY / MEASURE / REUSE
          |
      TR-02 gate
          v
Capability State K_t -- baseline / repeat / retention / generalization / interference / cost
          |
      TR-03 gate
          v
ORP/Controller -- next scientific action under evidence / cost / risk / authority constraints

ORP/Receipt is orthogonal evidence infrastructure:
identity + canonical bytes + signatures + provenance/checkpoints.
It does not itself prove capability or scientific validity.
```

## 4. Current convergence facts

### VEA-G3

- Existing cross-repo audit records the 2026-09-09 serial-spine execution as a valid terminal research state.
- G4 is CLOSED with `FAIL / NOT_IDENTIFIABLE`; treatment population D is empty and tau is uncomputable.
- This is research closure, not evidence that VEA efficacy is positive.
- HD-53 First-Completion remains human-only.

### LoopCell

- Phase 0 SSOT v1.1.2 is frozen.
- The canonical Phase 0 experiment has not been executed in the recovered state.
- No capability promotion may be inferred from implementation or storage alone.

### Capability Accumulation

- `NEXORA_ECD_Model_v1` supplies the formal integration model and T1-T8 conditional results.
- The formal model is an addendum, not a retroactive rewrite of frozen VEA/LoopCell experiments.
- Actual transfer rate, effect, NES, retention, generalization and interference remain empirical quantities.

### ORP

Two namespaces are mandatory:

- `ORP/Receipt`: cryptographic/provenance receipt protocol.
- `ORP/Controller`: evidence-governed research/action controller.

A valid receipt is not proof that an action was complete, truthful, scientifically valid or beneficial.

## 5. Completion predicate

NEXORA is complete only when C0-C8 are all closed as PASS in the generated state.

| Gate | Predicate |
|---|---|
| C0 Corpus Convergence | authoritative sources identified/frozen; no silent source substitution |
| C1 Repository Truth | current state derivable from append-only events and consistent across repositories |
| C2 VEA Research Closure | frozen execution/evidence/claim ceiling/human closure resolved |
| C3 VEA→LoopCell | identity + provenance + retrieval + verification + application + measured benefit demonstrated |
| C4 LoopCell | STORE/IDENTIFY/RETRIEVE/VERIFY/APPLY/MEASURE/REUSE separately demonstrated |
| C5 Capability | K_t definition + baseline + repeat + retention + generalization + interference + cost closed |
| C6 ORP/Receipt | interoperable receipt + signature + checkpoint/recovery + verification boundaries closed |
| C7 ORP/Controller | prospective action-selection evaluation closes actual information/cost outcome loop |
| C8 Operational Release | authority/security/recovery/reproducibility/cost ceiling/rollback/final audit closed |

Current statuses live only in `state_events.csv` and are projected by the reducer.

## 6. No-teleportation transition rules

### TR-01 VEA-G3 → LoopCell

Requires validity, identity, provenance, retrieval, verification, application and measured benefit.  
Current state: **BLOCKED_EVIDENCE**.

### TR-02 LoopCell → Capability

Requires verified reuse, operational K_t, baseline, repeated measurement, retention,
generalization and interference assessment.  
Current state: **NOT_EXECUTED**.

### TR-03 Capability → ORP/Controller

Requires machine-readable capability identity, validity, applicability, cost and limitations,
plus evidence that the capability is actionable.  
Current state: **FORMAL_ONLY**.

### TR-04 ORP/Receipt support

Receipt infrastructure may bind evidence at any layer, but never promotes a scientific layer.  
Current state: **SUPPORTING_ONLY**.

## 7. Scientific change control

Never mutate a frozen experiment to rescue a blocked, null, negative or unidentifiable result.

If a materially different treatment, policy, estimator, endpoint, stopping rule or model is required:

1. preserve the old experiment as closed historical evidence;
2. create a new protocol/phase;
3. preregister the changed assumptions and estimand;
4. run it as a new experiment.

## 8. Unknown / invention boundary

Unknowns are classified before work:

- `REDUCIBLE`: collect evidence.
- `COSTLY`: defer or require explicit budget approval.
- `STRUCTURALLY_NOT_IDENTIFIABLE`: redesign the experiment.
- `FORMAL_OPEN`: new theorem/model may be required.
- `ENGINEERING_GAP`: implement/test without changing scientific meaning.
- `HUMAN_ONLY`: do not synthesize a machine decision.

New mechanisms remain proposals until implementation, falsification and evidence close the relevant gate.

## 9. Required invariants

1. Every current-state claim points to evidence or an explicit human directive.
2. Every frozen source has an immutable identifier before it can close C0.
3. Work/Library artifacts without a content hash are `RECEIVED_UNHASHED`, never silently canonical.
4. A recovered historical claim is `RECOVERED`, not `VERIFIED`, until reproduced or bound to primary artifacts.
5. `UNKNOWN`, `NOT_IDENTIFIABLE`, `FAIL`, `HOLD`, `BLOCKED` and `NOT_EXECUTED` are not interchangeable.
6. Capability count is never inferred from artifact count.
7. ORP/Receipt authenticity is never upgraded into content truth or scientific validity.
8. The reducer fails closed on duplicate IDs, illegal states, missing gate/transition events, invalid immutable refs or snapshot drift.
