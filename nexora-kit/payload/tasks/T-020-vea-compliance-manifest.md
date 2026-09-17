# T-020 — VEA-G3 Compliance Manifest 作成

- blocked_by: T-010, DEC-001, DEC-003
- unlocks: T-110

## 目的
SRC-02 冒頭および ISO§12 の指示に従い、Compliance Manifest **のみ** を作成する。

## 絶対禁止
- 実装を開始しない。実験を開始しない。データを取得しない。
- 原文に無い値を埋めない。欠落は `UNSPECIFIED` として `control/open_questions.md` に記録する。

## 手順
1. SRC-02 の該当節を読み、Manifest の項目を漏れなく列挙する。
2. 各項目について、原文の該当箇所を `SRC-02:L開始-L終了` で引用参照する。
3. 値が原文に無い項目は `UNSPECIFIED` とし、依存タスクを停止する。
4. モデル束縛（provider / model_id / snapshot / endpoint / decoding）は DEC-003 の決定値のみを使う。
   履歴の qwen3:8b を持ち込まない（SRC-02 ISO§2）。

## 完了条件
- Manifest の全項目が「値」または `UNSPECIFIED` のいずれかで埋まっている（空欄なし）。
- `UNSPECIFIED` が 1 件でもあれば T-110 は BLOCKED のままとする。

## 停止時の報告
どの項目が `UNSPECIFIED` か、それが塞ぐ後続タスクは何かを列挙する。
