# Agent Kit

`agent-kit` is now a small personal asset manager for prompts, skills, and `AGENTS.md` files.

The package name stays `agent-kit`, while the CLI name is `akit`.

## Store layout

By default assets live in:

```text
~/.akit/
  assets/
    prompts/<id>.md
    skills/<id>/...
    agents/<id>/AGENTS.md
```

Override the store location with `AKIT_HOME=/some/path`.

## Commands

From the `python/` directory:

```bash
PYTHONPATH=. python -m agent_kit list
PYTHONPATH=. python -m agent_kit add ./agent_kit/raw_prompts --yes
PYTHONPATH=. python -m agent_kit show prompt:socratic
PYTHONPATH=. python -m agent_kit install prompt:socratic --target codex
PYTHONPATH=. python -m agent_kit install skill:my-skill --project /path/to/repo
PYTHONPATH=. python -m agent_kit diff prompt:socratic ./some/other/file.md
```

If installed via `pip install .`, use:

```bash
akit list
akit add ./raw_prompts
```

## Install targets

- `prompt` + `--target codex` => `$CODEX_HOME/prompts/<id>.md` or `~/.codex/prompts/<id>.md`
- `prompt` + `--target opencode` => `<project>/.opencode/command/<id>.md`
- `skill` => `<project>/.agents/skills/<id>/...` (copies the whole skill package and rewrites `SKILL.md`)
- `agents` => `<project>/AGENTS.md` (installs Markdown body without frontmatter)

Installed prompt/skill files use lightweight frontmatter like the files in `raw_prompts/`. Internal store-only fields such as `id`, `kind`, and `version` are not written into installed files.

## Import heuristics

`akit add <dir>` scans Markdown files recursively and classifies them as:

- `SKILL.md` => `skill`
- `AGENTS.md` => `agents`
- any other Markdown file => `prompt`

When a directory contains `SKILL.md`, `akit` treats that whole directory as a single skill package. Markdown files under that skill directory are bundled with the skill and are not imported separately as prompts.

The command normalizes frontmatter to ensure each stored asset has:

- `id`
- `kind`
- `version`
