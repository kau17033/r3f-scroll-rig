# sources/ — 正本（原文そのまま）

**このディレクトリのファイルは編集禁止である。** 要約・整形・誤字修正も禁止する。
要約を正本の代替にすると、仕様からのずれは検出できなくなる。

## 収容物
| ID | ファイル名（推奨） | 内容 | 状態 |
|---|---|---|---|
| SRC-01 | `SRC-01-ultracode.md` | ULTRACODE 指令群（CONV§0–34 / AUDIT§0–73 / SOV§0–1313、計 1,423 節） | 未投入 |
| SRC-02 | `SRC-02-vea-g3-ssot.md` | VEA-G3 実装仕様 SSOT v2.0 | 未投入 |
| SRC-03 | `SRC-03-paper4.md` | 論文4（実証なし・Freeze 未通過） | 未投入 |
| SRC-04 | `SRC-04-loopcell.md` | LoopCell Phase 0 | 未投入 |
| SRC-05 | `SRC-05-outlier.md` | Outlier v1.0 製品仕様 | 未投入 |
| SRC-06 | `SRC-06-session.md` | セッション共有 URL（**非権威**） | 未投入 |
| SRC-07 | `SRC-07-dev-protocol.md` | 開発プロトコル | 未投入 |
| SRC-08 | `SRC-08-evidence-kernel/` | 外部 kernel（27 不変条件・SPEC・各 register）。**非権威**: 監査対象であり正本ではない | 未投入（EXTERNAL-001 参照） |

## 投入手順（人間が実行する）
```bash
# 1) 原文をそのまま配置する。抽出テキストの残骸（"# ["、"# ERS" 等）も削らない。
cp <原文> sources/SRC-01-ultracode.md
# 2) マニフェストを作る
python3 tools/manifest.py build
# 3) 書込不可にする
chmod a-w sources/SRC-*
# 4) 照合する（PASS になること）
python3 tools/manifest.py verify
# 5) 索引を作る（節数と欠番を確認する）
python3 tools/index_sections.py sources/SRC-01-ultracode.md --source-id SRC-01 \
    --out control/section_index.csv --disposition control/disposition.csv
```

## 注意
- 抽出テキストであること自体を記録する。数式変換の残骸を「欠落」と判断しない。
- 欠番が出た場合、まず索引器の欠陥を疑う（見出しに `→` を含む節を落とした前歴がある）。
- `MANIFEST.sha256` が無い状態では `SOURCES_INTEGRITY` は `NOT_IDENTIFIABLE` となり、
  CLAUDE.md §0 により実装は禁止される。これは想定された初期状態である。
- SRC-06 は認証が必要で内容を取得できない（`INFRASTRUCTURE_BLOCKED`）。
  SRC-02 ISO§2 上、過去セッションは非権威であるため、取得不能は仕様の欠落ではない。
