---
id: options-33
title: "Notebook 01 — Connect and Explore"
type: task
status: closed
priority: 5
created: 2026-02-05
updated: 2026-02-06
closed: 2026-02-06
parent: options-32
depends-on: options-21, options-22
---

# Notebook 01 — Connect and Explore

Create the first notebook that demonstrates connecting to TastyTrade paper account and exploring available option chains.

## Branch
`feature/notebooks`

## Files to Create
- `notebooks/01_connect_and_explore.ipynb`

## Notebook Cells (in order)

### 1. Setup & Config
- Load config from YAML
- Import options_analyzer modules
- Display config (redacted credentials)

### 2. Connect to TastyTrade
- Create TastyTradeSession with paper config
- Connect and verify authentication
- List available accounts

### 3. Fetch Option Chain
- Choose underlying (e.g., SPY or AAPL)
- Fetch option chain via MarketDataProvider
- Display expirations available

### 4. Explore Chain Data
- Filter to a specific expiration
- Display calls and puts with strikes
- Show current underlying price
- Identify ATM strike

### 5. Display as DataFrame
- Convert option chain to pandas DataFrame for easy viewing
- Show strike, type, bid, ask, IV, delta, etc.

### 6. Cleanup
- Disconnect session

## TDD Approach
Notebooks are not unit-tested in the traditional sense. Instead:
- Verify notebook runs end-to-end without errors (`uv run jupyter execute`)
- Visual inspection of output
- Integration test coverage from options-24 covers the underlying adapter

## Notes
- Use `%load_ext autoreload` and `%autoreload 2` for development
- First cell should have clear instructions for configuring credentials
- Handle connection errors gracefully with clear messages
- This notebook is the "hello world" — keep it simple and welcoming
