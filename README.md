# Agent Kit

This directory contains a small Python CLI that generates AI tool integration files (commands, hooks, skills) and borrows managed-block update patterns from OpenSpec.

## Usage

From the repo root:

```
PYTHONPATH=. python -m agent_kit --project . --tools opencode,codex
```

By default it generates commands, hooks, and skills for the selected tools. Use flags to restrict output:

```bash
python3 -m agent_kit --tools opencode --commands
python3 -m agent_kit --tools opencode --hooks
python3 -m agent_kit --tools claudecode --skills

# If installed via `pip install . `, the cli cmd is:
ak --project . --tools opencode,codex
```

## Notes

- OpenCode commands are written under `.opencode/command/` to match existing OpenSpec conventions.
- OpenCode hooks are written to `.opencode/hooks.jsonc` using commented OpenSpec markers.
- Codex commands are written under `$CODEX_HOME/prompts` or `~/.codex/prompts`.
