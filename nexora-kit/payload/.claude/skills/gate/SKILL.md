---
name: gate
description: 実装解禁および「完遂」宣言の断定条件を機械判定する。T-070 と、完了を主張する前に必ず使う。
---

# /gate — 断定条件の判定

```bash
python3 tools/gate_check.py
```

## 条件
| ID | 条件 |
|---|---|
| G1 | SOURCES_INTEGRITY = PASS |
| G2 | disposition PENDING = 0 |
| G3 | decisions PENDING = 0 |
| G4 | traceability 全行に task / test / evidence |
| G5 | AUDIT§70 の 11 項目がすべて 0 |

## 出力の扱い
- `exit 0 / UNLOCKED` → 実装または完遂宣言が可能。
- `exit 1 / BLOCKED` → **BLOCK された条件を列挙して停止する。**

## 禁止
- BLOCK が 1 件でも残る状態で「完遂」「完了」と書かない。
- 判定を会話で上書きしない。判定者は本スクリプトのみである。
- 条件を緩めて PASS にしない。条件の変更は人間の決定（DEC）を要する。
