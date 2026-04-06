# Product Guidelines

## Voice and Tone

Concise and direct — Bloomberg terminal style, dense information display. Use precise financial terminology. Labels and UI text should be terse and information-rich. No fluff.

## Design Principles

1. **Hexagonal Architecture** — Domain logic is pure and isolated. Adapters implement ports. Presentation layers (notebooks, web app) consume engine + visualization. Nothing depends on a specific data provider.
2. **TDD Discipline** — Tests first (red), implementation (green), refactor. Property-based testing for mathematical invariants. Integration tests gated behind markers.
3. **Separation of Concerns** — Domain models, engine computation, visualization, adapters, and presentation are strictly layered. No cross-layer imports.
4. **DRY** — Reuse existing functions and patterns. The Bloomberg theme is authoritative in `theme.py` and mirrored (not duplicated) in CSS. Engine compute functions are called by both notebooks and API.

## Visual Standards

- Bloomberg dark theme: black paper (#000000), dark navy plot (#1a1a2e), orange primary (#ff6600)
- Monospace typography throughout
- Information density over whitespace
- Right-side Y-axes on all financial charts
