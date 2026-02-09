"""Tests for config loader with .env and YAML interpolation."""

import os
from pathlib import Path
from unittest.mock import patch

import pytest
import yaml

from options_analyzer.config.loader import load_config, resolve_env_vars


class TestResolveEnvVars:
    """Tests for resolve_env_vars()."""

    def test_resolves_simple_string(self) -> None:
        with patch.dict(os.environ, {"MY_VAR": "hello"}):
            result = resolve_env_vars({"key": "${MY_VAR}"})
        assert result == {"key": "hello"}

    def test_resolves_nested_dicts(self) -> None:
        with patch.dict(os.environ, {"SECRET": "s3cret"}):
            result = resolve_env_vars({"outer": {"inner": "${SECRET}"}})
        assert result == {"outer": {"inner": "s3cret"}}

    def test_resolves_values_in_lists(self) -> None:
        with patch.dict(os.environ, {"A": "alpha", "B": "beta"}):
            result = resolve_env_vars({"items": ["${A}", "${B}"]})
        assert result == {"items": ["alpha", "beta"]}

    def test_leaves_non_placeholder_strings_unchanged(self) -> None:
        result = resolve_env_vars({"key": "plain_value"})
        assert result == {"key": "plain_value"}

    def test_leaves_non_string_values_unchanged(self) -> None:
        result = resolve_env_vars({"count": 42, "flag": True, "rate": 0.05})
        assert result == {"count": 42, "flag": True, "rate": 0.05}

    def test_raises_keyerror_for_undefined_var(self) -> None:
        env = {k: v for k, v in os.environ.items() if k != "UNDEFINED_VAR_XYZ"}
        with patch.dict(os.environ, env, clear=True):
            with pytest.raises(KeyError, match="UNDEFINED_VAR_XYZ"):
                resolve_env_vars({"key": "${UNDEFINED_VAR_XYZ}"})

    def test_partial_placeholder_in_string(self) -> None:
        with patch.dict(os.environ, {"HOST": "example.com"}):
            result = resolve_env_vars({"url": "https://${HOST}/api"})
        assert result == {"url": "https://example.com/api"}

    def test_multiple_placeholders_in_one_string(self) -> None:
        with patch.dict(os.environ, {"HOST": "example.com", "PORT": "8080"}):
            result = resolve_env_vars({"url": "${HOST}:${PORT}"})
        assert result == {"url": "example.com:8080"}

    def test_preserves_none_values(self) -> None:
        result = resolve_env_vars({"key": None})
        assert result == {"key": None}


