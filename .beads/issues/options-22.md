---
id: options-22
title: "TastyTrade account provider"
type: task
status: open
priority: 3
created: 2026-02-05
updated: 2026-02-05
parent: options-17
depends-on: options-20
---

# TastyTrade account provider

Implement the TastyTradeAccountProvider that implements the AccountProvider port.

## Branch
`feature/data-layer`

## Files to Create
- `src/options_analyzer/adapters/tastytrade/account.py`
- `tests/test_adapters/test_account.py`

## Class Design

### TastyTradeAccountProvider(AccountProvider)
```python
class TastyTradeAccountProvider(AccountProvider):
    def __init__(self, session: TastyTradeSession):
        ...

    async def get_accounts(self) -> list[str]:
        """List account numbers."""

    async def get_positions(
        self, account_id: str, underlying: str | None = None
    ) -> list[Leg]:
        """Get current positions, optionally filtered by underlying."""
```

## TDD Approach
1. **Red**: Write unit tests with mocked session:
   - get_accounts returns list of account ID strings
   - get_positions returns list of Leg domain objects
   - Filtering by underlying works
   - Empty positions returns empty list
   - Error handling for invalid account_id
2. **Green**: Implement using tastytrade SDK + mapping layer
3. **Refactor**: Clean up

## Notes
- Use Context7 MCP to check `tastytrade` SDK API for account/position retrieval
- Delegates type conversion to mapping.py
- Unit tests mock the SDK
