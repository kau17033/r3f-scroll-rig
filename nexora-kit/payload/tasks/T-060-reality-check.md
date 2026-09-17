# T-060 — 実態照合

- blocked_by: T-040, DEC-002
- unlocks: T-070

## 目的
要求とリポジトリの実態を突き合わせ、`traceability.csv` を埋める。

## 手順
各 `req_id` について次を記録する。
- `task_ids`: 実装/検証タスク
- `test_ids`: 対応テスト（無ければ作る。作れないなら `NOT_VERIFIABLE`）
- `evidence_paths`: 実測ログの相対パス
- `status`: `SATISFIED` / `UNSATISFIED` / `NOT_IMPLEMENTED` / `NOT_IDENTIFIABLE`

## 完了条件
- 全行の 3 列が埋まっている（`tools/gate_check.py` の G4）。

## 禁止
- テスト合格を仮説の支持として記録しない（層が違う。CLAUDE.md §4）。
- 未実行を実行済みと書かない。
