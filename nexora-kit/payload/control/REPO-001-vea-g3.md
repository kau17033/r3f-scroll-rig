# REPO-001 — `kau17033/vea-g3` の実態調査

出典: `COMPLIANCE_MANIFEST.md`（blob SHA `92d3cbc635b314a1622e3aa12c6aabcbf68c4fbb`）および root のファイル一覧。
**`PROTOCOL_LOCK.md` / `SPEC.md` の本文は未読。** 以下は Manifest の記述に基づく二次情報である。
一次確認（T-010 の残り）で突き合わせること。

## 1. T-020 は完了している

`COMPLIANCE_MANIFEST.md` は `SPEC.md` §77 の 42 項目に加え、Addendum（4 項目）と
依存グラフを持つ。**本キットの T-020（Compliance Manifest 作成）は重複作業である。**
T-020 の残作業は「作成」ではなく「既存 Manifest の照合」に変わる。

## 2. 既に LOCKED と報告されている値（DEC-003 / DEC-004 の大半）

| 本キットの項目 | vea-g3 での状態 | 根拠（Manifest の行） |
|---|---|---|
| モデル束縛 | **LOCKED** `qwen3:8b`（Ollama、2026-08-18 live 検証） | 19 |
| α | **LOCKED** 0.05 | 27 |
| 検出力 | **LOCKED** 0.80 | 28 |
| MDE | **LOCKED** 0.10 | 26 |
| N | **LOCKED** `n_rule=fixed-N`、`n_seeds=155`（`psi=0.25` から McNemar の標本数式で導出） | 6, 25 |
| 主要検定 | **LOCKED** McNemar exact one-sided | 29 |
| 多重比較 | **LOCKED** Holm | 30 |
| source selection | **LOCKED** `ORDERED_RETRY`、昇順 j=0,1,2、`max_attempts=3` | 11 |
| U 規則 | **LOCKED**（`validity.py::determine_outcome` に実装・テスト済） | 37 |
| prompt | **LOCKED**（sha256 で on-disk 照合） | 20 |
| 環境 | RE-ANCHORED `MiniGrid-DoorKey-8x8-v0`、gymnasium 1.3.0、minigrid 3.1.0 | 22 |
| seed 規則 | **LOCKED**（式は §88 で RE-ANCHORED、.NET 実装と交差検証済） | 24 |

**重要**: `RE-ANCHORED` は「値の同一性・再現性の承認」であって「科学的に最適との判断ではない」と
Manifest 自身が明記している。両者を混同してはならない。

## 3. 未だ UNSPECIFIED と報告されている値

| # | 項目 |
|---|---|
| 2 | Experiment ID |
| 7 | Primary endpoint |
| 8 | Effect estimator |
| 9 | Effect direction |
| 12 | Evaluation generation rule |
| 13 | Novelty rule（task 選定に依存） |
| 23 | Scaffold version |
| 31 | Stopping rule |
| 32, 33 | Cost rule / Human-cost rule（Class-C、MVP 範囲外） |

## 4. 実行を止めている唯一の工学的要因

> `llm_client.py` の `complete()` は意図的な `NotImplementedError` スタブ（Layer C）。
> 実際の Ollama HTTP 統合の構築が次の具体的な工学作業であり、**承認済みだが未実施**。

Execution Authorization は RECEIVED。**人間の決定待ちではなく、実装待ちである。**

## 5. 検出した内部矛盾（CONF-15）

Manifest の行 39 は「UNSPECIFIED の項目」として **11, 25, 26, 27, 28, 30** を挙げる。
しかし同じ文書の行 11 / 25 / 26 / 27 / 28 / 30 はいずれも **LOCKED** と記載されている。
行 42 も「All PROTOCOL_LOCK.md fields LOCKED」と述べ、`primary_endpoint` /
`effect_estimator` / `effect_direction` を含めている。一方で行 7 / 8 / 9 は UNSPECIFIED である。

**行 39 と行 42 が、行 7–9 および行 25–30 と整合しない。** 更新漏れの可能性が高いが、
どちらが現状かは本文書だけでは確定できない。`PROTOCOL_LOCK.md` の一次確認を要する。

## 6. 「75」の正体（OQ-012 / OQ-013 の更新）

Addendum の記述:

> **Prospective only** — historical 75 outcomes remain `NOT ASSESSABLE`,
> run `32814702092` remains `INVALID`, no historical record re-adjudicated.

- 「75」は**過去の 75 件の outcome** を指す。
- リポジトリ自身がそれらを **NOT ASSESSABLE**（評価不能）としている。
- したがって外部 kernel の `population.py` が「75/75 SOURCE_SELECTION_FAILED、γ=0、R0=0」と
  読むことは、**リポジトリが評価不能としている対象に確定値を与える行為**である。
  当該読みは CLASS_H（未検証）として扱うのが正しく、R0=0 を事実として使ってはならない。
- 96a87f4 の commit が記す「19/19 pairs、57/57 source attempts」は、また別の時点・別の単位の量である。
  **3 つを等値してはならない。**

## 7. 本キットの前提を裏づける事実

> `SPEC.md` v2.0 は "unrecovered"（chat に貼られただけで保存されず、現在は所在不明）。
> コードが引用する `SPEC.md` §9.1/9.2/9.3/9.5 は、現行 v2.1 に**存在しない**（grep で 0 件）。
> 環境選択・seed 導出式・action-parse 形式・VEA 構造は「実装され、テストされ、内部整合的だが、
> 現存する授権仕様を持たない」。

要約を正本の代替にすると何が起きるかの実例である。本キットの `sources/` 不変化と
MANIFEST 照合は、この事故を防ぐために存在する。

## 8. 次の作業（優先順）

1. `PROTOCOL_LOCK.md` を読み、第 2 節の LOCKED 値と第 5 節の矛盾を一次確認する。
2. `SSOT.md` と `SPEC.md` を `nexora-core/sources/` に SRC-02 として投入し、ハッシュ固定する。
3. `RESEARCH_STATE.md` / `GATE_STATUS.json` / `CLAIM_STATUS.md` を読み、現在の Gate 状態を確定する。
4. `LoopCell` リポジトリを同様に調査する。
