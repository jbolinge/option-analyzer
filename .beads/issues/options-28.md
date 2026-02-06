---
id: options-28
title: "Greeks charts — risk profiles + per-leg breakdown"
type: task
status: closed
priority: 4
created: 2026-02-05
updated: 2026-02-06
closed: 2026-02-06
parent: options-25
depends-on: options-16, options-26
---

# Greeks charts — risk profiles + per-leg breakdown

Implement Greeks visualization functions showing first-order risk profiles.

## Branch
`feature/visualization`

## Files to Create
- `src/options_analyzer/visualization/greeks_charts.py`
- `tests/test_visualization/test_greeks_charts.py`

## Functions

### `plot_greeks_vs_price(price_range: np.ndarray, greeks: dict[str, np.ndarray], title: str = "Greeks vs Price") -> go.Figure`
Subplots: delta, gamma, theta, vega each as a subplot vs underlying price. Uses `make_subplots(rows=2, cols=2)`.

### `plot_greeks_summary(greeks: dict[str, float], title: str = "Position Greeks") -> go.Figure`
Bar chart or table showing current position-level Greeks values.

### `plot_per_leg_greeks(price_range: np.ndarray, per_leg: dict[str, dict[str, np.ndarray]], greek_name: str, title: str | None = None) -> go.Figure`
Overlaid traces showing each leg's contribution to a specific Greek. Useful for understanding which leg drives risk.

## TDD Approach
1. **Red**: Write tests:
   - plot_greeks_vs_price creates figure with 4 subplots
   - Each subplot has correct y-axis label (delta, gamma, theta, vega)
   - Bloomberg theme applied
   - plot_greeks_summary creates valid figure
   - plot_per_leg_greeks has one trace per leg
   - Correct number of traces in each figure
2. **Green**: Implement
3. **Refactor**: Extract subplot layout helper

## Notes
- Use `plotly.subplots.make_subplots` for multi-panel Greeks view
- Use Context7 MCP to check plotly make_subplots API
- Color each Greek trace distinctly using PALETTE
