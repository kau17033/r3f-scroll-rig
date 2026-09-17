# REPO-006 — R5@640 実行記録（`SERIAL_SPINE_R5_640_RESULT.md` の確認）

出典: `evidence/reports/SERIAL_SPINE_R5_640_RESULT.md`（blob `d114bafd…`）。2026-09-09 実行。
凍結科学 SHA `bf276fe4a34b33ee7a0ffd72f6f032dd6a3bca2b`。

## 0. 重大な訂正 — R5@640 は既に完了しており、G4 は既に閉じている

REPO-004 および REPO-005 で次のように報告した。**いずれも誤りである。**

| 前回の記述 | 実際 |
|---|---|
| 「R5@640 は `INFRASTRUCTURE_BLOCKED`。≥8GB 専有ホストが必要」 | **H-2 は解決済**。GitHub Actions `ubuntu-latest`（2 vCPU / 7.8 GiB、x86_64）が人間 H2-1 により十分と批准された |
| 「R-b は AUTHORIZED、ホスト待ち」 | **R-b は COMPLETE**（run `34294080720`、6/6 green、2026-09-09） |
| 「G4 は BLOCKED。現在の閉塞ゲート」 | **G4 は CLOSED**。`FAIL / NOT_IDENTIFIABLE`（有効な科学的終端状態） |
| 「必要なのはホストだけ。$3–7 の投資」 | **不要**。GitHub Actions 上で完了済。**費用の議論自体が成立しない** |
| 「退化方策は SUPPORTED, NOT ESTABLISHED」 | **R5 源脚の挙動は DETERMINED**（6/6 TRUNCATED、A/B byte-identical、3 seed すべて非終端） |

### 誤りの原因

`GATE_STATUS.json` は**日付の異なる 2 層を含んでいた**。

- `readiness_gates_2026_09_08` — **ローカルホスト**の準備評価（2026-09-08）。`INFRASTRUCTURE_BLOCKED`
- `gates.G4.evidence` — **GitHub Actions** 上の実測（2026-09-09）。run 番号まで記載

私は G4 の evidence を読みながら、`readiness_gates_2026_09_08` を現状と取り違えた。
**同一ファイル内の古い層を、新しい層より優先して読んだ。** 二次情報を一次確認せずに結論へ用いた
前回の失敗（REPO-002 §5-bis）と同型である。

## 1. 実行基盤（H-2）— ESTABLISHED

| 項目 | 値 |
|---|---|
| 基盤 | GitHub Actions `ubuntu-latest`（private repo → 2 vCPU / 7.8 GiB Xeon Platinum 8573C、Ubuntu 24.04.4、x86_64） |
| 批准 | 人間 H2-1。**固定実験条件に対して十分**（最小仕様の変更ではない） |
| Runtime | Ollama 0.32.13（CLI と `/api/version` の双方）、qwen3:8b digest `500a1f06…`、size `5225388164` 一致 |
| `num_ctx` | **測定値 4096**（`OLLAMA_CONTEXT_LENGTH` 未設定、サーバ既定） |
| pytest | **372 passed**（DECISION-1 正典） |
| **スループット** | **5.37 s/step** — ローカルホストの 37.2 s/step に対し約 **7 倍** |

## 2. R5@640 — COMPLETE（run `34294080720`、6/6 green）

| seed (j) | leg | outcome | steps | parse_fail | label | 出力された行動の集合 |
|---|---|---|---|---|---|---|
| 1073091360 (j0) | A / B | 0 | 640 | 0 | TRUNCATED | **`[2]`** |
| 1368102451 (j1) | A / B | 0 | 640 | 0 | TRUNCATED | **`[2,4]`** |
| 3106902319 (j2) | A / B | 0 | 640 | 0 | TRUNCATED | **`[1,2]`** |

- **A/B が全 3 seed で byte-identical**（`temperature=0` / `top_p=1` の決定性をこの基盤で確認）
- **どの source leg も `terminated` に到達しない。** 3 seed すべてが LOCKED 640 step 予算を通じて非終端
- **真の truncation** であってパース失敗ではない（`parse_failures_at_end=0`）

### 本キットの推論の精密化

前回「方策は action 2 のみを出す」と記した。**source leg では seed ごとに異なる**（`[2]` / `[2,4]` / `[1,2]`）。
単一の固定行動ではない。

