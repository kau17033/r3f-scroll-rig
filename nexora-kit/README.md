# NEXORA 引き継ぎキット v1.0

Claude Code が NEXORA の仕様からずれずに開発を進めるための、配置可能な一式である。
要約を渡す方式では、仕様からのずれを防げない。本キットは **原文を不変の正本（SSOT）として固定し、
全節の処置が 100% 埋まるまで実装を禁止する** ことを、フック・権限 deny・人間判断キューで強制する。

## 現在の状態

| 項目 | 状態 |
|---|---|
| キットの健全性（T-000） | **PASS**（`python3 payload/tools/kit_check.py`） |
| 正本（`payload/sources/`） | **未投入** — 原文は本セッションから到達できない |
| 実装解禁ゲート | **BLOCKED**（G1..G5 すべて） |
| 人間判断（DEC-001..009） | **すべて PENDING** |

原文が無い状態で実装が始まらないことは欠陥ではなく、設計どおりの停止である。

## 配置先について（DEC-002 未決）

本キットは、対象リポジトリが未決（DEC-002）であるため、**この リポジトリのルートには置いていない**。
`nexora-kit/payload/` に置かれている限り、Claude Code は `CLAUDE.md` も `.claude/` も読まないため、
規約は一切効かない。強制力を持たせるには、対象リポジトリのルートへ配置する必要がある。

```bash
python3 nexora-kit/install.py --target /path/to/target-repo --dry-run
python3 nexora-kit/install.py --target /path/to/target-repo
```

詳細は `INSTALL.md`。

## 構成（62 ファイル）

```
payload/
├── CLAUDE.md                     運用規約（70 行。原文と矛盾したら原文が優先）
├── .claude/settings.json         auto memory 無効化 / deny / hooks
├── .claude/hooks/guard.py        PreToolUse。fail-closed（例外時も exit 2）
├── .claude/hooks/session_start.py 正本の完全性・未決件数を毎回提示
├── .claude/skills/               board, manifest, ingest, next, run-task,
│                                 gate, decision, deviation, handoff
├── .claude/agents/               protocol-guardian, evidence-auditor,
│                                 adversarial-reviewer, forensic-investigator,
│                                 implementer, test-engineer
├── sources/                      正本の置き場（README に投入手順。現在は空）
├── control/                      AUTHORITY / STATE / conflicts / decisions /
│                                 open_questions / deviations / glossary /
│                                 section_index / disposition / requirements /
│                                 traceability / audit70
├── tasks/                        INDEX + T-000..T-070 + T-100/110/200/300
├── tools/                        manifest, index_sections, seed_derive,
│                                 gate_check, kit_check, guard_fixtures
├── tests/                        36 件（stdlib unittest。外部依存なし）
└── .github/workflows/nexora-ci.yml
```

## 4 層の防御

1. 原文そのものを不変の正本にする（要約しない）。
2. SHA-256 マニフェストをセッション開始時と CI で照合する。
3. 権限 deny とフックで変更を遮断する。
4. 全節の処置表を 100% 埋めるまで実装を禁止する（`tools/gate_check.py`）。

`guard.py` は難読化されたシェルを捕捉できない。これは 2 と 4 で補う設計である。
単層に依存しない理由は、PreToolUse が黙って無効化され得るためである
（スクリプトのパス誤り、タイムアウト、設定の読み込み失敗は、いずれも非ブロッキングになる）。

## 断定条件（「完遂」と言える条件）

```bash
python3 tools/gate_check.py   # exit 0 のときのみ
```
G1 正本の完全性 PASS / G2 disposition PENDING=0 / G3 decisions PENDING=0 /
G4 traceability 完備 / G5 AUDIT§70 の 11 項目が 0。

## 検証済みの事実（本セッションの実測）

| 項目 | 結果 |
|---|---|
| guard.py の期待挙動 | 35/35 一致（ブロック 25 件 / 通過 10 件） |
| guard.py の fail-closed | 不正入力で exit 2 |
| seed 導出ゴールデン | 18 ベクタ一致（`status: UNVERIFIED_AGAINST_SOURCE`） |
| 索引器の回帰（`→` を含む見出し） | 取りこぼしなし |
| unittest | 36 件 OK |
| インストール後の単独動作 | T-000 PASS |

**断定不可**: 上記はキットの健全性であり、NEXORA 仕様への適合ではない。
仕様適合は原文投入後（T-010 以降）にしか判定できない。

## 未決の人間判断

`payload/control/decisions.md` の DEC-001..009。とくに次を先に決めないと Phase A は開始できない。
- DEC-001 権威階層とロック状態
- DEC-002 対象リポジトリ（既存 / 新規）
- DEC-003 モデル束縛
- DEC-004 Phase A 固定値（13 項目）
