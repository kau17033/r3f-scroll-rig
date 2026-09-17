# OPEN QUESTIONS — UNSPECIFIED / NOT_IDENTIFIABLE 台帳

原文に存在しない値、または特定不能な事項を記録する。**補完を禁止する**（SRC-02 ISO§8）。
`blocks` に挙げたタスクは、解決まで開始しない。

| ID | 事項 | 種別 | 出典 | blocks | status |
|---|---|---|---|---|---|
| OQ-001 | `master_seed_source` の導出式が原文に無い | UNSPECIFIED | SRC-03 §9.5 | T-1xx | OPEN |
| OQ-002 | LoopCell の A1–A13 の定義本文 | — | `loopcell:experiments/loopcell_phase0/spec/reference/assertions.json` | T-2xx | **CLOSED_RECOVERED**（13 件すべて定義あり） |
| OQ-003 | LoopCell の N-01–N-12 の定義本文 | NOT_IDENTIFIABLE | SRC-04 | T-2xx | OPEN。候補: `spec/reference/reject_reasons.json`（REPO-003 §2） |
| OQ-004 | LoopCell の D-M0-1–6 の定義本文 | NOT_IDENTIFIABLE | SRC-04 | T-2xx, DEC-006 | OPEN。候補: `DECISIONS/decision-log.md`（REPO-003 §2） |
| OQ-005 | LoopCell の R-04 の定義本文 | NOT_IDENTIFIABLE | SRC-04 | T-2xx | OPEN。候補: `spec/reference/` 配下（REPO-003 §2） |
| OQ-006 | SRC-06（過去セッション）は認証が必要で内容取得不可 | INFRASTRUCTURE_BLOCKED | SRC-06 | — | CLOSED_AS_NON_AUTHORITATIVE |
| OQ-007 | リポジトリ本体（96a87f4 を含む履歴）の所在 | — | `kau17033/VEA-G3` | T-010 | **CLOSED_RECOVERED**（2026-09-17） |
| OQ-008 | SRC-05 末尾に仕様外の会話断片が混入している | 要判断 | SRC-05 末尾 | T-3xx, DEC-007 | OPEN |
| OQ-009 | 外部 kernel の 27 不変条件の本文が本リポジトリに無い | NOT_IDENTIFIABLE | EXTERNAL-001 | DEC-010 | OPEN |
| OQ-010 | A1–A13 / N-01–N-12 / D-M0-1–6 / R-04 の定義が外部 kernel 側に在るか未確認 | NOT_IDENTIFIABLE | EXTERNAL-001 | T-2xx | OPEN |
| OQ-011 | 外部 `release_check.py` が要求する 4 値（著作権者・著者・URL・セキュリティ連絡先）は実装者が供給できない | UNSPECIFIED | EXTERNAL-001 | 公開判断 | OPEN |
| OQ-012 | `historical_gamma()` の 75/75 と R0=0 の読み | **誤用の疑い** | EXTERNAL-001 / REPO-001 §6 | T-010 | **OPEN（重大度上昇）**。リポジトリは当該 75 件を `NOT ASSESSABLE` としている。評価不能な対象に確定値を与える読みであり、R0=0 を事実として使ってはならない |
| OQ-013 | 「75 件の outcome（NOT ASSESSABLE）」「19/19 pairs」「57/57 source attempts」は時点も単位も異なる 3 つの量である。**等値してはならない** | 確認済（判断は不要） | 96a87f4 / REPO-001 §6 | T-010 | **CLOSED_AS_DISTINCT** |
| OQ-014 | `vea-g3` の既存統治文書と本キットの責務分担 | 要判断 | REPO-001 | DEC-010 | OPEN。ただし構成 A により物理的な衝突は解消済。残るのは権威の重複のみ |
| OQ-016 | `SPEC.md` v2.0 が unrecovered。コードが引用する §9.1/9.2/9.3/9.5 は現行 v2.1 に存在しない（grep 0 件） | NOT_IDENTIFIABLE | REPO-001 §7 | T-040 | OPEN |
| OQ-017 | `LLMClient.__init__` が Ollama でも非空 api_key を要求する。実クライアント構築を塞ぐ | 実装待ち（人間判断は不要） | REPO-002 §5 | 実行フェーズ | OPEN |
| OQ-018 | `complete()` の状態が 2 文書で不整合。Manifest は `NotImplementedError` スタブ、PROTOCOL_LOCK は `think` パラメータを既存機能として記述 | NOT_IDENTIFIABLE | REPO-001 §4 / REPO-002 §5 | 実行フェーズ | OPEN。コードの直接確認を要する |
| OQ-015 | `vea-g3` の `tests/` は pytest 構成。本キットの `tests/`（unittest）を同一ディレクトリに置くと衝突し得る | 要判断 | vea-g3 リポジトリ構成 | DEC-002 | **RESOLVED**（キットは `nexora-core` に置く。同居しない） |

## 種別
- `UNSPECIFIED`: 実行に必要だが原文に値が無い。
- `NOT_IDENTIFIABLE`: 参照はあるが定義本文が到達不能。
- `INFRASTRUCTURE_BLOCKED`: 環境要因で取得不能。仕様の欠落ではない。
