from __future__ import annotations

from difflib import SequenceMatcher
import os
import re
import shutil
import hashlib
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Tuple

from .assets import ASSET_KINDS, Asset, ImportCandidate, MutationResult
from .frontmatter import compose_document, split_frontmatter


DEFAULT_STORE_ENV = "AKIT_HOME"
DEFAULT_VERSION = "1"
SOURCE_TIMESTAMP_KEY = "_source_timestamp_ns"
CONTENT_FINGERPRINT_KEY = "_content_fingerprint"


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


def history_dir(root: Path, kind: str, asset_id: str) -> Path:
    return kind_dir(root, kind) / ".history" / asset_id


def history_entry_path(root: Path, kind: str, asset_id: str, version: str) -> Path:
    base = history_dir(root, kind, asset_id)
    version_dir = base / f"v{int(version):04d}"
    if kind == "prompt":
        return version_dir / f"{asset_id}.md"
    if kind == "skill":
        return version_dir / "SKILL.md"
    if kind == "agents":
        return version_dir / "AGENTS.md"
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
    source_timestamp_target = path.resolve() if kind == "skill" else entry_path.resolve()
    normalized = dict(metadata)
    normalized["id"] = asset_id
    normalized["kind"] = kind
    normalized["version"] = str(normalized.get("version") or DEFAULT_VERSION)
    normalized[SOURCE_TIMESTAMP_KEY] = str(compute_source_timestamp(source_timestamp_target, kind))
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


def import_candidates(root: Path, candidates: List[ImportCandidate]) -> List[MutationResult]:
    ensure_store(root)
    results: List[MutationResult] = []
    for candidate in candidates:
        target = asset_path(root, candidate.kind, candidate.asset_id)
        status, touched_paths = _import_candidate(root, target, candidate)
        results.append(MutationResult(status=status, asset=load_asset(target), touched_paths=touched_paths))
    return results


def _import_candidate(root: Path, target: Path, candidate: ImportCandidate) -> Tuple[str, List[Path]]:
    fingerprint = compute_candidate_fingerprint(candidate)
    candidate.metadata[CONTENT_FINGERPRINT_KEY] = fingerprint

    if not target.exists():
        _write_current_candidate(target, candidate)
        history_path = _snapshot_current_asset(root, candidate.kind, candidate.asset_id, candidate.metadata["version"])
        return "created", _touched_paths_for_asset(load_asset(target), extra_paths=[history_path])

    existing = load_asset(target)
    if _should_skip_new_version(root, existing, candidate, fingerprint):
        return "unchanged", []

    next_version = str(_next_version(existing.version))
    touched_paths: List[Path] = []
    if not _history_snapshot_exists(root, existing.kind, existing.id, existing.version):
        touched_paths.append(_snapshot_existing_asset(root, existing))

    candidate.metadata["version"] = next_version
    candidate.metadata[CONTENT_FINGERPRINT_KEY] = fingerprint
    _write_current_candidate(target, candidate)
    touched_paths.append(_snapshot_current_asset(root, candidate.kind, candidate.asset_id, next_version))
    current = load_asset(target)
    return "updated", _touched_paths_for_asset(current, extra_paths=touched_paths)


def _write_current_candidate(target: Path, candidate: ImportCandidate) -> None:
    target.parent.mkdir(parents=True, exist_ok=True)
    if candidate.kind == "skill":
        target_root = target.parent
        if target_root.exists():
            shutil.rmtree(target_root)
        shutil.copytree(candidate.source_path, target_root)
    document = compose_document(candidate.metadata, candidate.body)
    target.write_text(document, encoding="utf-8")


def _should_skip_new_version(root: Path, existing: Asset, candidate: ImportCandidate, fingerprint: str) -> bool:
    candidate_timestamp = str(candidate.metadata.get(SOURCE_TIMESTAMP_KEY, ""))
    for known_version in _iter_known_versions(root, existing):
        existing_fingerprint = str(known_version.metadata.get(CONTENT_FINGERPRINT_KEY, "")) or compute_asset_fingerprint(known_version)
        existing_timestamp = str(known_version.metadata.get(SOURCE_TIMESTAMP_KEY, ""))
        if existing_fingerprint and existing_fingerprint == fingerprint:
            return True
        if existing_timestamp and existing_timestamp == candidate_timestamp:
            return True
    return False


