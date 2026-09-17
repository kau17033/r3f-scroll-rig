# T-040 — 要求正規化

- blocked_by: T-030
- unlocks: T-050, T-060

## 目的
`REQUIREMENT` / `CONSTRAINT` の節を、検証可能な単位に正規化する。

## 手順
`control/requirements.csv` の各行を埋める。
- `req_id`: `REQ-<SRC>-<連番>`
- `source_ref`: `SRC-xx §n` / `quote_ref`: `SRC-xx:L開始-L終了`
- `normalized_requirement`: 1 文。主語と判定条件を含む。
- `type`: MUST / MUST_NOT / SHOULD / MAY
- `scope`: AUTHORITY.md §1 のスコープ名
- `verifiable`: `TEST` / `INSPECTION` / `NOT_VERIFIABLE`
- `NOT_VERIFIABLE` の要求は `open_questions.md` に起案する。丸めない。

## 完了条件
- 全行の `verifiable` が判定済み。
- RQ 番号は `VEA-RQ3` / `P4-RQ3` の表記のみ（裸の `RQ3` は禁止。DEC-005）。

## 禁止
- 複数要求を 1 行に押し込まない。判定条件が 2 つなら行を分ける。
