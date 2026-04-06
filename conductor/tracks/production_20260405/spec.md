# Specification: SPA Serving + Production Polish

**Track ID:** production_20260405
**Type:** Feature
**Created:** 2026-04-05
**Status:** Active

## Summary

Configure FastAPI to serve the built SPA, add build/dev scripts, implement pop-out window support, and polish layout persistence.

## Acceptance Criteria

- [ ] `uv run uvicorn options_analyzer.api.app:app` serves both API and SPA
- [ ] API routes under /api take priority over SPA catch-all
- [ ] Client-side routing works (catch-all returns index.html)
- [ ] Makefile with dev, build, and serve targets
- [ ] Pop-out windows render the correct module
- [ ] Layout reset button works
- [ ] Integration tests pass

## Dependencies

- Track 5 (dashboard) — Frontend rendering complete

## Out of Scope

- Docker containerization
- Authentication
- CI/CD pipeline
