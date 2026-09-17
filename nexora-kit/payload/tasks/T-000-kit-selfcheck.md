# T-000 — キット自己検証

- blocked_by: —
- unlocks: T-010
- role: implementer（検証は protocol-guardian が独立に再実行する）

## 目的
ゲートが黙って無効化されていないことを実測で確認する。宣言では確認しない。

## 手順
```bash
python3 tools/kit_check.py --evidence
```

## 完了条件（機械判定）
- `tools/kit_check.py` が exit 0。
- guard.py の全ケースが期待終了コードと一致（`tools/guard_fixtures.py`）。
- 不正入力で guard.py が exit 2（fail-closed。exit 1 は非ブロッキング扱いになる）。
- `evidence/T-000/<UTC>.md` に実測が保存されている。

## 手動確認（Claude Code 上でのみ可能。自動化できない）
1. `/hooks` で PreToolUse と SessionStart が登録されていることを見る。
2. `/context` で CLAUDE.md が読み込まれていることを見る。
3. 実際に `sources/` 配下への Edit を試み、ブロックされることを確認する。
   フックが起動しない場合（パス誤り・タイムアウト）は非ブロッキングになる。
   ブロックされなければ、キットは無効である。STATE.md に記録して停止する。

## 禁止
- 失敗を「環境要因」として片付けない。フックが動かない状態は `FAIL` である。
- T-010 以降へ進まない。
