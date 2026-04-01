# Proposal: Rework `agent-kit` into a Personal Asset Manager

## Why

The current Python package is a narrow generator for a few OpenSpec-specific integrations. It does not solve the higher-value problem: managing a personal library of prompts, skills, and `AGENTS.md` files without manually moving files between scattered folders.

## Goals

- Make `agent-kit` a simple personal asset manager with CLI name `akit`.
- Use a global user-owned asset store as the source of truth.
- Support three first-class asset kinds:
  - `prompt`
  - `skill`
  - `agents`
- Keep assets as Markdown plus frontmatter.
- Support `list`, `show`, `add`, `del`, `install`, and `diff`.
- Support first-install targets for:
  - Codex prompts
  - OpenCode commands in the current project
  - `.agents/skills/<name>/SKILL.md`
  - project-root `AGENTS.md`

## Non-Goals

- Reusing the old OpenSpec command-generation workflow.
- Template composition for `AGENTS.md`.
- Rich schema validation or complex inheritance.
- Tool-specific hooks in v1.

## Deliverables

- New Python CLI architecture centered on a global asset store.
- Recursive import flow with heuristic kind detection and confirmation.
- Git-backed diff helpers for asset-to-file and asset-to-revision comparisons.
- Updated Python package docs aligned with the new workflow.
