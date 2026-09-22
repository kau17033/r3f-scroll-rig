# DECISIONS — 人間判断キュー

Claude Code は本ファイルに **起案** のみ行う（`/decision`）。Status の変更は人間が commit する。
Status: PENDING / APPROVED / REJECTED / DEFERRED。

| ID | 内容 | 依存 CONF | 影響タスク | Status |
|---|---|---|---|---|
| DEC-001 | 権威階層の承認（CONF-01）と SRC-02 のロック状態確定（CONF-02） | 01, 02, 09, 10 | T-020 以降すべて | PENDING |
| DEC-002 | 対象リポジトリ（既存 / 新規） | — | T-010 | **APPROVED**（案 A、2026-09-17。構成の決定は委任された） |
| DEC-003 | VEA-G3 モデル束縛（provider / model_id / snapshot / endpoint / decoding） | 06 | T-020, T-1xx | PENDING |
| DEC-004 | Phase A 固定値一式（下表） | 04, 07 | T-1xx | PENDING |
| DEC-005 | RQ 番号の名前空間化 | 03 | T-040 | PENDING |
| DEC-006 | LoopCell Phase 0（SSOT 本文・D-M0-2・モデル/価格） | — | T-2xx | **大半が解決済**（REPO-003）。SSOT v1.1.2 は凍結済で存在、モデル/価格も決定済。残るのは **C-06**（`runner.py` の `experiment_repo.name` が `langgraph-reflection` をハードコード。正本は `loopcell` へ移設済。**t0 開始前に人間の裁定が必要**）。D-M0-2 は原文不在のため **NOT_IDENTIFIABLE** として確定（REPO-007 §1） |
| DEC-007 | Outlier v1.0 の現行性確認と法務ゲート | — | T-3xx | PENDING |
| DEC-008 | 優先順位は SOV§114 と SOV§181 のどちらか | 05 | T-070 | PENDING |
| DEC-009 | コスト方針のスコープ分割 | 08 | T-2xx, T-3xx | PENDING |
| DEC-010 | 統治系の一本化（外部 27 不変条件 / 本キット control/ / 責務分割） | 12 | 全タスク | **APPROVED**（2026-09-22。横断 control plane を唯一の統合現在地正本とし、凍結 SSOT は各実験スコープの上位正本として保持） |
| DEC-011 | 統合プロダクト名の確定と `ORP` の名前空間化 | 13 | 全識別子 | **APPROVED**（案 C、2026-09-17） |

## DEC-004 の内訳（すべて未決。1 つでも欠ければ Phase A を開始しない）
| 項目 | 値 | 根拠 |
|---|---|---|
| 主要指標 | PENDING | — |
| 推定対象（ITT / pair-complete ∩ received-valid） | PENDING | CONF-04 |
| α | PENDING | SRC-03 候補: 片側 0.05 |
| 検出力 | PENDING | SRC-03 候補: 0.80 |
| MDE（τ） | PENDING | SRC-03 候補: 0.10 |
| N（n_pair） | PENDING | SRC-03 候補: 153（生成 184） |
| 多重比較 | PENDING | — |
| CF の種別 | PENDING | — |
| AFR 閾値 | PENDING | — |
| 意味的汚染の方法と閾値 | PENDING | — |
| 人件費の時給 | PENDING | — |
| 1 use の定義 | PENDING | — |
| 経済 MDE | PENDING | — |
| 停止規則（固定n / anytime-valid） | PENDING | CONF-11。e-value 採用時は GATE 1 の `b+c >= 20` が不要になる |
| 検出力の代償の許容範囲 | PENDING | EXTERNAL-001: p=0.6, n=200 で検出力 0.787 → 0.580 |

注: SRC-03 の候補値は **候補** であり、採用の可否自体が DEC-004 の一部である（SRC-03 に実行権限はない）。

## 起案フォーマット
```
| DEC-0NN | <決定すべき一文> | <CONF-ID または —> | <影響タスク> | PENDING |
```
起案時は本文末尾に、選択肢 A/B と各々の帰結、決定しない場合に停止する作業を併記する。

## 外部提出物により具体化した点（EXTERNAL-001）

- **DEC-002**: evidence-kernel 系リポジトリが対象候補に加わった。現在接続中の
  `kau17033/r3f-scroll-rig` は研究リポジトリではない。
- **DEC-004**: 停止規則の選択肢が 2 つに確定した。
  - 案 A: 固定n（McNemar 正確検定）。のぞき見を禁止する。適応的 argmax IG/cost と両立しない。
  - 案 B: anytime-valid（e-value）。任意停止を許す。同一 n_max で検出力が下がる
    （実測: p=0.6, n_max=200 で 0.787 → 0.580）。
  どちらも根拠は揃っている。**選択は人間が行う。** 自律で案 B を採らない。
