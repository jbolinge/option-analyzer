# Implementation Plan: Backend Market Conditions API

**Track ID:** api-market_20260405
**Spec:** [spec.md](./spec.md)
**Created:** 2026-04-05
**Status:** [ ] Not Started

## Phase 1: Config + Dependencies

### Tasks

- [ ] Task 1.1: Add ApiConfig to config/schema.py
- [ ] Task 1.2: Create dependencies.py with lifespan + get_providers()
- [ ] Task 1.3: Update app.py to use lifespan context manager

### Verification

- [ ] Existing health tests still pass

## Phase 2: Market Conditions Service + Router

### Tasks

- [ ] Task 2.1: Write test for dashboard endpoint (RED)
- [ ] Task 2.2: Create services/market_conditions.py (orchestration logic)
- [ ] Task 2.3: Create routers/market_conditions.py (endpoints)
- [ ] Task 2.4: Wire router into app.py
- [ ] Task 2.5: Create test fixtures with mock MarketDataProvider + CandleSeries
- [ ] Task 2.6: Verify dashboard endpoint test passes (GREEN)
- [ ] Task 2.7: Write and verify individual panel endpoint tests

### Verification

- [ ] `uv run pytest tests/test_api/` — all pass
- [ ] `curl /api/market-conditions/dashboard` returns valid Plotly JSON
- [ ] All 824+ existing tests still pass
