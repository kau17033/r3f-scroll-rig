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
| OQ-007 | リポジトリ本体（96a87f4 を含む履歴）の所在 | NOT_IDENTIFIABLE | 履歴記述のみ | T-010, DEC-002 | OPEN |
| OQ-008 | SRC-05 末尾に仕様外の会話断片が混入している | 要判断 | SRC-05 末尾 | T-3xx, DEC-007 | OPEN |

## 種別
- `UNSPECIFIED`: 実行に必要だが原文に値が無い。
- `NOT_IDENTIFIABLE`: 参照はあるが定義本文が到達不能。
- `INFRASTRUCTURE_BLOCKED`: 環境要因で取得不能。仕様の欠落ではない。
