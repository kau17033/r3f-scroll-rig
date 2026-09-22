# NEXORA Final Host Migration Plan

Status: **READY_TO_EXECUTE / TARGET_REPOSITORY_ABSENT**  
Target: **`kau17033/kau17033-nexora-core` (private)**  
Source carrier: `kau17033/r3f-scroll-rig` PR #1, subtree `nexora-kit/payload/`

## 1. Purpose

Move the single logical NEXORA control plane from the bootstrap carrier into DEC-002's
final physical host without creating two writable canonical copies.

This is a physical-host migration only. It does not change frozen VEA-G3 / LoopCell
scientific authority, does not satisfy HG-* gates, and does not promote C2-C8.

## 2. Human prerequisite

Use the explicitly selected private GitHub repository:

`kau17033/kau17033-nexora-core`

The selected repository currently has a single initial `README.md` commit. Migration MUST construct a new root tree from the payload only, so the final working tree contains no bootstrap README. The GitHub connection has admin/push access.

Repository creation itself is currently outside the available GitHub connector capabilities.

## 3. Migration source

At execution time, freeze:

- source repository
- source branch
- exact source commit SHA
- exact `nexora-kit/payload/` tree SHA
- destination initial HEAD (or EMPTY)
- migration timestamp

Do not use a remembered SHA. Re-read the current PR head immediately before migration.

## 4. Copy rule

Copy **the contents of `nexora-kit/payload/` to the root of `kau17033-nexora-core`**,
preserving relative paths and bytes.

Do not copy the carrier repository's unrelated r3f-scroll-rig application files.
Do not make VEA-G3 or LoopCell source copies canonical; their external immutable references remain external.

The payload's own `.github/workflows/` becomes the final-host workflow surface.
The carrier-only top-level `.github/workflows/nexora-kit.yml` is not part of the payload.

## 5. Verification

Before authority cutover, verify all of the following in the destination:

1. file-set equality against the frozen source subtree;
2. content equality for every copied file;
3. `python3 tools/kit_check.py` passes;
4. `python3 tools/source_registry_check.py` passes;
5. `python3 tools/disposition_check.py` passes;
6. `python3 tools/requirements_check.py` passes;
7. `python3 tools/conflict_check.py` passes;
8. `python3 tools/traceability_check.py` passes;
9. `python3 tools/state_reduce.py --check` passes;
10. `python3 tools/convergence_gate.py` passes after the final-host event is appended.

If any comparison is UNKNOWN or mismatched, **do not cut over**.

## 6. Authority cutover

Only after destination verification:

- append a new state event setting `NEXORA:FINAL_HOST = VERIFIED`;
- append a C0 event only if its predicate is then fully satisfied;
- regenerate `STATE.generated.json`;
- rerun full CI in `kau17033-nexora-core`;
- record the destination run/commit as migration evidence;
- mark this bootstrap carrier **NON_CANONICAL / READ_ONLY_REFERENCE** in its control-plane prose.

Do not delete historical evidence from this carrier. Do not leave it as a second writable SSOT.

## 7. Rollback

Until cutover is verified, the bootstrap carrier remains authoritative for cross-repo integration state.
If destination verification fails, discard/repair the destination copy and keep authority here.
No scientific state changes as a result of migration failure.

## 8. Completion condition

Migration is complete only when:

`destination_exists && byte_equivalent && full_checks_pass && final_host_event_verified && destination_CI_pass`

Until then, T-070 remains `BLOCKED_FINAL_HOST`.
