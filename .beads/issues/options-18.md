---
id: options-18
title: "Port ABCs — MarketDataProvider, AccountProvider"
type: task
status: closed
priority: 3
created: 2026-02-05
updated: 2026-02-05
parent: options-17
depends-on: options-5, options-6
---

# Port ABCs — MarketDataProvider, AccountProvider

Define the abstract base classes for the provider-agnostic data layer. These are the hexagonal architecture "ports" that adapters implement.

## Branch
`feature/data-layer`

## Files to Create
- `src/options_analyzer/ports/__init__.py`
- `src/options_analyzer/ports/market_data.py`
- `src/options_analyzer/ports/account.py`
- `tests/test_ports/__init__.py`
- `tests/test_ports/test_interfaces.py`

## Interfaces

### MarketDataProvider (ABC) in `ports/market_data.py`
```python
class MarketDataProvider(ABC):
    @abstractmethod
    async def connect(self) -> None: ...

    @abstractmethod
    async def disconnect(self) -> None: ...

    @abstractmethod
    async def get_option_chain(
        self, underlying: str
    ) -> dict[date, list[OptionContract]]: ...

    @abstractmethod
    async def get_underlying_price(self, symbol: str) -> Decimal: ...

    @abstractmethod
    async def stream_greeks(
        self, contracts: list[OptionContract]
    ) -> AsyncIterator[tuple[str, FirstOrderGreeks]]: ...

    @abstractmethod
    async def stream_quotes(
        self, symbols: list[str]
    ) -> AsyncIterator[tuple[str, Decimal, Decimal]]: ...
```

### AccountProvider (ABC) in `ports/account.py`
```python
class AccountProvider(ABC):
    @abstractmethod
    async def get_accounts(self) -> list[str]: ...

    @abstractmethod
    async def get_positions(
        self, account_id: str, underlying: str | None = None
    ) -> list[Leg]: ...
```

## TDD Approach
1. **Red**: Write tests:
   - Verify ABCs cannot be instantiated directly
   - Verify concrete subclass must implement all abstract methods
   - Create a mock implementation and verify it satisfies the interface
   - Verify type annotations are correct
2. **Green**: Implement ABCs
3. **Refactor**: Ensure async context manager protocol support if needed

## Notes
- All methods are async — the adapter will use async HTTP/streaming
- Use `from abc import ABC, abstractmethod`
- Use `from collections.abc import AsyncIterator`
- Use Context7 MCP to check `tastytrade` SDK async patterns for interface alignment
- These ABCs reference domain types (OptionContract, Leg, FirstOrderGreeks) — hence depends on options-5 and options-6
