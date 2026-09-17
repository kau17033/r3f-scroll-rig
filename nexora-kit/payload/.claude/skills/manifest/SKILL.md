---
name: manifest
description: 正本（sources/）の SHA-256 マニフェストを照合し、改変の有無を判定する。セッション開始時、CI 失敗時、原文を差し替えた直後に使う。
---

# /manifest — 正本の完全性照合

```bash
python3 tools/manifest.py verify
```

## 判定
| 出力 | 意味 | 行動 |
|---|---|---|
| `VERIFY: PASS` | 改変なし | 通常作業を継続する |
| `VERIFY: FAIL` | 改変・欠落・未追跡がある | **変更を一切行わず**報告して停止する |
| `VERIFY: NOT_IDENTIFIABLE` | 原文未投入 | T-000 / T-010 のみ実行可 |

## FAIL 時の報告
1. どのファイルが `MODIFIED` / `MISSING` / `UNTRACKED` か。
2. 直近の commit で誰が触ったか（`git log --oneline -- <path>`）。
3. 自分の操作が原因か否か。原因不明なら「原因不明」と書く。推測を書かない。

## 禁止
- `manifest.py build` を自律実行して FAIL を消さない。build は人間の操作である。
