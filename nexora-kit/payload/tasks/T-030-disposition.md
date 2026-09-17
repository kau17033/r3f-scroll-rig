# T-030 — 全節 disposition

- blocked_by: T-010
- unlocks: T-040

## 目的
全 1,423 節（および他正本の全節）に処置を与える。読み飛ばしを許さない。

## 手順
```bash
python3 tools/index_sections.py sources/SRC-01-*.md --source-id SRC-01 \
    --out control/section_index.csv --disposition control/disposition.csv
```
`control/disposition.csv` の各行に処置を記入する。

## 処置語
| 語 | 意味 |
|---|---|
| `REQUIREMENT` | 実行すべき要求。`requirements.csv` に正規化する |
| `CONSTRAINT` | 禁止・制約。テストで担保する |
| `CONTEXT` | 背景。実行を伴わない |
| `DEFER` | 人間の決定が必要。`decisions.md` に起案する |
| `CONFLICT` | 他の正本と矛盾。`conflicts.md` に記録する |
| `UNSPECIFIED` | 実行に必要な値が無い。`open_questions.md` に記録する |
| `SUPERSEDED` | 後段の節に置換された。置換元を明記する |
| `ARTIFACT` | 抽出残骸。原文は削らず、処置のみ記録する |

## 完了条件
- `disposition.csv` の行数 = 索引された節数。
- `PENDING` が 0（`tools/gate_check.py` の G2）。
- 欠番が報告された場合、索引器の欠陥を検証した記録があること。

## 禁止
- 「重要でない」を理由に節を飛ばさない。処置語を与えることが処置である。
