# T-005 — Convergence baseline reducer

blocked_by: T-000

## Objective

Make cross-repository current state a deterministic projection of append-only evidence/state events,
instead of a manually maintained narrative.

## Inputs

- control/source_registry.csv
- control/state_events.csv
- control/completion_gates.csv
- control/transitions.csv

## Outputs

- control/STATE.generated.json
- tools/state_reduce.py
- tests/test_state_reduce.py

## Acceptance

`python3 tools/state_reduce.py --check` exits 0 and the complete unit-test suite passes in CI.

## Scientific boundary

This task may reconcile state metadata. It MUST NOT modify any frozen experiment, endpoint,
estimand, treatment, statistical rule, model binding, corpus or empirical artifact.
