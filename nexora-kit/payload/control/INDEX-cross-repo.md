# INDEX — 横断索引

本プログラムの実態は「統治の不足」ではない。**高品質な統治が 3 系統あり、互いを知らない**ことである。
本書はその橋渡しをする。各主張には出典を付す。出典の無い断定は置かない。

最終更新: 2026-09-17（調査 REPO-001..005 / EXTERNAL-001 に基づく）

---

## 1. 正本の所在

| ID | 内容 | 所在 | 状態 |
|---|---|---|---|
| SRC-01 | ULTRACODE（CONV§0–34 / AUDIT§0–73 / SOV§0–1313、計 1,423 節） | **未投入** | 本キット `sources/` が受け皿 |
| SRC-02 | VEA-G3 の仕様 | `vea-g3:SSOT.md` / `SPEC.md`（v2.1、2,308 行） | **既存** |
| SRC-02b | VEA-G3 の凍結値 | `vea-g3:PROTOCOL_LOCK.md` | **既存**（一次資料） |
| SRC-03 | 論文4 | **未投入** | — |
| SRC-04 | LoopCell Phase 0 | `loopcell:experiments/loopcell_phase0/spec/SPEC_v1.1.md`（v1.1.2、45,632 bytes） | **既存・凍結済**（`M0_FROZEN_v1.1.2`, 2026-08-08, 19 ファイルの sha256） |
| SRC-05 | Outlier / FOCAL | `kau17033/focal`（未調査） | 未確認 |
| SRC-07 | 開発プロトコル | **未投入** | — |
| SRC-08 | 外部 evidence-kernel（27 不変条件） | リポジトリ未特定 | **非権威**（監査対象） |

**注意**: `vea-g3:SPEC.md` v2.0 は unrecovered（chat に貼られただけで保存されず所在不明）。
コードが引用する §9.1/9.2/9.3/9.5 は現行 v2.1 に存在しない（grep 0 件）。→ OQ-016

---

## 2. 既に決まっていた事項（本キットが「未決」と記録していたもの）

| 本キットの記録 | 実態 | 出典 |
|---|---|---|
| DEC-003 モデル束縛 未決 | **決定済** `qwen3:8b`、Ollama、`127.0.0.1:11434`、digest `500a1f06…` | PROTOCOL_LOCK Class A |
| DEC-004 α / 検出力 / MDE 未決 | **決定済** 0.05（片側）/ 0.80 / 0.10 | PROTOCOL_LOCK Class B |
| DEC-004 N 未決 | **決定済** `fixed-N`、`n_seeds=155`（`psi=0.25` から導出） | 同上 |
| DEC-004 主要検定 未決 | **決定済** McNemar exact one-sided | 同上 |
| DEC-004 多重比較 未決 | **決定済** Holm | 同上 |
| DEC-004 主要指標 未決 | **決定済** `primary_endpoint = terminated == True` | 同上 |
| DEC-004 停止規則 未決 | **決定済** `max_local_steps=640`、`parse_failure_threshold=0` | 同上 |
| DEC-006 LoopCell SSOT 未投入 | **既存・凍結済** v1.1.2 | `loopcell:spec/FREEZE_MANIFEST.json` |
| DEC-006 モデル/価格 未決 | **決定済** `claude-haiku-4-5-20251001`、1.0/5.0 USD per MTok | `loopcell:config.yaml` |
| OQ-002 A1–A13 定義なし | **定義あり** 13 件 | `loopcell:spec/reference/assertions.json` |
| OQ-007 リポジトリ所在不明 | **特定** `kau17033/VEA-G3`、`96a87f45d3b08f2…` 実在 | GitHub |

**教訓**: 不足していたのは決定ではなく索引である。

---

## 3. 訂正した記録

