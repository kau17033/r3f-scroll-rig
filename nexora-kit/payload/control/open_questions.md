# OPEN QUESTIONS — UNSPECIFIED / NOT_IDENTIFIABLE 台帳

原文に存在しない値、または特定不能な事項を記録する。**補完を禁止する**（SRC-02 ISO§8）。
`blocks` に挙げたタスクは、解決まで開始しない。

| ID | 事項 | 種別 | 出典 | blocks | status |
|---|---|---|---|---|---|
| OQ-001 | `master_seed_source` の導出式が原文に無い | UNSPECIFIED | SRC-03 §9.5 | T-1xx | OPEN |
| OQ-002 | LoopCell の A1–A13 の定義本文が全ファイルに無い | NOT_IDENTIFIABLE | SRC-04 参照のみ | T-2xx | OPEN |
| OQ-003 | LoopCell の N-01–N-12 の定義本文が無い | NOT_IDENTIFIABLE | SRC-04 参照のみ | T-2xx | OPEN |
| OQ-004 | LoopCell の D-M0-1–6 の定義本文が無い | NOT_IDENTIFIABLE | SRC-04 参照のみ | T-2xx, DEC-006 | OPEN |
| OQ-005 | LoopCell の R-04 の定義本文が無い | NOT_IDENTIFIABLE | SRC-04 参照のみ | T-2xx | OPEN |
| OQ-006 | SRC-06（過去セッション）は認証が必要で内容取得不可 | INFRASTRUCTURE_BLOCKED | SRC-06 | — | CLOSED_AS_NON_AUTHORITATIVE |
| OQ-007 | リポジトリ本体（96a87f4 を含む履歴）の所在 | — | `kau17033/VEA-G3` | T-010 | **CLOSED_RECOVERED**（2026-09-17） |
| OQ-008 | SRC-05 末尾に仕様外の会話断片が混入している | 要判断 | SRC-05 末尾 | T-3xx, DEC-007 | OPEN |
| OQ-009 | 外部 kernel の 27 不変条件の本文が本リポジトリに無い | NOT_IDENTIFIABLE | EXTERNAL-001 | DEC-010 | OPEN |
| OQ-010 | A1–A13 / N-01–N-12 / D-M0-1–6 / R-04 の定義が外部 kernel 側に在るか未確認 | NOT_IDENTIFIABLE | EXTERNAL-001 | T-2xx | OPEN |
| OQ-011 | 外部 `release_check.py` が要求する 4 値（著作権者・著者・URL・セキュリティ連絡先）は実装者が供給できない | UNSPECIFIED | EXTERNAL-001 | 公開判断 | OPEN |
| OQ-012 | `historical_gamma()` の 75/75 は CLASS_H（未検証・ハッシュ無し）。R0=0 の読みが履歴事実に依存する | 要判断 | EXTERNAL-001 | T-010 | OPEN |
| OQ-013 | 「75/75」と、96a87f4 が記録する「19/19 pairs・57/57 source attempts」が一致しない。**同一の量ではない可能性が高く、等値してはならない** | 要判断 | 96a87f4 / EXTERNAL-001 | T-010, T-2xx | OPEN |
| OQ-014 | `vea-g3` に既存の統治文書（PROTOCOL_LOCK / GATE_C_SPECIFICATION / RESEARCH_STATE / COMPLIANCE_MANIFEST）がある。本キットとの責務分担が未定 | 要判断 | vea-g3 リポジトリ構成 | DEC-002, DEC-010 | OPEN |
| OQ-015 | `vea-g3` の `tests/` は pytest 構成。本キットの `tests/`（unittest）を同一ディレクトリに置くと衝突し得る | 要判断 | vea-g3 リポジトリ構成 | DEC-002 | OPEN |

## 種別
- `UNSPECIFIED`: 実行に必要だが原文に値が無い。
- `NOT_IDENTIFIABLE`: 参照はあるが定義本文が到達不能。
- `INFRASTRUCTURE_BLOCKED`: 環境要因で取得不能。仕様の欠落ではない。
