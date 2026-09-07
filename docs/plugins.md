# プラグイン

Copilot CLI にはマーケットプレイスが2つ同梱されている。`copilot-plugins`（GitHub と Microsoft 公式）と `awesome-copilot`（コミュニティ、151件）。`copilot plugin marketplace browse <名前>` で一覧、`copilot plugin install <名前>@<マーケット>` で導入、`copilot plugin uninstall` で削除する。登録簿は `~/.copilot/config.json` にあり、ディレクトリを手で消すと食い違うので、必ずコマンドで消す。

一覧を全件見た上での結論は、**必須のものは無い。** 常時載るものを増やすほど毎リクエストの費用が増えるので、条件に合うときだけ入れる。

## 見送ったもの

| プラグイン | 内容 | 見送る理由 |
|---|---|---|
| cache-stats | キャッシュ再利用率と AIU をキャンバスで可視化 | 対話専用の表示。組み込みの `/usage` と `/statusline quota ai-used` で足りる |
| where-was-i | ブランチ、コミット、未コミットから作業文脈を復元 | `git status` と `git log` で同じことができる |
| structured-autonomy | 計画は上位モデル、実装は下位モデルの3コマンド | 方針は同じで、設定ファイルによる振り分けで既に実現している |
| doublecheck | 出力の主張を抽出して根拠を照合する3層検証 | review-rubric と重なる |
| agent-council | 5エージェントによる出荷判定 | 1回の判定に5モデル分の費用がかかる |

## 検討に値するもの

| プラグイン | 入れる条件 |
|---|---|
| keep-the-why | コードの判断理由をリポジトリ内 Markdown に残す規約とスキル。`docs/decisions.md` が1ファイルで収まらなくなったとき、引き継ぎが要るときの上位互換。詳細は `docs/recording-policy.md` |
| cpp-language-server | C や C++ を書くなら。公式マーケット。コードの参照解決が要るとき |
| dotnet、csharp-dotnet-development | C# を書くなら |
| azure-devops-copilot-plugin | 課題管理とリポジトリが Azure DevOps にあるなら |
| microsoft-docs | Windows、.NET、Azure の公式ドキュメント参照が多いなら |
| convert-to-md | 仕様が docx や pptx で来る職場なら。エージェントが読める形に変換する |
| sonarqube、sentry-triage、datadog | それぞれの製品を既に使っているなら |
| database-data-management | DB を触る作業が多いなら。接続は読み取り専用ユーザーに限定する |

## 入れたあとに見ること

`/env` で読み込まれたスキル、エージェント、フック、MCP を一覧する。プラグインが常時載る指示を持ち込んでいないか、ツール数が128に近づいていないかを確認する。
