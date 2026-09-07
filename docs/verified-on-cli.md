# 実機検証結果

GitHub Copilot CLI 1.0.83、Windows 11、node 24.13、uv 0.10.7 で実際に導入して確認した結果。VS Code 側は未検証で、以下は CLI での挙動である。

## 動いたもの

| 対象 | 結果 |
|---|---|
| `.github/skills/` のスキル6本 | `copilot skill list` に Project skills として全件表示 |
| `.github/copilot-instructions.md` | 読み込まれる |
| preToolUse フック | `~/.copilot/hooks/` に置けば発火。拒否も正しく伝わる |
| ガードスクリプト | 拒否、通過、不正入力での素通しの3系統とも期待どおり |
| context7 | 接続成功 |
| memory (MCP) | 起動は成功したが採用を取り消した。Copilot 組み込みの Memory があり、CLI では設定 `memory` が既定で有効 |
| desktop | 接続成功。ウィンドウ列挙と VS Code の GUI 操作まで実行 |
| `.github/agents/` のカスタムエージェント | `--agent reviewer` で役割と参照スキルを正しく答えた。frontmatter の `# model:` コメント行は問題ない |

フックの拒否時、Copilot は「資格情報を含む可能性のあるファイルは表示できない」と返した。ツール呼び出しはブロックされ、`Denied by preToolUse hook` がログに残る。

`.github/prompts/` のプロンプトファイルは VS Code の機能で、CLI のヘルプには対応する項目がない。CLI では同じ内容をスキルとして呼ぶ。

導入後の確認には対話モードの `/env` を使う。読み込まれた指示ファイル、MCP サーバ、スキル、エージェント、フックが一覧される。`/instructions` で指示ファイルの有効無効を切り替えられる。

## 動かなかったもの

### ワークスペースの `.mcp.json` が読まれない

`copilot mcp --help` は Workspace として `.mcp.json` と `.github/mcp.json` を読むと書いているが、どちらに置いても `copilot mcp list` は「No MCP servers configured」を返した。トップレベルのキーを `mcpServers` と `servers` の両方で試し、コメントキーを外しても変わらない。

`~/.copilot/mcp-config.json` に同じ内容を置くと全サーバが認識された。**CLI ではユーザーレベルに置く。**

### `.github/hooks/` が読まれない

デバッグログにポリシーディレクトリの探索は出るが、リポジトリ内のフック設定を読んだ形跡がない。`~/.copilot/hooks/guard.json` に置くと発火した。

あわせて、当初の設定に書いていた `$GITHUB_WORKSPACE` は CLI では未定義である。cloud agent 専用の変数なので、CLI 用には絶対パスか作業ディレクトリからの相対パスを使う。

### windows-mcp が CLI に接続できない

```
failed to initialize MCP client: JSON-RPC error: -32022:
connection is serving the 2026-07-28 protocol;
the initialize handshake is not accepted
```

サーバ自体は起動する。エラー文の `supported` は Copilot CLI 側、`requested` はサーバ側で、**CLI は 2026-07-28 版しか受け付けず、windows-mcp は 2025-11-25 版しか話せない。** サーバに直接ハンドシェイクを送って確認したところ、0.8.2 でも 0.8.5 でも 2025-11-25 を返した。古い側が windows-mcp である。

初回起動時に `uvx` が numpy を含む92パッケージを取得し、起動までおよそ50秒かかった点も注意。

**代替の `@zavora-ai/computer-use-mcp` は CLI で動いた。** 起動ログに `MCP 2026-07-28 + legacy 2025` と出るとおり両方の版を話す。接続後にウィンドウ列挙を実行させたところ、開いている9枚のタイトルを正しく返した。さらに VS Code のウィンドウを前面化し、キー送信で Copilot Chat を開き、入力欄に文字を打って送信するところまで CLI から操作できた。**GUI 操作は CLI から可能である。**

ハーネスではこれを `desktop` として登録している。

### remote の github MCP は CLI で認証できない

```
MCP OAuth authorization failed
Browser-based OAuth required for https://api.githubcopilot.com/mcp/
HTTP 401
```

CLI と cloud agent はブラウザ経由の OAuth を使うリモート MCP に対応していない。加えて **CLI には github-mcp-server が内蔵されている**。`--disable-builtin-mcps` の説明文で確認できる。

設定に `github` を書くと `Tools: * (all)` になり、CLI が既定で絞っている部分集合を上書きしてしまう。**CLI 用の設定に github を書かない。** ツールを増やしたいときは `--add-github-mcp-toolset` を使う。

VS Code には内蔵されていないので、`.vscode/mcp.json` には残してある。

## VS Code での検証

VS Code 1.130 には Copilot Chat 0.58.0 が同梱されており、`code --install-extension GitHub.copilot-chat` は「組み込み拡張は下位版に置き換えられない」と拒否される。別途入れる必要はない。

このリポジトリを開いたところ、ログディレクトリに MCP サーバ単位のログファイルが作られた。名前から読み込み元が分かる。

