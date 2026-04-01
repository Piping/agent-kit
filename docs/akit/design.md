# Design: `akit` Global Asset Store

## Store Layout

`akit` uses a user-owned store rooted at:

- `$AKIT_HOME` when set
- otherwise `~/.akit`

Assets are stored under:

```text
~/.akit/
  assets/
    prompts/<id>.md
    skills/<id>/...
    agents/<id>/AGENTS.md
```

This separates the source-of-truth library from installed tool files.

## Asset Model

Each asset is a Markdown file with frontmatter. Minimal normalized metadata:

```yaml
id: socratic
kind: prompt
version: 1
description: ...
```

Optional fields are preserved, but `id`, `kind`, and `version` are always present after import.

## Detection Rules

`akit add <path>` scans Markdown files recursively and classifies them with heuristics:

- `SKILL.md` => `skill`
- `AGENTS.md` => `agents`
- any other `*.md` => `prompt`

If a directory contains `SKILL.md`, that directory becomes the skill package root. The whole directory is imported, and Markdown files inside it are excluded from prompt discovery.

ID inference:

- frontmatter `id` wins
- `SKILL.md` defaults to parent directory name
- `AGENTS.md` defaults to parent directory name
- prompts default to the file stem

The command prints detected assets and asks for confirmation unless `--yes` is provided.

## Install Targets

- `prompt` + `codex` => `~/.codex/prompts/<id>.md`
- `prompt` + `opencode` => `<project>/.opencode/command/<id>.md`
- `skill` => `<project>/.agents/skills/<id>/...`
- `agents` => `<project>/AGENTS.md`

`install` renders prompts and skills using public frontmatter only, matching the lightweight style in `raw_prompts/`. Internal management fields such as `id`, `kind`, and `version` stay in the asset store and are stripped from installed files. Skill installs copy the whole stored package directory and then rewrite only the installed `SKILL.md`. For `agents`, it writes the Markdown body without frontmatter so the final `AGENTS.md` stays natural.

## Diff Semantics

The diff feature is intentionally source-oriented:

- compare an asset against another file path via `git diff --no-index`
- compare an asset against a Git revision inside the asset store via `git -C <store> diff <rev> -- <asset>`

This keeps `diff` useful when the store itself is versioned with Git.

## Trade-offs

- A global store is the right first abstraction for a personal toolbox, but it means project-local assets must be explicitly installed.
- Heuristic import is fast and practical, but not perfect; confirmation remains part of the import flow.
- No templating for `AGENTS.md` keeps v1 simple and predictable.
