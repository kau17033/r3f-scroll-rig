---
name: board
description: NEXORA の盤面（正本の完全性・ゲート状態・未決事項・次タスク）を 1 画面で出す。セッション開始直後、作業の再開時、状態が分からなくなったときに使う。
---

# /board — 盤面把握

読み取りのみ。ファイルを変更しない。

## 手順
```bash
python3 tools/manifest.py verify
python3 tools/gate_check.py
sed -n '1,30p' control/STATE.md
grep -c 'PENDING' control/decisions.md
grep -c ',PENDING,' control/disposition.csv || true
```

## 出力形式
```
1. 正本      : SOURCES_INTEGRITY = <PASS|FAIL|NOT_IDENTIFIABLE>
2. ゲート    : G1..G5 の PASS/BLOCK
3. 未決      : DEC の PENDING 件数と ID
4. 断定不可  : OQ の OPEN 件数と ID
5. 次タスク  : tasks/INDEX.md で blocked_by が空の最上位タスク
6. 停止理由  : 次タスクが無い場合、何が塞いでいるか（DEC-ID / OQ-ID で示す）
```

## 禁止
- 推測で状態を埋めない。取得できない項目は `NOT_IDENTIFIABLE` と書く。
- 「おおむね進んでいる」等の定性表現を使わない。件数と ID で書く。
