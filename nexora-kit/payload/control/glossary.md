# GLOSSARY — 名前空間の分離

強制変換を禁止する。層をまたぐ語の読み替えは、必ず本表に追記してから行う。

## RQ 番号（CONF-03 / DEC-005）
| 表記 | 定義元 | 意味 |
|---|---|---|
| `VEA-RQ3` | SRC-02 | 経済余剰に関する問い |
| `P4-RQ3` | SRC-03 | TPS 解釈に関する問い |
| `RQ3`（裸） | — | **使用禁止**。曖昧のため断定不可扱い |

## Gate 名前空間（CONF-10 / SRC-01 SOV§13）
| 表記 | 定義元 | 範囲 |
|---|---|---|
| `ULTRA-G0..G16` | SRC-01 | 収束指令のゲート |
| `REPO-GateC` 等 | リポジトリ履歴 | 実装検証ゲート |
| `LC-GATE0..4` | SRC-04 | LoopCell Phase 0 |

## 判定語彙（CONF-09）
| 層 | 語彙 | 変換 |
|---|---|---|
| 工学 | PASS / FAIL / REFUTED / NOT_IDENTIFIABLE / INFRASTRUCTURE_BLOCKED | — |
| VEA-G3 (SRC-02) | S / E / U / N / O | 他層へ変換禁止 |
| LoopCell (SRC-04) | GO / KILL / HOLD / INVALID | 他層へ変換禁止 |
| 観測値 | Y ∈ {0, 1, U} | `U` を 0/1 に丸めない |

## その他
| 語 | 本リポジトリでの定義 |
|---|---|
| `ORP` | SRC-01 の「自律研究コントローラの行動選択仮説」。Outlier Protocol とは別概念 |
| `SSOT` | Single Source of Truth。`sources/` の原文のみを指す |
| `DEFER` | 原文が人間の決定を要求している事項。自律補完を禁止する |
| `UNSPECIFIED` | 実行に必要な値が原文に存在しない状態。補完禁止、依存作業停止 |
