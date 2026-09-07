# 導入手順

## 前提

- VS Code と GitHub Copilot 拡張。エージェントモードとスキルには比較的新しいバージョンが要る。
- `playwright` を使うなら Node.js。`windows-mcp` を使うなら `uv`。
- Visual Studio でカスタムエージェントを使う場合は 2026 の 18.4 以降。

## A. まず個人スコープで試す

チームのリポジトリを変更せずに全プロジェクトで効かせる方法。

1. このリポジトリを任意の場所にクローンする。
2. `.github/skills/` の中身を `~/.copilot/skills/` にコピーする。Windows なら `%USERPROFILE%\.copilot\skills\`。
3. `.mcp.json` の内容を `~/.copilot/mcp-config.json` にコピーする。**ワークスペースに置いたままでは CLI に読まれない。** 実測で確認済み。詳細は `docs/verified-on-cli.md`。
4. VS Code のユーザープロファイルにカスタムエージェントとプロンプトを登録する。チャットビューの設定から追加できる。

この状態で `/plan` と `/review` が使える。

## B. リポジトリに入れる

チームで共有する場合。`.github/` と `.vscode/mcp.json` を対象リポジトリの直下にコピーしてコミットする。

入れる前に確認すること。

- `.github/copilot-instructions.md` の内容がチームの合意と矛盾しないか。
- `instructions/` の `applyTo` が実際のディレクトリ構成に合っているか。合っていないルールは無駄に読み込まれる。
- `AGENTS.md` を使うかどうか。Copilot だけなら不要なので削除する。

## C. フックを有効にする

`scripts/guard_sensitive_paths.py` は資格情報を含むファイルへの操作を拒否する preToolUse フック。

フックが動くのは Copilot CLI と cloud agent の2面だけで、IDE のエージェントモードでは動かない。cloud agent は Linux サンドボックスで動くため `bash` フィールドしか読まない。

**CLI 1.0.83 はリポジトリ内の `.github/hooks/` を読まなかった。** 実際に発火させるにはユーザーレベルに置く。

1. `~/.copilot/hooks/guard.json` を作る。Windows なら `%USERPROFILE%\.copilot\hooks\guard.json`。
2. 中身は `.github/hooks/guard.json` と同じ形にし、`bash` のパスを絶対パスにする。`$GITHUB_WORKSPACE` は CLI では未定義なので使わない。
3. `python` または `python3` が PATH にあることを確認する。

動作確認は、資格情報を含む名前のファイルを読ませてみる。拒否されれば成功で、ログに `Denied by preToolUse hook` が残る。

`.github/hooks/guard.json` は cloud agent 用に残してある。

拒否されたときは標準出力に理由が出る。誤検知したら `scripts/guard_sensitive_paths.py` の `PATTERNS` を調整する。フックは失敗時に素通しする設計なので、壊れても作業は止まらない。

## D. 自分の環境に合わせる

そのままでは合わない箇所。

- `instructions/c-embedded.instructions.md` と `instructions/python.instructions.md` は使う言語に合わせて差し替える。使わない言語のファイルは消す。`applyTo` に一致しなければ読み込まれないので害は小さいが、置いておく理由もない。
- `.vscode/mcp.json` の `github` は GitHub Enterprise Server だと URL が変わる。
- MCP は全部有効にしない。`docs/mcp-catalog.md` の運用に従い、常時オンは2つまでにする。
- `agents/*.agent.md` と `prompts/plan.prompt.md` の `model:` はコメントアウトしてある。VS Code のモデルピッカーに出る名前を確認して埋める。存在しない名前を書くとそのエージェントが動かなくなる。手順は `docs/model-routing.md`。
- memory MCP を使うなら、保存先の `.copilot-memory.jsonl` を対象リポジトリの `.gitignore` に足す。個人の作業経緯なので共有しない。

## 確認

VS Code でチャットを開き、指示が読まれているかを確認する。エージェントモードでツールピッカーを開き、有効なサーバが意図どおりかを見る。ツール数が128に近いなら減らす。
