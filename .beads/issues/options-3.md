---
id: options-3
title: "CLAUDE.md project context file"
type: task
status: closed
priority: 1
created: 2026-02-05
updated: 2026-02-05
parent: options-1
depends-on: options-2
---

# CLAUDE.md project context file

Create the CLAUDE.md file that gives AI agents full context about the project architecture, conventions, and development workflow.

## Branch
`feature/scaffolding`

## Files to Create
- `CLAUDE.md`

## Content Requirements
- Project overview (options position analyzer with Greeks)
- Technology stack (Python 3.12+, uv, Pydantic v2, plotly, OR-Tools not used here)
- Architecture description (hexagonal: ports & adapters)
- Project structure (full directory tree)
- Key concepts (OptionContract, Leg, Position, Greeks, BSM)
- Development workflow (TDD, beads tracking, feature branches)
- Running commands (pytest, mypy, ruff, jupyter)
- Configuration details
- Testing strategy (known values, finite-difference, hypothesis)

## TDD
No tests — this is documentation. Commit directly.
