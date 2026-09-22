# STATE — current convergence projection

- Phase: **P0.5 / CONVERGENCE_BASELINE**
- Canonical cross-repo SSOT: **control/CONVERGED-SSOT.md**
- Machine-readable source/evidence state: **source_registry.csv + state_events.csv**
- Gate definitions: **completion_gates.csv + transitions.csv**
- Derived snapshot: **control/STATE.generated.json**
- Reducer: **tools/state_reduce.py**
- 実装解禁: **NO**. The existing implementation gate remains fail-closed.
- Updated: **2026-09-22**

## Verified corrections to the previous hand-maintained state

- T-000 is not TODO. GitHub Actions run `35190376080` already verified it.
- VEA-G3 / LoopCell external canonical files were revalidated on 2026-09-22: **34/34 blob SHA MATCH**.
- VEA-G3 live `GATE_STATUS.json` now governs current-state wording: G4 is **BLOCKED**, `closure=null`, with `FAIL / NOT_IDENTIFIABLE` only as the closure candidate pending HD-53; truth state remains NOT_DETERMINABLE and tau is uncomputable.
- LoopCell Phase 0 is **NOT_EXECUTED** in the recovered state.
- Capability has a formal ECD layer, but empirical accumulation is **NOT_EXECUTED**.
- ORP is split into `ORP/Receipt` and `ORP/Controller`.

## Current completion gates

C0 PARTIAL / C1 PARTIAL / C2 PARTIAL / C3 BLOCKED_EVIDENCE /
C4 NOT_EXECUTED / C5 FORMAL_ONLY / C6 PARTIAL_PASS / C7 FORMAL_ONLY / C8 BLOCKED.

The exact current state and evidence references are in `control/STATE.generated.json`.
If this prose disagrees with generated state, generated state is authoritative for cross-repository current-state reporting.

## Next executable work

1. T-005 is **VERIFIED** by CI run `35728612031`.
2. T-010 is **IN_PROGRESS**: local attachments are SHA-256 fixed and external 34/34 validation is recorded; CI verification remains.
3. T-012 Dream-Replay controller substrate is **IN_PROGRESS** and diagnostic-only until prospective validation.
4. After T-010/T-012 CI closure, continue disposition / requirements / traceability without changing frozen experiments.
