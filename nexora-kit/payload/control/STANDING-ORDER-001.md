# STANDING-ORDER-001 — 恒常命令（2026-09-17 受領）

> 「あらかじめ指示しておく。準備が整い次第徹底監査し、プロダクトとして完成品まで完遂させよ。」

本書はこの命令を**機械判定可能な形**に落としたものである。曖昧なまま実行すると、
達成不能な目標に無限に近づく作業になる。それは完遂ではない。

## 1. 発動条件 — 「準備が整った」の定義

`python3 tools/readiness_check.py` が当該ワークストリームを **READY** と判定したとき。
判定は `control/readiness.csv` に基づく。人間しか報告できない条件は `HUMAN` 行として明示し、
**推測で埋めない**。

発動条件を満たさない間は着手しない。**待機は怠慢ではなく、設計である。**

## 2. 「徹底監査」の範囲（着手時に全項目を実施する）

| # | 監査項目 | 手段 |
|---|---|---|
| A1 | 正本の完全性 | `tools/manifest.py verify` が PASS |
| A2 | 全節の処置 | `disposition.csv` の PENDING = 0（`tools/index_sections.py` で索引化後） |
| A3 | 要求の追跡 | `traceability.csv` の全行に task / test / evidence |
| A4 | 矛盾の網羅 | `conflicts.md` の全件に DEC 紐付け。OPEN の CONF に依存する作業は BLOCKED |
| A5 | 主張と証拠の対応 | `evidence-auditor` で全主張を EVIDENCED / OVERCLAIM / UNEVIDENCED / HISTORICAL に分類 |
| A6 | 反証 | `adversarial-reviewer` で結論を崩す最短経路を探索 |
| A7 | 手順違反 | `protocol-guardian` で順序・権威・語彙・停止条件を検査 |
| A8 | 横断整合 | `INDEX-cross-repo.md` を全出典で再照合し、時点（日付）を含めて検証 |
| A9 | ゲート | `tools/gate_check.py` が exit 0 |

**A8 は特に重要である。** 本セッションで 2 度、時点の異なる情報を取り違えた
（Manifest の stale 記述、`GATE_STATUS.json` の 09-08 層）。出典には必ず日付を付す。

## 3. 「完成品」の定義 — スコープごとに異なる

**重要**: 「完成品」は「仮説が支持された状態」を意味しない。3 系統すべてが独立に
`SUCCESS ≠ HYPOTHESIS_SUPPORTED` を掲げている。これを覆す完遂は存在しない。

### W1 — 本キット（nexora-core）

| 完成の定義 | `tools/gate_check.py` が exit 0（G1–G5 すべて PASS） |
|---|---|
| 具体的には | 原文投入・全節 disposition・要求正規化・追跡完備・AUDIT§70 が 0 |
| 私が完遂できるか | **できる**。リポジトリが作成され原文が投入されれば、自律で到達可能 |

### W2 — VEA-G3

| 完成の定義 | **First-Completion 証拠パッケージの完成**（G4 の閉鎖を含む） |
|---|---|
| 現状 | **実質的に完成している**。serial spine 完走、G4 = `FAIL / NOT_IDENTIFIABLE`、MANDATORY STOP 到達 |
| 残作業 | `PROPOSAL-001`（Manifest 再生成）の適用。**文書の現状追随のみ** |
| 私が完遂できるか | **できない**。最終宣言は **HD-53（人間の権限）**。155-pair は明示的な人間 GO を要する |

**科学的結論は `NOT DETERMINABLE` で確定している。** LOCKED config を変えずに別の結論は出ない。
`hypothesis` / `model` / `task` / `system_prompt` はいずれも「変更してはならないもの」に含まれる。
**別の結論を得るには新しい事前登録が要る。それは Phase B であって、本実験の完遂ではない。**

### W3 — LoopCell Phase 0

| 完成の定義 | t0 → learn → t1 完走 → GATE 0–4 判定 → GO / KILL / HOLD |
|---|---|
| 現状 | M3-B の直前。API 呼び出し 0、determinism 0/30 |
| 阻害 | (a) `LOOPCELL_API_KEY` 不在（OQ-019）、(b) **C-06 の裁定**（t0 前に必須）、(c) `analyze`/`report` 未実装（OQ-023、t1 までに必要） |
| 私が完遂できるか | **できない**。API 呼び出しは**課金を伴う**ため委任の「無料なら」条件を外れる |

## 4. 私が完遂できないものの一覧（設計上の上限）

| 事項 | 理由 |
|---|---|
| HD-53 First-Completion 宣言 | 人間の権限 |
| 155-pair の GO | standing authorization が存在しない |
| LoopCell の API 呼び出し | 課金（1.0/5.0 USD per MTok） |
| C-06 の裁定 | 実験条件の決定 |
| 凍結値の変更 | 凍結の意味が失われる |
| 研究目的・仮説・指標・MDE・N・α・seed・除外・停止規則・モデル束縛 | 設計自身が人間判断を要求（CLAUDE.md §6） |

**この一覧は本命令によって縮まらない。** 「設計に理にかなっており」という委任条件が、
設計自身の禁止を上書きしないためである。

## 5. 実行規律

1. 発動条件を満たすまで着手しない。満たした時点で**その場で**着手する。
2. 監査は §2 の全項目。1 項目でも省略したら「徹底」ではない。
3. 出典には**日付**を付す。時点の取り違えを 2 度起こしている。
4. 到達できない完遂は、**到達できない理由と残り距離を明示して停止する**。
   「ほぼ完成」と書かない。何が何件残っているかを書く。
5. 各ワークストリームの完遂時は `/handoff` の 8 項目で報告する。

## 6. 現在の状態

`python3 tools/readiness_check.py` を実行して確認すること。
本書作成時点では **W1 / W2 / W3 いずれも NOT_READY**。
