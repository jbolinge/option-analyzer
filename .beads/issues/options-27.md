---
id: options-27
title: "Payoff charts — P&L diagrams + 3D surface"
type: task
status: closed
priority: 4
created: 2026-02-05
updated: 2026-02-06
closed: 2026-02-06
parent: options-25
depends-on: options-15, options-26
---

# Payoff charts — P&L diagrams + 3D surface

Implement payoff/P&L visualization functions.

## Branch
`feature/visualization`

## Files to Create
- `src/options_analyzer/visualization/payoff_charts.py`
- `tests/test_visualization/test_payoff_charts.py`

## Functions

### `plot_expiration_payoff(price_range: np.ndarray, payoff: np.ndarray, breakevens: list[float] | None = None, title: str = "P&L at Expiration") -> go.Figure`
Classic hockey-stick P&L diagram. Optional breakeven markers.

### `plot_theoretical_pnl(price_range: np.ndarray, pnl_by_dte: dict[str, np.ndarray], title: str = "Theoretical P&L") -> go.Figure`
Multiple P&L curves at different DTEs overlaid. Keys are DTE labels (e.g., "30 DTE", "15 DTE", "0 DTE").

### `plot_pnl_surface(price_range: np.ndarray, dte_range: np.ndarray, surface: np.ndarray, title: str = "P&L Surface") -> go.Figure`
3D surface plot: price x time x P&L. Uses `go.Surface`.

## TDD Approach
1. **Red**: Write tests:
   - plot_expiration_payoff returns go.Figure with correct trace count
   - Figure has correct axis labels ("Underlying Price", "P&L ($)")
   - Bloomberg theme is applied
   - Breakeven markers appear when provided
   - plot_theoretical_pnl has one trace per DTE
   - plot_pnl_surface creates a Surface trace
   - 3D plot has correct axis labels
   - All figures have non-empty data
2. **Green**: Implement chart functions
3. **Refactor**: Extract common figure setup

## Notes
- Accept pre-computed arrays — no computation in chart functions
- Apply theme via `apply_theme()` from theme.py
- Use PALETTE colors for traces
- Zero-line on P&L axis for reference (horizontal dashed line at y=0)