class TestLoadConfig:
    """Tests for load_config()."""

    def test_loads_yaml_with_resolved_env_vars(self, tmp_path: Path) -> None:
        config_yaml = tmp_path / "config.yaml"
        config_yaml.write_text(
            yaml.dump({
                "provider": {
                    "name": "tastytrade",
                    "client_secret": "${TEST_SECRET}",
                    "refresh_token": "${TEST_TOKEN}",
                    "is_paper": True,
                },
                "engine": {"risk_free_rate": 0.05, "dividend_yield": 0.0},
                "visualization": {"theme": "bloomberg"},
            })
        )
        with patch.dict(
            os.environ, {"TEST_SECRET": "my_secret", "TEST_TOKEN": "my_token"}
        ):
            config = load_config(config_path=config_yaml)

        assert config.provider.client_secret.get_secret_value() == "my_secret"
        assert config.provider.refresh_token.get_secret_value() == "my_token"
        assert config.provider.name == "tastytrade"
        assert config.provider.is_paper is True

    def test_loads_dotenv_before_resolving(self, tmp_path: Path) -> None:
        env_file = tmp_path / ".env"
        env_file.write_text("DOTENV_SECRET=from_dotenv\nDOTENV_TOKEN=tok_dotenv\n")

        config_yaml = tmp_path / "config.yaml"
        config_yaml.write_text(
            yaml.dump({
                "provider": {
                    "client_secret": "${DOTENV_SECRET}",
                    "refresh_token": "${DOTENV_TOKEN}",
                },
            })
        )
        # Clear these vars so only .env provides them
        env = {
            k: v
            for k, v in os.environ.items()
            if k not in ("DOTENV_SECRET", "DOTENV_TOKEN")
        }
        with patch.dict(os.environ, env, clear=True):
            config = load_config(config_path=config_yaml, env_path=env_file)

        assert config.provider.client_secret.get_secret_value() == "from_dotenv"
        assert config.provider.refresh_token.get_secret_value() == "tok_dotenv"

    def test_shell_env_takes_precedence_over_dotenv(self, tmp_path: Path) -> None:
        env_file = tmp_path / ".env"
        env_file.write_text("PREC_SECRET=from_dotenv\nPREC_TOKEN=from_dotenv\n")

        config_yaml = tmp_path / "config.yaml"
        config_yaml.write_text(
            yaml.dump({
                "provider": {
                    "client_secret": "${PREC_SECRET}",
                    "refresh_token": "${PREC_TOKEN}",
                },
            })
        )
        with patch.dict(
            os.environ,
            {"PREC_SECRET": "from_shell", "PREC_TOKEN": "from_shell"},
        ):
            config = load_config(config_path=config_yaml, env_path=env_file)

        assert config.provider.client_secret.get_secret_value() == "from_shell"

    def test_non_secret_yaml_fields_preserved(self, tmp_path: Path) -> None:
        config_yaml = tmp_path / "config.yaml"
        config_yaml.write_text(
            yaml.dump({
                "provider": {
                    "client_secret": "${NS_SECRET}",
                    "refresh_token": "${NS_TOKEN}",
                },
                "engine": {"risk_free_rate": 0.03, "dividend_yield": 0.01},
                "visualization": {"theme": "dark"},
            })
        )
        with patch.dict(
            os.environ, {"NS_SECRET": "s", "NS_TOKEN": "t"}
        ):
            config = load_config(config_path=config_yaml)

        assert config.engine.risk_free_rate == 0.03
        assert config.engine.dividend_yield == 0.01
        assert config.visualization.theme == "dark"

    def test_filenotfounderror_when_yaml_missing(self, tmp_path: Path) -> None:
        missing = tmp_path / "nonexistent.yaml"
        with pytest.raises(FileNotFoundError):
            load_config(config_path=missing)

    def test_keyerror_when_env_var_unset(self, tmp_path: Path) -> None:
        config_yaml = tmp_path / "config.yaml"
        config_yaml.write_text(
            yaml.dump({
                "provider": {
                    "client_secret": "${MISSING_SECRET_XYZ}",
                    "refresh_token": "${MISSING_TOKEN_XYZ}",
                },
            })
        )
        env = {
            k: v
            for k, v in os.environ.items()
            if k not in ("MISSING_SECRET_XYZ", "MISSING_TOKEN_XYZ")
        }
        with patch.dict(os.environ, env, clear=True):
            with pytest.raises(KeyError, match="MISSING_SECRET_XYZ"):
                load_config(config_path=config_yaml)

    def test_missing_dotenv_file_is_graceful_noop(self, tmp_path: Path) -> None:
        config_yaml = tmp_path / "config.yaml"
        config_yaml.write_text(
            yaml.dump({
                "provider": {
                    "client_secret": "${GRACEFUL_SECRET}",
                    "refresh_token": "${GRACEFUL_TOKEN}",
                },
            })
        )
        missing_env = tmp_path / "does_not_exist.env"
        with patch.dict(
            os.environ,
            {"GRACEFUL_SECRET": "s", "GRACEFUL_TOKEN": "t"},
        ):
            config = load_config(config_path=config_yaml, env_path=missing_env)

        assert config.provider.client_secret.get_secret_value() == "s"

    def test_auto_discovers_paths_from_project_root(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        # Simulate project structure
        (tmp_path / "pyproject.toml").write_text("[project]\nname = 'test'\n")
        config_dir = tmp_path / "config"
        config_dir.mkdir()
        config_yaml = config_dir / "config.yaml"
        config_yaml.write_text(
            yaml.dump({
                "provider": {
                    "client_secret": "${AUTO_SECRET}",
                    "refresh_token": "${AUTO_TOKEN}",
                },
            })
        )
        env_file = tmp_path / ".env"
        env_file.write_text("AUTO_SECRET=auto_s\nAUTO_TOKEN=auto_t\n")

        # Run from a subdirectory (like notebooks/)
        notebooks_dir = tmp_path / "notebooks"
        notebooks_dir.mkdir()
        monkeypatch.chdir(notebooks_dir)

        env = {
            k: v
            for k, v in os.environ.items()
            if k not in ("AUTO_SECRET", "AUTO_TOKEN")
        }
        with patch.dict(os.environ, env, clear=True):
            config = load_config()

        assert config.provider.client_secret.get_secret_value() == "auto_s"
