---
id: options-24
title: "TastyTrade integration tests"
type: task
status: closed
priority: 3
created: 2026-02-05
updated: 2026-02-05
parent: options-17
depends-on: options-21, options-22, options-23
---

# TastyTrade integration tests

Write integration tests that connect to a real TastyTrade paper account. These tests are marked and skipped by default — only run when credentials are available.

## Branch
`feature/data-layer`

## Files to Create
- `tests/test_adapters/test_integration.py`

## Test Configuration

### pytest marker
```python
# In conftest.py
import pytest

def pytest_configure(config):
    config.addinivalue_line("markers", "integration: requires TastyTrade credentials")

# In test file
pytestmark = pytest.mark.integration
```

### Running
```bash
# Skip integration tests (default)
uv run pytest -m "not integration"

# Run integration tests
uv run pytest -m integration
```

## Tests to Write

### Session
- Connect to paper account
- Verify session is authenticated
- Disconnect cleanly

### Account
- Get accounts list (non-empty)
- Get positions for account

### Market Data
- Get option chain for SPY (known liquid underlying)
- Verify chain has multiple expirations
- Verify contracts have valid fields
- Get underlying price for SPY (reasonable value)

### Streaming (time-boxed)
- Connect to DXLink streamer
- Subscribe to Greeks for 1-2 SPY options
- Receive at least one Greeks update within 10 seconds
- Disconnect cleanly

## TDD Approach
These are validation tests — they verify the adapter works end-to-end against a real API.

## Notes
- All tests marked `@pytest.mark.integration`
- Use `pytest.skip` if credentials not available (check env vars or config)
- Use `asyncio` fixtures for async tests
- Time-box streaming tests with `asyncio.wait_for(timeout=10)`
- Paper account has no real money risk
- Use Context7 MCP to verify correct tastytrade SDK usage patterns
