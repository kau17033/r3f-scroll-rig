# REPO-007 — LoopCell の矛盾台帳と完全性監査

出典: `DECISIONS/contradictions.md`（blob `005124bf…`）、`AUDIT/completeness.md`（blob `53b4ad69…`）。

## 1. D-M0-2 の決着 — 原文はリポジトリに存在しない

`AUDIT/completeness.md` §7:

> **承認の原文（APPROVAL-1/2/3、B-1〜B-4、D-M0-1〜6）** | **Not found** |
> SPEC §19 と §21 が**参照するのみ。原文はリポジトリに存在しない** `[E1]`

**OQ-004 の答え**: D-M0-1〜6 の原文は到達不能である。SPEC は ID を参照するだけで、
承認の本文を保持していない。リポジトリ自身がこれを `Not found` として記録している。

さらに §10「この作業で埋めなかった穴」に「人間承認（APPROVAL / B / D-M0）の原文」が
明示的に列挙されている。**推測で埋めていない**ことが宣言されている。

**DEC-006 の最後の 1 件は、リポジトリからは解決できない。** 人間が原文を提供するか、
`NOT_IDENTIFIABLE` として確定させるかのいずれかである。

## 2. R-04 は存在しない可能性が高い

`AUDIT/completeness.md` §9「未解決事項の一覧（SPEC §19 由来）」の実際の内容:

| 系統 | ID |
|---|---|
| 除去不能な残余リスク | **R-01**（時間交絡）/ **R-02**（チェーンの外部検証不能）/ **R-03**（実行時 gaming の残余経路） |
| 限界 | L-01 〜 L-07 |

**`R-04` は存在しない。** 当初の記述にあった `R-04` は、`R-01`〜`R-03` の誤記か、
別体系（`5-A`/`5-D`/`5-E` など）との取り違えの可能性が高い。
**OQ-005 は `NOT_IDENTIFIABLE`（該当 ID なし）として扱う。**

## 3. N-* 名前空間は実在する

§9 の R-02 の説明に「**N-04 が外部アンカーを禁止する**」とある。
したがって `N-01`〜`N-12` は SPEC 本文に実在する非目標/制約の体系である。
本監査文書には列挙がないため、**OQ-003 は OPEN のまま**（所在は SPEC 本文）。

## 4. LoopCell 自身の矛盾台帳（C-01 〜 C-06）

| ID | 内容 | 解消の要否 |
|---|---|---|
| C-01 | corpus の `error_class` は v1.1.1 規則（最後の E 行）、実行時は v1.1.2 規則（最初の E 行） | **不要**（意図的。corpus は不変、当該値は層別キーにのみ使用され Cell に渡らない） |
| C-02 | SPEC §15 の `analyze` / `report` が未実装。`derived/` も不在 | **t1 完了までに必要**。M3-B は阻害しない |
| C-03 | ルート文書に LoopCell の記述がなかった | 解消済（ポインタ追加） |
| C-04 | `tests_m3/test_m3.py` が pytest 形式でない。`pytest` 実行で `no tests collected` になる | **不要**。ただし誤読すると 49 チェックが未検証のまま「0 件」と読まれる |
| C-05 | 反証スイートが `/tmp` と target 側に worktree 残骸を残しうる | 実験結果に影響なし。修正可否は人間判断 |
| **C-06** | `runner.py` が `experiment_repo.name = "kau17033/langgraph-reflection"` をハードコード。正本は `kau17033/loopcell` へ移設済 | **t0 開始前に人間の裁定が必要**。manifest は t0 で凍結され、A12 が t1 で不一致を検出する |

**C-06 は DEC-006 に追加すべき未決事項である。** M3-B は阻害しないが、t0 の前に決着が要る。

## 5. 矛盾が「なかった」ことの確認（同文書）

品質の高さを示す事実として記録する。

- SPEC §5 の config 定義 ↔ `config.yaml` の実値 — 一致
- `config.yaml` ↔ `config.schema.json` — 一致
- **SPEC §10.2 の A1–A13 ↔ `loopcell/assertions.py` — 13 個すべて実装**
- corpus manifest（件数・split・operator 下限）↔ 実データ — 一致
- SPEC §21 の改版履歴 ↔ Git の変更履歴 — 一致（3 コミットで 3 版）
- `.gitignore` の Tier 1 保護 ↔ 実際の追跡状況 — `runs/` `cells/` `.worktrees/` `.tmp/` すべて未追跡

## 6. その他の `Not found`

| 項目 | 状態 |
|---|---|
| LoopCell 専用の依存定義（requirements / pyproject） | **Not found**（親の `pyproject.toml` は別ライブラリ用） |
| SPEC v1.0 の本文 | **Not found**。v1.0 → v1.1 の差分は検証不能 `[E1]` |
| Claude API 仕様の根拠資料 | **Not found**。前セッションが参照した原文は未保存 `[E1]` |
| M3-A 49/49 の現環境での再実行 | **未実施** |

`SPEC.md v2.0` が unrecovered だった VEA-G3（OQ-016）と**同型の事故**である。
会話に貼られただけの文書は、参照 ID だけを残して本文が消える。

## 7. 本キットへの反映

| ID | 変更 |
|---|---|
| OQ-004（D-M0-1〜6） | **CLOSED_NOT_IDENTIFIABLE**。原文はリポジトリに存在しない（リポジトリ自身が記録） |
| OQ-005（R-04） | **CLOSED_NOT_IDENTIFIABLE**。該当 ID は存在しない（実体は R-01〜R-03） |
| OQ-003（N-01〜N-12） | OPEN 継続。実在するが本監査文書に列挙なし。所在は SPEC 本文 |
| DEC-006 | 残るのは **C-06（`experiment_repo.name` の裁定）**。D-M0-2 は解決不能として確定 |
| OQ-023 新規 | C-02（`analyze` / `report` 未実装）は t1 完了までに必要 |
