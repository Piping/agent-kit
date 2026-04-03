# Agent Kit Scope

## Core CLI

Agent Kit provides these primary commands:

- `list`
- `show`
- `add`
- `edit`
- `del`
- `install`
- `diff`
- `push`

## Asset Coverage

The current scope includes:

- prompts as standalone Markdown files
- skills as package directories rooted by `SKILL.md`
- `AGENTS.md` as a project document asset

## Import Behavior

Import supports:

- recursive scanning of local directories
- automatic asset classification
- skill package detection
- confirmation before import unless `--yes` is provided
- normalized store metadata for every saved asset
- hidden history retention for same-name assets
- version bumps only for content or timestamp states that are not already known
- automatic version checks after edits

## Installation Behavior

Installation supports:

- Codex prompt directories
- OpenCode command directories inside a project
- `.agents/skills/<id>/...` inside a project
- project-root `AGENTS.md`

Skill installation preserves package contents such as `references/`, `scripts/`, and other package-local files.

## Editing Behavior

Editing supports:

- prompt editing from the canonical stored file
- agents editing from the canonical stored file
- skill editing from the canonical stored package directory
- automatic post-edit import and version evaluation

## Inspection and Comparison

Inspection supports:

- listing by asset kind or across the whole store
- direct asset viewing by selector
- comparison against another file path
- comparison against a Git revision when the asset store is versioned

## Git Workflow

Git workflow support includes:

- automatic staging for `add`, `edit`, and `del`
- one conventional-style commit per mutating command when changes occur
- manual `push` to a configured single remote

## Documentation Expectations

The documentation set should answer these questions for a first-time reader:

- what Agent Kit is for
- what an asset looks like
- where assets are stored
- how to import assets
- how to install assets into a project or tool
- how to inspect and compare stored assets
