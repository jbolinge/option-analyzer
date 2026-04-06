# Specification: Frontend Market Conditions Dashboard

**Track ID:** dashboard_20260405
**Type:** Feature
**Created:** 2026-04-05
**Status:** Active

## Summary

Connect the frontend to the backend market conditions API, rendering the 5-panel Plotly dashboard with manual refresh capability.

## Acceptance Criteria

- [ ] PlotlyChart component renders Plotly figures from backend JSON
- [ ] Market Conditions view fetches /api/market-conditions/dashboard via TanStack Query
- [ ] Refresh button triggers manual refetch with loading indicator
- [ ] Error state shows with retry button on fetch failure
- [ ] Last-updated timestamp displayed
- [ ] Charts auto-resize when FlexLayout panels resize
- [ ] All frontend tests pass, build succeeds

## Dependencies

- Track 2 (theme) — Bloomberg CSS variables
- Track 3 (layout) — FlexLayout shell + module registry
- Track 4 (api-market) — Backend dashboard endpoint

## Out of Scope

- SPA static file serving (Track 6)
- Pop-out window rendering (Track 6)
- Real-time WebSocket streaming
