# AUTHORITY — 権威階層（提案 / 未承認）

Status: **PROPOSED — DEC-001 承認まで拘束力なし**
編集は人間のみ（guard.py と permissions.deny で保護）。

## 0. 常に最上位
1. 安全・法令・第三者の権利
2. 人間の明示承認（`control/decisions.md` に記録されたもの）

## 1. スコープ分割（CONF-01 の処置案）
権威は単一の直線順位ではなく、スコープで分割する。スコープを跨いだ流用を禁止する。

| スコープ | 一次正本 | 補助 | 備考 |
|---|---|---|---|
| VEA-G3 実験（設計・実行・解析・判定） | SRC-02 (ISO§/SPEC§) | SRC-03 は候補値の供給のみ | SRC-03 に実行権限なし |
| LoopCell Phase 0 / 製品層 | SRC-04 | — | Phase 0 GO 前に MCP 開発禁止 |
| リポジトリ全体の工学・研究統治 | SRC-01 (CONV§/AUDIT§/SOV§) | — | 手順は SRC-07 |
| Outlier v1.0 | SRC-05 | — | DEC-007 まで実装保留 |
| 過去セッション | — | — | SRC-06 は非権威（SRC-02 ISO§2） |

## 2. 衝突時の解決順序
1. 安全・法令・権利保護
2. 会話内の最新の明示的人間指示（`decisions.md` に記録済みのもの）
3. スコープ一次正本の明示的優先規則
4. より具体的な文面
5. より新しい文面（SRC-01 内部の時系列。CONF-05: SOV§181 > SOV§114 を提案）

上記で解決しない部分は **断定不可** として `open_questions.md` に記録し、依存作業を停止する。丸めない。

## 3. ロック状態（CONF-02）
- SRC-02 は「唯一の正式な SSOT」と「Status: SSOT Candidate」を併記している。
- DEC-001 でどちらかに確定するまで、SRC-02 を根拠とする *不可逆な* 実行（実験の本実行）を禁止する。
- Compliance Manifest の *作成* は許可する（SRC-02 冒頭の指示に一致するため）。

## 4. 本ファイルの変更手順
1. `control/decisions.md` に DEC を起案する。
2. 人間が Status を APPROVED に変更し commit する。
3. 同一 commit で本ファイルを更新する。Claude Code は本ファイルを編集しない。
