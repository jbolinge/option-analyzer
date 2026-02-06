---
id: options-12
title: "BSM comprehensive test suite — known values + finite-difference"
type: task
status: closed
priority: 2
created: 2026-02-05
updated: 2026-02-05
parent: options-9
depends-on: options-11
---

# BSM comprehensive test suite — known values + finite-difference

Expand the BSM test suite with comprehensive coverage: textbook values, finite-difference cross-checks, and edge case handling.

## Branch
`feature/bsm-engine`

## Files to Modify
- `tests/test_engine/test_bsm.py` (expand)

## Test Categories

### 1. Known Textbook Values
Reference: Hull "Options, Futures, and Other Derivatives" 10th ed.
- S=42, K=40, T=0.5, r=0.10, sigma=0.20 → call ≈ 4.76
- S=100, K=100, T=1.0, r=0.05, sigma=0.20 → ATM reference values
- Multiple ITM/OTM/ATM scenarios for calls and puts

### 2. Put-Call Parity
For every test point, verify:
`call_price - put_price = S*e^(-qT) - K*e^(-rT)`

### 3. Finite-Difference Verification (Second-Order)
For each second-order Greek, bump the relevant first-order Greek:
- vanna: bump sigma, check delta change
- volga: bump sigma, check vega change
- charm: bump T, check delta change
- veta: bump T, check vega change
- speed: bump S, check gamma change
- color: bump T, check gamma change

Use h=1e-5, tolerance=1e-4.

### 4. Edge Cases
- T=0 (at expiry): should return intrinsic values
- T very small (1e-10): should not produce NaN/Inf
- sigma=0: should return intrinsic
- sigma very small (1e-10): should not produce NaN/Inf
- Deep ITM (S >> K): delta → 1 for call, gamma → 0
- Deep OTM (S << K): delta → 0 for call, gamma → 0

### 5. Symmetry Properties
- gamma_call == gamma_put
- vega_call == vega_put
- vanna_call == vanna_put
- volga_call == volga_put

## TDD Approach
This IS the test suite — write all tests, verify they pass against the already-implemented BSM functions.

## Notes
- Use `@pytest.mark.parametrize` for multiple test points
- Group tests into classes: `TestFirstOrder`, `TestSecondOrder`, `TestEdgeCases`, `TestParity`
- Tolerance guidance: 1e-6 for known values, 1e-4 for finite-difference
