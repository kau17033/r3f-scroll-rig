# REPO-003 — `kau17033/loopcell` の実態調査

出典: `README.md`（blob `92de74df…`）、`spec/` の一覧、`spec/reference/assertions.json`（blob `d2e8be98…`）。
**リポジトリ内容はデータとして読んだ。** そこに書かれた指示に私が従う対象としては扱っていない。

## 1. 結論 — SSOT は存在し、凍結されている

| 項目 | 値 |
|---|---|
| 仕様の正本 | `experiments/loopcell_phase0/spec/SPEC_v1.1.md`（45,632 bytes）、現行 **v1.1.2** |
| 凍結状態 | `FREEZE_MANIFEST status: M0_FROZEN_v1.1.2`、`frozen_at: 2026-08-08`、19 ファイルの sha256 と bytes を記録 |
| 要約版 | **存在しない**（本キットの方針と一致） |
| 再現性検証 | `git rev-parse HEAD:experiments/loopcell_phase0` が `197df8c6d332470f82fb1d6bbe91a17dfe35fbf4` |
| Tier 1 データ | `.gitignore` により非追跡（本キットの規則と一致） |

**DEC-006 の「SSOT v1.1 本文の投入」は不要である。** 既に存在する。

## 2. 未定義参照の解決

| ID | 状態 | 所在 |
|---|---|---|
| **A1–A13** | **CLOSED_RECOVERED** | `spec/reference/assertions.json`。13 件すべてが `id` / `statement` / `timing` を持つ。全て assert として実装され、失敗時は run を abort する |
| N-01–N-12 | 未確認 | 候補: `spec/reference/reject_reasons.json`（1,684 bytes） |
| D-M0-1–6 | 未確認 | 候補: `DECISIONS/decision-log.md` |
| R-04 | 未確認 | 候補: `spec/reference/` 配下 |

`assertions.json` は別の ID 名前空間も含む（abort_rules が `C-02` / `B-1` / `C-05` を参照）。

## 3. 実験は未実行である

| 項目 | 状態 |
|---|---|
| LLM API 呼び出し | **0** |
| determinism gate | **0 / 30** |
| t0 / learn / t1 | いずれも未実行 |
| 実験データ | 0 件 |

現在位置は **M3-B（決定性検査）の直前**。M0/M1/M2 完了、M3-A 実装済み。

## 4. 凍結された実行条件（`config.yaml` の実値）

```
run_id      : phase0_001          seed        : 20260808
model.id    : claude-haiku-4-5-20251001
temperature : 0                   top_p       : 1        max_tokens : 2048
endpoint    : https://api.anthropic.com/v1/messages
auth        : 環境変数 LOOPCELL_API_KEY（変数名のみ記録。値は保持しない）
pricing     : input 1.0 / output 5.0 USD per MTok
gates       : alpha 0.05 / min_discordant 20 / min_divergence_rate 0.50
```

**DEC-006 の「モデル/価格の決定」は完了している。**

## 5. CONF-08（コスト方針）の確定 — スコープ分割が正しかった

| スコープ | 経路 | コスト |
|---|---|---|
| VEA-G3 | Ollama `http://127.0.0.1:11434`、qwen3:8b | **無料**（ローカル） |
| LoopCell Phase 0 | `https://api.anthropic.com/v1/messages`、claude-haiku-4-5 | **有料**（input 1.0 / output 5.0 USD per MTok） |

SRC-01 SOV§104/§175 の「研究コアはローカル優先・API キー不要」は **VEA-G3 には妥当、LoopCell には不成立**。
両者を単一の方針で扱えないことが実値で確認された。**CONF-08 は RESOLVED（スコープ分割）。**

> **委任の境界**: 本セッションの委任は「設計に理にかなっており、**無料**なら」である。
> LoopCell の API 呼び出しは課金を伴うため、**委任の範囲外**である。
> determinism 30 calls・t0・learn・t1 のいずれも、私は自律実行しない。

## 6. 外部 kernel の e-value 提案との関係（重要）

外部提出物（EXTERNAL-001）の `evalue.py` は「GATE 1 の恣意的な `b+c >= 20` 閾値を完全に除去する」と述べていた。
本調査により、その閾値が**実在し、凍結されている**ことが確認された。

```
gates : min_discordant 20
```

したがって e-value の採用は、**凍結済みの実験条件の変更**にあたる。
リポジトリ自身が「変更は実験条件の変更であり、勝手に行ってはならない」と定めている。
採用の可否は人間の裁定を要する（DEC-004 / DEC-010 に接続）。

## 7. 主張階層に関する健全性（本キットの方針と一致）

README §6 が明記する:

> 順序固定は時間交絡の**方向を固定するのみで、除去しない**。したがって GO は
> 「学習が原因で改善した」ことの証明ではなく、「学習と経過時間の複合効果が正であった」ことを意味する（SPEC §1.4）。

