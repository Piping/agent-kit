import os
from typing import Optional

START_MARKER = "<!-- OPENSPEC:START -->"
END_MARKER = "<!-- OPENSPEC:END -->"


def ensure_parent_dir(path: str) -> None:
    parent = os.path.dirname(path)
    if parent:
        os.makedirs(parent, exist_ok=True)


def build_managed_content(
    body: str,
    frontmatter: Optional[str] = None,
    marker_prefix: str = "",
    suffix: Optional[str] = None,
) -> str:
    parts = []
    if frontmatter:
        parts.append(frontmatter.rstrip())
    start_marker = f"{marker_prefix}{START_MARKER}"
    end_marker = f"{marker_prefix}{END_MARKER}"
    parts.append(f"{start_marker}\n{body.rstrip()}\n{end_marker}")
    if suffix:
        parts.append(suffix.lstrip().rstrip())
    return "\n".join(parts) + "\n"


def update_managed_block(
    path: str,
    body: str,
    frontmatter: Optional[str] = None,
    marker_prefix: str = "",
    suffix: Optional[str] = None,
) -> None:
    if not os.path.exists(path):
        ensure_parent_dir(path)
        with open(path, "w", encoding="utf-8") as handle:
            handle.write(build_managed_content(body, frontmatter, marker_prefix, suffix))
        return

    with open(path, "r", encoding="utf-8") as handle:
        content = handle.read()

    start_marker = START_MARKER
    end_marker = END_MARKER
    if marker_prefix:
        prefixed_start = f"{marker_prefix}{START_MARKER}"
        prefixed_end = f"{marker_prefix}{END_MARKER}"
        if prefixed_start in content and prefixed_end in content:
            start_marker = prefixed_start
            end_marker = prefixed_end

    start_index = content.find(start_marker)
    end_index = content.find(end_marker)
    if start_index == -1 or end_index == -1 or end_index <= start_index:
        raise ValueError(f"Missing OpenSpec markers in {path}")

    before = content[: start_index + len(start_marker)]
    after = content[end_index:]
    updated = f"{before}\n{body.rstrip()}\n{after}"

    with open(path, "w", encoding="utf-8") as handle:
        handle.write(updated)
