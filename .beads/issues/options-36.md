---
id: options-36
title: "Notebook 04 — Vol Surfaces"
type: task
status: closed
priority: 5
created: 2026-02-05
updated: 2026-02-06
closed: 2026-02-06
parent: options-32
depends-on: options-30, options-31
---

# Notebook 04 — Vol Surfaces

Create the volatility surface and 3D Greek surface notebook for advanced vol analysis.

## Branch
`feature/notebooks`

## Files to Create
- `notebooks/04_vol_surfaces.ipynb`

## Notebook Cells (in order)

### 1. Setup
- Load config, connect to TastyTrade
- Import engine and visualization modules

### 2. Fetch IV Data
- Get option chain with IVs across multiple expirations
- Build IV surface data: strike x expiration x IV

### 3. Implied Vol Surface
- Plot 3D IV surface (strike x time x IV)
- Show vol smile/skew across strikes
- Show term structure across expirations

### 4. Select a Position
- Build or fetch a multi-leg position

### 5. Delta Surface
- Compute delta across price x vol grid
- Plot 3D delta surface
- Identify regions of high delta sensitivity

### 6. Gamma Surface
- Compute gamma across price x time grid
- Plot 3D gamma surface
- Show gamma concentration near ATM at expiration

### 7. Vanna/Volga Analysis
- Compute vanna and volga across price range
- Plot vol sensitivity profiles
- Explain implications for the position

### 8. Vol Scenario Analysis
- Compute P&L under different vol scenarios (vol up 5%, down 5%, unchanged)
- Plot overlaid P&L curves for each scenario
- Show which scenario is worst for the position

### 9. Cleanup
- Disconnect session

## TDD Approach
- Visual inspection of surface shapes
- IV surface should show smile/skew pattern
- Delta surface should show smooth transition
- Gamma surface should peak near ATM near expiration

## Notes
- This is the most analytically advanced notebook
- 3D surfaces should be interactive (rotate, zoom)
- Include markdown explanations of what each surface reveals
- Vol scenario analysis is particularly useful for risk management