| 項目 | 誤 | 正 | 出典 |
|---|---|---|---|
| テスト数 | 337/337 が現行 | **372 が正典**（DECISION-1, 2026-09-09）。337 は 96a87f4 時点の値。392 は棄却 | GATE_STATUS `h2_6_test_count_reconciliation` |
| 155 vs 153 | 別文書の別量 | **同一設計・2 つの標準式**。単純形→155、Connor 形→153。差 2 対（実測確認） | 本キットで計算 |
| `complete()` | 未実装スタブ | **Ollama に対し実装済**。Manifest 行 42 が stale | `llm_client.py` 直接確認 |
| api_key 要求 | バグ | **意図的な不変条件 INV-9**。解消は設定 1 行 | 同上 |
| ≥8GB ホスト | G4 解決より後の投資 | **R-b により失敗様式を ESTABLISH しゲートを閉じるために必要** | ROOT_CAUSE §結語 |
| 「75」 | 75/75 SOURCE_SELECTION_FAILED | **75 = 25 instance × 3 attempt**。当該 outcome は**一度も保存されていない**（NOT ASSESSABLE） | ROOT_CAUSE §13 |

---

## 4. 何が何を塞いでいるか（種別ごとに異なる）

### VEA-G3 — 科学

```
方策が action 3(pickup) / 5(toggle) を一度も出力しない        [C0 25/25、640/640 steps]
  → source leg が terminate しない                            [3/3 seeds、25/25 instance]
    → source selection が常に失敗（選択器は正しい）            [CONFIRMED]
      → 割付集団 D が空                                        [10-pair pilot で確認]
        → tau が計算不能 → G8 に到達しない                     [CONFIRMED]
```

- 現在の閉塞ゲート: **G4（selection）**。G0/G1/G2 は PASS、G7 は PASS_CONTRACT。
- 原因仮説 **H_A / WS-C（退化した非終端方策）**: **SUPPORTED, NOT ESTABLISHED**。
  source leg の per-step trace が保存されていないため直接確認できない。
- 次の一手 **R-b**（R5@640 で失敗様式を ESTABLISH）は **AUTHORIZED 済**。**H-2 ホスト待ち**。
- 実行環境: ローカルは RAM 7.65GB / 空き 0.4GB、37.2 s/step、1 episode 6.6h、R5 全体 40h。
  → `INFRASTRUCTURE_BLOCKED`。必要条件は ≥8GB 専有 Linux ホスト。
- **到達し得る終端**: `FAIL / NOT_IDENTIFIABLE with full evidence`。
  **これは有効な科学的終端状態であり、プログラムの失敗ではない。**

### LoopCell — インフラ

- `LOOPCELL_API_KEY` が実行環境に存在しない（3 経路すべて UNAVAILABLE `[E4]`）。
- 原因は**特定しない**と裁定済（D-02）。候補 3 件は UNCONFIRMED のまま保持。
- 実験は完全に未実行（API 呼び出し 0、determinism 0/30）。現在位置は M3-B の直前。
- 課金を伴う（1.0/5.0 USD per MTok）ため、本セッションの委任範囲外。

### 本キット — 権限

- `kau17033/nexora-core` が未作成。GitHub App は `create_repository` を拒否（403）。
- 人間が private リポジトリを 1 つ作れば、配置・T-000・原文投入は自動で進む。

---

## 5. 残る真の未決事項

| ID | 内容 | 種別 |
|---|---|---|
| **H-2** | 実験ホストの調達（≥8GB 専有 Linux） | **費用**。R5@640 全体で約 40h ≈ $3–7（$0.08–0.17/h 想定） |
| DEC-001 | 権威階層の承認（CONF-01/02） | 人間判断 |
| DEC-004 残 | Class C の 4 件（`cf_operator` / `afr_definition` / `afr_threshold` / `human_hourly_rate`）。SPEC §63 により MVP 外 | 人間判断（先送り可） |
| CONF-04 | 解析対象集団（ITT か pair-complete ∩ received-valid か）。`primary_endpoint` も `effect_estimator` も規定していない | 人間判断 |
| DEC-010 | 統治系の一本化（3 系統） | 人間判断 |
| CONF-16 | `FIRST_FREEZE_SCOPE` を Class B へ拡張するか | 人間判断 |
| CONF-18 | 外部 e-value の採用可否。`analysis plan` / `source_success_rule` / `min_discordant` の 3 点に抵触 | 人間判断 |
| OQ-003/004/005 | N-01–N-12 / D-M0-2–6 / R-04 の本文（所在は SPEC 本文と推定） | 調査（無料） |
| OQ-020 | `COMPLIANCE_MANIFEST.md` の再生成（2 箇所が stale） | 作業（無料） |

