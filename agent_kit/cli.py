import argparse
import os
import sys
from typing import Iterable, List

from .managed import update_managed_block
from .registry import build_registry
from .types import ManagedFile


DEFAULT_TOOLS = "opencode,codex"


def parse_tools(value: str, available: List[str]) -> List[str]:
    if value == "all":
        return sorted(available)
    if value == "none":
        return []
    tools = [item.strip() for item in value.split(",") if item.strip()]
    invalid = [tool for tool in tools if tool not in available]
    if invalid:
        raise ValueError(f"Unknown tools: {', '.join(invalid)}")
    return tools


def apply_files(files: Iterable[ManagedFile]) -> List[str]:
    updated = []
    for item in files:
        update_managed_block(
            path=item.path,
            body=item.body,
            frontmatter=item.frontmatter,
            marker_prefix=item.marker_prefix,
            suffix=item.suffix,
        )
        updated.append(item.path)
    return updated


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Generate AI tool integration files (commands, hooks, skills)."
    )
    parser.add_argument(
        "--project",
        default=".",
        help="Project root where tool files should be generated.",
    )
    parser.add_argument(
        "--tools",
        default=DEFAULT_TOOLS,
        help="Comma-separated tool ids, or 'all'/'none'. Default: opencode,codex",
    )
    parser.add_argument("--commands", action="store_true", help="Generate commands")
    parser.add_argument("--hooks", action="store_true", help="Generate hooks")
    parser.add_argument("--skills", action="store_true", help="Generate skills")
    parser.add_argument("--list-tools", action="store_true", help="List available tool ids")
    return parser


def main() -> int:
    registry = build_registry()
    parser = build_parser()
    args = parser.parse_args()

    if args.list_tools:
        print("\n".join(sorted(registry.keys())))
        return 0

    try:
        tools = parse_tools(args.tools, list(registry.keys()))
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 1

    if not tools:
        print("No tools selected.")
        return 0

    any_flag = args.commands or args.hooks or args.skills
    enable_commands = args.commands or not any_flag
    enable_hooks = args.hooks or not any_flag
    enable_skills = args.skills or not any_flag

    project_root = os.path.abspath(args.project)

    created = {"commands": [], "hooks": [], "skills": []}

    for tool_id in tools:
        adapter = registry[tool_id]
        if enable_commands:
            created["commands"].extend(apply_files(adapter.command_files(project_root)))
        if enable_hooks:
            created["hooks"].extend(apply_files(adapter.hook_files(project_root)))
        if enable_skills:
            created["skills"].extend(apply_files(adapter.skill_files(project_root)))

    for section in ("commands", "hooks", "skills"):
        items = created[section]
        if not items:
            continue
        print(f"{section}:")
        for path in items:
            print(f"  - {path}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
