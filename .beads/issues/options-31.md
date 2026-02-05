---
id: options-31
title: "3D surface charts — Greeks vs price x vol/time"
type: task
status: open
priority: 4
created: 2026-02-05
updated: 2026-02-05
parent: options-25
depends-on: options-16, options-26
---

# 3D surface charts — Greeks vs price x vol/time

Implement 3D surface plots for visualizing Greeks across two dimensions simultaneously.

## Branch
`feature/visualization`

## Files to Create
- `src/options_analyzer/visualization/surface_charts.py`
- `tests/test_visualization/test_surface_charts.py`

## Functions

### `plot_greek_surface(x_range: np.ndarray, y_range: np.ndarray, z_surface: np.ndarray, x_label: str, y_label: str, z_label: str, title: str = "Greek Surface") -> go.Figure`
Generic 3D surface for any Greek. Reusable for different combinations.

### `plot_delta_surface(price_range: np.ndarray, vol_range: np.ndarray, delta_surface: np.ndarray, title: str = "Delta Surface") -> go.Figure`
Delta vs price x vol — shows how delta changes across price and implied vol.

### `plot_gamma_surface(price_range: np.ndarray, dte_range: np.ndarray, gamma_surface: np.ndarray, title: str = "Gamma Surface") -> go.Figure`
Gamma vs price x time — shows gamma concentration near ATM at expiration.

## TDD Approach
1. **Red**: Write tests:
   - Each function returns go.Figure with Surface trace
   - Correct axis labels on all 3 axes
   - Bloomberg theme applied (dark background for 3D)
   - Surface data shape matches inputs
   - Generic function works with arbitrary labels
2. **Green**: Implement
3. **Refactor**: Factor common 3D setup into helper

## Notes
- Use `go.Surface` for 3D plots
- Plotly 3D surfaces are interactive by default (rotate, zoom)
- Bloomberg theme on 3D needs scene bgcolor settings
- Use Context7 MCP to check plotly 3D surface API for scene configuration
- Colorscale: use a custom dark-compatible colorscale (e.g., "Plasma" or custom)
