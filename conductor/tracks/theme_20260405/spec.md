# Specification: Bloomberg CSS Theme System

**Track ID:** theme_20260405
**Type:** Feature
**Created:** 2026-04-05
**Status:** Active

## Summary

Port the Python Bloomberg theme (`theme.py`) to CSS custom properties so the entire React frontend matches the existing Plotly aesthetic.

## Acceptance Criteria

- [ ] CSS custom properties mirror every color from `theme.py` PALETTE
- [ ] Background, grid, border, and typography variables defined
- [ ] FlexLayout dark theme overridden with Bloomberg colors
- [ ] Global reset with Bloomberg body styling
- [ ] TypeScript constants export palette for JS usage
- [ ] Theme test verifies CSS variables are set

## Dependencies

- `src/options_analyzer/visualization/theme.py` (authoritative color source)
- Track 1 (scaffold) complete

## Out of Scope

- Plotly figure theme override from frontend (figures come pre-themed from backend)
- Multiple theme support (Bloomberg only for now)
