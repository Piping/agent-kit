import argparse
import sys
from pathlib import Path
from typing import Optional

from .git_tools import diff_asset_to_path, diff_asset_to_revision, is_git_repo
from .installers import (
    default_target_for,
    install_skill_package,
    render_install_content,
    resolve_install_target,
    skill_install_is_up_to_date,
)
from .store import delete_asset, get_store_root, import_candidates, list_assets, resolve_asset, scan_candidates


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="akit",
        description="Manage personal prompt, skill, and AGENTS assets from a global store.",
    )
    parser.add_argument(
        "--store",
        help="Override the asset store root. Defaults to $AKIT_HOME or ~/.akit.",
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    list_parser = subparsers.add_parser("list", help="List managed assets")
    list_parser.add_argument("--kind", choices=("prompt", "skill", "agents"))

    show_parser = subparsers.add_parser("show", help="Show an asset")
    show_parser.add_argument("selector", help="Asset selector: kind:id or unique id")
    show_parser.add_argument("--body-only", action="store_true", help="Print only the body")

    add_parser = subparsers.add_parser("add", help="Import assets from a file or directory")
    add_parser.add_argument("source", help="File or directory to scan")
    add_parser.add_argument("--kind", choices=("prompt", "skill", "agents"))
    add_parser.add_argument("-y", "--yes", action="store_true", help="Skip confirmation")

    del_parser = subparsers.add_parser("del", help="Delete an asset from the store")
    del_parser.add_argument("selector", help="Asset selector: kind:id or unique id")
    del_parser.add_argument("-y", "--yes", action="store_true", help="Skip confirmation")

    install_parser = subparsers.add_parser("install", help="Install an asset into a target tool path")
    install_parser.add_argument("selector", help="Asset selector: kind:id or unique id")
    install_parser.add_argument("--target", choices=("codex", "opencode", "skill", "agents"))
    install_parser.add_argument("--project", help="Project root for project-scoped targets")
    install_parser.add_argument("--dest", help="Explicit destination file path")
    install_parser.add_argument("--force", action="store_true", help="Overwrite when destination exists")

    diff_parser = subparsers.add_parser("diff", help="Diff an asset against a file path or git revision")
    diff_parser.add_argument("selector", help="Asset selector: kind:id or unique id")
    diff_parser.add_argument("other", nargs="?", help="Other file path to compare against")
    diff_parser.add_argument("--rev", help="Git revision inside the asset store")

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    store_root = get_store_root(args.store)

    try:
        if args.command == "list":
            return cmd_list(store_root, args.kind)
        if args.command == "show":
            return cmd_show(store_root, args.selector, args.body_only)
        if args.command == "add":
            return cmd_add(store_root, args.source, args.kind, args.yes)
        if args.command == "del":
            return cmd_del(store_root, args.selector, args.yes)
        if args.command == "install":
            return cmd_install(store_root, args.selector, args.target, args.project, args.dest, args.force)
        if args.command == "diff":
            return cmd_diff(store_root, args.selector, args.other, args.rev)
    except (FileNotFoundError, ValueError) as exc:
        print(str(exc), file=sys.stderr)
        return 1

    parser.error(f"Unknown command: {args.command}")
    return 2


def cmd_list(store_root: Path, kind: Optional[str]) -> int:
    assets = list_assets(store_root, kind=kind)
    if not assets:
        print(f"No assets in {store_root}")
        return 0

    for asset in assets:
        description = asset.metadata.get("description", "")
        suffix = f" - {description}" if description else ""
        print(f"{asset.selector} v{asset.version}{suffix}")
    return 0


def cmd_show(store_root: Path, selector: str, body_only: bool) -> int:
    asset = resolve_asset(store_root, selector)
    if body_only:
        sys.stdout.write(asset.body)
        return 0

    print(f"selector: {asset.selector}")
    print(f"path: {asset.path}")
    print(f"version: {asset.version}")
    for key in sorted(asset.metadata):
        if key in ("id", "kind", "version"):
            continue
        print(f"{key}: {asset.metadata[key]}")
    print("")
    sys.stdout.write(asset.body)
    return 0


def cmd_add(store_root: Path, source: str, kind: Optional[str], yes: bool) -> int:
    candidates = scan_candidates(Path(source), kind_hint=kind)
    if not candidates:
        print("No Markdown assets found.")
        return 0

    for candidate in candidates:
        print(f"{candidate.selector} <= {candidate.source_path}")

    if not yes and not _confirm(f"Import {len(candidates)} asset(s) into {store_root}? [y/N]: "):
        print("Cancelled.")
        return 1

    results = import_candidates(store_root, candidates)
    for status, asset in results:
        print(f"{status}: {asset.selector} -> {asset.path}")
    return 0


def cmd_del(store_root: Path, selector: str, yes: bool) -> int:
    asset = resolve_asset(store_root, selector)
    if not yes and not _confirm(f"Delete {asset.selector} from {store_root}? [y/N]: "):
        print("Cancelled.")
        return 1
    removed = delete_asset(store_root, selector)
    print(f"deleted: {removed.selector}")
    return 0


def cmd_install(
    store_root: Path,
    selector: str,
    target: Optional[str],
    project: Optional[str],
    dest: Optional[str],
    force: bool,
) -> int:
    asset = resolve_asset(store_root, selector)
    resolved_target = target or default_target_for(asset)
    destination = resolve_install_target(asset, resolved_target, project=project, dest=dest)
    desired = render_install_content(asset)

    if asset.kind == "skill":
        destination_root = destination.parent
        if skill_install_is_up_to_date(asset, destination_root):
            print(f"up-to-date: {destination_root}")
            return 0
        if destination_root.exists() and not force:
            raise ValueError(f"Destination exists: {destination_root}. Re-run with --force to overwrite.")
        destination_root.parent.mkdir(parents=True, exist_ok=True)
        install_skill_package(asset, destination)
        print(f"installed: {asset.selector} -> {destination_root}")
        return 0

    destination.parent.mkdir(parents=True, exist_ok=True)

    if destination.exists():
        existing = destination.read_text(encoding="utf-8")
        if existing == desired:
            print(f"up-to-date: {destination}")
            return 0
        if not force:
            raise ValueError(f"Destination exists: {destination}. Re-run with --force to overwrite.")

    destination.write_text(desired, encoding="utf-8")
    print(f"installed: {asset.selector} -> {destination}")
    return 0


def cmd_diff(store_root: Path, selector: str, other: Optional[str], revision: Optional[str]) -> int:
    asset = resolve_asset(store_root, selector)
    if other and revision:
        raise ValueError("Use either a file path or --rev, not both.")

    if other:
        result = diff_asset_to_path(asset, Path(other))
    else:
        if not revision:
            raise ValueError("Provide a file path or --rev for diff.")
        if not is_git_repo(store_root):
            raise ValueError(f"Asset store is not a git repository: {store_root}")
        result = diff_asset_to_revision(store_root, asset, revision)

    if result.stdout:
        sys.stdout.write(result.stdout)
    if result.stderr and result.returncode not in (0, 1):
        sys.stderr.write(result.stderr)
    return result.returncode


def _confirm(prompt: str) -> bool:
    return input(prompt).strip().lower() in {"y", "yes"}


if __name__ == "__main__":
    raise SystemExit(main())
