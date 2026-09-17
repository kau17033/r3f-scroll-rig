# REPO-005 — G4 根本原因（`SOURCE_SELECTION_ROOT_CAUSE.md` の確認）

出典: `evidence/reports/SOURCE_SELECTION_ROOT_CAUSE.md`（blob `49e61dbc…`）。
`main` `c613510` 時点の既存証拠に対する read-only の法医学的パス。
**コード・プロトコル・実験条件・モデル・prompt・seed・runtime のいずれも変更せずに作成されている。**

## 1. 問いへの回答 — 「正しい拒否」か「実装欠陥」か

**選択器は正しい。欠陥ではない。**

| 主張 | 状態 |
|---|---|
| `source_selection.py` は正しい | **OBSERVED / CONFIRMED**（コード読解） |
| SSF は Selection ゲートでの**処置の非成立**であり、VEA の無効性ではない | **OBSERVED / CONFIRMED** |
| 原因は退化した非終端方策である | **SUPPORTED**（C0 について直接、source leg について推移的）— **NOT ESTABLISHED** |
| 「退化方策のみ」が唯一かつ十分な原因である | **NOT ESTABLISHED** |
| τ は計算不能、efficacy は NOT DETERMINABLE | **OBSERVED / CONFIRMED** |

`select_source(ORDERED_RETRY, max_attempts=3)` は j=0,1,2 を順に試し、最初の `terminated=True` で停止する。
3 つとも terminate しないため `selected=None` となる。**ロックされた規則の忠実な出力である。**

## 2. 決定的な観測 — C0 の 640/640

C0 は完全に計装された 25 レコードを持つ。そこで観測された事実:

> qwen3:8b が生の `"ACTION: 2"` を **640/640 steps**、**25/25 レコード**で決定論的に出力し、
> DoorKey を一度も解かずに truncation に至る。`parse_failures_at_end=0`。
> **DoorKey の要となる action 3（pickup）と 5（toggle）が一度も出力されていない。**

`_run_source_leg_episode` は同一のモデル・prompt・ロック設定を使い、seed と `artifact_text=None` のみが異なる。

### 本キットの推論（原文の主張ではない）

MiniGrid-DoorKey は、鍵の pickup（action 3）と扉の toggle（action 5）なしには解けない。
それらが一度も出力されないなら、**terminate は構造的に不可能である**。
「たまたま解けなかった」のではなく「解ける動作を出していない」。

これは REPO-002 §6 に記した Bridge Probe の 639/640 より強い観測である
（640/640 × 25 レコード、かつ必要動作の欠如が名指しされている）。

## 3. パースやプロンプトの欠陥は排除されている

| 反証対象 | 根拠 |
|---|---|
| パーサのバグ | 正規表現 `^\s*ACTION:\s*([0-6])\s*$` は `"ACTION: 2"` に一意に一致。`parse_failures_at_end=0` |
| 応答の破損 | 生応答そのものが一様。パース由来の産物ではない |
| プロンプトの欠陥 | `prompt_hash` が `observation.text` と 1:1。**プロンプトは、実際に変化していない観測を忠実に再符号化している** |
| データ破損 | manifest `CORRUPTED=0`。重複 batch は byte-identical |

**観測そのものが変化していない。** action 2（前進）を壁に向かって出し続けている状態と整合する。

## 4. 仮説の棚卸し

| 仮説 | 判定 |
|---|---|
| H3 選択器が適格な VEA を拒否 | **RULED OUT** — 候補が一度も生成されないため拒否の機会がない |
| H4 選択器のバグ | **RULED OUT** |
| H7 メタデータ誤分類 | **RULED OUT** |
| H8 インフラ/オーケストレーション欠陥 | **PARTIALLY LIVE** — 計装の欠落はインフラ欠陥。ただし実行時障害が*原因*かは未確定（例外なし、`not_usable` は clean） |
| **H_A 退化した非終端方策（seed 非依存）** | **LEADING / SUPPORTED** |
| H_C source leg の設定非対称 | **UNLIKELY** — コード経路は seed を除き同一と検証済 |
| H_D source seed 固有の難レイアウト | **LIVE, LOW** — 排除には per-seed レイアウト検査と実行が必要 |

