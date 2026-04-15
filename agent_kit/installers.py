from __future__ import annotations

import os
import shutil
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
    user: bool = False,
) -> Path:
    if dest:
        return Path(dest).expanduser().resolve()

    if asset.kind == "prompt":
        if target not in PROMPT_TARGETS:
            raise ValueError("Prompt assets require --target codex or --target opencode")
        if target == "codex":
            if user:
                root = Path.home() / ".codex"
            elif project:
                root = Path(project).expanduser().resolve() / ".codex"
            else:
                codex_home = os.environ.get("CODEX_HOME")
                if codex_home:
                    root = Path(codex_home).expanduser()
                else:
                    root = Path.home() / ".codex"
            return (root / "prompts" / f"{asset.id}.md").resolve()
        if user:
            return (Path.home() / ".opencode" / "command" / f"{asset.id}.md").resolve()
        project_root = Path(project or ".").expanduser().resolve()
        return (project_root / ".opencode" / "command" / f"{asset.id}.md").resolve()

    if asset.kind == "skill":
        if target and target not in SKILL_TARGETS:
            raise ValueError("Skill assets only support --target skill")
        if user:
            project_root = Path.home()
        else:
            project_root = Path(project or ".").expanduser().resolve()
        return (project_root / ".agents" / "skills" / asset.id / "SKILL.md").resolve()

    if asset.kind == "agents":
        if target and target not in AGENTS_TARGETS:
            raise ValueError("Agents assets only support --target agents")
        if user:
            project_root = Path.home()
        else:
            project_root = Path(project or ".").expanduser().resolve()
        return (project_root / "AGENTS.md").resolve()

    raise ValueError(f"Unsupported asset kind: {asset.kind}")


def render_install_content(asset: Asset) -> str:
    if asset.kind == "agents":
        return asset.body
    return compose_install_document(asset.metadata, asset.body)


def skill_install_is_up_to_date(asset: Asset, destination_root: Path) -> bool:
    if not destination_root.is_dir():
        return False

    source_files = {
        path.relative_to(asset.root_path): path
        for path in asset.root_path.rglob("*")
        if path.is_file()
    }
    destination_files = {
        path.relative_to(destination_root): path
        for path in destination_root.rglob("*")
        if path.is_file()
    }

    if set(source_files.keys()) != set(destination_files.keys()):
        return False

    for relative_path, source_path in source_files.items():
        destination_path = destination_files[relative_path]
        if relative_path == Path("SKILL.md"):
            if destination_path.read_text(encoding="utf-8") != render_install_content(asset):
                return False
            continue
        if source_path.read_bytes() != destination_path.read_bytes():
            return False
    return True


def install_skill_package(asset: Asset, destination_entry: Path) -> None:
    destination_root = destination_entry.parent
    if destination_root.exists():
        shutil.rmtree(destination_root)
    shutil.copytree(asset.root_path, destination_root)
    destination_entry.write_text(render_install_content(asset), encoding="utf-8")