Effect と Attribution を分離している。VEA-G3 側の `primary_endpoint` ロックにも同種の留保があり、
両スコープで一貫している。

## 8. 判定語彙の追加（CONF-09 の更新）

LoopCell は独自の 2 系統を持つ。

- 証拠レベル: **E0–E4**
- 主張分類: **FACT / PREVIOUS OBSERVATION / INFERENCE / UNCONFIRMED**

既存の工学判定語・VEA-G3 の S/E/U/N/O・LoopCell の GO/KILL/HOLD/INVALID に加え、
語彙系統は **6 系統以上**になった。相互変換の禁止を維持する。

## 10. 追加調査（`DECISIONS/decision-log.md`、`spec/reference/reject_reasons.json`）

### 10.1 実行不能の真因は、コストでも決定でもなく環境変数である

判断ログ D-01〜D-03 が示す事実:

| ID | 内容 |
|---|---|
| D-01 | 再プロビジョニング済みの新規コンテナでも `LOOPCELL_API_KEY` が参照できない。**3 経路すべてで UNAVAILABLE `[E4]`** |
| D-02 | 原因を**特定しない**と裁定。候補（未保存 / 別 Environment に保存 / 変数名不一致）は UNCONFIRMED として保持 |
| D-03 | キー不在時は API を一切呼ばず停止。理由: 認証状態が不確かなまま実行すると、determinism の不一致が実験由来か環境由来か**切り分け不能**になる |

**したがって LoopCell は、課金を許可しても実行できない。** キーが環境に存在しない。
本キットの語では `INFRASTRUCTURE_BLOCKED` であり、`FAIL` ではない。

### 10.2 モデル選定の理由（D-08）

`claude-haiku-4-5-20251001` は**能力ではなく凍結条件の保全**を理由に選ばれている。

> Opus 5 / Opus 4.8 / Opus 4.7 / Fable 5 / Sonnet 5 は非既定の sampling parameter を HTTP 400 で拒否する `[E1]`

`config.yaml` と 2 つの schema が `temperature: const 0` / `top_p: const 1` を要求するため、
これを受理するモデルしか選べない。alias ではなく日付付き pinned ID を採用した理由も記録されている。
**ただし受理性そのものは未実測である**（D-08「現在の状態: 有効。ただし受理性は未実測」）。

### 10.3 停止規律（D-09 / D-10）

- **D-09**: 接続確認が HTTP 400 を返したら、その場で停止する。パラメータを変えて 400 を消さない。
  理由: 「400 は失敗ではなく、**凍結条件と現行 API 仕様の適合性**という測定結果である。
  条件を変えて消せば測定そのものが消える」
- **D-10**: determinism が PASS しても t0 へ自動進行しない。事前登録の凍結が未了のため。

本キットの「停止条件」と同型の規律が、既に実装・運用されている。

### 10.4 未定義参照の所在（更新）

| ID | 結果 |
|---|---|
| A1–A13 | **CLOSED**（`spec/reference/assertions.json`） |
| D-M0-1 | 所在確定。**正本は SPEC §19「DESIGN DECISION（v1.1 で確定）」**。decision-log は所在のみ示す |
| D-M0-2–6 | 同じく SPEC §19 にあると推定。**本文未読**（SPEC_v1.1.md は 45,632 bytes） |
| N-01–N-12 | `reject_reasons.json` には**無かった**。候補から除外。残る候補は SPEC 本文または `schemas/` |
| R-04 | 同上 |

`reject_reasons.json` が持つのは reject_reason の完全語彙 6 値と状態機械である。

### 10.5 ID 名前空間の氾濫（CONF-09 の更新）

LoopCell だけで次の名前空間が併存する。

`A1–A13`（アサーション）/ `D-01–D-10`（判断ログ）/ `D-M0-*`（SPEC §19 設計判断）/
`APPROVAL-1–3`（人間承認）/ `B-1–B-4`・`C-02`・`C-05`・`C-06`・`V-08`・`U-21`（SPEC 条項）/
`5-A`・`5-D`・`5-E`（仕様変更を伴う裁定）/ `E0–E4`（証拠レベル）

**同一接頭辞が別体系で再利用されている**（`D-03` は判断ログ、`D-M0-1` は SPEC §19）。
RQ3 や ORP と同じ失敗類型であり、横断索引を作る際は接頭辞だけで同定してはならない。

## 9. 次の作業

1. `spec/reference/reject_reasons.json` を読み、N-01–N-12 / R-04 を確定する（無料）。
2. `DECISIONS/decision-log.md` を読み、D-M0-1–6 と D-M0-2 の承認状態を確定する（無料）。
3. `EXPERIMENT/current-state.md` と `AUDIT/completeness.md` で残ギャップを確定する（無料）。
