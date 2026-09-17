# NEXORA — Claude Code Constitution v1.0

本書は `sources/` 原文の運用要約である。原文と矛盾する場合は原文を優先し、`control/conflicts.md` に記録して停止する。
引用表記: SRC-01 `CONV§`/`AUDIT§`/`SOV§`、SRC-02 `ISO§`/`SPEC§`。行番号は `SRC-xx:L開始-L終了`。

## 0. セッション開始時
1. SessionStart 出力を読む。`SOURCES_INTEGRITY` が `PASS` 以外なら、いかなる変更も行わず報告して停止する。
2. `control/STATE.md` で現在 Phase と次タスクを確認する（未作成なら T-000 のみ実行可）。
3. 会話履歴・過去セッション・記憶を仕様または証拠として使わない（SRC-02 ISO§2）。

## 1. 正本（編集禁止）
| ID | 正本 | 権威範囲 |
|---|---|---|
| SRC-01 | ULTRACODE 指令群 | リポジトリ全体の工学・研究統治 |
| SRC-02 | VEA-G3 実装仕様 SSOT | VEA-G3 実験の全判断 |
| SRC-03 | 論文4 | 主張階層・CE-01..05・設計候補（実行権限なし） |
| SRC-04 | LoopCell | Phase 0 と製品層 |
| SRC-05 | Outlier v1.0 | 実装保留（DEC-007） |
| SRC-06 | session URL | 非権威 |
| SRC-07 | 開発プロトコル | 作業手順 |

- 要約・言い換えを原文の代替にしない。権威順位は `control/AUTHORITY.md`（DEC-001 承認前は提案扱い）。

## 2. 停止条件（実装せず報告）
- 実行に必要な値が原文に無い → `UNSPECIFIED` を `control/open_questions.md` に記録し依存作業を停止（SRC-02 ISO§8）。補完禁止。
- 原文同士の矛盾 → `CONF-ID` で記録し停止。有利な側を選ばない（SRC-02 ISO§9）。
- §6 の人間判断事項に触れる／整合性 NG／保護パス違反／履歴証拠の改変が必要。
- SRC-01 SOV§182 のブロッカーが残る状態で episode 数を増やさない。

## 3. 順序（監査が実装より先）
T-000 キット検証 → T-010 状態固定 → T-020 VEA-G3 Compliance Manifest（実装・実験禁止）
→ T-030 全節 disposition（PENDING=0）→ T-040 要求正規化 → T-050 矛盾監査
→ T-060 実態照合 → T-070 収束成果物 → 研究実行（SRC-01 SOV§181 順、ゲート付き）。

- `blocked_by` が空でないタスクは開始しない。1 ターン 1 タスク。無関係な変更を混ぜない。

## 4. タスク実行ループ（SRC-07）
仮説 → 最小実装 → 実測（コマンド・環境・ログ保存）→ 判定 → 記録。

- 工学判定: `PASS` / `FAIL` / `REFUTED` / `NOT_IDENTIFIABLE` / `INFRASTRUCTURE_BLOCKED`
- 研究判定は各 SSOT の語彙を使い相互変換しない（SRC-02: S/E/U/N/O、SRC-04: GO/KILL/HOLD/INVALID、Y∈{0,1,U}）。
- `U` を `PASS`/`FAIL` にしない。テスト合格を仮説支持にしない。
- 変更ごとに WHY/WHAT/IMPACT/TEST/EVIDENCE/ROLLBACK を記録（SRC-01 AUDIT§71）。

## 5. 証拠と状態
- `evidence/` `historical/` `protocol/` は新規作成のみ。訂正は correction record を追加（SRC-01 SOV§1139）。
- 研究状態は `control/` と台帳に置き、会話に置かない。未実行を実行済みと書かない。
- 履歴事実を現在の妥当性へ昇格させない（337/337 = 実装検証のみ、Run 32814702092 = INVALID 保持）。

## 6. 人間判断事項（自律実行禁止）
研究目的・仮説・推定対象・指標・MDE・N・α・seed・除外・停止規則／モデル束縛／
`sources` `CLAUDE.md` `.claude` `control/AUTHORITY.md` の変更／push・外部公開・有料 API・資格情報・不可逆操作。
起案先: `control/decisions.md`（`/decision`）。

## 7. 研究コア規則（抜粋、原文優先）
- VEA-G3: 実装前に Compliance Manifest（SRC-02 冒頭, ISO§12）。結果閲覧後にデータ・モデル・プロンプト・閾値・N・seed・除外・検定・停止・コスト・判定規則を変えない。
- 主張階層 Effect → Attribution → Interpretation。性能差 ≠ 転移（SRC-03 §1.3, 付録A）。
- 研究コアはローカル経路前提。`ANTHROPIC_API_KEY` / `OPENAI_API_KEY` を前提にしない（SRC-01 SOV§104, §175）。
- 統計計算は決定論的スクリプト。LLM に検定選択を委ねない（SRC-02 SPEC§39, §73）。
- LoopCell: Phase 0 GO 前に MCP 開発を始めない（SRC-04 §25, §27）。Tier 1 を公開 Git に入れない。

## 8. 用語
`RQ3` → `VEA-RQ3` / `P4-RQ3`。`Gate` → `ULTRA-G*` / `REPO-Gate*` / `LC-GATE*`。
`ORP` = SRC-01 の自律研究行動選択仮説（Outlier Protocol とは別概念）。

## 9. 検証の独立性
重要変更は実装者と別役割（`protocol-guardian` / `evidence-auditor` / `adversarial-reviewer`、読み取り専用）で検証する。

## 10. 終了時
`/handoff` で 8 項目（現状・作業・変更・実測・判定根拠・未解決・停止理由・必要な人間判断）を報告し、`control/STATE.md` を更新する。
