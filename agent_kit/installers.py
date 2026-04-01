from __future__ import annotations

import os
from pathlib import Path
from typing import Optional

from .assets import Asset
from .frontmatter import compose_install_document


PROMPT_TARGETS = ("codex", "opencode")
SKILL_TARGETS = ("skill",)
AGENTS_TARGETS = ("agents",)


def default_target_for(asset: Asset) -> Optional[str]:
    if asset.kind == "skill":
        return "skill"
    if asset.kind == "agents":
        return "agents"
    return None


def resolve_install_target(
    asset: Asset,
    target: Optional[str],
    project: Optional[str] = None,
    dest: Optional[str] = None,
) -> Path:
    if dest:
        return Path(dest).expanduser().resolve()

    if asset.kind == "prompt":
        if target not in PROMPT_TARGETS:
            raise ValueError("Prompt assets require --target codex or --target opencode")
        if target == "codex":
            codex_home = os.environ.get("CODEX_HOME")
            if codex_home:
                root = Path(codex_home).expanduser()
            else:
                root = Path.home() / ".codex"
            return (root / "prompts" / f"{asset.id}.md").resolve()
        project_root = Path(project or ".").expanduser().resolve()
        return (project_root / ".opencode" / "command" / f"{asset.id}.md").resolve()

    if asset.kind == "skill":
        if target and target not in SKILL_TARGETS:
            raise ValueError("Skill assets only support --target skill")
        project_root = Path(project or ".").expanduser().resolve()
        return (project_root / ".agents" / "skills" / asset.id / "SKILL.md").resolve()

    if asset.kind == "agents":
        if target and target not in AGENTS_TARGETS:
            raise ValueError("Agents assets only support --target agents")
        project_root = Path(project or ".").expanduser().resolve()
        return (project_root / "AGENTS.md").resolve()

    raise ValueError(f"Unsupported asset kind: {asset.kind}")


def render_install_content(asset: Asset) -> str:
    if asset.kind == "agents":
        return asset.body
    return compose_install_document(asset.metadata, asset.body)
