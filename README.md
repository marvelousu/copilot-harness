# copilot-harness

Drop-in harness for a bare GitHub Copilot: instructions, skills, custom agents, MCP config, guard hook, and a cost playbook for token-based billing.

GitHub Copilot に載せる作業規約の一式です。指示ファイル、スキル、カスタムエージェント、プロンプト、MCP 設定、ガードフック、CLI の設定テンプレートをまとめています。Copilot CLI と VS Code の両方を対象にしています。

## 設計方針

- **常時読み込まれるものを小さく保つ。** 指示ファイルは全リクエストに載り、プロンプトキャッシュの外に置かれるため、同じトークン数でも他より高くつきます。手順はスキルに置き、関連するときだけ読み込ませます。
- **モデルは作業で振り分ける。** 計画とレビューは上位、実装は中位、機械的な変換は下位のモデルに固定します。設定ファイルで決まるので、毎回選ぶ必要がありません。
- **取り返しのつかない操作は機械的に止める。** 資格情報を含むファイルへの操作は拒否し、force push などは確認を挟みます。

## 構成

```
.github/
  copilot-instructions.md         全リクエストに載る規約
  instructions/*.instructions.md  applyTo で対象ファイルを絞った規約
  skills/*/SKILL.md               関連するときだけ読み込まれる手順
  agents/*.agent.md               役割を固定したカスタムエージェント
  prompts/*.prompt.md             定型作業の起動 (VS Code 用)
  hooks/guard.json                preToolUse フック定義 (cloud agent 用)
scripts/guard_sensitive_paths.py  ガードフック本体
.vscode/mcp.json                  VS Code 用 MCP 設定
templates/copilot-cli-mcp-config.json  CLI 用 MCP 設定 (~/.copilot/mcp-config.json へ)
templates/copilot-cli-settings.json    CLI 用設定 (~/.copilot/settings.json へ)
templates/user-copilot-instructions.md 個人の指示 (~/.copilot/copilot-instructions.md へ)
docs/install.md                   導入手順
docs/recording-policy.md          何をどこに残すか
docs/model-routing.md             モデル振り分けと単価表
docs/cost-playbook.md             クレジット消費を抑える運用
docs/mcp-catalog.md               MCP サーバの選定
docs/plugins.md                   プラグインの選定
docs/verified-on-cli.md           動作確認の結果と既知の制約
docs/decisions.md                 コードから読めない決定の記録
```

## 何がどこで効くか

| ファイル | 読み込まれるタイミング | 置く内容 |
|---|---|---|
| `copilot-instructions.md` | 毎回 | 全作業に効く短い規約 |
| `~/.copilot/copilot-instructions.md` | 自分の毎回 | 個人の好み。チームのリポジトリには置かない |
| `*.instructions.md` | 対象ファイルを触るとき | 言語別、ディレクトリ別の規約 |
| `SKILL.md` | 関連すると判断されたとき | 長い手順、チェックリスト |
| `*.prompt.md` | 明示的に呼んだとき | 定型作業の指示 |
| `*.agent.md` | そのエージェントを選んだとき | 役割の固定 |

## スキル

| 名前 | 使うとき |
|---|---|
| spec | 大きめの機能の前に、対話で仕様を詰めて SPEC.md を書く |
| plan-first | 非自明な変更の前に、案を比較して受け入れ基準を決める |
| debug-workflow | エラー、クラッシュ、原因不明の挙動を調べる |
| review-rubric | 完了報告を受けたとき、PR を見るとき。48項目のチェックリスト |
| git-workflow | コミット、PR、ブランチ名を決めるとき |
| handoff | 作業を別セッションや他の人へ渡すとき |

## エージェント

| 名前 | 用途 | モデルの段 |
|---|---|---|
| implementer | 方針が決まった実装 | 中位 |
| reviewer | 差分レビューとゲート判定 | 上位 |
| mechanical | 一括リネーム、定型変換 | 下位 |

CLI では `templates/copilot-cli-settings.json` の `subagents.agents` でモデルを固定します。VS Code では frontmatter の `model:` を使います。詳細は `docs/model-routing.md` を参照してください。

## 使い方

大きめの機能は仕様から始めます。

```
/spec 注文一覧に CSV 書き出しを付けたい
```

小さめなら計画から始めます。

```
/plan このモジュールにリトライ処理を入れたい
```

実装は implementer に任せ、レビューは reviewer に投げます。

```
/review
```

## MCP

VS Code 用は `.vscode/mcp.json`、CLI 用は `templates/copilot-cli-mcp-config.json` です。含めているのは context7（ライブラリ文書）、playwright（ブラウザ操作）、desktop（デスクトップ GUI 操作）で、VS Code 用にはこれに github と playwright-ext（ログイン済みブラウザへの接続）が加わります。CLI には GitHub MCP サーバが内蔵されているため、CLI 用には含めていません。同時に有効にするのは3つ程度に抑えます。選定理由は `docs/mcp-catalog.md` にあります。

## 記録

Copilot 組み込みの Memory に任せる範囲を限定し、失効させたくない決定は `docs/decisions.md` に、個人の好みは `~/.copilot/copilot-instructions.md` に置きます。別途 memory MCP は使いません。組織管理のプランでは Memory のポリシーが有効かを先に確認してください。詳細は `docs/recording-policy.md` を参照してください。

## ガード

`scripts/guard_sensitive_paths.py` は preToolUse フックとして2段で動きます。資格情報を含むファイルへの操作は拒否し、force push、`--no-verify`、`reset --hard` は確認を挟みます。cloud agent では確認が拒否に格下げされるため、無人環境ほど安全側に倒れます。

## 導入

`docs/install.md` を参照してください。個人プロファイルに置く方法と、リポジトリに置く方法があります。チームのリポジトリに `.github/` を追加するのはチームの合意が要るため、まず個人スコープで試すことを勧めます。

## 動作確認

Copilot CLI 1.0.83 で、スキル、指示ファイル、カスタムエージェント、フック、MCP 接続、設定テンプレートの動作を確認しています。VS Code は設定ファイルの読み込みまで確認しています。結果と既知の制約は `docs/verified-on-cli.md` にまとめています。

## ライセンス

MIT
