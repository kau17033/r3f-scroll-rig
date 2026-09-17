# DECISIONS — 人間判断キュー

Claude Code は本ファイルに **起案** のみ行う（`/decision`）。Status の変更は人間が commit する。
Status: PENDING / APPROVED / REJECTED / DEFERRED。

| ID | 内容 | 依存 CONF | 影響タスク | Status |
|---|---|---|---|---|
| DEC-001 | 権威階層の承認（CONF-01）と SRC-02 のロック状態確定（CONF-02） | 01, 02, 09, 10 | T-020 以降すべて | PENDING |
| DEC-002 | 対象リポジトリ（既存 / 新規） | — | T-010 | PENDING |
| DEC-003 | VEA-G3 モデル束縛（provider / model_id / snapshot / endpoint / decoding） | 06 | T-020, T-1xx | PENDING |
| DEC-004 | Phase A 固定値一式（下表） | 04, 07 | T-1xx | PENDING |
| DEC-005 | RQ 番号の名前空間化 | 03 | T-040 | PENDING |
| DEC-006 | LoopCell Phase 0 SSOT v1.1 本文の投入、D-M0-2 の承認、モデル/価格の決定 | — | T-2xx | PENDING |
| DEC-007 | Outlier v1.0 の現行性確認と法務ゲート | — | T-3xx | PENDING |
| DEC-008 | 優先順位は SOV§114 と SOV§181 のどちらか | 05 | T-070 | PENDING |
| DEC-009 | コスト方針のスコープ分割 | 08 | T-2xx, T-3xx | PENDING |
| DEC-010 | 統治系の一本化（外部 27 不変条件 / 本キット control/ / 責務分割） | 12 | 全タスク | PENDING |
| DEC-011 | 統合プロダクト名の確定と `ORP` の名前空間化 | 13 | 全識別子 | PENDING |

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

## DEC-011 統合プロダクト名（2026-09-17 起案）

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
