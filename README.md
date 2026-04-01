# Agent Kit

Agent Kit is a personal asset manager for prompts, skills, and `AGENTS.md` files.

The package name is `agent-kit`. The CLI command is `akit`.

## What It Manages

Agent Kit works with three asset kinds:

- `prompt`: a Markdown prompt file
- `skill`: a skill package rooted by `SKILL.md`
- `agents`: a project-level `AGENTS.md` document

The asset store is the source of truth. Installed files are derived copies placed into tool-specific locations when needed.

## Asset Store

By default, assets are stored under `~/.akit`:

```text
~/.akit/
  assets/
    prompts/<id>.md
    skills/<id>/...
    agents/<id>/AGENTS.md
```

To use a different location:

```bash
export AKIT_HOME=/path/to/akit-home
```

## Installation

From the `python/` directory:

```bash
pip3 install .
```

If you prefer running from the repo without installing a script entry point:

```bash
PYTHONPATH=. python3 -m agent_kit list
```

## Quick Start

Import a prompt library:

```bash
akit add ./agent_kit/raw_prompts --yes
```

Inspect the imported assets:

```bash
akit list
akit show prompt:socratic
```

Install a prompt into Codex:

```bash
akit install prompt:socratic --target codex
```

Install a skill package into a project:

```bash
akit install skill:my-skill --project /path/to/project
```

Compare a stored asset with another file:

```bash
akit diff prompt:socratic ./some/other/file.md
```

## Command Summary

```bash
akit list [--kind prompt|skill|agents]
akit show <selector> [--body-only]
akit add <path> [--kind prompt|skill|agents] [--yes]
akit del <selector> [--yes]
akit install <selector> [--target codex|opencode|skill|agents] [--project <path>] [--dest <file>] [--force]
akit diff <selector> <file>
akit diff <selector> --rev <git-revision>
```

Selectors accept either a unique asset id or an explicit `kind:id` form such as `prompt:socratic` or `skill:mega-skill`.

## Import Rules

`akit add <path>` scans Markdown files recursively and classifies them with these rules:

- `SKILL.md` defines a `skill`
- `AGENTS.md` defines an `agents` asset
- any other Markdown file is treated as a `prompt`

If a directory contains `SKILL.md`, that directory is imported as a single skill package. Files inside the package stay bundled with the skill and are not imported separately as prompts.

Stored assets are normalized with internal metadata so they can be listed, selected, and installed consistently. Each stored asset always has:

- `id`
- `kind`
- `version`

## Install Targets

- `prompt` + `--target codex` installs to `$CODEX_HOME/prompts/<id>.md` or `~/.codex/prompts/<id>.md`
- `prompt` + `--target opencode` installs to `<project>/.opencode/command/<id>.md`
- `skill` installs to `<project>/.agents/skills/<id>/...`
- `agents` installs to `<project>/AGENTS.md`

Installed prompt and skill files use lightweight frontmatter suitable for direct tool consumption. Internal store metadata such as `id`, `kind`, and `version` stays in the asset store and is not written into installed prompt or skill entry files.

Skill installation copies the whole package directory and writes the installed `SKILL.md` with public-facing frontmatter. `AGENTS.md` installs as plain Markdown body text.

## Git-Based Diff

Agent Kit supports two diff modes:

- compare an asset to another file path
- compare an asset to a Git revision inside the asset store

Examples:

```bash
akit diff prompt:socratic ./drafts/socratic.md
akit diff skill:mega-skill --rev HEAD~1
```

For revision-based diffs, the asset store directory itself should be a Git repository.

## Typical Workflow

1. Collect prompts, skills, or `AGENTS.md` files from different directories.
2. Import them into the asset store with `akit add`.
3. Review what is available with `akit list` and `akit show`.
4. Install only the assets needed for the current tool or project.
5. Use `akit diff` to compare stored assets with files or earlier revisions before updating installations.
