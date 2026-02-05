---
id: options-29
title: "Decay charts — theta, charm, veta over time"
type: task
status: open
priority: 4
created: 2026-02-05
updated: 2026-02-05
parent: options-25
depends-on: options-16, options-26
---

# Decay charts — theta, charm, veta over time

Implement time decay visualization showing how Greeks evolve as expiration approaches.

## Branch
`feature/visualization`

## Files to Create
- `src/options_analyzer/visualization/decay_charts.py`
- `tests/test_visualization/test_decay_charts.py`

## Functions

### `plot_theta_decay(dte_range: np.ndarray, theta: np.ndarray, title: str = "Theta Decay") -> go.Figure`
Theta vs DTE — shows the acceleration of time decay near expiration.

### `plot_decay_profiles(dte_range: np.ndarray, greeks: dict[str, np.ndarray], title: str = "Time Decay Profiles") -> go.Figure`
Multiple time-dependent Greeks (theta, charm, veta) overlaid on same chart or subplots.

## TDD Approach
1. **Red**: Write tests:
   - plot_theta_decay returns go.Figure with one trace
   - X-axis is "Days to Expiration" (reversed — high DTE on left)
   - Bloomberg theme applied
   - plot_decay_profiles has one trace per Greek
   - Correct trace names
2. **Green**: Implement
3. **Refactor**: Clean up

## Notes
- DTE axis should be reversed (countdown to expiration: 60, 45, 30, 15, 0)
- Theta decay accelerates near expiration — chart should clearly show this
- Use PALETTE colors for each Greek trace
