# T-040 — requirement normalization

blocked_by: T-030  
unlocks: T-050, T-060

## Objective

Normalize every one of the 1,652 disposed source sections into an addressable
requirement/reference record without silently replacing the source semantics.

## Canonical representation

`control/requirements.csv` contains exactly one `REQ-xxxxx` per section.

- `source_ref`: canonical section ID.
- `quote_ref`: immutable section SHA-256 or frozen source-blob binding.
- `normalized_requirement`: scope-preserving operational wrapper. The underlying
  section remains authoritative; the wrapper does not become a substitute source.
- `type`: normalized requirement class.
- `scope`: NEXORA / VEA-G3 / LoopCell / REFERENCE.
- `verifiable`: explicit verification class.

Frozen VEA-G3 and LoopCell sections retain experiment-scope authority.
SRC-03 remains `REFERENCE_ONLY / NOT_EXECUTABLE`: normalization cannot grant it
execution authority.

## Acceptance

```
python3 tools/requirements_check.py
# REQUIREMENTS: PASS (rows=1652 coverage=1652/1652 PENDING=0)
```

## Prohibitions

- Do not invent a scientific value.
- Do not use a normalized row to override its source section.
- Do not turn a reference-only paper section into an executable requirement.
- Do not collapse unresolved human/scientific gates into an automatic decision.
