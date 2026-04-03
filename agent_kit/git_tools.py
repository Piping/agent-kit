from __future__ import annotations

import os
import shlex
import subprocess
from pathlib import Path
from typing import Iterable, List, Optional

from .assets import Asset


def diff_asset_to_path(asset: Asset, other: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", "diff", "--no-index", "--", str(asset.path), str(other.resolve())],
        text=True,
        capture_output=True,
        check=False,
    )


def diff_asset_to_revision(store_root: Path, asset: Asset, revision: str) -> subprocess.CompletedProcess[str]:
    relative = asset.path.resolve().relative_to(store_root.resolve())
    return subprocess.run(
        ["git", "-C", str(store_root), "diff", revision, "--", str(relative)],
        text=True,
        capture_output=True,
        check=False,
    )


def is_git_repo(path: Path) -> bool:
    result = subprocess.run(
        ["git", "-C", str(path), "rev-parse", "--is-inside-work-tree"],
        text=True,
        capture_output=True,
        check=False,
    )
    return result.returncode == 0 and result.stdout.strip() == "true"


def run_git(path: Path, args: List[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", "-C", str(path), *args],
        text=True,
        capture_output=True,
        check=False,
    )


def current_branch(path: Path) -> str:
    result = run_git(path, ["rev-parse", "--abbrev-ref", "HEAD"])
    if result.returncode != 0:
        raise ValueError(result.stderr.strip() or "Unable to determine current git branch")
    return result.stdout.strip()


def ensure_remote(path: Path, remote: str, url: Optional[str]) -> None:
    existing = run_git(path, ["remote", "get-url", remote])
    if existing.returncode == 0:
        if url and existing.stdout.strip() != url:
            updated = run_git(path, ["remote", "set-url", remote, url])
            if updated.returncode != 0:
                raise ValueError(updated.stderr.strip() or f"Unable to update remote {remote}")
        return

    if not url:
        raise ValueError(f"Git remote '{remote}' is not configured and no URL was provided")

    created = run_git(path, ["remote", "add", remote, url])
    if created.returncode != 0:
        raise ValueError(created.stderr.strip() or f"Unable to add remote {remote}")


def stage_paths(path: Path, paths: Iterable[Path]) -> None:
    pathspecs = _to_relative_pathspecs(path, paths)
    if not pathspecs:
        return
    result = run_git(path, ["add", "-A", "--", *pathspecs])
    if result.returncode != 0:
        raise ValueError(result.stderr.strip() or "Unable to stage paths")


def commit_paths(path: Path, paths: Iterable[Path], message: str) -> bool:
    pathspecs = _to_relative_pathspecs(path, paths)
    if not pathspecs:
        return False
    diff = run_git(path, ["diff", "--cached", "--quiet", "--", *pathspecs])
    if diff.returncode == 0:
        return False
    if diff.returncode not in (0, 1):
        raise ValueError(diff.stderr.strip() or "Unable to inspect staged changes")

    result = run_git(path, ["commit", "--only", "-m", message, "--", *pathspecs])
    if result.returncode != 0:
        raise ValueError(result.stderr.strip() or "Unable to create git commit")
    return True


def push_current_branch(path: Path, remote: str, branch: str) -> None:
    fetch = run_git(path, ["fetch", remote])
    if fetch.returncode != 0:
        raise ValueError(fetch.stderr.strip() or f"Unable to fetch from {remote}")

    remote_branch = run_git(path, ["ls-remote", "--heads", remote, branch])
    if remote_branch.returncode != 0:
        raise ValueError(remote_branch.stderr.strip() or f"Unable to inspect {remote}/{branch}")
    if not remote_branch.stdout.strip():
        push = run_git(path, ["push", remote, f"HEAD:{branch}"])
        if push.returncode != 0:
            raise ValueError(push.stderr.strip() or f"Unable to push to {remote}")
        return

    rebase = run_git(path, ["pull", "--rebase", remote, branch])
    if rebase.returncode != 0:
        raise ValueError(rebase.stderr.strip() or "Unable to rebase local branch")

    push = run_git(path, ["push", remote, f"HEAD:{branch}"])
    if push.returncode != 0:
        raise ValueError(push.stderr.strip() or f"Unable to push to {remote}")


def resolve_editor_command() -> List[str]:
    for key in ("AKIT_EDITOR", "VISUAL", "EDITOR"):
        value = os.environ.get(key, "").strip()
        if value:
            return shlex.split(value)
    return ["vim"]


def _to_relative_pathspecs(root: Path, paths: Iterable[Path]) -> List[str]:
    seen = []
    root_resolved = root.resolve()
    for path in paths:
        try:
            rel = path.resolve().relative_to(root_resolved)
        except ValueError:
            continue
        text = rel.as_posix() or "."
        if text not in seen:
            seen.append(text)
    return seen
