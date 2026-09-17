# REPO-004 — `vea-g3/GATE_STATUS.json` の確認

出典: `GATE_STATUS.json`（blob `0c57fe58…`）。`generated_by: "L1-3 convergence pass (read-only)"`。
**注意**: 当該ファイルの `head` は `c613510986…` だが、取得時のリポジトリ HEAD は `afc23323…`。
生成時点のスナップショットであり、現行 HEAD と一致しない可能性がある。`repo` の値は Windows パス。

## 1. リポジトリ自身の総合判定

```json
"truth_state": "NOT_DETERMINABLE"
"scientific_promotion": "NONE"
"standing_invariant": "SUCCESS != HYPOTHESIS_SUPPORTED"
```

最後の不変条件は、本キット CLAUDE.md §4「テスト合格を仮説支持にしない」と同一の規律である。

## 2. 根本原因 — G4（selection）に集約されている

```json
"current_blocker_gate": "G4"
```

| Gate | 状態 |
|---|---|
| G0 repo/state integrity | PASS |
| G1 experience validity | PASS |
| G2 artifact identity | PASS |
| G3 eligibility | PASS_IMPL（closure: NOT_APPLICABLE。実験データなし） |
| **G4 selection** | **BLOCKED** |
| G5 transfer / G6 application | NOT_STARTED（G4 の下流） |
| G7 outcome measurement | PASS_CONTRACT |
| G8 causal effect (tau) | NOT_STARTED（**tau uncomputable, \|D\|=0**） |
| G10 NES | DEFERRED（RQ3、MVP 外） |
| G12–G14 | HYPOTHESIS |
| G15 novelty | UNKNOWN |

### G4 の証拠（実測）

| 実行 | 結果 |
|---|---|
| 履歴 | `SOURCE_SELECTION_FAILED` **×25/25** |
| R5@640 run `34294080720` | 6/6 source legs が `outcome=0/TRUNCATED/640-steps`。**A/B byte-identical。どの leg も terminate しない** |
| ONE VALID TREATMENT run `34296827883` | 2/2 が `SOURCE_SELECTION_FAILED` / `outcome=U`、instance-independent |
| 10-pair pilot run `34301420718` | 20/20 COMPLETED、**10/10 C1-VEA=SSF**、reconciliation population **D empty**、**tau uncomputable** |

`select_source` は `terminated is True` のみを受理するため `selected=None` になる。

**因果の鎖**: source leg が terminate しない → source selection が常に失敗 → 割付集団 D が空 →
tau が計算不能 → G8 に到達できない。**G4 が全体を塞いでいる。**

## 3. CONF-17 の強化 — 退化方策仮説には名前が付いている

```
"seed j0 first 4 steps = [2,2,2,2], parse_failures=0 -- consistent with the
 WS-C degenerate-policy hypothesis"
```

**`WS-C` 退化方策仮説**として既に命名・記録されている。
Bridge Probe の 639/640 同一応答（REPO-002 §6）は独立した観測であり、同じ仮説を支持する。

ただし当該断片は「engineering fragment only (NOT R5 evidence)」「4 steps far too short」と
明記されており、**仮説の確証ではない**。CONF-17 は OPEN のままとするが、
「未知の異常」ではなく「**命名済みの仮説 WS-C**」として扱う。

## 4. 実行環境 — INFRASTRUCTURE_BLOCKED（科学的未準備ではない）

```json
"R5_at_640": "INFRASTRUCTURE_BLOCKED (local host). Runtime identity + model digest +
              num_ctx all PASS/measured; blocker is compute throughput, not scientific readiness."
```

| 項目 | 実測値 |
|---|---|
| ホスト RAM | 7.65 GB total / **~0.4 GB free** |
| 実行形態 | CPU のみ（`size_vram=0`）、pagefile 依存 |
| 速度 | **37.2 s/step** |
| 1 episode | 640 steps × 37.2 s ≈ **6.6 時間** |
| R5@640 全体 | 3 seeds × 2 legs ≈ **40 時間** |
| 実績 | background run は 30–40 分で外部 kill、0 episode 完了 |

`GATE_A` PASS（pytest 372 passed、provenance 14/14 MATCH、system_prompt sha256 MATCH）、
`RUNTIME_IDENTITY_GATE` PASS、`MODEL_DIGEST_GATE` PASS、`GATE_B_num_ctx` MEASURED=4096。
**科学・プロトコル・ランタイム同定はすべて通っている。** 詰まっているのは計算資源だけである。

必要条件として「**Claude Code が ≥8 GB の Linux VM 上で動作すること**」が明記されている。
文書は `~$0.08–0.17/h` のクラウド VM を示唆しており、**これは費用を伴うため本セッションの
委任範囲外**である（`control/decisions.md` の委任の境界）。

**本セッションの環境でも実行できない**（Ollama 未導入、外向き egress がポリシーで遮断、
qwen3:8b の 5,225,388,164 bytes を取得できない）。判定は同じく `INFRASTRUCTURE_BLOCKED`。

## 5. テスト数の訂正 — 337 は当時の値、正典は 372

`h2_6_test_count_reconciliation`（human **DECISION-1**, 2026-09-09）:

| 値 | 位置づけ |
|---|---|
| **372** | **正典**（`canonical_frozen_repo_test_count`）。`frozen_head: bf276fe4…`。判定基準は `pytest -q == 372 passed` |
| 392 | **棄却**。372 + `tests/test_actions_resource_observer.py` の 20 件（DP-27 probe、どの ref にも commit されていない） |
| 337 | 96a87f4（2026-08-27）時点の値 |
| 308 / 303 | さらに古い文書中の値 |

**本キットの記録を訂正する。** 「337/337 PASS」は 96a87f4 時点の事実であり、
**現在の正典は 372** である。履歴事実を現在の妥当性へ昇格させない原則（CLAUDE.md §5）の実例。

## 6. OQ-013 の更新 — 同種の数値が 4 つになった

`SOURCE_SELECTION_FAILED` 関連の計数は、時点も単位も異なる **4 つ**が存在する。

| 値 | 出典 | 単位 |
|---|---|---|
| 75 件 | Addendum（NOT ASSESSABLE） | 過去 outcome |
| 25/25 | GATE_STATUS G4 | 履歴 |
| 19/19 + 57/57 | commit 96a87f4 | pairs / source attempts |
| 10/10 | 10-pair pilot `34301420718` | C1-VEA |

**いずれも等値してはならない。** 外部 kernel の「75/75 → γ=0 → R0=0」は、
このうち 1 つを選び、リポジトリが評価不能としている集合に確定値を与えたものである。

## 7. その他

- `layer_a_gate_c`: `GATE_C_SPECIFICATION.md` は**提案であり、人間の採択待ち**。opened でも passed でもない。
- `required_approval_obtained`: R5@640 / one-valid-treatment / pilot は H-3/B の standing 承認あり。
  **155-pair は manual go**（別途の人間承認が必要）。
