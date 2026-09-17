# T-050 — 矛盾監査

- blocked_by: T-040
- unlocks: T-070

## 目的
正本間の矛盾を網羅し、各件に決定要求を紐付ける。解消しない。記録して停止する。

## 手順
1. `requirements.csv` を scope 横断で突き合わせる。
2. 矛盾を `conflicts.md` に `CONF-NN` として追記する（既存 CONF-01..10 を含む）。
3. 各 CONF に DEC を紐付ける。未起案なら `decisions.md` に起案する。

## 完了条件
- `conflicts.md` の全行に `decision` 列の DEC がある。
- `status` が OPEN の CONF に依存するタスクがすべて BLOCKED である。

## 禁止
- 自分に有利な側を選ばない（SRC-02 ISO§9）。
- 「実質同じ」と述べて統合しない。CONF-04（ITT と pair-complete ∩ received-valid）は
  受領で条件付ける点で ITT と一致しない。統合は誤りである。
