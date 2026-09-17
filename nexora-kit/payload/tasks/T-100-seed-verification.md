# T-100 — seed 導出の原文照合

- blocked_by: T-010
- status: BLOCKED（SRC-03 未投入）

## 目的
`tools/seed_derive.py` の解釈が SRC-03 §9.5 と一致することを原文で確認する。

## 現在の解釈（再実装）
```
eval seed : sha256(UTF-8 "VEA-G3|eval|{env_seed}|{i}")[:4] をビッグエンディアンで読む
order     : sha256(UTF-8 "VEA-G3|order|{env_seed}")[:4] をビッグエンディアンで読み mod 2
```

## 手順
1. SRC-03 §9.5 の定義文を `SRC-03:L開始-L終了` で引用する。
2. 原文に記載されたテストベクタがあれば、`tests/golden/seed_vectors.json` に追加し
   `status` を `VERIFIED_AGAINST_SOURCE` に変更する。
3. 一致しない場合、`tools/seed_derive.py` を原文に合わせ、差分を `deviations.md` に記録する。

## 未解決
- `OQ-001`: `master_seed_source`（env_seed 自体の作り方）が原文に無い → `UNSPECIFIED`。
  本モジュールは env_seed を生成しない。決定は DEC-004 に含める。

## 禁止
- ゴールデン値を実装出力に合わせて書き換えることで「一致」としない。照合先は原文である。
