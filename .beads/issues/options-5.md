---
id: options-5
title: "Domain models — OptionContract, Leg, Position"
type: task
status: closed
priority: 1
created: 2026-02-05
updated: 2026-02-05
parent: options-1
depends-on: options-4
---

# Domain models — OptionContract, Leg, Position

Create the core domain models using Pydantic v2 frozen models.

## Branch
`feature/domain-models`

## Files to Create/Modify
- `src/options_analyzer/domain/models.py`
- `tests/test_domain/test_models.py`

## Models

### OptionContract (frozen Pydantic BaseModel)
Fields:
- `symbol: str` — option symbol (e.g., "AAPL  240119C00150000")
- `underlying: str` — underlying ticker (e.g., "AAPL")
- `option_type: OptionType`
- `strike: Decimal`
- `expiration: date`
- `exercise_style: ExerciseStyle = ExerciseStyle.AMERICAN`
- `multiplier: int = 100`
- `streamer_symbol: str | None = None` — for streaming data

### Leg (frozen Pydantic BaseModel)
Fields:
- `contract: OptionContract`
- `side: PositionSide`
- `quantity: int` — always positive
- `open_price: Decimal` — per-contract price paid/received

Computed properties:
- `signed_quantity: int` — positive for LONG, negative for SHORT

### Position (frozen Pydantic BaseModel)
Fields:
- `id: str` — unique identifier
- `name: str` — human-readable (e.g., "AAPL Jan 150/160/170 BWB")
- `underlying: str`
- `legs: list[Leg]`
- `opened_at: datetime`

Computed properties:
- `net_debit_credit: Decimal` — sum of signed_quantity * open_price * multiplier across legs

## TDD Approach
1. **Red**: Write tests first:
   - OptionContract creation with valid/invalid data
   - Leg.signed_quantity returns correct sign
   - Position.net_debit_credit computes correctly for multi-leg
   - Models are frozen (assignment raises error)
   - Pydantic validation rejects invalid types
   - Round-trip serialization (model_dump / model_validate)
2. **Green**: Implement models
3. **Refactor**: Extract any shared validation logic

## Notes
- Use `from decimal import Decimal` for financial precision
- Use `model_config = ConfigDict(frozen=True)` for immutability
- Use `@computed_field` or `@property` for derived values
- Use Context7 MCP to check Pydantic v2 computed_field API
