---
id: options-35
title: "Notebook 03 — Greeks Dashboard (Live Streaming)"
type: task
status: open
priority: 5
created: 2026-02-05
updated: 2026-02-05
parent: options-32
depends-on: options-23, options-28, options-29
---

# Notebook 03 — Greeks Dashboard (Live Streaming)

Create a real-time Greeks dashboard notebook that streams live data from TastyTrade and updates visualizations.

## Branch
`feature/notebooks`

## Files to Create
- `notebooks/03_greeks_dashboard.ipynb`

## Notebook Cells (in order)

### 1. Setup
- Load config, connect to TastyTrade
- Import streaming, engine, visualization modules

### 2. Select Position
- Fetch current positions from account
- Or manually construct a position
- Display position summary

### 3. Initialize Dashboard
- Create initial Greeks charts with static data
- Display using `ipywidgets` for updateable output

### 4. Stream Live Greeks
- Connect DXLink streamer
- Subscribe to Greeks for position's contracts
- Update first-order Greeks from stream
- Compute second-order Greeks via BSM engine
- Update visualization on each tick

### 5. Time Decay View
- Show theta, charm, veta decay profiles
- Compare current Greeks to projected values at future DTEs

### 6. Greeks Summary Table
- Live-updating table of all Greeks (first + second order)
- Per-leg and aggregated

### 7. Cleanup
- Stop streaming
- Disconnect session

## TDD Approach
- Verify streaming connects and receives data
- Visual inspection of live updates
- Integration coverage from options-24

## Notes
- Use `ipywidgets.Output` for in-place chart updates
- Use `asyncio` event loop integration in Jupyter
- Time-box streaming demos (e.g., stream for 30 seconds)
- Handle stream disconnections gracefully
- This is the most technically complex notebook
