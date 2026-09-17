# PROPOSAL-001 — `vea-g3/COMPLIANCE_MANIFEST.md` 再生成案

**これは提案である。適用は人間が行う。** 本キットは `vea-g3` に一切書き込まない。

根拠: `PROTOCOL_LOCK.md`（blob `e535476b…`）、`llm_client.py`（blob `5b9bdde3…`）、
`SERIAL_SPINE_R5_640_RESULT.md`（blob `d114bafd…`）、`GATE_STATUS.json`（blob `0c57fe58…`）。

## 0. なぜ再生成が要るか

Manifest は現状より古い箇所を **3 系統**持つ。いずれも「実装が進んだのに文書が追随していない」型である。

## 1. 行 7 / 8 / 9 — `UNSPECIFIED` → `LOCKED`

| # | 項目 | 現在の記載 | あるべき記載 | 根拠 |
|---|---|---|---|---|
| 7 | Primary endpoint | UNSPECIFIED / Class-B `DEFERRED_FIRST_RUN` | **LOCKED** `terminated == True`（`validity.determine_outcome`）。解釈上の留保（運用上の成功エンドポイントであり、それ自体を因果的有効性の証明として読まない）をロックの一部として併記 | PROTOCOL_LOCK Class B |
| 8 | Effect estimator | UNSPECIFIED | **LOCKED** `tau_hat = risk(C1-VEA) − risk(C0)` | 同上 |
| 9 | Effect direction | UNSPECIFIED | **LOCKED** `C1-VEA − C0 > 0` | 同上 |

## 2. 行 39 — UNSPECIFIED 一覧の是正

現在の記載: 「(2, 7, 8, 9, 11, 12, 13, 14\*, 15\*, 23, 25, 26, 27, 28, 30, 31, 32, 33)」

**誤っている項目**: 7 / 8 / 9 / 11 / 25 / 26 / 27 / 28 / 30 はいずれも同文書内で **LOCKED** と記載されている。

あるべき一覧（UNSPECIFIED として残るもの）:

```
2  Experiment ID
12 Evaluation generation rule
13 Novelty rule          （task 選定に依存）
14 Contamination rule    （PARTIAL、dataset 依存）
15 Leakage rule          （PARTIAL、Class-C 依存）
23 Scaffold version
31 Stopping rule         （※ max_local_steps=640 / parse_failure_threshold=0 との関係を要整理）
32 Cost rule             （Class-C、SPEC §63 により MVP 外）
33 Human-cost rule       （同上）
```

**注意**: 行 31（Stopping rule）は、PROTOCOL_LOCK に `n_rule: fixed-N` と
`max_local_steps: 640` があるため「未決」か「決定済」か両義的である。
**本提案では断定しない。** 人間が区別を明記すること。

## 3. 行 42 — `complete()` の記述

現在の記載:

> **Still blocking actual execution**: `llm_client.py`'s `complete()` remains an intentional
> `NotImplementedError` stub (Layer C, not yet implemented) -- building real Ollama HTTP
> integration is the next concrete engineering step, now authorized but not yet done.

**実際**（`llm_client.py` 直接確認）:

- `complete()` は `provider="Ollama"` に対し**実装済**。`/api/generate` への非ストリーミング POST
- `NotImplementedError` は **Ollama 以外の provider に対してのみ**送出
- `think` パラメータ実装済み（top-level フィールド）
- `api_endpoint` / `temperature` / `top_p` / `max_output_tokens` は既定値を持たず、`None` なら `ValueError`
- 失敗は `ProviderRequestError`。プレースホルダ文字列を返さない

あるべき記載（案）:

> Execution Authorization RECEIVED. `complete()` implements the real Ollama request path
> (`/api/generate`, non-streaming); `NotImplementedError` is raised only for non-Ollama
> providers. `LLMClient.__init__` still requires a non-empty value in `api_key_env_var`
> even for Ollama — this is INVARIANT INV-9 ("never silently defaulted"), not a defect;
> it is satisfied by configuration, not by a code change.

## 4. 追加すべき節 — Serial spine の完了と G4 の閉鎖

Manifest の現行本文は R5@640 以前の状態を前提としている。次の事実が未反映である。

```
2026-09-09, GitHub Actions ubuntu-latest (2 vCPU / 7.8 GiB, x86_64), frozen bf276fe:
  H-2                   ESTABLISHED   (human H2-1 ratified; 5.37 s/step)
  Gate A                PASS          (pytest 372; provenance 14/14; self-checks)
  Runtime Identity      PASS          (0.32.13 == freeze)
  Gate B                num_ctx = 4096 (measured)
  Freeze Check          PASS
  R5 @ 640              COMPLETE      run 34294080720, 6/6, A/B byte-identical,
                                      all 3 LOCKED seeds non-terminating
  ONE VALID TREATMENT   COMPLETE      run 34296827883, 2/2 SSF / outcome "U"
  10-pair pilot         COMPLETE      run 34301420718, 20/20, population_D_size = 0
  G4 SELECTION GATE     CLOSED        FAIL / NOT_IDENTIFIABLE
  tau                   UNCOMPUTABLE
  VEA-G3 EFFICACY       NOT DETERMINABLE
  MANDATORY STOP        REACHED       (155-pair requires explicit human GO; HD-53 pending)
```

## 5. 適用手順（人間が実行）

1. 上記 1〜4 を `COMPLIANCE_MANIFEST.md` に反映する。
2. **`SPEC.md` §77 の 42 項目の構造を変えない。** 行の追加・削除ではなく、
   `Status` 列と `Evidence` 列の更新に留める（§4 のみ Addendum として追記）。
3. 変更は追加的・非科学的である旨を明記する。`PROTOCOL_LOCK.md` の値は**一切変更しない**。
4. 反映後、`freeze_gate.check_gate()` を再実行し `passed=true` を確認する。

## 6. 本提案が触れないもの

`PROTOCOL_LOCK.md` の全値 / `SPEC.md` 本文 / `runs/g3/*.json` / `evidence/**` /
凍結 SHA `bf276fe4…` のツリー。

`ROOT_CAUSE.md` §16「変更してはならないもの」の全項目を尊重する。
本提案は**文書の現状追随のみ**であり、実験条件には一切触れない。
