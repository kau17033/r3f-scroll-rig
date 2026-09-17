# 導入手順

## 前提
- Python 3.8 以上（外部パッケージ不要）
- git

## 1. 配置

```bash
# 内容を確認する（書き込みなし）
python3 nexora-kit/install.py --target /path/to/target-repo --dry-run

# 配置する
python3 nexora-kit/install.py --target /path/to/target-repo
```

既存ファイルがある場合は中止する。上書きするなら内容を確認してから `--force` を付ける。

## 2. キットの自己検証（T-000）

```bash
cd /path/to/target-repo
python3 tools/kit_check.py --evidence
```
`RESULT: PASS` と exit 0 を確認する。`evidence/T-000/<UTC>.md` に実測が残る。

## 3. 原文の投入（人間が実行）

```bash
cp <原文> sources/SRC-01-ultracode.md      # 以下 SRC-02..07
python3 tools/manifest.py build
chmod a-w sources/SRC-*
python3 tools/manifest.py verify           # VERIFY: PASS
```

原文はそのまま置く。要約・整形・誤字修正をしない。抽出テキストの残骸も削らない。

## 4. commit と push

```bash
git add -A && git commit -m "NEXORA kit + sources" && git push -u origin <branch>
```

## 5. Claude Code 上での確認（自動化できない。必ず目視する）

1. `/hooks` — PreToolUse と SessionStart が登録されていること。
2. `/context` — `CLAUDE.md` が読み込まれていること。
3. 実際に `sources/` 配下の Edit を試み、ブロックされること。

**3 でブロックされない場合、キットは無効である。** PreToolUse は次の場合に黙って
非ブロッキングになる: スクリプトのパス誤り、フックのタイムアウト、設定の読み込み失敗。
その状態で作業を続けてはならない。

## 6. 初回投入プロンプト

```
CLAUDE.md を読み §0 を実行せよ。次に T-000（キット自己検証）のみを実行し、
T-010 以降へ進まず停止せよ。

完了条件:
1) python3 tools/kit_check.py --evidence が exit 0
2) guard.py が全 35 ケースで期待終了コードを返す（0 / 2 のみ。1 を返さない）
3) sources/ への Edit が実際にブロックされることを Claude Code 上で確認する
4) 各実測コマンドと出力を evidence/T-000/ に保存する

報告は 8 項目形式（現状・作業・変更・実測・判定と根拠・未解決・停止理由・必要な人間判断）とする。
```

## 7. 同期ループ

- Claude Code 側: セッション末尾で `/handoff`。`control/STATE.md` と `control/decisions.md` を commit。
- 人間側: その 2 ファイルを見て DEC を決定し、Status を書き換えて commit。
- 正本は常にリポジトリ側に置く。会話側は判断に専念する。

## 既知の制約

| 制約 | 補い方 |
|---|---|
| `guard.py` は難読化シェル・未知のインタプリタを捕捉できない | manifest 照合（SessionStart と CI） |
| Bash の deny 規則は別表記（`/bin/rm` 等）を捕捉しない。セキュリティ境界ではない | 同上 |
| Read/Edit の規則はサブプロセス経由の間接的な読み書きに及ばない | 同上 |
| クラウドセッションはローカルの `~/.claude/settings.json` を読まない | 設定をリポジトリ側に置く（本キットの構成） |
| PreToolUse のタイムアウトはツール呼び出しを止めない | CI とマニフェスト照合で事後検出する |
| Windows の PowerShell ツールは guard の対象外 | 同上 |