- **DEC-006**: 外部 README は LoopCell Phase 0 v1.1 を「人間承認済み」「ULTRACODE §4 precedence に
  より再設計対象外」と記載する。ただし本キットは当該 README を正本として扱わない。
  SRC-04 本文の投入をもって確定する。

## DEC-011 統合プロダクト名 — **決定済み（案 C、2026-09-17、人間による決定）**

### 決定内容

| 項目 | 値 | 状態 |
|---|---|---|
| **内部コード名** | **NEXORA** | **確定**。リポジトリ・識別子・文書はこれを使う |
| **対外名** | 未定 | **保留**。弁理士のクリアランス完了まで決定しない |

### この決定が固定すること

- キットの識別子（`nexora-kit/`、`[NEXORA-GUARD]`、ワークフロー名）を**変更しない**。
- 対外名の決定は、原文投入（DEC-002）以降の作業を**塞がない**。
- 対外名を決める際は、下記「選定手続き」に従う。候補 4 案から選ばない。

### この決定が固定しないこと

- 商標の出願可否。ドメインの取得可否。**いずれも断定不可のまま。**
- 対外名そのもの。NEXORA が対外名になる可能性も、ならない可能性も残る。

### 以下は決定に至るまでの調査記録（2026-09-17 起案時）


### 予備調査（**商標クリアランスではない**。法的判断は資格を持つ人間が行う）

| 候補 | 同分野での使用 | 商標 | 調査所見 |
|---|---|---|---|
| NEXORA | **多数**。AI/ソフトウェア企業が複数、GitHub に `NEXORA-AI` も存在 | US Reg. #7833669（Jewelry、2025-06-17 登録、Guangzhou Lingshi E-commerce）。近接語 NEXERA も登録あり | 造語としての独自性は市場では既に失われている。ソフトウェアの区分とは別区分だが、識別性の前提が崩れる |
| LOOPERA | **あり**。LoopEra Labs（`looperalabs.com`）が `LoopEraSell` を Google Play で配信。ソフトウェア分野 | 確認できず | 追加調査で判明。前回の「確認できず」を訂正する |
| SYMBORA | K-POP 物販（別分野）。`symbora.com` はプレミアムドメインとして売り出し中 | 確認できず | AI 分野での衝突は相対的に小さい |
| ORIGIN | 一般語。多数 | — | 識別性が低い（提案者自身も指摘） |

### 調査できなかった事項（INFRASTRUCTURE_BLOCKED）

本セッションのネットワークポリシーは、DNS 解決・RDAP 照会・任意ドメインへの HTTP 取得を拒否する
（`dns.google:443` / `rdap.org:443` / `nexora.com` いずれも CONNECT に 403）。したがって次は**未確認**である。

- 各ドメインの登録の有無、登録日、登録者
- `nexora.com` / `nexora.ai` / `loopera.ai` / `symbora.ai` の取得可否
- 日本（J-PlatPat）および各国での商標登録状況
- 区分 9 / 42 における NEXORA の登録の有無（確認できたのは Jewelry 区分のみ）

これらは仕様の欠落ではなく環境の制約である。判断の前に、制約のない環境で実施すること。

### 改名コストの実測

| 指標 | 値 |
|---|---|
| 文字列出現 | 48 回 / 22 ファイル |
| パス名 | 3 件（`nexora-kit/`, `.github/workflows/nexora-kit.yml`, `payload/.github/workflows/nexora-ci.yml`） |
| 機械が参照する識別子 | 1 組のみ（`[NEXORA-GUARD]` と `tests/test_guard.py` の対応する表明） |

**改名は工学的な障害ではない。** 判断はブランド上の根拠だけで行える。
ただし原文投入後は `sources/` がハッシュ固定されるため、名称が本文に現れる場合は
投入前に確定しておくほうが安い。

### 選択肢

- 案 A: NEXORA を維持し、区分（ソフトウェア）での登録可能性を法務に確認する。
  市場での識別性は低いまま残る。
- 案 B: 別名（LOOPERA / SYMBORA / 新規造語）へ変更する。現在の改名コストは 48 箇所・1 識別子。
- 案 C: 内部コード名として NEXORA を継続し、対外名は公開直前に確定する。
  本キットの識別子は内部名で固定できるため、対外名の決定を遅らせても工学的負債は増えない。

### 所見の要約

4 案すべてに同分野または近接分野での使用が確認された。
「造語だから識別性がある」という前提は、4 案のいずれについても成立していない。
候補の選択より先に、**選定手続き**（下記）を固定するほうが費用対効果が高い。

**いずれも自律で選ばない。** 商標・ドメインの可否は法的判断であり、断定不可である。

## DEC-002 対象リポジトリ — 調査結果（2026-09-17、暫定指定を受けて）

