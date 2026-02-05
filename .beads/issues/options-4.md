---
id: options-4
title: "Domain enums — OptionType, PositionSide, ExerciseStyle"
type: task
status: open
priority: 1
created: 2026-02-05
updated: 2026-02-05
parent: options-1
depends-on: options-2
---

# Domain enums — OptionType, PositionSide, ExerciseStyle

Create the core domain enums used throughout the application.

## Branch
`feature/domain-models`

## Files to Create
- `src/options_analyzer/domain/__init__.py`
- `src/options_analyzer/domain/enums.py`
- `tests/test_domain/__init__.py`
- `tests/test_domain/test_enums.py`

## Enums

### OptionType (str, Enum)
- `CALL = "call"`
- `PUT = "put"`

### PositionSide (str, Enum)
- `LONG = "long"`
- `SHORT = "short"`

### ExerciseStyle (str, Enum)
- `AMERICAN = "american"`
- `EUROPEAN = "european"`

## TDD Approach
1. **Red**: Write tests first:
   - Each enum has correct members
   - String values are lowercase
   - Enums are iterable
   - Invalid values raise ValueError
2. **Green**: Implement enums to pass tests
3. **Refactor**: Clean up if needed

## Notes
- Use `(str, Enum)` pattern for JSON serialization compatibility
- Keep it simple — these are just enums
