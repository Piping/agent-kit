from __future__ import annotations

import os
import re
import shutil
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

from .assets import ASSET_KINDS, Asset, ImportCandidate
from .frontmatter import compose_document, split_frontmatter


DEFAULT_STORE_ENV = "AKIT_HOME"
DEFAULT_VERSION = "1"


def get_store_root(explicit: Optional[str] = None) -> Path:
    if explicit:
        return Path(explicit).expanduser().resolve()
    home = os.environ.get(DEFAULT_STORE_ENV)
    if home:
        return Path(home).expanduser().resolve()
    return (Path.home() / ".akit").resolve()


def ensure_store(root: Path) -> None:
    for kind in ASSET_KINDS:
        kind_dir(root, kind).mkdir(parents=True, exist_ok=True)


def kind_dir(root: Path, kind: str) -> Path:
    if kind == "prompt":
        return root / "assets" / "prompts"
    if kind == "skill":
        return root / "assets" / "skills"
    if kind == "agents":
        return root / "assets" / "agents"
    raise ValueError(f"Unknown asset kind: {kind}")


def asset_path(root: Path, kind: str, asset_id: str) -> Path:
    base = kind_dir(root, kind)
    if kind == "prompt":
        return base / f"{asset_id}.md"
    if kind == "skill":
        return base / asset_id / "SKILL.md"
    if kind == "agents":
        return base / asset_id / "AGENTS.md"
    raise ValueError(f"Unknown asset kind: {kind}")


def list_assets(root: Path, kind: Optional[str] = None) -> List[Asset]:
    ensure_store(root)
    kinds = (kind,) if kind else ASSET_KINDS
    assets: List[Asset] = []
    for item_kind in kinds:
        base = kind_dir(root, item_kind)
        if item_kind == "prompt":
            paths = sorted(base.glob("*.md"))
        elif item_kind == "skill":
            paths = sorted(base.glob("*/SKILL.md"))
        else:
            paths = sorted(base.glob("*/AGENTS.md"))
        assets.extend(load_asset(path) for path in paths)
    return sorted(assets, key=lambda item: (item.kind, item.id))


def load_asset(path: Path) -> Asset:
    text = path.read_text(encoding="utf-8")
    metadata, body = split_frontmatter(text)
    asset_id = str(metadata.get("id") or infer_id(path, detect_kind(path), metadata))
    kind = str(metadata.get("kind") or detect_kind(path))
    version = str(metadata.get("version") or DEFAULT_VERSION)
    root_path = path.parent if kind in ("skill", "agents") else path
    return Asset(
        id=asset_id,
        kind=kind,
        version=version,
        path=path.resolve(),
        root_path=root_path.resolve(),
        body=body.rstrip() + "\n",
        metadata=metadata,
    )


def detect_kind(path: Path) -> str:
    if path.name == "SKILL.md":
        return "skill"
    if path.name == "AGENTS.md":
        return "agents"
    return "prompt"


def infer_id(path: Path, kind: str, metadata: Dict[str, object]) -> str:
    if metadata.get("id"):
        return slugify(str(metadata["id"]))
    if kind in ("skill", "agents"):
        return slugify(path.parent.name)
    return slugify(path.stem)


def slugify(value: str) -> str:
    value = value.strip().lower()
    value = re.sub(r"[^\w.-]+", "-", value, flags=re.UNICODE)
    value = value.strip("-._")
    return value or "asset"


def scan_candidates(source: Path, kind_hint: Optional[str] = None) -> List[ImportCandidate]:
    resolved = source.expanduser().resolve()
    if resolved.is_file():
        return [build_candidate(resolved, kind_hint=kind_hint)]
    if not resolved.exists():
        raise FileNotFoundError(f"Path does not exist: {resolved}")

    if kind_hint == "skill" and (resolved / "SKILL.md").is_file():
        return [build_candidate(resolved, kind_hint=kind_hint)]

    skill_roots = _find_skill_roots(resolved)
    candidates: List[ImportCandidate] = [
        build_candidate(skill_root, kind_hint="skill") for skill_root in skill_roots
    ]

    for path in _scan_markdown_files(resolved):
        if path.name == "SKILL.md":
            continue
        if _is_within_any(path, skill_roots):
            continue
        candidates.append(build_candidate(path, kind_hint=kind_hint))

    return sorted(candidates, key=lambda item: (item.kind, item.asset_id, str(item.source_path)))


def _scan_markdown_files(source: Path) -> List[Path]:
    return sorted(path for path in source.rglob("*.md") if path.is_file())


def _find_skill_roots(source: Path) -> List[Path]:
    return sorted(path.parent.resolve() for path in source.rglob("SKILL.md") if path.is_file())


