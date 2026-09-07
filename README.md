# copilot-harness

素の GitHub Copilot に載せる作業規約一式。指示ファイル、スキル、カスタムエージェント、プロンプト、MCP 設定、機密ファイル保護フックをまとめてある。

トークン従量課金を前提に、常時読み込まれるものを小さく、詳細は必要時に読み込まれるスキルへ、という方針で構成している。

## 構成

```
.github/
  copilot-instructions.md         全リクエストに載る。ここは小さく保つ
  instructions/*.instructions.md  applyTo で対象ファイルを絞った規約
  skills/*/SKILL.md               関連するときだけ読み込まれる手順
  agents/*.agent.md               役割とモデルを固定したカスタムエージェント
  prompts/*.prompt.md             定型作業の起動
  hooks/guard.json                preToolUse フック定義
scripts/guard_sensitive_paths.py  資格情報を含むファイルへの操作を拒否する
.vscode/mcp.json                  VS Code 用 MCP 設定
.mcp.json                         Copilot CLI / Agent Host 用の可搬 MCP 設定
docs/cost-playbook.md             クレジット消費を抑える運用
docs/model-routing.md             作業ごとのモデル振り分け
docs/mcp-catalog.md               入れる MCP と入れない MCP
docs/install.md                   導入手順
```

## 何がどこで効くか

| ファイル | 読み込まれるタイミング | 置いてよい内容 |
|---|---|---|
| `copilot-instructions.md` | 毎回 | 全作業に効く短い規約だけ |
| `*.instructions.md` | 対象ファイルを触るとき | 言語別、ディレクトリ別の規約 |
| `SKILL.md` | 関連すると判断されたとき | 長い手順、チェックリスト |
| `*.prompt.md` | 明示的に呼んだとき | 定型作業の指示 |
| `*.agent.md` | そのエージェントを選んだとき | 役割とモデルの固定 |

長い内容を `copilot-instructions.md` に書くと、使わないリクエストでも毎回課金される。手順はスキルに置く。

## エージェント

| 名前 | 用途 | 想定モデル |
|---|---|---|
| implementer | 方針が決まった実装 | 中位 |
| reviewer | 差分レビューとゲート判定 | 上位 |
| mechanical | 一括リネーム、定型変換 | 下位 |

`model:` は組織の契約でモデル名が変わるためコメントアウトしてある。導入時に `docs/model-routing.md` に従って埋める。

## 使い方

計画から始める。

```
/plan このモジュールにリトライ処理を入れたい
```

実装は implementer に任せ、レビューは reviewer に投げる。

```
/review
```

`review-rubric` スキルは「完成した」「全緑」という報告を受けたときに通すチェックリストで、この一式で最も価値がある部分。

## 記憶

Copilot には自動メモリがない。セッションをまたいで事実を持ち越すには memory MCP を使う。置くだけでは機能しないので、書く条件と読む条件を `.github/skills/memory-policy/SKILL.md` に定義してある。保存先はリポジトリ直下で、プロジェクトごとに分かれる。

## 導入

`docs/install.md` を参照。リポジトリに置く方法と、個人プロファイルに置く方法の両方がある。チームのリポジトリに `.github/` を足すのはチームの合意が要るので、まず個人スコープで試すことを勧める。

## ライセンス

MIT