しかし**不変なのは次の点である。どの seed も action 3（pickup）と 5（toggle）を一度も出力しない。**
MiniGrid-DoorKey はこの 2 つなしに解けない。したがって **terminate は構造的に不可能**であり、
この観測は 3 seed すべてで成立する。

## 3. ONE VALID TREATMENT — COMPLETE（run `34296827883`、2/2 green）

- instance 0 / 1 ともに `status = SOURCE_SELECTION_FAILED`、`outcome = "U"`、`selected_source_index = null`
- `source_selection_attempts` は 3 × `{not_usable, terminated: false}`、**instance 非依存**
- `llm_runtime_case = PASS`、AMEND-001 の `llm_runtime_identity` あり

## 4. G4 — CLOSED

```
G4 SELECTION GATE     = FAIL / NOT_IDENTIFIABLE   (valid scientific terminal state)
ONE VALID TREATMENT   = NOT INSTANTIABLE under the LOCKED config
τ = P(0,1) − P(1,0)   = UNCOMPUTABLE (analysis population D empty)
VEA-G3 EFFICACY       = NOT DETERMINABLE
```

**これは到達すべき終端状態である。** 原文が明示するとおり、
「no valid treatment under the LOCKED config → Selection gate closes FAIL / NOT_IDENTIFIABLE
with full evidence」。プログラムの失敗ではない。

## 5. 10-pair pilot — COMPLETE（run `34301420718`）

20 ジョブ（10 instance × {C0, C1-VEA}）@ LOCKED 640 + 凍結 reconciliation。全 green。

- MANIFEST: `{COMPLETED: 20, PENDING: 0, CORRUPTED: 0}`
- **10 × C0 はすべて `outcome = 0`** — C0 経路が LOCKED 640 予算で端から端まで実行された（本セッション初）
- 10 × C1-VEA はすべて `SSF` / `"U"`、instance 非依存
- reconciliation: `included_instance_ids = []`、10 対すべて `ExclusionReason.C1_VEA_NOT_ELIGIBLE` で除外
- `population_D_size = 0` → **τ uncomputable**（実行可能性の pilot のみ。確証解析にプールしない）

**pilot の判定**: パイプラインはインフラ障害ゼロで端から端まで動作し、
**Selection ゲート閉鎖が含意するとおりの構造を正確に産出した**。

## 6. MANDATORY STOP — 到達済

```
H-2 → Gate A → Runtime Identity → Gate B → Freeze Check → R5@640
    → ONE VALID TREATMENT → 10-pair pilot → STOP
```

- **155-pair の確証実験は未開始。明示的な人間の GO を要する。standing authorization は存在しない。**
- First-Completion の**宣言**は **HD-53**（人間の権限）。本記録は**証拠パッケージであって宣言ではない**。

## 7. 領域別の最終認識状態（原文 §8）

| 領域 | 状態 |
|---|---|
| 実行基盤（H-2） | **ESTABLISHED** |
| 環境再現性（Gate A） | PASS |
| Runtime identity（SPEC §92） | PASS |
| R5 源脚の挙動 @640 | **DETERMINED** |
| Selection gate（G4） | **FAIL / NOT_IDENTIFIABLE** |
| 因果効果 τ | **NOT DETERMINABLE** |
| VEA efficacy（RQ） | **NOT DETERMINED** |
| CPU アーキテクチャ比較可能性 | CAVEAT（本 run は x86_64。過去も x86-64 のため比較可能性は害されない） |

## 8. 統治上の健全性

本セッションのリポジトリ書込は**すべて追加的かつ非科学的**であると明記されている。
各ワークフローは `ref: bf276fe…` を checkout し、`git rev-parse HEAD == bf276fe…`、
`git status --porcelain` が空、`git diff --quiet` を**ランナー上で表明**している。すべて PASS。

凍結ツリーは不変のまま、実行だけが行われた。本キットが設計した MANIFEST 照合と同じ機能を、
CI 側で既に実装している。

## 9. 本キットへの反映

| 対象 | 変更 |
|---|---|
| OQ-021（ホスト） | **CLOSED_RESOLVED**。GitHub Actions で解決済。費用の議論は成立しない |
| CONF-17 / WS-C | 源脚について **DETERMINED**。ただし「なぜ非終端か」の機序は依然 NOT_IDENTIFIABLE |
| G4 | **CLOSED**（BLOCKED ではない） |
| 残る人間判断 | **HD-53（First-Completion 宣言）と 155-pair の GO の 2 件のみ** |
