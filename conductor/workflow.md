# Workflow

## TDD Policy

**Strict** — Tests are required before implementation.

1. Write failing test (red)
2. Write minimal implementation to pass (green)
3. Refactor with confidence (refactor)

Backend: pytest + hypothesis for property-based tests. Frontend: Vitest + React Testing Library.

## Commit Strategy

**Conventional Commits** format:

- `feat:` — New feature
- `fix:` — Bug fix
- `chore:` — Tooling, config, dependencies
- `test:` — Test additions or modifications
- `refactor:` — Code restructuring without behavior change
- `docs:` — Documentation updates

Small, focused commits. Each commit should be atomic and self-contained.

## Code Review Policy

**Optional / self-review** — Single developer project. Self-review diffs before committing.

## Verification Checkpoints

**After each phase completion** — Run full test suite and verify functionality before proceeding to the next phase.

Backend verification: `uv run pytest -m "not integration"`
Frontend verification: `cd frontend && npm test`

## Task Lifecycle

1. **Specification** — Define what needs to be built (track spec)
2. **Planning** — Break into phased implementation plan
3. **Implementation** — TDD per task within each phase
4. **Verification** — Run tests, manual check at phase boundaries
5. **Completion** — All phases done, track archived

## Branch Strategy

- `main` — Stable, production-ready
- `feature/<track-name>` — Feature branches for active tracks
- Frequent commits on feature branches
- Merge to main when track complete