---

## 6. 変更してはならないもの（横断）

VEA-G3 `ROOT_CAUSE.md` §16 と LoopCell の凍結条件を統合した禁止集合。

`hypothesis` / `treatment definition` / `C0・C1-VEA 定義` / `primary endpoint` / `success criterion` /
`randomization・assignment` / `n_seeds=155` / `analysis plan (McNemar one-sided)` /
`source_success_rule (terminated is True)` / `source pool j∈{0,1,2}` / `ORDERED_RETRY・max_attempts=3` /
`parse_failure_threshold=0` / `system_prompt` と sha256 / モデル同一性 / タスク同一性 / leakage 境界 /
commit 済みの `runs/g3/*.json` と `evidence/**` /
LoopCell の `corpus`（210 件）・`SPEC`・`schemas`・`config.yaml` の凍結値

本キットの `guard.py` が `evidence/` を追記専用として扱う規則は、この禁止集合と整合する。

---

## 7. ID 名前空間（接頭辞だけで同定してはならない）

| 体系 | 例 |
|---|---|
| VEA-G3 Gate | `G0–G16`（15-gate program architecture, DP-06） |
| VEA-G3 Class | `Class A / B / C` |
| VEA-G3 仮説 | `H1–H9`, `H_A`, `H_C`, `H_D`, `WS-C` |
| VEA-G3 修復 | `R-a`–`R-d`、`R5` |
| VEA-G3 人間判断 | `H-2`, `H-3/B`, `HD-53`, `HD-S5`, `DP-06`, `DP-10`, `DP-15`, `DP-16`, `DP-27` |
| LoopCell アサーション | `A1–A13` |
| LoopCell 判断ログ | `D-01–D-10` |
| LoopCell SPEC 設計判断 | `D-M0-*` ← **`D-01` と別体系** |
| LoopCell 承認 | `APPROVAL-1–3` |
| LoopCell SPEC 条項 | `B-1–B-4`, `C-02`, `C-05`, `C-06`, `V-08`, `U-21` |
| LoopCell 裁定 | `5-A`, `5-D`, `5-E` |
| LoopCell 証拠レベル | `E0–E4` |
| 本キット | `CONF-*`, `DEC-*`, `OQ-*`, `DEV-*`, `T-*`, `REPO-*`, `EXTERNAL-*` |

---

## 8. 判定語彙（相互変換を禁止する）

| 層 | 語彙 |
|---|---|
| 工学（本キット） | PASS / FAIL / REFUTED / NOT_IDENTIFIABLE / INFRASTRUCTURE_BLOCKED |
| VEA-G3 outcome | `Y ∈ {0, 1, U}` |
| VEA-G3 Gate closure | PASS / FAIL / REFUTED / NOT_IDENTIFIABLE / NOT_APPLICABLE |
| VEA-G3 証拠強度 | OBSERVED / CONFIRMED / SUPPORTED / NOT ESTABLISHED / NOT ASSESSABLE |
| LoopCell verdict | GO / KILL / HOLD / INVALID |
| LoopCell 主張分類 | FACT / PREVIOUS OBSERVATION / INFERENCE / UNCONFIRMED |
| LoopCell 証拠レベル | E0–E4 |

共通の不変条件（3 系統すべてが独立に持つ）: **`SUCCESS ≠ HYPOTHESIS_SUPPORTED`**
