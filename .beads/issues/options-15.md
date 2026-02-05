---
id: options-15
title: "PayoffCalculator — expiration P&L, theoretical P&L, surfaces"
type: task
status: open
priority: 2
created: 2026-02-05
updated: 2026-02-05
parent: options-9
depends-on: options-5, options-11
---

# PayoffCalculator — expiration P&L, theoretical P&L, surfaces

Implement the PayoffCalculator for computing payoff diagrams and P&L surfaces across price and time dimensions.

## Branch
`feature/bsm-engine`

## Files to Create
- `src/options_analyzer/engine/payoff.py`
- `tests/test_engine/test_payoff.py`

## Class Design

### PayoffCalculator
```python
class PayoffCalculator:
    def __init__(self, risk_free_rate: float = 0.05, dividend_yield: float = 0.0):
        ...

    def expiration_payoff(
        self, position: Position, price_range: np.ndarray
    ) -> np.ndarray:
        """P&L at expiration for each price in range. The hockey-stick diagram."""

    def theoretical_pnl(
        self, position: Position, price_range: np.ndarray,
        ivs: dict[str, float], dte: float
    ) -> np.ndarray:
        """Theoretical P&L at given DTE using BSM pricing."""

    def pnl_surface(
        self, position: Position, price_range: np.ndarray,
        ivs: dict[str, float], dte_range: np.ndarray
    ) -> np.ndarray:
        """2D surface: price x time -> P&L. Shape: (len(dte_range), len(price_range))"""
```

## Computation Logic

### expiration_payoff
For each price S in price_range:
- For each leg: `payoff = max(0, S - K) for call, max(0, K - S) for put`
- Apply signed_quantity * multiplier
- Subtract cost basis (open_price * signed_quantity * multiplier)
- Sum across legs

### theoretical_pnl
For each price S:
- For each leg: compute BSM price at given DTE and IV
- Apply signed_quantity * multiplier
- Subtract cost basis
- Sum across legs

### pnl_surface
- Grid of (DTE, price) pairs
- theoretical_pnl at each DTE row

## TDD Approach
1. **Red**: Write tests first:
   - Long call: hockey stick shape (loss below strike, linear gain above)
   - Long put: hockey stick shape (linear gain below strike, loss above)
   - Vertical spread: capped gain/loss
   - Butterfly: tent shape with max profit at middle strike
   - Iron condor: flat profit in middle, losses on wings
   - theoretical_pnl approaches expiration_payoff as DTE→0
   - pnl_surface shape is correct
   - Use factories for Position construction
2. **Green**: Implement
3. **Refactor**: Vectorize with numpy where possible

## Notes
- Accept numpy arrays for vectorized computation
- IVs are per-leg (keyed by contract symbol) — different strikes have different IVs
- Use factories from options-7 to construct test positions