## 5. 証拠の欠落（なぜ ESTABLISHED にならないか）

| 欠落 | 影響 |
|---|---|
| SSF レコードに per-step trace / 生応答 / `prompt_hash` が無い | **source seed について H_A を直接確認できない** |
| per-attempt の `outcome`（0 か "U" か）が未保存 | 「0」の読みは C0 からの類推 |
| 当時の serving Ollama バージョンが未記録（`ollama=0.32.13` は**ハードコード定数**であり live read ではない） | 当時の挙動を特定 runtime に結び付けられない |

```
SSF の機構（3/3 が terminated=false → selector が None）  = ROOT_CAUSE_CONFIRMED
3 つの source seed が非終端である理由                      = NOT_IDENTIFIABLE（既存証拠から）
過去 75 attempt（25 × 3）の outcome                        = NOT ASSESSABLE（保存されていない）
```

**「75」の正体がここで確定した。25 instance × 3 attempt = 75 である。**
外部 kernel の `population.py` が「75/75 SOURCE_SELECTION_FAILED → γ=0 → R0=0」と読んだ対象は、
**一度も保存されなかった outcome の集合**である。R0=0 を事実として使ってはならない。

## 6. 次の一手は既に承認されている — 必要なのはホストだけ

| # | 修復候補 | 状態 |
|---|---|---|
| R-a | `_atomic_write_text` 証拠耐久化 | **DONE**（commit `c613510`） |
| **R-b** | **R5 計装付き source leg を LOCKED `max_local_steps=640` で実行し、失敗様式を ESTABLISH する** | **AUTHORIZED（H-3/B）、H-2 ホスト待ち** |
| R-c | C0 0–16 の追加再採点記録 | **DONE** |
| R-d | Source Agent Identity vs SPEC §22 | AUTO-RESOLVED（DP-10、Approach B 継続 + 緊張の注記） |

**開いている人間判断は H-2（実験ホストの調達）のみ。** R5@640 と one-valid-treatment は
ホストと readiness gate が PASS になれば H-3/B により**自動で発火する**。
155-pair の確証実験のみ manual go のまま。

## 7. 本キットの前回推論の訂正

REPO-004 の報告で「≥8 GB ホストの調達は G4 の解決より先に行う投資ではない」と述べた。
**この評価は誤りである。訂正する。**

ホストが必要なのは実験を成功させるためではない。**R-b により失敗様式を ESTABLISH し、
Selection ゲートを証拠付きで閉じるため**である。原文の結語がこれを明示する。

> If the R5@640 run confirms non-termination at the LOCKED horizon and no valid treatment
> can be instantiated under the LOCKED config, the Selection gate closes as
> **FAIL / NOT_IDENTIFIABLE with full evidence** — itself a **valid scientific terminal state,
> not a program failure**.

すなわち、この研究は**否定的または不確定の結論で正しく終了し得る**。それはプロトコルの
失敗ではなく、成功である。ホストへの投資はその終了状態に到達するための費用であり、
仮説を支持させるための費用ではない。

## 8. 変更してはならないもの（原文 §16 の列挙）

`hypothesis` / `treatment definition` / `C0・C1-VEA の定義` / `primary endpoint (terminated==True)` /
`success criterion` / `randomization・assignment` / `n_seeds=155` / `analysis plan (McNemar one-sided)` /
`source_success_rule (terminated is True)` / `source pool (j∈{0,1,2})` / `ORDERED_RETRY・max_attempts=3` /
`parse_failure_threshold=0` / `system_prompt` と its sha256 / モデル同一性 / タスク同一性 / leakage 境界 /
**commit 済みの `runs/g3/*.json` および `evidence/**` の全ファイル**

本キットの `guard.py` が `evidence/` を追記専用として扱う規則と一致する。
外部 kernel の e-value 提案（EXTERNAL-001）は `analysis plan` と `source_success_rule` に触れるため、
**この列挙に正面から抵触する。** 採用には人間の裁定が要る（CONF-18）。