def _is_within_any(path: Path, roots: List[Path]) -> bool:
    for root in roots:
        if root == path or root in path.parents:
            return True
    return False


def build_candidate(path: Path, kind_hint: Optional[str] = None) -> ImportCandidate:
    entry_path = _resolve_entry_path(path, kind_hint=kind_hint)
    if entry_path.name != "SKILL.md":
        enclosing_skill_root = _find_enclosing_skill_root(entry_path)
        if enclosing_skill_root is not None:
            raise ValueError(
                f"Markdown inside a skill package must be imported via the skill root: {enclosing_skill_root}"
            )
    text = entry_path.read_text(encoding="utf-8")
    metadata, body = split_frontmatter(text)
    kind = kind_hint or str(metadata.get("kind") or detect_kind(entry_path))
    if kind not in ASSET_KINDS:
        raise ValueError(f"Unsupported asset kind: {kind}")
    asset_id = infer_id(entry_path, kind, metadata)
    normalized = dict(metadata)
    normalized["id"] = asset_id
    normalized["kind"] = kind
    normalized["version"] = str(normalized.get("version") or DEFAULT_VERSION)
    return ImportCandidate(
        source_path=path.resolve(),
        entry_path=entry_path.resolve(),
        asset_id=asset_id,
        kind=kind,
        body=body.rstrip() + "\n",
        metadata=normalized,
    )


def _resolve_entry_path(path: Path, kind_hint: Optional[str] = None) -> Path:
    resolved = path.resolve()
    if resolved.is_dir():
        if kind_hint == "skill" or (resolved / "SKILL.md").is_file():
            entry_path = resolved / "SKILL.md"
            if not entry_path.is_file():
                raise FileNotFoundError(f"Skill directory is missing SKILL.md: {resolved}")
            return entry_path
        if kind_hint == "agents" or (resolved / "AGENTS.md").is_file():
            entry_path = resolved / "AGENTS.md"
            if not entry_path.is_file():
                raise FileNotFoundError(f"Agents directory is missing AGENTS.md: {resolved}")
            return entry_path
        raise ValueError(f"Cannot infer entry file for directory: {resolved}")
    return resolved


def _find_enclosing_skill_root(path: Path) -> Optional[Path]:
    for parent in path.parents:
        if (parent / "SKILL.md").is_file():
            return parent
    return None


def import_candidates(root: Path, candidates: List[ImportCandidate]) -> List[Tuple[str, Asset]]:
    ensure_store(root)
    results: List[Tuple[str, Asset]] = []
    for candidate in candidates:
        target = asset_path(root, candidate.kind, candidate.asset_id)
        if candidate.kind == "skill":
            status = _import_skill_candidate(target, candidate)
        else:
            status = _import_single_file_candidate(target, candidate)
        results.append((status, load_asset(target)))
    return results


def _import_single_file_candidate(target: Path, candidate: ImportCandidate) -> str:
    target.parent.mkdir(parents=True, exist_ok=True)
    document = compose_document(candidate.metadata, candidate.body)
    status = "created"
    if target.exists():
        existing = target.read_text(encoding="utf-8")
        status = "updated" if existing != document else "unchanged"
    target.write_text(document, encoding="utf-8")
    return status


def _import_skill_candidate(target: Path, candidate: ImportCandidate) -> str:
    target_root = target.parent
    status = "created"
    if target_root.exists():
        shutil.rmtree(target_root)
        status = "updated"
    shutil.copytree(candidate.source_path, target_root)
    target.write_text(compose_document(candidate.metadata, candidate.body), encoding="utf-8")
    return status


def resolve_asset(root: Path, selector: str) -> Asset:
    ensure_store(root)
    if ":" in selector:
        kind, asset_id = selector.split(":", 1)
        path = asset_path(root, kind, slugify(asset_id))
        if not path.exists():
            raise FileNotFoundError(f"Asset not found: {selector}")
        return load_asset(path)

    matches = [asset for asset in list_assets(root) if asset.id == slugify(selector)]
    if not matches:
        raise FileNotFoundError(f"Asset not found: {selector}")
    if len(matches) > 1:
        options = ", ".join(item.selector for item in matches)
        raise ValueError(f"Asset id '{selector}' is ambiguous. Use one of: {options}")
    return matches[0]


def delete_asset(root: Path, selector: str) -> Asset:
    asset = resolve_asset(root, selector)
    target = asset.root_path if asset.kind in ("skill", "agents") else asset.path
    if asset.kind == "prompt":
        target.unlink()
    else:
        shutil.rmtree(target)
    return asset
