# T-070 — cross-repository convergence closure

blocked_by: T-050, T-060, DEC-008  
unlocks: migration into the final canonical host, then scoped research execution

## Objective

Determine whether the **control plane itself** has converged. Do not conflate this with
scientific/operational completion C2-C8.

## Acceptance

```bash
python3 tools/convergence_gate.py
```

Required structural checks:

1. source registry / immutable-source evidence passes;
2. section disposition passes;
3. 1,652/1,652 requirement normalization passes;
4. all recorded conflicts are terminal or explicitly HG-bound;
5. 1,652/1,652 traceability passes without claiming satisfaction;
6. HG registry is structurally valid;
7. deterministic state projection passes;
8. the final canonical physical host is verified.

Checks 1-7 pass. DEC-012 selected `kau17033/kau17033-nexora-core` as the final host. Check 8 remains open until payload byte/tree equivalence, final-host event, and destination CI are verified.

## Separation from global completion

`tools/gate_check.py` remains the stricter global completion/release gate and may remain
BLOCKED while C2-C8, scientific transitions, security/recovery, or human gates remain open.

T-070 MUST NOT zero `audit70.csv` merely to unlock engineering work.

## Human/scientific boundary

HG-* gates are **out of scope for structural convergence**. They continue to block only the
specific experimental, paid, legal, or human-authority actions listed in
`control/human_gates.csv`.