def _iter_known_versions(root: Path, current: Asset) -> Iterable[Asset]:
    yield current
    base = history_dir(root, current.kind, current.id)
    if not base.exists():
        return
    if current.kind == "prompt":
        paths = sorted(base.glob(f"v*/{current.id}.md"))
    elif current.kind == "skill":
        paths = sorted(base.glob("v*/SKILL.md"))
    else:
        paths = sorted(base.glob("v*/AGENTS.md"))
    for path in paths:
        yield load_asset(path)


def _next_version(version: str) -> int:
    try:
        return int(version) + 1
    except ValueError:
        return int(DEFAULT_VERSION) + 1


def _history_snapshot_exists(root: Path, kind: str, asset_id: str, version: str) -> bool:
    return history_entry_path(root, kind, asset_id, version).exists()


def _snapshot_existing_asset(root: Path, asset: Asset) -> Path:
    destination = history_entry_path(root, asset.kind, asset.id, asset.version)
    _copy_asset_to_snapshot(asset.path, asset.root_path, asset.kind, destination)
    return destination.parent if asset.kind in ("skill", "agents") else destination


def _snapshot_current_asset(root: Path, kind: str, asset_id: str, version: str) -> Path:
    current = load_asset(asset_path(root, kind, asset_id))
    destination = history_entry_path(root, kind, asset_id, version)
    _copy_asset_to_snapshot(current.path, current.root_path, current.kind, destination)
    return destination.parent if current.kind in ("skill", "agents") else destination


def _copy_asset_to_snapshot(entry_path: Path, root_path: Path, kind: str, destination_entry: Path) -> None:
    snapshot_root = destination_entry.parent
    snapshot_root.mkdir(parents=True, exist_ok=True)
    if kind == "prompt":
        destination_entry.write_bytes(entry_path.read_bytes())
        return
    if snapshot_root.exists():
        shutil.rmtree(snapshot_root)
        snapshot_root.mkdir(parents=True, exist_ok=True)
    shutil.copytree(root_path, snapshot_root, dirs_exist_ok=True)


def compute_source_timestamp(source_path: Path, kind: str) -> int:
    if kind == "skill":
        files = list(_iter_files(source_path))
        if not files:
            return source_path.stat().st_mtime_ns
        return max(path.stat().st_mtime_ns for path in files)
    return source_path.stat().st_mtime_ns


def compute_candidate_fingerprint(candidate: ImportCandidate) -> str:
    public_metadata = {
        key: value
        for key, value in candidate.metadata.items()
        if key not in {"version", SOURCE_TIMESTAMP_KEY, CONTENT_FINGERPRINT_KEY}
    }
    if candidate.kind == "skill":
        return _fingerprint_skill_package(candidate.source_path, candidate.body, public_metadata)
    return _fingerprint_bytes([compose_document(public_metadata, candidate.body).encode("utf-8")])


def compute_asset_fingerprint(asset: Asset) -> str:
    public_metadata = {
        key: value
        for key, value in asset.metadata.items()
        if key not in {"version", SOURCE_TIMESTAMP_KEY, CONTENT_FINGERPRINT_KEY}
    }
    if asset.kind == "skill":
        return _fingerprint_skill_package(asset.root_path, asset.body, public_metadata)
    return _fingerprint_bytes([compose_document(public_metadata, asset.body).encode("utf-8")])


def _fingerprint_skill_package(source_root: Path, skill_body: str, skill_metadata: Dict[str, object]) -> str:
    chunks: List[bytes] = []
    skill_entry = source_root / "SKILL.md"
    for file_path in sorted(_iter_files(source_root)):
        relative = file_path.relative_to(source_root).as_posix().encode("utf-8")
        chunks.append(relative + b"\0")
        if file_path == skill_entry:
            chunks.append(compose_document(skill_metadata, skill_body).encode("utf-8"))
        else:
            chunks.append(file_path.read_bytes())
        chunks.append(b"\0")
    return _fingerprint_bytes(chunks)


