# Specification: FlexLayout Shell + Module Registry

**Track ID:** layout_20260405
**Type:** Feature
**Created:** 2026-04-05
**Status:** Active

## Summary

Build the tiling window manager shell using flexlayout-react with a module registration system that allows views to self-register and be resolved by the tab factory.

## Acceptance Criteria

- [ ] FlexLayout renders with Bloomberg-themed tabsets
- [ ] Module registry supports register/get/getAll operations
- [ ] TabFactory resolves registered modules, shows fallback for unknown
- [ ] Layout persists to localStorage and restores on reload
- [ ] Default layout includes a "Market Conditions" placeholder tab
- [ ] Maximize and pop-out buttons visible on tab headers
- [ ] All tests pass

## Dependencies

- Track 1 (scaffold) complete
- Track 2 (theme) complete — Bloomberg CSS variables needed

## Out of Scope

- Actual market conditions content (Track 5)
- StatusBar component (Track 5)
