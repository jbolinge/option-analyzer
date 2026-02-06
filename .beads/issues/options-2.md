---
id: options-2
title: "Project setup with uv and pyproject.toml"
type: task
status: closed
priority: 1
created: 2026-02-05
updated: 2026-02-05
parent: options-1
---

# Project setup with uv and pyproject.toml

Initialize the options-analyzer project with uv, modern Python 3.12+ tooling, and src layout.

## Branch
`feature/scaffolding`

## Files to Create
- `pyproject.toml`
- `src/options_analyzer/__init__.py`
- `.python-version` (3.12)
- `.gitignore`
- `tests/__init__.py`
- `tests/conftest.py`
- `config/config.yaml` (placeholder)

## Tasks
- [ ] Run `uv init` in project root
- [ ] Configure pyproject.toml with src layout and all dependencies
- [ ] Create src/options_analyzer/ package directory
- [ ] Create tests/ directory with conftest.py
- [ ] Create config/ directory with placeholder config.yaml
- [ ] Verify `uv sync` installs all dependencies
- [ ] Verify `uv run pytest` runs (0 tests collected, no errors)

## Dependencies (pyproject.toml)

### Core
- pydantic>=2.0
- numpy>=1.26
- scipy>=1.12
- plotly>=5.18
- pyyaml>=6.0
- tastytrade>=11.1

### Dev
- pytest>=8.0
- pytest-asyncio>=0.23
- pytest-cov
- hypothesis>=6.0
- ruff
- mypy

### Jupyter extras (optional group)
- jupyterlab>=4.0
- ipywidgets>=8.0

## TDD
This is scaffolding — no tests to write yet. Verify the toolchain works:
```bash
uv run pytest        # exits 0, no collection errors
uv run mypy src/     # exits 0
uv run ruff check src/  # exits 0
```

## Notes
- Use `uv` exclusively (no pip, no poetry)
- Use Context7 MCP to verify latest `tastytrade` SDK API if needed
- Use src layout: `src/options_analyzer/`