| ログ名の接頭辞 | 読み込み元 |
|---|---|
| `mcpServer.mcp.config.ws0.<name>` | `.vscode/mcp.json` |
| `mcpServer.workspace-dot-mcp.0.<name>` | ルートの `.mcp.json` |

**両方が読まれ、同じサーバが二重に登録されていた。** context7、memory、playwright が2回ずつ現れた。CLI は `.mcp.json` を読まないので、ルートに置く利点がない。`templates/` へ移した。

**実行時の接続は未検証。** サーバは Agent モードで実際に使われるまで起動せず、全ログが 0 バイトのままだった。Copilot Chat のパネルは Agent モードで開いたが、ステータスバーに Sign In が表示されており、Copilot へのサインインが済んでいない。サインインは利用者の操作なので、ここで止めた。

したがって VS Code 側で未確認のものは、MCP サーバの接続、`.github/agents/` のカスタムエージェント、`.github/prompts/` のプロンプトファイル、`applyTo` 付き指示ファイルの4つ。サインイン後に Agent モードで「利用可能な MCP サーバとツールを列挙して」と投げれば、上記ログにサーバごとの結果が書かれる。

## 設定テンプレートとモデル振り分け

`~/.copilot/settings.json` は読まれる。デバッグログに `Model '...' from config file` と出る。

**存在しても契約で使えないモデル名を書くと、黙って別のモデルに落ちる。** `claude-sonnet-5` を書いたところ、この検証アカウントでは権利がなく、警告をログに残しただけで `mai-code-1.1-flash` に切り替わった。設定なしのときの既定は `gpt-5.6-luna` なので、落ち先は既定とも違う。`--model` で明示した場合だけエラーで止まる。導入後は `--usage-output-file` の `modelMetrics` で実際に使われたモデルを必ず確認する。

`subagents.agents.<名前>` は `--agent <名前>` で呼ぶカスタムエージェントに効く。既定を `mai-code-1.1-flash`、`reviewer` を `gpt-5.6-luna` にして実行したところ、通常起動は前者、`--agent reviewer` は後者になった。振り分けは設定だけで成立する。

モデルの権利区分はログ内の `/models` 応答に載っている。Business で使える主なものは次のとおり。テンプレートは Business 前提で GPT の3段にしてある。Claude で組むなら `claude-opus-5` が上位、`claude-sonnet-5` が中位に当たる。`claude-haiku-4.5` は権利区分が空で選べるか判然としないので、下位には `gpt-5.6-luna` を使う。

| 段 | GPT 系 | Claude 系 |
|---|---|---|
| 上位 | gpt-5.6-sol、gpt-5.5、gpt-6-astra | claude-opus-5、claude-fable-5.1 |
| 中位 | gpt-5.6-terra、gpt-5.4 | claude-sonnet-5 |
| 下位 | gpt-5.6-luna、gpt-5.4-mini | 該当なし |

## 実測コスト

`--usage-output-file` で取得した値。プロンプトは「Reply with exactly: DONE」の1往復。

| 構成 | 非キャッシュ入力 | キャッシュ読み | nanoAIU |
|---|---|---|---|
| 初回セッション（キャッシュ無し） | 29,155 (書き込み) | 0 | 729,460,000 |
| ハーネス有・MCP 3本 | 7,739 | 17,536 | 190,452,000 |
| 指示ファイル無効・MCP 3本 | 590 | 23,808 | 60,016,000 |
| ハーネス有・MCP 全停止 | 7,582 | 6,528 | 165,296,000 |

読み取れることが3つある。

**指示ファイルはキャッシュの外に載る。** 総入力量は指示あり25,275、指示なし24,398でほとんど変わらないのに、費用は3倍違う。差は非キャッシュ分の7,739対590である。キャッシュ済みトークンは桁違いに安いので、**指示ファイルの1トークンは MCP の1トークンより高い。**

**MCP のツール定義はキャッシュ側に載る。** MCP を全部止めるとキャッシュ読みが17,536から6,528へ約11,000減るが、費用は13%しか下がらない。サーバを3本程度に抑えている限り、MCP は思ったほど高くない。

**指示やスキルを書き換えるとキャッシュが無効になる。** スキルを外した測定では次の実行がキャッシュミスになり、full price の書き込みが発生した。指示ファイルを頻繁にいじると、そのたびに初回コストを払い直す。

結論として、削る優先順位は指示ファイルが先、MCP が後になる。当初の想定と逆である。

## CLI 固有のコスト制御

ヘルプで確認できた実用的なフラグ。

| フラグ | 用途 |
|---|---|
| `--max-ai-credits <n>` | セッションあたりのクレジット上限。暴走の保険になる |
| `--usage-output-file <f>` | 使用量を JSON で書き出す。作業単位の実測に使う |
| `--effort <level>` | 推論の深さ。none から max まで |
| `--context <tier>` | `default` と `long_context`。既定のままで足りるなら上げない |
| `--model <name>` | 明示指定。`auto` で自動選択 |
| `--disable-builtin-mcps` | 内蔵 github-mcp-server を止める |

既定で選ばれたモデルは `gpt-5.6-luna` だった。モデル名は契約と時期で変わるので、`--model` に書く前に自分の環境で確認する。
