---
name: git-workflow
description: コミット、PR、ブランチ管理のルール。コミットメッセージを書くとき、PR を作るとき、ブランチ名を決めるときに参照する。
---

# git-workflow

## コミットメッセージ

- 形式は `<type>: <summary>`。type は feat/fix/refactor/test/docs/chore。
- 「なぜ」を説明する。「何を」は diff で分かる。
- 作業単位ごとにこまめにコミットする。

## ブランチ

- `feature/<issue番号>-<概要>` の形式。
- main への直接コミットは避ける。

## PR

- 150 行以内を目安に小さく保つ。
- タイトルには変更の目的を書く。実装詳細は書かない。
- 出す前にテストとリントを自分で通す。

## 禁止

- `--no-verify` と force push は明示指示がない限り使わない。
- main への force push は行わない。
- 資格情報を含むファイルはコミットしない。
