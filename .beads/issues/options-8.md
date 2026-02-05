---
id: options-8
title: "Configuration schema — AppConfig, ProviderConfig"
type: task
status: open
priority: 1
created: 2026-02-05
updated: 2026-02-05
parent: options-1
depends-on: options-2
---

# Configuration schema — AppConfig, ProviderConfig

Create the Pydantic v2 configuration schema for loading app settings from YAML.

## Branch
`feature/domain-models`

## Files to Create/Modify
- `src/options_analyzer/config/__init__.py`
- `src/options_analyzer/config/schema.py`
- `config/config.yaml` (update placeholder with real structure)
- `tests/test_config/__init__.py`
- `tests/test_config/test_schema.py`

## Models

### ProviderConfig (BaseModel)
- `name: str = "tastytrade"`
- `username: SecretStr`
- `password: SecretStr`
- `is_paper: bool = True` — maps to tastytrade Session `is_test` flag

### EngineConfig (BaseModel)
- `risk_free_rate: float = 0.05`
- `dividend_yield: float = 0.0`

### VisualizationConfig (BaseModel)
- `theme: str = "bloomberg"` — for future theme switching

### AppConfig (BaseModel)
- `provider: ProviderConfig`
- `engine: EngineConfig`
- `visualization: VisualizationConfig`
- Class method: `from_yaml(path: Path) -> AppConfig`

## config/config.yaml structure
```yaml
provider:
  name: tastytrade
  username: "${TASTYTRADE_USERNAME}"
  password: "${TASTYTRADE_PASSWORD}"
  is_paper: true

engine:
  risk_free_rate: 0.05
  dividend_yield: 0.0

visualization:
  theme: bloomberg
```

## TDD Approach
1. **Red**: Write tests first:
   - AppConfig.from_yaml loads valid config
   - SecretStr masks credentials in repr/str
   - Validation rejects missing required fields
   - Default values work correctly
   - Environment variable substitution in YAML (or note it for future)
2. **Green**: Implement schema
3. **Refactor**: Clean up

## Notes
- Use `pydantic.SecretStr` for credential fields
- Use Context7 MCP to verify Pydantic v2 SecretStr usage
- YAML loading: use `pyyaml` with `yaml.safe_load()`
- Do NOT commit real credentials — config.yaml uses placeholders
