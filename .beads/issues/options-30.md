---
id: options-30
title: "Vol charts — vanna, volga profiles"
type: task
status: open
priority: 4
created: 2026-02-05
updated: 2026-02-05
parent: options-25
depends-on: options-16, options-26
---

# Vol charts — vanna, volga profiles

Implement volatility sensitivity charts showing second-order vol Greeks.

## Branch
`feature/visualization`

## Files to Create
- `src/options_analyzer/visualization/vol_charts.py`
- `tests/test_visualization/test_vol_charts.py`

## Functions

### `plot_vanna_profile(price_range: np.ndarray, vanna: np.ndarray, title: str = "Vanna Profile") -> go.Figure`
Vanna vs underlying price — shows where delta is most sensitive to IV changes.

### `plot_volga_profile(price_range: np.ndarray, volga: np.ndarray, title: str = "Volga Profile") -> go.Figure`
Volga vs underlying price — shows where vega is most sensitive to IV changes.

### `plot_vol_sensitivity(price_range: np.ndarray, greeks: dict[str, np.ndarray], title: str = "Vol Sensitivity") -> go.Figure`
Combined vanna + volga subplots.

## TDD Approach
1. **Red**: Write tests:
   - Each function returns go.Figure
   - Correct axis labels
   - Bloomberg theme applied
   - plot_vol_sensitivity has 2 subplots
   - Correct trace count
2. **Green**: Implement
3. **Refactor**: Clean up

## Notes
- Vanna and volga are the most important second-order Greeks for vol traders
- These profiles help identify where a position is most exposed to vol changes
- Use PALETTE colors
