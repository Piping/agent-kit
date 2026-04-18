# Agent Kit Instructions

## Project Context

This repository is the Python implementation of Agent Kit, a personal asset manager for:

- prompts
- skill packages
- `AGENTS.md` assets

The source of truth is the asset store under `AKIT_HOME`. Installed files are derived outputs.

## Rules for project spec

- Treat `AKIT_HOME` as the canonical asset repository.
- Treat installed tool files as deploy targets, not as the primary editing surface.
- Keep prompt assets as single files.
- Keep skill assets as package directories rooted by `SKILL.md`.
- Do not treat Markdown files inside a skill package as standalone prompt assets.
- Preserve skill package contents such as `references/`, `scripts/`, and supporting files across import, edit, install, and delete.
- Keep installed prompt and skill entry files free of store-only metadata.
- Keep `akit push` manual. Mutating commands must not push as a side effect.
- When `AKIT_HOME` is a git repository, stage and commit only paths touched by the current command.
- Ignore unrelated working tree changes when performing `add`, `edit`, and `del`.
- Validate both current-state logic and historical-state logic whenever versioning changes.
- Test empty-remote, dirty-worktree, and repeated-import scenarios whenever git behavior changes.
- Avoid parallel mutation tests against a single git repo unless the locking behavior itself is under test.

## Rules for working on this project
- local install command: `pip3 install -e . --break-system-packages`
- commits/docs for the project MUST not include personal info, system infos
- 编辑文档的时候请按最终成稿方式输出，面向第一次阅读的人。不要保留编辑痕迹，不要解释修改过程
