---
id: options-14
title: "GreeksCalculator class"
type: task
status: closed
priority: 2
created: 2026-02-05
updated: 2026-02-05
parent: options-9
depends-on: options-11
---

# GreeksCalculator class

Create a GreeksCalculator class that wraps the pure BSM functions with config defaults and returns domain Greeks models.

## Branch
`feature/bsm-engine`

## Files to Create
- `src/options_analyzer/engine/greeks_calculator.py`
- `tests/test_engine/test_greeks_calculator.py`

## Class Design

### GreeksCalculator
```python
class GreeksCalculator:
    def __init__(self, risk_free_rate: float = 0.05, dividend_yield: float = 0.0):
        ...

    def first_order(
        self, S: float, K: float, T: float, sigma: float,
        option_type: OptionType, r: float | None = None, q: float | None = None
    ) -> FirstOrderGreeks:
        """Compute first-order Greeks. Uses config defaults for r/q if not provided."""

    def second_order(
        self, S: float, K: float, T: float, sigma: float,
        option_type: OptionType, r: float | None = None, q: float | None = None
    ) -> SecondOrderGreeks:
        """Compute second-order Greeks."""

    def full(
        self, S: float, K: float, T: float, sigma: float,
        option_type: OptionType, r: float | None = None, q: float | None = None
    ) -> FullGreeks:
        """Compute all Greeks (first + second order)."""
```

## TDD Approach
1. **Red**: Write tests first:
   - Constructor stores config defaults
   - first_order() returns valid FirstOrderGreeks with correct values
   - second_order() returns valid SecondOrderGreeks
   - full() returns FullGreeks composing both
   - Config defaults are used when r/q not provided
   - Explicit r/q overrides config defaults
   - Edge cases: T<=0, sigma<=0
2. **Green**: Implement class, delegating to bsm.py pure functions
3. **Refactor**: Clean up

## Notes
- This class is a thin wrapper — all math lives in bsm.py
- Returns domain model types (FirstOrderGreeks, etc.), not raw floats
- Can be initialized from EngineConfig
