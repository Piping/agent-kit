from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict


ASSET_KINDS = ("prompt", "skill", "agents")


@dataclass(frozen=True)
class Asset:
    id: str
    kind: str
    version: str
    path: Path
    root_path: Path
    body: str
    metadata: Dict[str, Any] = field(default_factory=dict)

    @property
    def selector(self) -> str:
        return f"{self.kind}:{self.id}"


@dataclass(frozen=True)
class ImportCandidate:
    source_path: Path
    entry_path: Path
    asset_id: str
    kind: str
    body: str
    metadata: Dict[str, Any] = field(default_factory=dict)

    @property
    def selector(self) -> str:
        return f"{self.kind}:{self.asset_id}"
