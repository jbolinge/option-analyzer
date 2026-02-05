---
id: options-10
title: "BSM pure functions — d1, d2, first-order Greeks"
type: task
status: open
priority: 2
created: 2026-02-05
updated: 2026-02-05
parent: options-9
depends-on: options-6
---

# BSM pure functions — d1, d2, first-order Greeks

Implement the core Black-Scholes-Merton formulas as pure functions. These take scalar inputs and return scalar outputs — no classes, no state.

## Branch
`feature/bsm-engine`

## Files to Create
- `src/options_analyzer/engine/__init__.py`
- `src/options_analyzer/engine/bsm.py`
- `tests/test_engine/__init__.py`
- `tests/test_engine/test_bsm.py` (first-order portion)

## Functions to Implement in `bsm.py`

### Helpers
- `d1(S, K, T, r, sigma, q=0.0) -> float`
- `d2(S, K, T, r, sigma, q=0.0) -> float`

### First-Order Greeks
- `call_price(S, K, T, r, sigma, q=0.0) -> float`
- `put_price(S, K, T, r, sigma, q=0.0) -> float`
- `delta(S, K, T, r, sigma, q=0.0, option_type="call") -> float`
- `gamma(S, K, T, r, sigma, q=0.0) -> float` (same for call/put)
- `theta(S, K, T, r, sigma, q=0.0, option_type="call") -> float`
- `vega(S, K, T, r, sigma, q=0.0) -> float` (same for call/put)
- `rho(S, K, T, r, sigma, q=0.0, option_type="call") -> float`

### Parameters
- `S`: spot price
- `K`: strike price
- `T`: time to expiry in years
- `r`: risk-free rate (annualized)
- `sigma`: implied volatility (annualized)
- `q`: continuous dividend yield (default 0.0)

## TDD Approach
1. **Red**: Write tests with known textbook values:
   - ATM call/put: S=100, K=100, T=1.0, r=0.05, sigma=0.20
   - ITM call: S=110, K=100, T=0.5, r=0.05, sigma=0.25
   - OTM put: S=100, K=90, T=0.25, r=0.05, sigma=0.30
   - Verify call_price - put_price = S*e^(-qT) - K*e^(-rT) (put-call parity)
   - Delta bounds: 0 <= call_delta <= 1, -1 <= put_delta <= 0
   - Gamma always >= 0
   - Vega always >= 0
2. **Green**: Implement using `scipy.stats.norm` for N(x) and n(x)
3. **Refactor**: Extract common subexpressions

## Known Test Values (Hull, 10th ed.)
S=42, K=40, T=0.5, r=0.10, sigma=0.20, q=0:
- call_price ≈ 4.76
- delta(call) ≈ 0.7791

## Notes
- Use `scipy.stats.norm.cdf` for N(x) and `scipy.stats.norm.pdf` for n(x)
- All functions are pure — no side effects, no state
- Handle edge case: T <= 0 should return intrinsic value
- Handle edge case: sigma <= 0 should return intrinsic value
