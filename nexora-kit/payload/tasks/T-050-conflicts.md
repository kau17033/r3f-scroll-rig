# T-050 — conflict convergence

blocked_by: T-040

## Objective

Classify every recorded cross-source conflict without silently selecting the hypothesis-favorable side.

## Terminal classes

- RESOLVED
- SUPERSEDED
- OPEN only when bound to an explicit scoped HG-* human gate.

An OPEN human-gated scientific conflict does not block unrelated convergence work, but it
continues to block the exact scientific execution listed by that human gate.

## Acceptance

python3 tools/conflict_check.py

Expected: CONFLICTS: PASS (19/19 classified; open_scientific=3 human_gated=3)
