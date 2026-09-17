# T-010 — 状態固定

- blocked_by: T-000, DEC-002
- unlocks: T-020, T-030, T-060, T-100

## 目的
正本を不変化し、履歴事実の到達可能性を判定する。

## 手順
1. `sources/README.md` の投入手順に従い SRC-01..07 を配置する（人間が実行）。
2. `python3 tools/manifest.py build` → `chmod a-w sources/SRC-*` → `verify`。
3. 履歴事実の到達可能性を判定し `control/STATE.md` に記録する。

| 履歴事実 | 判定語 |
|---|---|
| テスト 337/337 PASS（既存 325 + 新規 12） | `RECOVERED` / `NOT_RECOVERED` |
| 修正チェックポイント 96a87f4 | 同上 |
| 失敗 Run 32814702092（SHA ce13a06、`dataclasses.asdict` → Enum の JSON 直列化失敗） | `INVALID` を保持 |
| 研究経路 qwen3:8b（Ollama）、タスク DoorKey-8x8 | 履歴として記録のみ |

## 完了条件
- `tools/manifest.py verify` が PASS。
- 履歴事実がすべて上表の語で判定済み。

## 禁止
- 履歴事実を現在の妥当性へ昇格させない。337/337 は実装検証の事実であり、仮説の支持ではない。
- Run 32814702092 を再解釈して有効化しない（`INVALID` 保持）。
- DEC-002 が新規リポジトリと決した場合、履歴証拠は `NOT_RECOVERED` とし、SOV§181 の 1–3 で停止する。
