---
id: options-1
title: "Project Scaffolding & Domain Models"
type: epic
status: closed
priority: 1
created: 2026-02-05
updated: 2026-02-05
---

# Project Scaffolding & Domain Models

Foundation phase: project setup, domain enums, core data models, Greeks dataclasses, test factories, and configuration schema. No external API calls — everything is pure Python and fully testable offline.

## Scope
- Project scaffolding with uv, pyproject.toml, src layout
- CLAUDE.md with project context for AI-assisted development
- Domain enums (OptionType, PositionSide, ExerciseStyle)
- Core models (OptionContract, Leg, Position) with Pydantic v2
- Greeks models (FirstOrderGreeks, SecondOrderGreeks, FullGreeks, PositionGreeks)
- Test object factories for reuse across all test suites
- Configuration schema (AppConfig, ProviderConfig) with Pydantic v2

## Acceptance Criteria
- [ ] `uv run pytest` passes with domain model tests
- [ ] `uv run mypy src/` passes cleanly
- [ ] `uv run ruff check src/` passes cleanly
- [ ] All domain models are immutable (frozen Pydantic models)
- [ ] Test factories produce valid domain objects
- [ ] Config loads from YAML with SecretStr for credentials
