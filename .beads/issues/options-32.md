---
id: options-32
title: "Jupyter Notebooks"
type: epic
status: closed
priority: 5
created: 2026-02-05
updated: 2026-02-06
closed: 2026-02-06
depends-on: options-25, options-17
---

# Jupyter Notebooks

End-to-end workflow notebooks that demonstrate the full system: connecting to TastyTrade, building positions, analyzing Greeks, and visualizing with the Bloomberg theme. These are both the primary user interface and living documentation.

## Scope
- 01_connect_and_explore.ipynb — Connect to TastyTrade paper, browse option chains
- 02_position_analysis.ipynb — Build a BWB, analyze P&L and Greeks
- 03_greeks_dashboard.ipynb — Stream live Greeks, real-time updating views
- 04_vol_surfaces.ipynb — 3D surfaces and vol sensitivity analysis

## Acceptance Criteria
- [ ] All notebooks run end-to-end with paper account
- [ ] Charts display with Bloomberg dark theme
- [ ] Second-order Greeks computed and visualized
- [ ] Live streaming works in notebook 03
- [ ] 3D surfaces are interactive in notebook 04
