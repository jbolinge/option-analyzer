"""Tests for configuration schema."""

import tempfile
from pathlib import Path

import pytest
from pydantic import ValidationError

from options_analyzer.config.schema import (
    AppConfig,
    EngineConfig,
    ProviderConfig,
    VisualizationConfig,
)


class TestProviderConfig:
    def test_creation(self) -> None:
        config = ProviderConfig(
            username="user",  # type: ignore[arg-type]
            password="pass",  # type: ignore[arg-type]
        )
        assert config.name == "tastytrade"
        assert config.is_paper is True

    def test_secret_str_masks_credentials(self) -> None:
        config = ProviderConfig(
            username="myuser",  # type: ignore[arg-type]
            password="mypass",  # type: ignore[arg-type]
        )
        repr_str = repr(config)
        assert "myuser" not in repr_str
        assert "mypass" not in repr_str

    def test_secret_str_reveals_value(self) -> None:
        config = ProviderConfig(
            username="myuser",  # type: ignore[arg-type]
            password="mypass",  # type: ignore[arg-type]
        )
        assert config.username.get_secret_value() == "myuser"
        assert config.password.get_secret_value() == "mypass"


class TestEngineConfig:
    def test_defaults(self) -> None:
        config = EngineConfig()
        assert config.risk_free_rate == 0.05
        assert config.dividend_yield == 0.0

    def test_overrides(self) -> None:
        config = EngineConfig(risk_free_rate=0.04, dividend_yield=0.02)
        assert config.risk_free_rate == 0.04
        assert config.dividend_yield == 0.02


class TestVisualizationConfig:
    def test_defaults(self) -> None:
        config = VisualizationConfig()
        assert config.theme == "bloomberg"


class TestAppConfig:
    def test_from_yaml(self, tmp_path: Path) -> None:
        yaml_content = """\
provider:
  name: tastytrade
  username: testuser
  password: testpass
  is_paper: true

engine:
  risk_free_rate: 0.04
  dividend_yield: 0.01

visualization:
  theme: bloomberg
"""
        config_file = tmp_path / "config.yaml"
        config_file.write_text(yaml_content)

        config = AppConfig.from_yaml(config_file)
        assert config.provider.name == "tastytrade"
        assert config.provider.username.get_secret_value() == "testuser"
        assert config.provider.password.get_secret_value() == "testpass"
        assert config.provider.is_paper is True
        assert config.engine.risk_free_rate == 0.04
        assert config.engine.dividend_yield == 0.01
        assert config.visualization.theme == "bloomberg"

    def test_from_yaml_with_defaults(self, tmp_path: Path) -> None:
        yaml_content = """\
provider:
  username: testuser
  password: testpass
"""
        config_file = tmp_path / "config.yaml"
        config_file.write_text(yaml_content)

        config = AppConfig.from_yaml(config_file)
        assert config.engine.risk_free_rate == 0.05
        assert config.visualization.theme == "bloomberg"

    def test_from_yaml_missing_credentials_raises(self, tmp_path: Path) -> None:
        yaml_content = """\
provider:
  name: tastytrade
"""
        config_file = tmp_path / "config.yaml"
        config_file.write_text(yaml_content)

        with pytest.raises(ValidationError):
            AppConfig.from_yaml(config_file)

    def test_from_yaml_file_not_found(self) -> None:
        with pytest.raises(FileNotFoundError):
            AppConfig.from_yaml(Path("/nonexistent/config.yaml"))
