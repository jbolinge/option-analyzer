---
id: options-16
title: "PositionAnalyzer — aggregate Greeks, risk profiles"
type: task
status: closed
priority: 2
created: 2026-02-05
updated: 2026-02-05
parent: options-9
depends-on: options-7, options-14, options-15
---

# PositionAnalyzer — aggregate Greeks, risk profiles

Implement the PositionAnalyzer that computes position-level Greeks by aggregating across legs, and generates risk profile data (Greeks vs price/time).

## Branch
`feature/bsm-engine`

## Files to Create
- `src/options_analyzer/engine/position_analyzer.py`
- `tests/test_engine/test_position_analyzer.py`

## Class Design

### PositionAnalyzer
```python
class PositionAnalyzer:
    def __init__(self, greeks_calculator: GreeksCalculator):
        ...

    def position_greeks(
        self, position: Position, spot: float, ivs: dict[str, float]
    ) -> PositionGreeks:
        """Compute per-leg and aggregated Greeks for entire position."""

    def greeks_vs_price(
        self, position: Position, price_range: np.ndarray,
        ivs: dict[str, float]
    ) -> dict[str, np.ndarray]:
        """Greeks profiles: {delta: [...], gamma: [...], ...} across price range."""

    def greeks_vs_time(
        self, position: Position, spot: float, ivs: dict[str, float],
        dte_range: np.ndarray
    ) -> dict[str, np.ndarray]:
        """Greeks decay: {theta: [...], charm: [...], ...} across time range."""

    def greeks_surface(
        self, position: Position, price_range: np.ndarray,
        ivs: dict[str, float], dte_range: np.ndarray
    ) -> dict[str, np.ndarray]:
        """3D surfaces: {delta: 2D array, ...} across price x time."""
```

## Aggregation Logic
For each leg in position:
1. Compute FullGreeks via GreeksCalculator
2. Scale by `leg.signed_quantity * leg.contract.multiplier`
3. Sum across legs for aggregated Greeks

## TDD Approach
1. **Red**: Write tests first:
   - Single long call: position Greeks == leg Greeks * quantity * multiplier
   - Vertical spread: delta partially cancels, gamma partially cancels
   - Butterfly: near-zero delta at center, peak gamma
   - Straddle: near-zero delta ATM, double gamma
   - greeks_vs_price returns correct shape arrays
   - greeks_vs_time returns correct shape arrays
   - greeks_surface returns correct 2D arrays
   - Use factories for Position construction
2. **Green**: Implement
3. **Refactor**: Optimize numpy operations

## Notes
- Depends on GreeksCalculator (options-14) for per-leg computation
- IVs are per-leg (different strikes have different IVs in practice)
- All outputs are numpy arrays for direct use by visualization layer
- Use factories from options-7
