# Implementation Plan: FlexLayout Shell + Module Registry

**Track ID:** layout_20260405
**Spec:** [spec.md](./spec.md)
**Created:** 2026-04-05
**Status:** [ ] Not Started

## Phase 1: Module Registry

### Tasks

- [ ] Task 1.1: Create modules/types.ts with ModuleDefinition interface
- [ ] Task 1.2: Create modules/registry.ts with ModuleRegistry class
- [ ] Task 1.3: Write registry tests (register, get, getAll, unknown key)

### Verification

- [ ] Registry tests pass

## Phase 2: Layout Shell

### Tasks

- [ ] Task 2.1: Create layout/layoutModel.ts with default JSON model
- [ ] Task 2.2: Create layout/TabFactory.tsx resolving modules via registry
- [ ] Task 2.3: Create layout/LayoutShell.tsx with FlexLayout + localStorage persistence
- [ ] Task 2.4: Update App.tsx to render LayoutShell with QueryClientProvider
- [ ] Task 2.5: Write layout tests (model creation, TabFactory lookup, persistence)
- [ ] Task 2.6: Verify build succeeds and all tests pass

### Verification

- [ ] `cd frontend && npm test` — all pass
- [ ] `cd frontend && npm run build` — succeeds
- [ ] FlexLayout renders with Bloomberg dark theme
