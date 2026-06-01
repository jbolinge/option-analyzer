"""Configuration schema with Pydantic v2 and YAML loading."""

from pathlib import Path

import yaml
from pydantic import BaseModel, SecretStr


class ProviderConfig(BaseModel):
    name: str = "tastytrade"
    client_secret: SecretStr
    refresh_token: SecretStr
    is_paper: bool = True
    use_dxlink_candles: bool = True
    include_latest_candle: bool = False


class EngineConfig(BaseModel):
    risk_free_rate: float = 0.05
    dividend_yield: float = 0.0


class VisualizationConfig(BaseModel):
    theme: str = "bloomberg"


class ApiConfig(BaseModel):
    host: str = "0.0.0.0"
    port: int = 8000
    cors_origins: list[str] = ["http://localhost:5173"]


class ReportConfig(BaseModel):
    """Settings for generated report artifacts (e.g. the market-outlook PDF).

    ``output_dir`` is the default save location for generated files. A relative
    path is resolved against the project root; an absolute path is used as-is.
    """

    output_dir: str = "reports"


class AppConfig(BaseModel):
    provider: ProviderConfig
    engine: EngineConfig = EngineConfig()
    visualization: VisualizationConfig = VisualizationConfig()
    api: ApiConfig = ApiConfig()
    reports: ReportConfig = ReportConfig()

    @classmethod
    def from_yaml(cls, path: Path) -> "AppConfig":
        """Load configuration from a YAML file."""
        if not path.exists():
            raise FileNotFoundError(f"Config file not found: {path}")
        with open(path) as f:
            data = yaml.safe_load(f)
        return cls.model_validate(data)
