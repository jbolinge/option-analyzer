# Implementation Plan: Bloomberg CSS Theme System

**Track ID:** theme_20260405
**Spec:** [spec.md](./spec.md)
**Created:** 2026-04-05
**Status:** [ ] Not Started

## Phase 1: CSS Theme + FlexLayout Overrides

### Tasks

- [ ] Task 1.1: Create bloomberg.css with CSS custom properties from theme.py
- [ ] Task 1.2: Create global.css with body reset and base styles
- [ ] Task 1.3: Create flexlayout-overrides.css for Bloomberg dark theme
- [ ] Task 1.4: Create theme/index.ts with TypeScript palette constants
- [ ] Task 1.5: Import theme CSS in App.tsx
- [ ] Task 1.6: Write theme test verifying CSS variables
- [ ] Task 1.7: Verify frontend builds and all tests pass

### Verification

- [ ] `cd frontend && npm test` — all pass
- [ ] `cd frontend && npm run build` — succeeds
- [ ] Visual: body background is black, text is light gray monospace
