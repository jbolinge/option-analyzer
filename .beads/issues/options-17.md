---
id: options-17
title: "Data Layer — Ports & TastyTrade Adapter"
type: epic
status: closed
priority: 3
created: 2026-02-05
updated: 2026-02-05
depends-on: options-1
---

# Data Layer — Ports & TastyTrade Adapter

Hexagonal architecture data layer: abstract port interfaces (ABCs) and the TastyTrade adapter implementation. The adapter is the ONLY place that imports the `tastytrade` SDK — all other code depends on the port abstractions.

## Scope
- MarketDataProvider ABC (option chains, quotes, streaming Greeks)
- AccountProvider ABC (accounts, positions)
- TastyTrade session management (paper vs live)
- TastyTrade mapping layer (SDK objects ↔ domain models)
- TastyTrade market data provider implementation
- TastyTrade account provider implementation
- TastyTrade DXLink streaming wrapper
- Integration tests (marked, require credentials)

## Acceptance Criteria
- [ ] Port ABCs define complete async interface
- [ ] TastyTrade adapter implements both ports
- [ ] Only `adapters/tastytrade/mapping.py` imports tastytrade SDK types
- [ ] Paper vs live toggle works via config
- [ ] Unit tests pass without network/credentials
- [ ] Integration tests connect to paper account (marked `@pytest.mark.integration`)
