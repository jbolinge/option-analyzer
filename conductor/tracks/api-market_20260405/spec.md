# Specification: Backend Market Conditions API

**Track ID:** api-market_20260405
**Type:** Feature
**Created:** 2026-04-05
**Status:** Active

## Summary

FastAPI endpoint that computes all market condition indicators and returns Plotly figure JSON, reusing existing engine and visualization code with zero rewrite.

## Acceptance Criteria

- [ ] `GET /api/market-conditions/dashboard` returns valid Plotly figure JSON
- [ ] Service orchestrates: fetch candles → compute indicators → plot_full_grid → serialize
- [ ] Provider dependency injection via FastAPI lifespan
- [ ] Individual panel endpoint: `GET /api/market-conditions/panels/{name}`
- [ ] Response includes `figure`, `computed_at`, and `symbol` fields
- [ ] Tests pass with mocked MarketDataProvider (no real API calls)
- [ ] ApiConfig added to schema.py

## Dependencies

- Existing engine: compute_ema_cloud, compute_dstfs, compute_atr_bollinger, compute_obv_bollinger, compute_ivts, compute_force_index_dual, compute_mc_warnings, compute_borg_transwarp_series
- Existing visualization: plot_full_grid, individual plot_* functions
- Existing factory: create_providers, ProviderContext
- Track 1 (scaffold) complete

## Out of Scope

- Frontend rendering (Track 5)
- Real-time WebSocket streaming
- Authentication
