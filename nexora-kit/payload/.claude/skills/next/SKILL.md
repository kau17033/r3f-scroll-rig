---
name: next
description: 次に着手してよいタスクを 1 件だけ決定する。作業開始前に必ず使う。blocked_by の解決状況を機械的に確認する。
---

# /next — 次タスクの決定

## 手順
1. `tasks/INDEX.md` を上から読む。
2. 各タスクの `blocked_by` を検査する。
   - `T-xxx` → その状態が `DONE` か。
   - `DEC-xxx` → `control/decisions.md` で Status が `PENDING` でないか。
3. `blocked_by` がすべて解決済みの最上位タスクを 1 件だけ選ぶ。

## 出力
```
次タスク : T-0NN <題名>
根拠     : blocked_by = [...] すべて解決済み（各々の根拠を 1 行で）
不可の理由: （着手可能なタスクが無い場合）塞いでいる DEC-ID / OQ-ID
```

## 禁止
- 2 件以上を同時に開始しない。
- 「先に軽い作業を済ませる」として順序を越えない（CLAUDE.md §3）。
- `blocked_by` を自分の判断で解除しない。解除は人間の決定（`/decision`）による。