指定: 「とりあえず VEA-G3 / LoopCell / ORP をリポジトリ名とする」

### 実在確認

| 名前 | 実在 | 可視性 | 最終 push | 備考 |
|---|---|---|---|---|
| `kau17033/VEA-G3` | **あり** | private | 2026-09-09 | 下記のとおり原文と統治文書を既に含む |
| `kau17033/LoopCell` | **あり** | private | 2026-08-10 | 未調査 |
| `ORP` | **なし** | — | — | 新規作成が必要。名称は CONF-14 |

参考: `kau17033/focal`（private）と `kau17033/-home-user-outlier-kill-bench-`（private）も存在する。
SRC-05 FOCAL / Outlier に対応する可能性があるが未確認。

### 履歴事実の照合（T-010 の一部が完了）

`96a87f45d3b08f26d8f3658d3c0ca42d0cbb6041`（2026-08-27、`kau17033/VEA-G3`）を確認した。
**OQ-007 は CLOSED_RECOVERED。** 当該 commit の記述は次を含む。

- 全テスト 337/337 PASS（既存 325 + 新規 12）— 本キットが記録していた履歴事実と一致
- 根本原因 A（`log_sink` 未配線）と C（`parse_failure_count >= 0` が常に真）
- 「19/19 pairs、C1=SOURCE_SELECTION_FAILED（19/19、source attempts 57/57）」
- 「Batch 14: NOT RUN. Human Re-Approval required」

**注意**: 337/337 は commit メッセージ内の記述であり、再実行による確認はしていない。
本キットの扱いでは `RECOVERED`（現物の存在を確認）であって、`VERIFIED`（再現）ではない。

### 前提の訂正

`vea-g3` は次を既に含む。**「原文がリポジトリに無い」という前提は SRC-02 について成立しない。**

```
SSOT.md  SPEC.md  PROTOCOL_LOCK.md  PREREGISTRATION.md  COMPLIANCE_MANIFEST.md
GATE_C_SPECIFICATION.md  GATE_STATUS.json  CLAIM_STATUS.md  RESEARCH_STATE.md
CORPUS_CONVERGED_SPEC.md  SERVICE_IMPLEMENTATION_SSOT.md  RECONCILIATION.md
canonical/  evidence/  runs/  research/  intake/  src/  tests/  scripts/  configs/
```

`COMPLIANCE_MANIFEST.md` が既に存在するため、**T-020 は未着手ではない可能性が高い**。
投入前に既存の内容を読み、重複作成しないこと。

### 構成の選択肢（未決）

| 案 | 構成 | 帰結 |
|---|---|---|
| A | 統治リポジトリを 1 つ新設し、SRC-01 と control/ をそこに置く。VEA-G3 / LoopCell / ORP は各スコープの実装 | 横断する矛盾（CONF-01..14）と全節 disposition に居場所ができる。リポジトリが 4 つになる |
| B | `vea-g3` をハブとし、キットをその root に置く | 既存の統治文書と三重化する（CONF-12）。`tests/` が衝突し得る（OQ-015） |
| C | 3 リポジトリそれぞれにキットを複製 | **禁止**。SSOT が 3 つに分岐し、キットの目的と正面から矛盾する |

**推奨は A。** 理由は 2 つ。SRC-01（1,423 節）は 3 スコープすべてに跨るため、
どれか 1 つのリポジトリに置くと残り 2 つから参照できない。また `gate_check.py` は
単一の `disposition.csv` 上で判定するため、リポジトリを分けると全体の完遂条件が定義できない。

## DEC-002 決定 — **構成 A、リポジトリ 3 つ（2026-09-17、委任により決定）**

### 決定内容

| リポジトリ | 状態 | 役割 | 収容物 |
|---|---|---|---|
| `kau17033/nexora-core` | **新規作成が必要** | 横断統治 + 統合・運用基盤 | 本キット、SRC-01（ULTRACODE 1,423 節）、SRC-03、SRC-07、`control/` 台帳一式、`sources/MANIFEST.sha256` |
| `kau17033/VEA-G3` | 既存 | VEA-G3 実験スコープ | 既存の SSOT.md / SPEC.md / PROTOCOL_LOCK.md / evidence/ を**そのまま維持** |
| `kau17033/LoopCell` | 既存 | LoopCell Phase 0 スコープ | 同上（未調査） |

**`ORP` という名前のリポジトリは作らない。**

### 決定 1: 構成 A を採る理由

