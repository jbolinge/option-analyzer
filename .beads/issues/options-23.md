---
id: options-23
title: "TastyTrade DXLink streaming wrapper"
type: task
status: closed
priority: 3
created: 2026-02-05
updated: 2026-02-05
parent: options-17
depends-on: options-21
---

# TastyTrade DXLink streaming wrapper

Implement the DXLink streamer wrapper for real-time Greeks and quote streaming from TastyTrade.

## Branch
`feature/data-layer`

## Files to Create
- `src/options_analyzer/adapters/tastytrade/streaming.py`
- `tests/test_adapters/test_streaming.py`

## Class Design

### DXLinkStreamer
```python
class DXLinkStreamer:
    def __init__(self, session: TastyTradeSession):
        ...

    async def connect(self) -> None:
        """Initialize DXLink streamer connection."""

    async def disconnect(self) -> None:
        """Close streamer."""

    async def subscribe_greeks(
        self, streamer_symbols: list[str]
    ) -> AsyncIterator[tuple[str, FirstOrderGreeks]]:
        """Subscribe to Greeks stream for given symbols."""

    async def subscribe_quotes(
        self, symbols: list[str]
    ) -> AsyncIterator[tuple[str, Decimal, Decimal]]:
        """Subscribe to bid/ask quote stream."""
```

## TDD Approach
1. **Red**: Write unit tests with mocked DXLink:
   - Connection lifecycle (connect/disconnect)
   - subscribe_greeks yields (symbol, FirstOrderGreeks) tuples
   - subscribe_quotes yields (symbol, bid, ask) tuples
   - Handles disconnection gracefully
   - Handles subscription to empty list
2. **Green**: Implement using tastytrade SDK DXLink API
3. **Refactor**: Clean up async generator patterns

## Notes
- Use Context7 MCP to check `tastytrade` SDK DXLinkStreamer API
- The tastytrade SDK has a built-in DXLink streamer — wrap it, don't reimplement
- Use `async for` and `AsyncIterator` patterns
- This is the most complex adapter piece — real-time streaming with websockets
- Unit tests mock the streamer; integration tests (options-24) test real streaming
