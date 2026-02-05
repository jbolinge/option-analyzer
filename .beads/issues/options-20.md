---
id: options-20
title: "TastyTrade mapping layer — SDK ↔ domain models"
type: task
status: open
priority: 3
created: 2026-02-05
updated: 2026-02-05
parent: options-17
depends-on: options-19
---

# TastyTrade mapping layer — SDK ↔ domain models

Implement the mapping layer that converts TastyTrade SDK objects to/from domain models. This is the ONLY file in the entire codebase that imports tastytrade SDK types (aside from session.py).

## Branch
`feature/data-layer`

## Files to Create
- `src/options_analyzer/adapters/tastytrade/mapping.py`
- `tests/test_adapters/test_mapping.py`

## Functions to Implement

### `map_option_to_contract(option: TastyTrade Option type) -> OptionContract`
Maps SDK option instrument to domain OptionContract.

### `map_position_to_leg(position: TastyTrade Position type) -> Leg`
Maps SDK position to domain Leg (with side, quantity, open price).

### `map_greeks_to_first_order(greeks: TastyTrade Greeks type) -> FirstOrderGreeks`
Maps SDK streaming Greeks to domain FirstOrderGreeks.

## TDD Approach
1. **Red**: Write tests:
   - Create mock/stub SDK objects with known field values
   - Verify mapping produces correct domain model fields
   - Test call vs put mapping
   - Test long vs short position mapping
   - Test quantity and price extraction
   - Test streamer_symbol passthrough
   - Test edge cases: missing fields, None values
2. **Green**: Implement mapping functions
3. **Refactor**: Clean up

## Notes
- Use Context7 MCP to check `tastytrade` SDK model types and field names
- This file is the adapter's "anti-corruption layer"
- All tastytrade SDK type imports are isolated here
- Mapping functions are pure — take SDK object, return domain model
- If SDK types are hard to construct in tests, use `unittest.mock.MagicMock` with spec
