# T-200 — LoopCell Phase 0 SSOT v1.1 投入

- blocked_by: DEC-006
- status: BLOCKED

## 目的
未定義参照を解消し、Phase 0 の判定基盤を成立させる。

## 未定義参照（現時点で全ファイルに定義本文が無い）
`A1–A13` (OQ-002) / `N-01–N-12` (OQ-003) / `D-M0-1–6` (OQ-004) / `R-04` (OQ-005)

## 手順
1. SSOT v1.1 本文を `sources/` に投入し manifest を再作成する。
2. 上記 ID の定義本文の所在を確認し、`open_questions.md` の該当行を CLOSED にする。
3. D-M0-2 の承認、モデル/価格の決定を DEC-006 として受ける。

## 絶対禁止
- Phase 0 が GO になる前に MCP 開発を始めない（SRC-04 §25, §27）。
- Tier 1 を公開 Git に入れない。
- 判定語は GO / KILL / HOLD / INVALID のみ。他層の語へ変換しない。
- `coding.patch` 300 loops / McNemar 検定 / GATE 0–4 の設計値を、原文確認前に採用しない。
