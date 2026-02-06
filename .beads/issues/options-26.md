---
id: options-26
title: "Bloomberg dark theme — template + apply_theme()"
type: task
status: closed
priority: 4
created: 2026-02-05
updated: 2026-02-06
closed: 2026-02-06
parent: options-25
depends-on: options-2
---

# Bloomberg dark theme — template + apply_theme()

Create the Bloomberg terminal-inspired dark theme for all plotly charts.

## Branch
`feature/visualization`

## Files to Create
- `src/options_analyzer/visualization/__init__.py`
- `src/options_analyzer/visualization/theme.py`
- `tests/test_visualization/__init__.py`
- `tests/test_visualization/test_theme.py`

## Theme Specification

### Colors
- `paper_bgcolor`: "#000000" (black)
- `plot_bgcolor`: "#1a1a2e" (dark navy)
- `grid_color`: "#2d2d44" (subtle grid)
- `text_color`: "#e0e0e0" (light gray)

### Color Palette (for traces)
- Primary: "#ff6600" (Bloomberg orange)
- Secondary: "#00cccc" (cyan)
- Tertiary: "#cc00cc" (magenta)
- Positive: "#00cc66" (green)
- Negative: "#cc3333" (red)
- Neutral: "#888888" (gray)

### Font
- Family: "Consolas, Monaco, 'Courier New', monospace"
- Size: 12 (default), 14 (axis titles), 16 (chart title)

### Layout
- Subtle grid lines (gridwidth=1, gridcolor=grid_color)
- No background grid pattern
- Clean axis labels

## Implementation

### `BLOOMBERG_TEMPLATE` — plotly template object
A `plotly.graph_objects.layout.Template` with all theme settings.

### `apply_theme(fig: go.Figure) -> go.Figure`
Applies the Bloomberg theme to any figure. Returns the figure for chaining.

### `PALETTE` — named color constants
Dict or dataclass with named colors for consistent use.

## TDD Approach
1. **Red**: Write tests:
   - BLOOMBERG_TEMPLATE has correct paper_bgcolor, plot_bgcolor
   - apply_theme sets the template on a figure
   - PALETTE has expected color keys
   - Font family is monospace
   - Theme can be applied to an empty figure without error
2. **Green**: Implement theme
3. **Refactor**: Clean up

## Notes
- Use Context7 MCP to check plotly Template API for proper theme registration
- Theme should be registerable as a plotly default: `pio.templates["bloomberg"] = BLOOMBERG_TEMPLATE`
- Keep chart functions and theme separate — theme is applied, not baked into chart logic
