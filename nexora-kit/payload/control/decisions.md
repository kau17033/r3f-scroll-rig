# DECISIONS — 人間判断キュー

Claude Code は本ファイルに **起案** のみ行う（`/decision`）。Status の変更は人間が commit する。
Status: PENDING / APPROVED / REJECTED / DEFERRED。

| ID | 内容 | 依存 CONF | 影響タスク | Status |
|---|---|---|---|---|
| DEC-001 | 権威階層の承認（CONF-01）と SRC-02 のロック状態確定（CONF-02） | 01, 02, 09, 10 | T-020 以降すべて | PENDING |
| DEC-002 | 対象リポジトリ（既存 / 新規） | — | T-010 | PENDING |
| DEC-003 | VEA-G3 モデル束縛（provider / model_id / snapshot / endpoint / decoding） | 06 | T-020, T-1xx | PENDING |
| DEC-004 | Phase A 固定値一式（下表） | 04, 07 | T-1xx | PENDING |
| DEC-005 | RQ 番号の名前空間化 | 03 | T-040 | PENDING |
| DEC-006 | LoopCell Phase 0 SSOT v1.1 本文の投入、D-M0-2 の承認、モデル/価格の決定 | — | T-2xx | PENDING |
| DEC-007 | Outlier v1.0 の現行性確認と法務ゲート | — | T-3xx | PENDING |
| DEC-008 | 優先順位は SOV§114 と SOV§181 のどちらか | 05 | T-070 | PENDING |
| DEC-009 | コスト方針のスコープ分割 | 08 | T-2xx, T-3xx | PENDING |

## DEC-004 の内訳（すべて未決。1 つでも欠ければ Phase A を開始しない）
| 項目 | 値 | 根拠 |
|---|---|---|
| 主要指標 | PENDING | — |
| 推定対象（ITT / pair-complete ∩ received-valid） | PENDING | CONF-04 |
| α | PENDING | SRC-03 候補: 片側 0.05 |
| 検出力 | PENDING | SRC-03 候補: 0.80 |
| MDE（τ） | PENDING | SRC-03 候補: 0.10 |
| N（n_pair） | PENDING | SRC-03 候補: 153（生成 184） |
| 多重比較 | PENDING | — |
| CF の種別 | PENDING | — |
| AFR 閾値 | PENDING | — |
| 意味的汚染の方法と閾値 | PENDING | — |
| 人件費の時給 | PENDING | — |
| 1 use の定義 | PENDING | — |
| 経済 MDE | PENDING | — |

注: SRC-03 の候補値は **候補** であり、採用の可否自体が DEC-004 の一部である（SRC-03 に実行権限はない）。

## 起案フォーマット
```
| DEC-0NN | <決定すべき一文> | <CONF-ID または —> | <影響タスク> | PENDING |
```
起案時は本文末尾に、選択肢 A/B と各々の帰結、決定しない場合に停止する作業を併記する。
