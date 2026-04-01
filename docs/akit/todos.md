## 1. CLI and Store

- [x] 1.1 Replace the old generator CLI with subcommands for asset management.
- [x] 1.2 Add `$AKIT_HOME` support and a normalized global store layout.
- [x] 1.3 Add selector-based asset lookup (`kind:id` or unique `id`).

## 2. Asset Import and Metadata

- [x] 2.1 Implement Markdown frontmatter parsing and normalization.
- [x] 2.2 Implement recursive asset scanning with heuristics for prompt/skill/agents.
- [x] 2.3 Add confirmation flow for imports and deletes.

## 3. Install Targets

- [x] 3.1 Install prompts to Codex.
- [x] 3.2 Install prompts to OpenCode command directories.
- [x] 3.3 Install skills to `.agents/skills/<id>/SKILL.md`.
- [x] 3.4 Install agents assets to project-root `AGENTS.md`.

## 4. Inspection and Diff

- [x] 4.1 Add `list` and `show`.
- [x] 4.2 Add delete support.
- [x] 4.3 Add Git-backed source diff support.

## 5. Validation

- [x] 5.1 Update package documentation.
- [x] 5.2 Run smoke checks with a temporary `AKIT_HOME`.
