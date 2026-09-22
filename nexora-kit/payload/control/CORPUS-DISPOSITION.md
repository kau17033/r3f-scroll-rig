# Corpus section disposition scope

Status: **DERIVED / MACHINE-VERIFIED**  
Effective: 2026-09-22

T-030 indexes and dispositions only sources that can normatively constrain the integrated program:

- SRC-01 — cross-program engineering/research governance.
- SRC-02A / SRC-02B — VEA-G3 frozen SSOT / protocol lock, VEA scope only.
- SRC-03 — paper/protocol candidate, retained as reference without execution authority.
- SRC-04A / SRC-04B — LoopCell Phase 0 frozen SSOT / freeze manifest, LoopCell scope only.

Recovery reports, audits, product analyses, formal addenda and Dream-RSI are evidence/method sources.
They remain in source_registry.csv but are not silently promoted into normative requirements.

Section bodies are **not copied** into this repository. Local DOCX sections are bound by SHA-256 of
their exact extracted paragraph block plus the source-file SHA-256. GitHub SSOT sections are bound
to the immutable parent git blob. The full section ledger is sharded under control/corpus_sections/.

Disposition meanings:
- KEEP_GOVERNANCE: retain as cross-program governance input.
- SCOPE_AUTHORITY: authoritative only inside its declared frozen experiment scope.
- REFERENCE_ONLY: retained for claims/design context; cannot authorize execution.
- CONFLICT_RECORDED: retained but blocked by a conflict record.
- DEFER_HUMAN: retained but execution requires an explicit human decision.
- SUPERSEDED: historical section retained for provenance but not current control.
- NOT_APPLICABLE: retained but outside current integrated scope.

T-030 does not resolve T-050 conflicts and does not promote a candidate paper or external research
method into an experimental SSOT.
