# CONFLICTS — 実行を止める矛盾

記録規則（SRC-02 ISO§9）: 矛盾は解消せず記録し停止する。自分に有利な側を選ばない。
`resolution` 列は **提案** であり、`decision` 列の DEC が APPROVED になるまで採用しない。

| ID | 衝突 | 出典 | 処置案 | decision | status |
|---|---|---|---|---|---|
| CONF-01 | 権威階層が 4 系統で不一致 | SRC-02 ISO§1 / SRC-01 CONV§3・SOV§4 / SRC-04 §2 | スコープ分割（AUTHORITY.md §1） | DEC-001 | OPEN |
| CONF-02 | SRC-02 が「唯一の正式な SSOT」と「Status: SSOT Candidate」を併記 | SRC-02 冒頭 | ロック状態を人間が確定 | DEC-001 | OPEN |
| CONF-03 | `RQ3` の意味衝突（経済余剰 / TPS 解釈） | SRC-02, SRC-03 | `VEA-RQ3` / `P4-RQ3` へ分離 | DEC-005 | OPEN |
| CONF-04 | 主推定対象の衝突（ITT vs pair-complete ∩ received-valid） | SRC-01 SOV§7.1 / SRC-03 U-A-12 | Phase A 前に確定。受領で条件付ける集団は ITT と一致しない | DEC-004 | OPEN |
| CONF-05 | 優先順位の衝突（P0–P22 と 27 段） | SRC-01 SOV§114 / SOV§181 | 時系列で解決し §181 を採用（提案） | DEC-008 | OPEN |
| CONF-06 | モデル選定の衝突（履歴 qwen3:8b / SRC-03 DEFER / 過去モデル持込禁止） | 履歴 / SRC-03 / SRC-02 ISO§2 | 新規に人間が決定 | DEC-003 | OPEN |
| CONF-07 | 標本数の衝突（履歴 155/arm と計画 n_pair=153・生成 184） | 履歴 / SRC-03 | 混同禁止。現行値は未ロック | DEC-004 | OPEN |
| CONF-08 | コスト方針の緊張（ローカル優先 vs 有料 API 前提） | SRC-01 SOV§104・§175 / SRC-04 / SRC-05 | スコープで分割 | DEC-009 | OPEN |
| CONF-09 | 判定語彙が 5 系統に分岐 | 全正本 | 層別対応表（glossary.md）。強制変換禁止 | DEC-001 | OPEN |
| CONF-10 | Gate 番号の多重化 | SRC-01 / 履歴 / SRC-04 | 名前空間分離（SRC-01 SOV§13 準拠） | DEC-001 | OPEN |
| CONF-11 | 任意停止の可否（517/1055/1056 が禁止、1173 が適応的 argmax IG/cost を要求） | SRC-01（節番号は外部提出物からの参照。原文未投入のため未照合） | 外部提出物は e-value による解決を主張。M1–M4 は PASS（EXTERNAL-001）。採用は未決 | DEC-004 | OPEN |
| CONF-12 | 統治系が二重（外部 27 不変条件 vs 本キットの control/ 台帳） | EXTERNAL-001 / 本キット | どちらを正とするか、または責務を分割するか | DEC-010 | OPEN |
| CONF-13 | `ORP` に 3 つの意味（SRC-01 の行動選択仮説 / Outlier Protocol / ブランド層の統合・運用基盤） | SRC-01, SRC-05, 命名体系案 | `SOV-ORP` / `OUTLIER-ORP` / `BRAND-ORP` に分離し、裸の `ORP` を禁止（RQ3 と同処置） | DEC-011 (APPROVED) | **RESOLVED**（glossary.md に処置を適用。表記の分離のみで、いずれの定義も変更していない） |

## 記録フォーマット（新規追加時）
```
| CONF-NN | <一文で衝突> | <SRC-xx §/L範囲> | <処置案> | DEC-xxx | OPEN |
```
`status` は OPEN / RESOLVED / SUPERSEDED のみ。RESOLVED には根拠 commit を併記する。
