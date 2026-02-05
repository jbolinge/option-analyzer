---
id: options-19
title: "TastyTrade session management"
type: task
status: open
priority: 3
created: 2026-02-05
updated: 2026-02-05
parent: options-17
depends-on: options-8, options-18
---

# TastyTrade session management

Implement session lifecycle management for the TastyTrade API. Handles authentication, paper vs live switching, and session cleanup.

## Branch
`feature/data-layer`

## Files to Create
- `src/options_analyzer/adapters/__init__.py`
- `src/options_analyzer/adapters/tastytrade/__init__.py`
- `src/options_analyzer/adapters/tastytrade/session.py`
- `tests/test_adapters/__init__.py`
- `tests/test_adapters/test_session.py`

## Class Design

### TastyTradeSession
```python
class TastyTradeSession:
    def __init__(self, config: ProviderConfig):
        self._config = config
        self._session: Session | None = None

    async def connect(self) -> None:
        """Authenticate and create session. Uses is_test flag for paper."""

    async def disconnect(self) -> None:
        """Close session cleanly."""

    @property
    def session(self) -> Session:
        """Access underlying tastytrade Session. Raises if not connected."""

    async def __aenter__(self) -> "TastyTradeSession": ...
    async def __aexit__(self, *args) -> None: ...
```

## TDD Approach
1. **Red**: Write tests:
   - Constructor stores config
   - session property raises RuntimeError if not connected
   - Paper mode passes `is_test=True` to tastytrade Session
   - Live mode passes `is_test=False`
   - Context manager protocol works
   - Use unittest.mock to mock tastytrade.Session (no real network calls in unit tests)
2. **Green**: Implement
3. **Refactor**: Clean up

## Notes
- Use Context7 MCP to verify `tastytrade` SDK Session constructor API (especially `is_test` flag)
- Paper trading URL vs production URL is handled by the SDK's `is_test` parameter
- ProviderConfig.password is SecretStr — use `.get_secret_value()` when passing to SDK
- This file imports `tastytrade.Session` — it's inside the adapter boundary, which is OK
