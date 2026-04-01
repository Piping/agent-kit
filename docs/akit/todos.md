# Agent Kit Scope

## Core CLI

Agent Kit provides these primary commands:

- `list`
- `show`
- `add`
- `del`
- `install`
- `diff`

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

## Installation Behavior

Installation supports:

- Codex prompt directories
- OpenCode command directories inside a project
- `.agents/skills/<id>/...` inside a project
- project-root `AGENTS.md`

Skill installation preserves package contents such as `references/`, `scripts/`, and other package-local files.

## Inspection and Comparison

Inspection supports:

- listing by asset kind or across the whole store
- direct asset viewing by selector
- comparison against another file path
- comparison against a Git revision when the asset store is versioned

## Documentation Expectations

The documentation set should answer these questions for a first-time reader:

- what Agent Kit is for
- what an asset looks like
- where assets are stored
- how to import assets
- how to install assets into a project or tool
- how to inspect and compare stored assets
