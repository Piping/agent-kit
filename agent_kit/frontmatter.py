from __future__ import annotations

from typing import Any, Dict, Iterable, Tuple


FRONTMATTER_DELIMITER = "---"
PREFERRED_KEYS = ("id", "kind", "version", "name", "title", "description", "tags")


def split_frontmatter(text: str) -> Tuple[Dict[str, Any], str]:
    if not text.startswith(f"{FRONTMATTER_DELIMITER}\n"):
        return {}, text

    remainder = text[len(FRONTMATTER_DELIMITER) + 1 :]
    delimiter = f"\n{FRONTMATTER_DELIMITER}\n"
    end = remainder.find(delimiter)
    if end == -1:
        return {}, text

    raw_meta = remainder[:end]
    body = remainder[end + len(delimiter) :]
    return parse_frontmatter(raw_meta), body


def parse_frontmatter(raw: str) -> Dict[str, Any]:
    metadata: Dict[str, Any] = {}
    current_list_key = None

    for line in raw.splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        if stripped.startswith("#"):
            continue
        if stripped.startswith("- ") and current_list_key:
            metadata.setdefault(current_list_key, [])
            metadata[current_list_key].append(parse_scalar(stripped[2:].strip()))
            continue
        current_list_key = None
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        key = key.strip()
        value = value.strip()
        if not value:
            metadata[key] = []
            current_list_key = key
            continue
        metadata[key] = parse_scalar(value)
    return metadata


def parse_scalar(value: str) -> Any:
    if len(value) >= 2 and value[0] == value[-1] and value[0] in ("'", '"'):
        return value[1:-1]
    if value.startswith("[") and value.endswith("]"):
        items = value[1:-1].strip()
        if not items:
            return []
        return [parse_scalar(item.strip()) for item in items.split(",")]
    lowered = value.lower()
    if lowered == "true":
        return True
    if lowered == "false":
        return False
    return value


def dump_frontmatter(metadata: Dict[str, Any]) -> str:
    ordered_keys = list(PREFERRED_KEYS)
    ordered_keys.extend(sorted(key for key in metadata.keys() if key not in PREFERRED_KEYS))

    lines = [FRONTMATTER_DELIMITER]
    for key in ordered_keys:
        if key not in metadata:
            continue
        value = metadata[key]
        lines.extend(_dump_pair(key, value))
    lines.append(FRONTMATTER_DELIMITER)
    return "\n".join(lines)


def _dump_pair(key: str, value: Any) -> Iterable[str]:
    if isinstance(value, list):
        if not value:
            return [f"{key}: []"]
        lines = [f"{key}:"]
        for item in value:
            lines.append(f"- {_format_scalar(item)}")
        return lines
    return [f"{key}: {_format_scalar(value)}"]


def _format_scalar(value: Any) -> str:
    if isinstance(value, bool):
        return "true" if value else "false"
    if value is None:
        return '""'
    text = str(value)
    if not text:
        return '""'
    if any(ch in text for ch in (":", "#")) or text != text.strip():
        return f'"{text}"'
    return text


def compose_document(metadata: Dict[str, Any], body: str) -> str:
    normalized_body = body.lstrip("\n").rstrip() + "\n"
    return f"{dump_frontmatter(metadata)}\n{normalized_body}"


def compose_install_document(metadata: Dict[str, Any], body: str) -> str:
    public_metadata = {
        key: value
        for key, value in metadata.items()
        if key not in {"id", "kind", "version"} and not key.startswith("_")
    }
    normalized_body = body.lstrip("\n").rstrip() + "\n"
    if not public_metadata:
        return normalized_body
    return f"{dump_frontmatter(public_metadata)}\n{normalized_body}"
