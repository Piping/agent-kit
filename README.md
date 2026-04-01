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
git clone https://github.com/Piping/agent-kit.git
cd agent-kit && pip3 install .
akit list
akit add ./agent_kit/raw_prompts --yes
akit show prompt:socratic
akit install prompt:socratic --target codex
akit install skill:my-skill --project /path/to/repo
akit diff prompt:socratic ./some/other/file.md
```

## Install targets

- `prompt` + `--target codex` => `$CODEX_HOME/prompts/<id>.md` or `~/.codex/prompts/<id>.md`
- `prompt` + `--target opencode` => `<project>/.opencode/command/<id>.md`
- `skill` => `<project>/.agents/skills/<id>/...` (copies the whole skill package and rewrites `SKILL.md`)
- `agents` => `<project>/AGENTS.md` (installs Markdown body without frontmatter)

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
