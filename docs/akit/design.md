# Agent Kit Design

## Storage Model

Agent Kit uses a user-owned store rooted at:

- `$AKIT_HOME` when set
- otherwise `~/.akit`

The store layout is:

```text
~/.akit/
  assets/
    prompts/<id>.md
    skills/<id>/...
    agents/<id>/AGENTS.md
```

The store contains normalized source assets. Tool-specific or project-specific installations are written elsewhere.

## Asset Types

### Prompt

A prompt is a single Markdown file. In the store it is saved as:

```text
assets/prompts/<id>.md
```

### Skill

A skill is a package directory rooted by `SKILL.md`. The whole directory is stored under:

```text
assets/skills/<id>/
```

Supporting files such as `references/`, `scripts/`, templates, or other package-local content remain inside the package.

### Agents

An `agents` asset is a single `AGENTS.md` file stored as:

```text
assets/agents/<id>/AGENTS.md
```

## Metadata Model

Stored assets use normalized metadata so the CLI can identify and manage them consistently. Every stored asset has:

```yaml
id: socratic
kind: prompt
version: 1
```

Additional metadata such as `name`, `title`, `description`, or `tags` is preserved when present.

## Import Pipeline

`akit add <path>` applies these rules:

- `SKILL.md` defines a skill package root
- `AGENTS.md` defines an agents asset
- other Markdown files are treated as prompts

When a skill package is detected:

- the package directory is imported as one asset
- nested Markdown files remain part of the package
- nested Markdown files are excluded from prompt discovery
- direct attempts to import Markdown from inside a skill package are rejected in favor of the package root

Asset ids are resolved in this order:

1. frontmatter `id`
2. parent directory name for `SKILL.md`
3. parent directory name for `AGENTS.md`
4. file stem for prompts

## Install Pipeline

### Prompt Installation

- Codex target: `$CODEX_HOME/prompts/<id>.md` or `~/.codex/prompts/<id>.md`
- OpenCode target: `<project>/.opencode/command/<id>.md`

### Skill Installation

- Target: `<project>/.agents/skills/<id>/...`
- The whole stored package directory is copied into the project
- The installed `SKILL.md` is written with public-facing frontmatter only

### Agents Installation

- Target: `<project>/AGENTS.md`
- The installed file is the Markdown body without frontmatter

## Frontmatter Rules

The asset store keeps internal management metadata such as `id`, `kind`, and `version`.

Installed prompt and skill entry files keep only public-facing metadata. This keeps the installed files close to natural hand-authored prompt and skill files while preserving management metadata in the store.

## Diff Model

Agent Kit supports two comparison modes:

- asset vs local file path using `git diff --no-index`
- asset vs Git revision inside the asset store using `git -C <store> diff <rev> -- <asset>`

This model keeps diff focused on the source asset rather than tool installation state.

## Operational Characteristics

- The global store keeps a single canonical copy of each asset.
- Project installation is explicit.
- Skill packages remain intact across import and installation.
- `AGENTS.md` stays readable as a normal document when installed into a project.
