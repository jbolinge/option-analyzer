---
id: options-25
title: "Visualization — Bloomberg Theme"
type: epic
status: closed
priority: 4
created: 2026-02-05
updated: 2026-02-06
closed: 2026-02-06
depends-on: options-9
---

# Visualization — Bloomberg Theme

Chart layer with Bloomberg terminal aesthetic. All chart functions return `plotly.graph_objects.Figure` objects — works in both Jupyter and future Dash web app. Chart functions accept pre-computed numpy arrays and do NO data fetching.

## Scope
- Bloomberg dark theme (black bg, orange/cyan accents, monospace font)
- Payoff charts (P&L at expiration, theoretical P&L at DTEs, 3D P&L surface)
- Greeks charts (delta/gamma/theta/vega vs price, per-leg breakdown)
- Decay charts (theta/charm/veta over time)
- Vol charts (vanna/volga profiles)
- 3D surface charts (Greeks vs price x vol/time)

## Design Principles
- All chart functions return `plotly.graph_objects.Figure`
- Accept pre-computed numpy arrays — NO I/O inside chart functions
- Pure visualization — no data fetching, no computation
- Theme is applied via a reusable template

## Acceptance Criteria
- [ ] Bloomberg theme applied consistently across all charts
- [ ] Charts render correctly in Jupyter notebooks
- [ ] Each chart function has unit tests verifying figure structure
- [ ] Charts handle multi-leg positions with per-leg breakdown
- [ ] 3D surfaces are interactive (plotly built-in)
