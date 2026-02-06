---
id: options-13
title: "Hypothesis property-based tests for BSM"
type: task
status: closed
priority: 2
created: 2026-02-05
updated: 2026-02-05
parent: options-9
depends-on: options-12
---

# Hypothesis property-based tests for BSM

Add property-based tests using Hypothesis to verify BSM invariants across randomly generated inputs.

## Branch
`feature/bsm-engine`

## Files to Create
- `tests/test_engine/test_bsm_properties.py`

## Properties to Test

### Put-Call Parity (strongest invariant)
For all valid S, K, T, r, sigma, q:
`call_price(S,K,T,r,sigma,q) - put_price(S,K,T,r,sigma,q) ≈ S*e^(-qT) - K*e^(-rT)`

### Delta Bounds
- `0 <= delta(call) <= 1`
- `-1 <= delta(put) <= 0`
- `delta(call) - delta(put) ≈ e^(-qT)` (delta parity)

### Non-Negative Greeks
- `gamma >= 0` (always)
- `vega >= 0` (always)
- `call_price >= 0` and `put_price >= 0`

### Monotonicity
- Call price increases with S (all else equal)
- Put price decreases with S (all else equal)
- Both prices increase with sigma (all else equal)
- Both prices increase with T (all else equal, for Europeans)

### Greeks Symmetries
- `gamma(call) == gamma(put)` (same inputs)
- `vega(call) == vega(put)` (same inputs)
- `vanna(call) == vanna(put)` (same inputs)

## Hypothesis Strategies
```python
spot = st.floats(min_value=10, max_value=500, allow_nan=False)
strike = st.floats(min_value=10, max_value=500, allow_nan=False)
time_to_expiry = st.floats(min_value=0.01, max_value=5.0, allow_nan=False)
risk_free = st.floats(min_value=0.0, max_value=0.20, allow_nan=False)
vol = st.floats(min_value=0.05, max_value=2.0, allow_nan=False)
div_yield = st.floats(min_value=0.0, max_value=0.10, allow_nan=False)
```

## TDD Approach
1. **Red**: Write property tests — they should pass against the existing BSM impl
2. **Green**: Fix any BSM edge cases that property tests uncover
3. **Refactor**: Tune Hypothesis settings (max_examples, deadline)

## Notes
- Use `@given(...)` decorator with custom strategies
- Use `pytest.approx` with `rel=1e-6` for floating-point comparisons
- Set `@settings(max_examples=500)` for thorough coverage
- Mark with `@pytest.mark.slow` if needed
