"""Configuration schema with Pydantic v2 and YAML loading."""

from pathlib import Path

import yaml
from pydantic import BaseModel, SecretStr


class ProviderConfig(BaseModel):
    name: str = "tastytrade"
    username: SecretStr
    password: SecretStr
    is_paper: bool = True


class EngineConfig(BaseModel):
    risk_free_rate: float = 0.05
    dividend_yield: float = 0.0


class VisualizationConfig(BaseModel):
    theme: str = "bloomberg"


class AppConfig(BaseModel):
    provider: ProviderConfig
    engine: EngineConfig = EngineConfig()
    visualization: VisualizationConfig = VisualizationConfig()

    @classmethod
    def from_yaml(cls, path: Path) -> "AppConfig":
        """Load configuration from a YAML file."""
        if not path.exists():
            raise FileNotFoundError(f"Config file not found: {path}")
        with open(path) as f:
            data = yaml.safe_load(f)
        return cls.model_validate(data)
