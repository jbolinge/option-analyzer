---
id: options-6
title: "Domain Greeks models — FirstOrder, SecondOrder, Full, Position"
type: task
status: closed
priority: 1
created: 2026-02-05
updated: 2026-02-05
parent: options-1
depends-on: options-4
---

# Domain Greeks models — FirstOrder, SecondOrder, Full, Position

Create the Greeks dataclass hierarchy for representing option sensitivities.

## Branch
`feature/domain-models`

## Files to Create/Modify
- `src/options_analyzer/domain/greeks.py`
- `tests/test_domain/test_greeks.py`

## Models

### FirstOrderGreeks (frozen Pydantic BaseModel)
Source: from data provider (streamed via TastyTrade)
Fields:
- `delta: float`
- `gamma: float`
- `theta: float`
- `vega: float`
- `rho: float`
- `iv: float` — implied volatility

### SecondOrderGreeks (frozen Pydantic BaseModel)
Source: computed via BSM engine
Fields:
- `vanna: float` — dDelta/dVol
- `volga: float` — dVega/dVol (aka vomma)
- `charm: float` — dDelta/dTime
- `veta: float` — dVega/dTime
- `speed: float` — dGamma/dSpot
- `color: float` — dGamma/dTime

### FullGreeks (frozen Pydantic BaseModel)
Fields:
- `first_order: FirstOrderGreeks`
- `second_order: SecondOrderGreeks`

### PositionGreeks (frozen Pydantic BaseModel)
Fields:
- `per_leg: dict[str, FullGreeks]` — keyed by leg contract symbol
- `aggregated: FullGreeks` — position-level totals

## TDD Approach
1. **Red**: Write tests first:
   - Creation with valid float values
   - Models are frozen
   - FullGreeks composes first + second order correctly
   - PositionGreeks holds per-leg and aggregated
   - Serialization round-trip
   - Default zero values or require all fields
2. **Green**: Implement models
3. **Refactor**: Clean up

## Notes
- Use float (not Decimal) for Greeks — they are approximations, not financial values
- All models frozen for immutability
