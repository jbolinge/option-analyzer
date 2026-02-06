---
id: options-34
title: "Notebook 02 — Position Analysis (BWB)"
type: task
status: closed
priority: 5
created: 2026-02-05
updated: 2026-02-06
closed: 2026-02-06
parent: options-32
depends-on: options-27, options-28
---

# Notebook 02 — Position Analysis (BWB)

Create the position analysis notebook. Builds a Broken Wing Butterfly (or other multi-leg strategy), computes P&L and Greeks, and visualizes with Bloomberg theme.

## Branch
`feature/notebooks`

## Files to Create
- `notebooks/02_position_analysis.ipynb`

## Notebook Cells (in order)

### 1. Setup
- Load config, connect to TastyTrade (paper)
- Import engine and visualization modules

### 2. Build a BWB Position
- Fetch option chain for a liquid underlying
- Select strikes for a BWB (e.g., AAPL 150/160/175 put BWB)
- Construct Position with 3 legs using domain models
- Display position summary

### 3. Expiration P&L
- Compute payoff curve via PayoffCalculator
- Plot hockey-stick diagram via payoff_charts
- Identify max profit, max loss, breakevens

### 4. Theoretical P&L at Multiple DTEs
- Compute theoretical P&L at 30, 15, 7, 0 DTE
- Plot overlaid P&L curves
- Show how position converges to expiration payoff

### 5. Greeks Analysis
- Compute position Greeks via PositionAnalyzer
- Display current Greeks (delta, gamma, theta, vega)
- Plot Greeks vs price profiles (4-panel subplot)

### 6. Second-Order Greeks
- Compute vanna, volga, charm profiles
- Plot vol sensitivity charts
- Explain what each second-order Greek means for the position

### 7. Per-Leg Breakdown
- Show each leg's contribution to position Greeks
- Plot per-leg delta and gamma vs price

### 8. 3D P&L Surface
- Compute P&L surface (price x time)
- Plot interactive 3D surface

### 9. Cleanup
- Disconnect session

## TDD Approach
- Visual verification: BWB should show tent-shaped payoff
- Greeks should be near-zero delta at center, negative gamma overall
- P&L surface should show convergence to expiration payoff

## Notes
- This is the flagship notebook — should be visually impressive
- All charts use Bloomberg theme
- Include markdown cells explaining each analysis step
- BWB is a good demo strategy: multi-leg, interesting Greeks, common in practice
