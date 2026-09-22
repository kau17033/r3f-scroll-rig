# T-060 — repository reality traceability

blocked_by: T-040, DEC-002

## Objective

Bind every normalized requirement to an explicit task, verification surface, and evidence location.
Trace coverage is not equivalent to requirement satisfaction.

## Status semantics

- TRACE_BOUND_NOT_CLAIMED_SATISFIED
- FROZEN_REQUIREMENT_TRACE_BOUND
- FROZEN_REQUIREMENT_TRACE_BOUND_NOT_EXECUTED
- REFERENCE_ONLY

No row may use SATISFIED merely because a source or test exists.

## Acceptance

python3 tools/traceability_check.py

Expected: TRACEABILITY: PASS (requirements=1652 traced=1652 satisfaction_not_implied=true)
