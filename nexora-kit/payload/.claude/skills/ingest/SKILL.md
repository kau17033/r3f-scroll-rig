---
name: ingest
description: 原文を節単位に索引化し、disposition 台帳の骨格を作る。原文投入直後（T-030）に使う。索引器の欠番報告の解釈手順を含む。
---

# /ingest — 原文の索引化

```bash
python3 tools/index_sections.py sources/<file> --source-id <SRC-xx> \
    --out control/section_index.csv --disposition control/disposition.csv
```

## 出力の読み方
- `sections` / `lines`: 索引された節数と行数。
- `suspect_headings`: 数式変換の残骸と疑われる見出し。**削除しない**。処置語 `ARTIFACT` を与える。
- `NUMBER_GAPS`: 欠番。**原文の欠落と断定しない。**

## 欠番が出たときの手順
1. 該当番号を原文から直接 grep する（`grep -n '§650' sources/<file>`）。
2. 原文に存在する場合 → 索引器の欠陥である。`tools/index_sections.py` を修正し、
   回帰ケースを `tools/kit_check.py` の `check_indexer` に追加する。
   （前歴: 見出しに `→` を含む節を検出器が落とした。）
3. 原文にも存在しない場合 → `open_questions.md` に `NOT_IDENTIFIABLE` として記録する。

## 禁止
- 原文を整形しない。抽出残骸も削らない。
- 索引の都合で原文を書き換えない（guard.py がブロックする）。
