# TASKS — 実行順序と依存

規則: `blocked_by` が空でないタスクは開始しない。1 ターン 1 タスク。
監査（T-0xx）が実装（T-1xx 以降）より先である。順序を越えない。

| ID | タスク | blocked_by | 判定 | 状態 |
|---|---|---|---|---|
| T-000 | キット自己検証 | — | `tools/kit_check.py` exit 0 | **DONE**（CI run 35190376080） |
| T-005 | 横断現在地の決定論的収束 | T-000 | `tools/state_reduce.py --check` exit 0 + full tests | **DONE**（CI run 35728612031） |
| T-010 | 状態固定（hash固定・履歴照合） | T-005, DEC-002 | `tools/source_registry_check.py` exit 0 + external 34/34 | **DONE**（CI run 35731846330） |
| T-012 | Dream-Replay探索方策基盤 | T-005 | `tools/dream_replay.py --bootstrap-check` exit 0 + prefix-only tests | **DONE**（CI run 35731846330） |
| T-020 | VEA-G3 Compliance Manifest **照合**（作成ではない） | T-010 | 既存 Manifest の 42 項目 + Addendum を一次資料と突合 | **DONE**（CI run 35739331939: 42 rows reconciled; stale=7を明示保持） |
| T-030 | 全節 disposition | T-010 | `tools/disposition_check.py` exit 0; normative sections=1652; PENDING=0 | **DONE**（CI run 35733289288） |
| T-040 | 要求正規化 | T-030 | `requirements.csv` 全行 verifiable 判定済 | **DONE**（CI run 35739331939: 1652/1652） |
| T-050 | 矛盾監査 | T-040 | `conflicts.md` 全件 DEC 紐付け | **DONE**（CI run 35739331939: 19/19、OPEN 3件はHGへ隔離） |
| T-060 | 実態照合（リポジトリ vs 要求） | T-040, DEC-002 | `traceability.csv` 全行埋め | **DONE**（CI run 35739331939: 1652/1652、satisfaction非含意） |
| T-070 | 収束成果物 | T-050, T-060, DEC-008 | `tools/convergence_gate.py`; scientific execution gates remain separate | **IN_PROGRESS_FINAL_HOST_MIGRATION**（DEC-012 target `kau17033/kau17033-nexora-core`; preflight CI 35788103422 PASS） |
| T-100 | seed 導出の原文照合 | T-010 | ゴールデン再検証 PASS | **DONE**（CI run 35739331939: 13 frozen checks; source verified） |
| T-110 | VEA-G3 Phase A / confirmatory gate | T-020, HG-VEA-ESTIMAND, HG-VEA-FREEZE-SCOPE, HG-VEA-WS-C, HG-VEA-HD53 | frozen values preserved + human gates satisfied | BLOCKED_HUMAN |
| T-200 | LoopCell Phase 0 execution readiness | HG-LOOP-C06, HG-LOOP-PAID | frozen SSOT intact + environment/paid human gates satisfied | BLOCKED_HUMAN |
| T-300 | Outlier v1.0 法務ゲート | HG-OUTLIER-LEGAL | 法務判断の記録 | BLOCKED_HUMAN |

## 状態語
`TODO` / `IN_PROGRESS` / `BLOCKED` / `DONE` / `ABANDONED`。
`DONE` にするには、判定列のコマンドの実測出力を `evidence/` に残すこと。