def _fingerprint_bytes(chunks: Iterable[bytes]) -> str:
    digest = hashlib.sha256()
    for chunk in chunks:
        digest.update(chunk)
    return digest.hexdigest()


def _iter_files(root: Path) -> Iterable[Path]:
    for path in root.rglob("*"):
        if path.is_file():
            yield path


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


def suggest_asset_selectors(root: Path, selector: str, limit: int = 5) -> List[str]:
    ensure_store(root)
    query = selector.strip().lower()
    if not query:
        return []

    requested_kind: Optional[str] = None
    if ":" in query:
        kind, asset_id = query.split(":", 1)
        if kind in ASSET_KINDS:
            requested_kind = kind
        query_id = slugify(asset_id)
        selector_query = f"{kind}:{query_id}"
    else:
        query_id = slugify(query)
        selector_query = query_id

    ranked: List[Tuple[float, str]] = []
    for asset in list_assets(root):
        if requested_kind and asset.kind != requested_kind:
            continue
        score = _selector_match_score(asset, selector_query, query_id, scoped=bool(requested_kind))
        if score > 0:
            ranked.append((score, asset.selector))

    ranked.sort(key=lambda item: (-item[0], item[1]))
    return [selector for _, selector in ranked[:limit]]


def _selector_match_score(asset: Asset, selector_query: str, query_id: str, scoped: bool) -> float:
    if not query_id:
        return 0.0

    token_score = _keyword_match_score(query_id, asset.id)
    if token_score > 0:
        return token_score

    selector_score = SequenceMatcher(None, selector_query, asset.selector).ratio()
    id_score = SequenceMatcher(None, query_id, asset.id).ratio()

    if asset.selector.startswith(selector_query):
        selector_score += 0.35
    elif selector_query in asset.selector:
        selector_score += 0.15

    if asset.id.startswith(query_id):
        id_score += 0.35
    elif query_id in asset.id:
        id_score += 0.15

    # Similarity is only a fallback when there is no direct keyword-style match.
    if scoped:
        score = min(max(selector_score, id_score + 0.05), 1.0)
    else:
        score = min(max(id_score, selector_score - 0.1), 1.0)
    return score if score >= 0.7 else 0.0


def _keyword_match_score(query_id: str, asset_id: str) -> float:
    if asset_id.startswith(query_id):
        return 1.0

    asset_tokens = [token for token in re.split(r"[-_.]+", asset_id) if token]
    query_tokens = [token for token in re.split(r"[-_.]+", query_id) if token]
    if not query_tokens:
        return 0.0

    if any(token == query_id for token in asset_tokens):
        return 0.98
    if any(token.startswith(query_id) for token in asset_tokens):
        return 0.96

    for query_token in query_tokens:
        if any(token == query_token for token in asset_tokens):
            return 0.94
    for query_token in query_tokens:
        if any(token.startswith(query_token) for token in asset_tokens):
            return 0.92

    if query_id in asset_id and len(query_id) >= 3:
        return 0.9

    return 0.0


def delete_asset(root: Path, selector: str) -> Asset:
    asset = resolve_asset(root, selector)
    target = asset.root_path if asset.kind in ("skill", "agents") else asset.path
    if asset.kind == "prompt":
        target.unlink()
    else:
        shutil.rmtree(target)
    asset_history = history_dir(root, asset.kind, asset.id)
    if asset_history.exists():
        shutil.rmtree(asset_history)
    return asset


def delete_asset_with_paths(root: Path, selector: str) -> MutationResult:
    asset = resolve_asset(root, selector)
    touched_paths = [asset.root_path if asset.kind in ("skill", "agents") else asset.path]
    asset_history = history_dir(root, asset.kind, asset.id)
    if asset_history.exists():
        touched_paths.append(asset_history)
    removed = delete_asset(root, selector)
    return MutationResult(status="deleted", asset=removed, touched_paths=touched_paths)


def _touched_paths_for_asset(asset: Asset, extra_paths: Optional[List[Path]] = None) -> List[Path]:
    touched = [asset.root_path if asset.kind in ("skill", "agents") else asset.path]
    for item in extra_paths or []:
        if item not in touched:
            touched.append(item)
    return touched
