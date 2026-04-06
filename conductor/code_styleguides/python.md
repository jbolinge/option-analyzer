# Python Style Guide

## Tool Configuration

Linting and formatting enforced via existing project config in `pyproject.toml`:

- **Linter**: ruff (select: E, F, I, UP; target: py312)
- **Type Checker**: mypy (strict mode, packages: options_analyzer)
- **Formatter**: ruff format (implicit)

## Language Version

Python 3.12+ — use modern type hints (`list[str]`, `dict[str, int]`, `X | Y` union syntax).

## Import Style

- Use `from __future__ import annotations` for forward references
- Group imports: stdlib, third-party, local (enforced by ruff `I`)
- Prefer explicit imports over star imports

## Type Hints

- All public functions must have complete type annotations
- Use `Decimal` for financial values (prices, strikes)
- Use `float` for computed values (Greeks, indicators)
- Use `npt.NDArray[np.float64]` for numerical arrays
- Use `Sequence[Any]` for timestamp parameters (accepts list or array)

## Pydantic Models

- All domain models: `model_config = ConfigDict(frozen=True)`
- Use `@computed_field` for derived properties
- Use `SecretStr` for credentials (never logged or displayed)

## Async Patterns

- All provider methods are `async`
- Use `AsyncIterator` for streaming
- Use `asynccontextmanager` for resource lifecycle

## Testing

- Test files mirror source structure: `tests/test_<module>/test_<file>.py`
- Use `@pytest.mark.integration` for tests requiring credentials
- Use `@pytest.mark.slow` for hypothesis property tests
- Fixtures in `conftest.py`, builders in `factories.py`

## Naming

- snake_case for functions, variables, modules
- PascalCase for classes
- UPPER_SNAKE for module-level constants
- Prefix private helpers with `_`
