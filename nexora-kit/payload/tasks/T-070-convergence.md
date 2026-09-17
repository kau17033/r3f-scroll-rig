# T-070 — 収束成果物

- blocked_by: T-050, T-060, DEC-008
- unlocks: 研究実行（SRC-01 SOV§181 順）

## 目的
「完遂」を宣言できる状態か否かを機械判定する。

## 完了条件（断定条件）
```bash
python3 tools/gate_check.py   # exit 0 であること
```
- G1 SOURCES_INTEGRITY = PASS
- G2 disposition PENDING = 0
- G3 decisions PENDING = 0
- G4 traceability 完備
- G5 AUDIT§70 の 11 項目がすべて 0（`control/audit70.csv`。SRC-01 投入後に項目名を転記する）

## 出力
- 収束レポート（上記 5 条件の実測出力を貼る）
- 残存 DEC / OQ / DEV の一覧
- 次フェーズ（SOV§181 の 1–15）の開始可否

## 禁止
- 1 つでも BLOCK が残る状態で「完遂」と書かない。
- 優先順位は DEC-008 の決定に従う。SOV§114 と SOV§181 を混在させない。
