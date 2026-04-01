# Agent Kit Overview

## Purpose

Agent Kit provides one place to manage a personal toolbox of prompts, skill packages, and project-level `AGENTS.md` files. It is designed for people who collect assets over time and want consistent import, inspection, installation, and comparison workflows.

## Product Shape

Agent Kit is centered on a global asset store and a small CLI:

- `list` shows what is available
- `show` opens an asset for inspection
- `add` imports assets from local files or directories
- `del` removes assets from the store
- `install` places an asset into a tool or project location
- `diff` compares an asset against a file or a Git revision

## Supported Assets

- `prompt`: a standalone Markdown prompt
- `skill`: a package directory identified by `SKILL.md`
- `agents`: a Markdown `AGENTS.md` document

## Supported Install Destinations

- Codex prompt directory
- OpenCode command directory inside a project
- `.agents/skills/<name>/...` inside a project
- project-root `AGENTS.md`

## Design Principles

- The asset store is the authoritative source.
- Import should be fast and practical for real folders on disk.
- Installed files should look natural to the target tool.
- Skill packages should stay intact, including supporting files such as `references/` and `scripts/`.
- Internal management metadata should stay in the store rather than leaking into installed prompt and skill entry files.

## Boundaries

Agent Kit focuses on local asset management. It does not attempt to be a workflow engine, a templating framework for `AGENTS.md`, or a universal plugin system for every AI tool.
