# TypeScript Style Guide

## Tool Configuration

- **Linter**: ESLint with TypeScript parser (to be configured in `frontend/.eslintrc`)
- **Formatter**: Prettier (to be configured in `frontend/.prettierrc`)
- **Type Checker**: TypeScript strict mode (`tsconfig.json`)
- **Build**: Vite with React plugin

## Language Version

TypeScript 5.x with strict mode enabled.

## Module Style

- ES modules (`import`/`export`) exclusively
- Named exports preferred over default exports (except for React components)
- Barrel exports via `index.ts` for module public APIs

## Type Conventions

- Use `interface` for object shapes, `type` for unions and intersections
- No `any` — use `unknown` when type is truly unknown
- Prefer explicit return types on exported functions
- Use `readonly` for immutable data structures

## React Patterns

- Functional components only (no class components)
- `React.FC` not required — use plain function with typed props
- Custom hooks prefixed with `use` (e.g., `useMarketConditions`)
- Lazy loading for module components via `React.lazy()`

## File Organization

```
ComponentName/
  ComponentName.tsx       # Component implementation
  ComponentName.module.css # Scoped styles (CSS Modules)
  index.ts                # Re-export
```

Or flat files for simple components:

```
components/
  PlotlyChart.tsx
  RefreshButton.tsx
```

## Naming

- PascalCase for components and types/interfaces
- camelCase for functions, variables, hooks
- UPPER_SNAKE for constants
- kebab-case for CSS class names and file directories

## CSS

- CSS Modules for component-scoped styles
- CSS custom properties (`--bb-*`) for theme values
- No inline styles except for dynamic Plotly dimensions
- No Tailwind — use Bloomberg theme variables directly

## Testing

- Test files colocated or in `__tests__/` mirroring source structure
- Use `describe` / `it` pattern
- Mock external dependencies (react-plotly.js, fetch)
- Use `@testing-library/react` for component tests
- Use `vi.mock()` for module mocking in Vitest

## State Management

- TanStack Query for all server state (API data)
- Zustand for UI-only state (layout, preferences)
- No prop drilling beyond 2 levels — use context or store
