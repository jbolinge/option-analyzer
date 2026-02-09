"""Config loader with .env support and YAML placeholder interpolation."""

import os
import re
from pathlib import Path
from typing import Any

import yaml
from dotenv import load_dotenv

from options_analyzer.config.schema import AppConfig

_ENV_VAR_PATTERN = re.compile(r"\$\{([^}]+)\}")


def resolve_env_vars(data: dict[str, Any]) -> dict[str, Any]:
    """Recursively resolve ``${VAR}`` placeholders using ``os.environ``.

    Raises ``KeyError`` if a referenced variable is not set.
    """
    return {k: _resolve_value(v) for k, v in data.items()}


def _resolve_value(value: Any) -> Any:
    if isinstance(value, dict):
        return resolve_env_vars(value)
    if isinstance(value, list):
        return [_resolve_value(item) for item in value]
    if isinstance(value, str) and "${" in value:
        return _resolve_string(value)
    return value


def _resolve_string(value: str) -> str:
    def _replacer(match: re.Match[str]) -> str:
        var_name = match.group(1)
        try:
            return os.environ[var_name]
        except KeyError:
            raise KeyError(
                f"Environment variable '{var_name}' is not set "
                f"(referenced in config as '${{{var_name}}}')"
            ) from None

    return _ENV_VAR_PATTERN.sub(_replacer, value)


def _find_project_root() -> Path:
    """Walk up from cwd looking for ``pyproject.toml``."""
    current = Path.cwd().resolve()
    for directory in (current, *current.parents):
        if (directory / "pyproject.toml").exists():
            return directory
    raise FileNotFoundError(
        "Could not find project root (no pyproject.toml in parent directories)"
    )


def load_config(
    *,
    config_path: Path | None = None,
    env_path: Path | None = None,
) -> AppConfig:
    """Load configuration from YAML with ``.env`` and env var interpolation.

    1. Loads ``.env`` file (if present) without overriding existing env vars.
    2. Reads and parses the YAML config file.
    3. Resolves ``${VAR}`` placeholders from ``os.environ``.
    4. Validates and returns an ``AppConfig``.

    When called with no arguments, auto-discovers paths relative to the
    project root (the nearest ancestor containing ``pyproject.toml``).
    """
    if config_path is None or env_path is None:
        root = _find_project_root()
        if config_path is None:
            config_path = root / "config" / "config.yaml"
        if env_path is None:
            env_path = root / ".env"

    # load_dotenv is a no-op if the file doesn't exist
    load_dotenv(env_path, override=False)

    if not config_path.exists():
        raise FileNotFoundError(f"Config file not found: {config_path}")

    with open(config_path) as f:
        data = yaml.safe_load(f)

    resolved = resolve_env_vars(data)
    return AppConfig.model_validate(resolved)
