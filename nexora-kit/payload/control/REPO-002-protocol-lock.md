# REPO-002 — `vea-g3/PROTOCOL_LOCK.md` の一次確認

出典: `PROTOCOL_LOCK.md`（blob SHA `e535476b4f981f3ca1f8dff9efb92253797c0a39`）。**一次資料である。**
REPO-001 は `COMPLIANCE_MANIFEST.md` に基づく二次情報であり、両者が食い違う箇所は本書が優先する。

## 1. CONF-15 の決着 — Manifest 側が古い

`PROTOCOL_LOCK.md` は Class B を**全件 LOCKED** と記載する。うち Manifest が UNSPECIFIED と
していた 3 件は、実際には LOCKED である。

| 項目 | PROTOCOL_LOCK の値 |
|---|---|
| `primary_endpoint` | `terminated == True`（`validity.determine_outcome`）。**運用上の成功エンドポイントにすぎず、それ自体を因果的有効性の証明として読んではならない**旨がロックの一部として明記されている |
| `effect_estimator` | `tau_hat = risk(C1-VEA) - risk(C0)` |
| `effect_direction` | `C1-VEA - C0 > 0` |

したがって **CONF-15 は RESOLVED**。`COMPLIANCE_MANIFEST.md` の行 7 / 8 / 9 と行 39 が
更新漏れであり、行 42（「All PROTOCOL_LOCK.md fields LOCKED」）が現状に一致する。

## 2. CONF-07 の訂正 — 155 と 153 は同じ設計である

REPO-001 では「155 と 153 は別文書の別量」と記録した。**これは誤りである。訂正する。**

同一の入力（片側 α=0.05、検出力 0.80、ψ=0.25、τ=0.10）に対し、McNemar の標本数式には
少なくとも 2 つの標準形がある。本キットで実測した結果:

| 式 | 計算 | 結果 | 対応 |
|---|---|---|---|
| 単純形 `N = (z_a + z_b)^2 * psi / tau^2` | `(1.6449+0.8416)^2 * 0.25 / 0.01 = 154.5639` | **155** | `PROTOCOL_LOCK.md` の記載値と一致 |
| Connor 形 `N = [z_a*sqrt(psi) + z_b*sqrt(psi - tau^2)]^2 / tau^2` | `[0.8224+0.4123]^2 / 0.01 = 152.4571` | **153** | SRC-03（論文4）の候補値と一致 |

差は **2 対（1.31%）**。両者は矛盾ではなく、**同一設計に対する 2 つの標準式の差**である。
155 のほうが保守的（大きい）。どちらを採るかは設計判断であり、実質的な衝突はない。

`PROTOCOL_LOCK.md` は `psi=0.25` を「明示的な設計**仮定**であり、実行から推定した観測値ではない
（ロック時点で Execution=NONE）」と明記している。この区別を崩してはならない。

## 3. 重要 — freeze_gate は Class A しか機械的に検査しない

```yaml
FIRST_FREEZE_SCOPE: CLASS_A_ONLY
freeze_gate.REQUIRED_FIELDS == CLASS_A_FIELDS   # Class B/C は含まれない
freeze_gate: PASS
```

Class B は実値で埋まっているが、**ゲートはそれを要求していない**。
`FIRST_FREEZE_SCOPE` の拡張は「別個の、未だなされていない決定」と明記されている。

**したがって `freeze_gate: PASS` は「実行可能」を意味しない。** 文書自身がこう述べる。

> This is not a claim that VEA-G3 is ready for Stage A execution or that any research
> question is answerable. It means exactly one thing: the execution-identity fields
> needed to make a real model call are all filled.

機械的な PASS の範囲を、実行準備の完了と読み替えてはならない。

## 4. 追加で LOCKED と判明した値

| 項目 | 値 | 備考 |
|---|---|---|
| `max_local_steps` | **640** | C0/C1 対称。環境自身の `max_steps` 上限。**科学的最適性は NOT_CLAIMED** と明記 |
| `thinking_control` | **EXPLICITLY_OFF** | C0/C1 対称。`max_output_tokens=128` 下で thinking が予算を食い尽くし `ACTION:` 行が出ないことを実測（run 32692963740: `response=""`, `thinking_length=465`, `done_reason="length"`）したため |
| `parse_failure_threshold` | **0** | ロックにより `runner.py` の実バグが露見し、修正後に登録された |
| `runner_content_hash` | `8055ac1a...` | 一度 stale になり再ロック済。`runner.py` を編集すれば無効化される |
| Source Agent | 評価 Agent と同一モデル・同一 prompt（approach B） | 「差は実験成果物の入力のみ。prompt 層の隠れた処置差は許さない」旨が根拠として明記 |

## 5. 実行を止めている工学的要因（2 件）

1. `LLMClient.__init__` が `provider="Ollama"` でも非空の `api_key` 解決値を要求する。
   Ollama は通常認証を要さない。**source / evaluation どちらの実クライアント構築も塞ぐ。**
2. REPO-001 §4 に記した `complete()` の未実装（Manifest の記述）。
   ただし本書は `complete()` の `think` パラメータを既存機能として記述しており、
   **2 文書の記述が整合しない。** コードの直接確認を要する（OQ-018）。

## 6. 解釈上の重大な留保 — 639/640 が同一応答

Bridge Probe（run `32696823173`、think:false 下の 640 step 全走）で、
**640 回の LLM 呼び出しのうち 639 回が byte 単位で同一の `"ACTION: 2"` を返した。**

文書自身が、これが「壁に突き当たって動けない正当な静的観測への正当な静的応答」なのか
「観測内容にほとんど反応しない方策」なのかを **未解決** とし、本決定では追加調査しないと述べている。

**これは C0/C1 の結果解釈に直接効く。** 方策が観測に反応していない場合、
C1-VEA と C0 の差が「経験転移の効果」を測っているという主張は成立しない。
`evidence-auditor` の判定語で言えば、この状態で得た差分を Attribution として読むことは
`OVERCLAIM` に該当する。実行前に決着させるべき事項として記録する。

## 7. 本キットへの反映

| 対象 | 結果 |
|---|---|
| CONF-15 | **RESOLVED**（Manifest 側が stale） |
| CONF-07 | **訂正のうえ RESOLVED**（同一設計・2 つの式） |
| CONF-04 | **OPEN 継続**。`primary_endpoint` も `effect_estimator` も**解析対象集団**（ITT か pair-complete ∩ received-valid か）を規定していない |
| DEC-004 | 残るのは Class C の 4 件（`cf_operator` / `afr_definition` / `afr_threshold` / `human_hourly_rate`、SPEC §63 により MVP 範囲外）と CONF-04 のみ |
