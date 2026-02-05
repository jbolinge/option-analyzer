---
id: options-7
title: "Test object factories"
type: task
status: open
priority: 1
created: 2026-02-05
updated: 2026-02-05
parent: options-1
depends-on: options-5, options-6
---

# Test object factories

Create reusable test object factory functions for all domain models. These will be used throughout the entire test suite.

## Branch
`feature/domain-models`

## Files to Create/Modify
- `tests/factories.py`

## Factories to Create

### `make_contract(**overrides) -> OptionContract`
Defaults: AAPL call, strike=150, expiration=30 days out, American, multiplier=100

### `make_leg(**overrides) -> Leg`
Defaults: uses make_contract(), LONG, quantity=1, open_price=5.00

### `make_position(**overrides) -> Position`
Defaults: single-leg position using make_leg()

### `make_first_order_greeks(**overrides) -> FirstOrderGreeks`
Defaults: typical ATM call values (delta=0.5, gamma=0.05, theta=-0.05, vega=0.2, rho=0.01, iv=0.25)

### `make_second_order_greeks(**overrides) -> SecondOrderGreeks`
Defaults: reasonable second-order values (all near zero)

### `make_full_greeks(**overrides) -> FullGreeks`
Defaults: combines make_first_order_greeks() + make_second_order_greeks()

### Strategy Helpers
- `make_vertical_spread(underlying, strikes, option_type) -> Position`
- `make_butterfly(underlying, strikes, option_type) -> Position`
- `make_iron_condor(underlying, strikes) -> Position`

## TDD Approach
1. **Red**: Write tests that factories produce valid domain objects
2. **Green**: Implement factories
3. **Refactor**: Ensure override pattern works cleanly

## Notes
- Use `**overrides` pattern: set defaults, merge overrides, construct model
- Factories should be importable from `tests.factories`
- Keep factories simple — no mocking, just object construction
