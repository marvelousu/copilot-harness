# copilot-harness

Drop-in harness for a bare GitHub Copilot: instructions, skills, custom agents, MCP config, guard hook, and a cost playbook for token-based billing.

素の GitHub Copilot に載せる作業規約一式。指示ファイル、スキル、カスタムエージェント、プロンプト、MCP 設定、ガードフック、CLI の設定テンプレートをまとめてある。

トークン従量課金を前提に、常時読み込まれるものを小さく、詳細は必要時に読み込まれるスキルへ、という方針で構成している。

## 構成

```
.github/
  copilot-instructions.md         全リクエストに載る。ここは小さく保つ
  instructions/*.instructions.md  applyTo で対象ファイルを絞った規約
  skills/*/SKILL.md               関連するときだけ読み込まれる手順
  agents/*.agent.md               役割を固定したカスタムエージェント
  prompts/*.prompt.md             定型作業の起動 (VS Code 用)
  hooks/guard.json                preToolUse フック定義 (cloud agent 用)
scripts/guard_sensitive_paths.py  資格情報ファイルは拒否、force push 等は確認を挟む
.vscode/mcp.json                  VS Code 用 MCP 設定
templates/copilot-cli-mcp-config.json  CLI 用 MCP 設定。~/.copilot/mcp-config.json にコピーする
templates/copilot-cli-settings.json    CLI 用設定。既定モデルとエージェント別モデルを固定する
docs/verified-on-cli.md           実機検証の結果と既知の不具合。先に読む
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
| `*.agent.md` | そのエージェントを選んだとき | 役割の固定 |

長い内容を `copilot-instructions.md` に書くと、使わないリクエストでも毎回課金される。実測では指示ファイルはプロンプトキャッシュの外に載るため、同じトークン数でも MCP のツール定義より高くつく。手順はスキルに置く。

## エージェント

| 名前 | 用途 | 段 |
|---|---|---|
| implementer | 方針が決まった実装 | 中位 |
| reviewer | 差分レビューとゲート判定 | 上位 |
| mechanical | 一括リネーム、定型変換 | 下位 |

CLI では `templates/copilot-cli-settings.json` の `subagents.agents` でモデルを固定する。VS Code では frontmatter の `model:` を使うが、ピッカーの名前を確認するまでコメントアウトしてある。詳細は `docs/model-routing.md`。

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

Copilot 組み込みの Memory を使う。リポジトリ単位で、coding agent、code review、CLI の間で共有され、28日で失効する。CLI では設定 `memory` が既定で有効。別途 memory MCP は置かない。

失効させたくない決定は、採らなかった案と理由を添えて `docs/decisions.md` に残す。指示ファイルにその一行を入れてあり、無ければエージェントが作る。

## ガード

`scripts/guard_sensitive_paths.py` は2段で動く。資格情報を含むファイルへの操作は拒否し、force push、`--no-verify`、`reset --hard` は確認を挟む。cloud agent では確認が拒否に格下げされるので、無人環境ほど安全側に倒れる。

## 検証状況

Copilot CLI 1.0.83 で実機導入し、スキル、指示ファイル、カスタムエージェント、フック、MCP 接続、設定テンプレート、コストを実測した。結果と既知の不具合は `docs/verified-on-cli.md` にある。導入前に読むこと。

要点は4つ。CLI はワークスペースの MCP 設定と `.github/hooks/` を読まないのでユーザーレベルに置く。CLI には github-mcp-server が内蔵されているので設定に書かない。GUI 操作は `desktop` サーバで CLI から可能で、ウィンドウ列挙から VS Code の操作まで実測した。VS Code は `.vscode/mcp.json` とルートの `.mcp.json` の両方を読むので、ルートには置かない。

VS Code は設定の読み込みまで確認済み。実行時の接続はサインイン待ちで未検証。

## 導入

`docs/install.md` を参照。リポジトリに置く方法と、個人プロファイルに置く方法の両方がある。チームのリポジトリに `.github/` を足すのはチームの合意が要るので、まず個人スコープで試すことを勧める。

## ライセンス

MIT
