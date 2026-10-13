from __future__ import annotations

import os
import re
from pathlib import Path
from typing import Any

import yaml
from jsonschema import Draft202012Validator

_ENV_PATTERN = re.compile(r"\$\{([A-Z_][A-Z0-9_]*)\}")


class ConfigurationError(ValueError):
    """Raised when client configuration is invalid or incomplete."""


def _expand_environment(value: Any) -> Any:
    if isinstance(value, str):
        missing: set[str] = set()

        def replace(match: re.Match[str]) -> str:
            name = match.group(1)
            resolved = os.getenv(name)
            if resolved is None:
                missing.add(name)
                return match.group(0)
            return resolved

        expanded = _ENV_PATTERN.sub(replace, value)
        if missing:
            names = ", ".join(sorted(missing))
            raise ConfigurationError(f"Missing environment variables: {names}")
        return expanded
    if isinstance(value, list):
        return [_expand_environment(item) for item in value]
    if isinstance(value, dict):
        return {key: _expand_environment(item) for key, item in value.items()}
    return value


def load_config(path: str | Path, schema_path: str | Path) -> dict[str, Any]:
    config_file = Path(path)
    schema_file = Path(schema_path)
    with config_file.open(encoding="utf-8") as stream:
        config = yaml.safe_load(stream)
    with schema_file.open(encoding="utf-8") as stream:
        schema = yaml.safe_load(stream)

    errors = sorted(Draft202012Validator(schema).iter_errors(config), key=lambda error: list(error.path))
    if errors:
        details = "; ".join(
            f"{'.'.join(str(part) for part in error.path) or '<root>'}: {error.message}"
            for error in errors
        )
        raise ConfigurationError(details)
    return _expand_environment(config)

