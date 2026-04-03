from __future__ import annotations

from pathlib import Path
from typing import Any, Dict


def load_akit_config(store_root: Path) -> Dict[str, Any]:
    config_path = store_root / "config.toml"
    if not config_path.exists():
        return {}

    try:
        import tomllib  # type: ignore[attr-defined]

        with config_path.open("rb") as handle:
            return tomllib.load(handle)
    except ImportError:
        return _parse_minimal_toml(config_path.read_text(encoding="utf-8"))


def _parse_minimal_toml(text: str) -> Dict[str, Any]:
    config: Dict[str, Any] = {}
    current = config

    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("[") and line.endswith("]"):
            section = line[1:-1].strip()
            config.setdefault(section, {})
            current = config[section]
            continue
        if "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in ("'", '"'):
            value = value[1:-1]
        current[key] = value
    return config
