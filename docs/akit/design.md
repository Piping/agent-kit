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

Hidden history snapshots are stored alongside current assets:

```text
~/.akit/
  assets/
    prompts/.history/<id>/v0001/...
    skills/.history/<id>/v0001/...
    agents/.history/<id>/v0001/...
```

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

Internal metadata fields also track source timestamps and content fingerprints so imports can decide whether a same-name asset represents a genuinely new version.

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

## Versioning Rules

Imports are versioned by `kind:id`.

For an existing asset:

- the current version remains at the standard asset path
- historical versions are stored in the hidden history directory
- a new version is created only when the incoming asset does not match any known version by content fingerprint or source timestamp

This avoids duplicate history entries when an earlier snapshot is imported again.

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

## Edit Pipeline

`akit edit` operates on the canonical stored asset in `AKIT_HOME`.

- prompts edit the current stored file
- agents edit the current stored `AGENTS.md`
- skills edit the current stored package directory

The command opens a temporary editable copy, waits for the editor to exit, then imports the result back into the store using normal versioning rules. This avoids in-place mutations that would interfere with version comparison.

## Frontmatter Rules

The asset store keeps internal management metadata such as `id`, `kind`, and `version`.

Installed prompt and skill entry files keep only public-facing metadata. This keeps the installed files close to natural hand-authored prompt and skill files while preserving management metadata in the store.

## Git Integration

When `AKIT_HOME` is a git repository, mutating commands stage and commit only their own touched paths.

- `add` stages newly created or updated current asset paths and new history snapshots
- `edit` stages updated current asset paths and any new history snapshots
- `del` stages asset removal paths and history removal paths

Each mutating command creates a single conventional-commit-style commit when changes occur.

## Push Model

`akit push` is a manual sync command.

- configuration is loaded from `AKIT_HOME/config.toml`
- the command targets a single remote
- if the remote branch does not exist yet, Agent Kit pushes directly
- if the remote branch exists, Agent Kit fetches, rebases, and then pushes

The push workflow never runs automatically as a side effect of other commands.

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
