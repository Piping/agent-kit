from __future__ import annotations

import subprocess
from pathlib import Path
from typing import Optional

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
