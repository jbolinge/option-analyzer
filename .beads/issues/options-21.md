---
id: options-21
title: "TastyTrade market data provider"
type: task
status: closed
priority: 3
created: 2026-02-05
updated: 2026-02-05
parent: options-17
depends-on: options-20
---

# TastyTrade market data provider

Implement the TastyTradeMarketDataProvider that implements the MarketDataProvider port using the TastyTrade SDK.

## Branch
`feature/data-layer`

## Files to Create
- `src/options_analyzer/adapters/tastytrade/market_data.py`
- `tests/test_adapters/test_market_data.py`

## Class Design

### TastyTradeMarketDataProvider(MarketDataProvider)
```python
class TastyTradeMarketDataProvider(MarketDataProvider):
    def __init__(self, session: TastyTradeSession):
        ...

    async def connect(self) -> None:
        """Connect session if not already connected."""

    async def disconnect(self) -> None:
        """Disconnect session."""

    async def get_option_chain(
        self, underlying: str
    ) -> dict[date, list[OptionContract]]:
        """Fetch option chain grouped by expiration date."""

    async def get_underlying_price(self, symbol: str) -> Decimal:
        """Get current underlying price."""

    async def stream_greeks(
        self, contracts: list[OptionContract]
    ) -> AsyncIterator[tuple[str, FirstOrderGreeks]]:
        """Stream live Greeks for given contracts via DXLink."""

    async def stream_quotes(
        self, symbols: list[str]
    ) -> AsyncIterator[tuple[str, Decimal, Decimal]]:
        """Stream bid/ask quotes."""
```

## TDD Approach
1. **Red**: Write unit tests with mocked session:
   - get_option_chain calls SDK API, maps results via mapping layer
   - get_underlying_price returns Decimal
   - Verify mapping.map_option_to_contract is called for each option
   - Error handling: network errors, empty chains, invalid symbols
2. **Green**: Implement using tastytrade SDK API calls + mapping layer
3. **Refactor**: Clean up async patterns

## Notes
- Use Context7 MCP to check `tastytrade` SDK API for fetching option chains
- Delegates all SDK type conversions to mapping.py
- Unit tests mock the SDK — no network calls
- Integration tests (options-24) will test real connectivity
