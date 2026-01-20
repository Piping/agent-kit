from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class ManagedFile:
    path: str
    body: str
    frontmatter: Optional[str] = None
    marker_prefix: str = ""
    suffix: Optional[str] = None
