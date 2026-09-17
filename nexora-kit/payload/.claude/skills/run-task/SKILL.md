---
name: run-task
description: タスクを 1 件実行する。仮説→最小実装→実測→判定→記録のループを強制し、判定語彙の混用を防ぐ。
---

# /run-task — タスク実行ループ（SRC-07）

## 手順
1. **仮説**: このタスクで何が真になるはずかを 1 文で書く。
2. **最小実装**: タスクの完了条件を満たす最小の変更。無関係な変更を混ぜない。
3. **実測**: 完了条件のコマンドを実行し、コマンド・環境・出力をそのまま保存する。
4. **判定**: 工学判定語のみを使う。
   `PASS` / `FAIL` / `REFUTED` / `NOT_IDENTIFIABLE` / `INFRASTRUCTURE_BLOCKED`
5. **記録**: 変更ごとに次の 6 項目（SRC-01 AUDIT§71）。
   `WHY` / `WHAT` / `IMPACT` / `TEST` / `EVIDENCE` / `ROLLBACK`

## 判定語彙の分離（強制変換禁止）
| 層 | 語彙 |
|---|---|
| 工学 | PASS / FAIL / REFUTED / NOT_IDENTIFIABLE / INFRASTRUCTURE_BLOCKED |
| VEA-G3 | S / E / U / N / O |
| LoopCell | GO / KILL / HOLD / INVALID |
| 観測 | Y ∈ {0, 1, U} |

`U` を `PASS`/`FAIL` に丸めない。テスト合格を仮説の支持として書かない。

## 禁止
- 実測なしに `PASS` と書かない。
- 完了条件のコマンドが失敗した状態で `DONE` にしない。
- 環境要因を理由に FAIL を無かったことにしない（`INFRASTRUCTURE_BLOCKED` は別語である）。