| # | 根拠 |
|---|---|
| 1 | SRC-01 は 3 スコープすべてに跨る。`vea-g3` の中に置けば、リポジトリ全体の統治が 1 スコープに従属する。`control/AUTHORITY.md` §1 のスコープ分割と矛盾する |
| 2 | `gate_check.py` は単一の `disposition.csv` 上で判定する。統治を分散させると全体の完遂条件が定義不能になる |
| 3 | `vea-g3` は既に PROTOCOL_LOCK / GATE_C_SPECIFICATION / RESEARCH_STATE を持つ。その root に第二の統治層を重ねる行為は、三重統治（CONF-12）を最も悪い場所——実行中のリポジトリの内部——に持ち込む |
| 4 | `vea-g3` の `tests/` は pytest 構成。本キットの unittest を同居させると衝突し得る（OQ-015） |
| 5 | **可逆性**。新規リポジトリは削除できる。既存リポジトリの root を書き換える行為は、実行中の研究の作業手順を一方的に変える |

### 決定 2: 3 つ目の名前を `ORP` にしない理由と、代替

`ORP` をリポジトリ名にすると、URL・clone パス・import パスという**最も撤回しにくい層**に
裸の `ORP` が焼き付く。DEC-011 で確定した処置（CONF-13: `SOV-ORP` / `OUTLIER-ORP` /
`BRAND-ORP` に分離、裸の `ORP` は使用禁止）が形骸化する。

さらに、指定された `ORP = 統合・運用基盤` は**ブランド層の役割名**（`BRAND-ORP`）である。
DEC-011（案 C）により対外名は未定であるから、ブランド層の語をリポジトリ名に固定するのは早い。

採用: **`nexora-core`**

| 条件 | 適合 |
|---|---|
| DEC-011 と整合 | `NEXORA` は承認済みの**内部コード名**。private リポジトリでの使用は対外ブランドの使用ではない |
| CONF-13 / CONF-14 と整合 | 裸の `ORP` を含まない |
| 役割を表す | `-core` は横断層であることを示し、特定スコープを含意しない |
| 形式 | 小文字・空白なし・GitHub のリポジトリ名として有効 |

統合・運用基盤の役割は当面 `nexora-core` が担う。実行時コードが分離を要する規模になった
時点で別リポジトリへ切り出す。そのときも裸の `ORP` は使わない。

### 付随して解決した項目

- **CONF-14**: RESOLVED。`ORP` というリポジトリ名を作らないことで解決した。
- **OQ-015**: RESOLVED。キットは `nexora-core` に置くため、`vea-g3` の `tests/` と衝突しない。
- **OQ-014**: OPEN のまま。`vea-g3` の既存統治文書と本キットの責務分担は、
  実際に読んでから決める（次の作業）。

### 決定が固定しないこと

- `vea-g3` / `LoopCell` の中身は**変更しない**。本決定は配置先の決定であり、既存資産の改変ではない。
- T-020 の既着手範囲。`vea-g3/COMPLIANCE_MANIFEST.md` を読むまで断定不可。

## 委任の境界（2026-09-17、人間による恒常的委任を受けて記録）

指示: 「今後全ての許可を設計に理にかなっており、無料なら君に任せる」

### 委任される（自律で実行する）
- 読み取り調査、台帳の更新、キットの実装・検証、commit / push、PR 運用
- 構造的・機械的な決定（配置、命名、索引、回帰テストの追加）

### 委任されない（条件により範囲外）
| 事項 | 理由 |
|---|---|
| LoopCell の API 呼び出し（determinism 30 calls / t0 / learn / t1） | **課金を伴う**（input 1.0 / output 5.0 USD per MTok）。「無料なら」の条件を満たさない |
| 研究目的・仮説・推定対象・指標・MDE・N・α・seed・除外・停止規則・モデル束縛 | **設計自身が人間判断を要求している**（CLAUDE.md §6）。委任で自動化すると、キットが防ぐはずの事故そのものになる |
| 凍結値の変更（`min_discordant` 等） | 同上。凍結の意味が失われる |
| `sources/` `CLAUDE.md` `.claude/` `AUTHORITY.md` の改変 | 同上 |

「設計に理にかなっており」という条件が、設計自身の禁止を上書きしないという読みに拠る。


## DEC-010 統治系の一本化 — 決定済み（2026-09-22）

人間の明示指示「この分岐を一本の正本へ収束」に基づき、構造的統治だけを確定した。
これは科学的 frozen values の変更承認ではない。

- 横断現在地・Source Registry・Completion Gate・Transition Gate は `control/CONVERGED-SSOT.md` 系を唯一の統合現在地正本とする。
- VEA-G3 / LoopCell の frozen experimental SSOT / protocol lock は、それぞれの実験スコープ内で上位権威を維持する。
- Work/Library の回収物・形式モデル・実装報告は、content hash / primary evidence が不足する限り lower-authority evidence/addendum とする。
- 27 executable invariants は横断 kernel の実装候補として保持するが、凍結実験の成功条件を遡及変更しない。
- 現在地は手書き STATE ではなく `state_events.csv -> state_reduce.py -> STATE.generated.json` で還元する。
