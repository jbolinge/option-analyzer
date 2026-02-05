---
id: options-11
title: "BSM second-order Greeks — vanna, volga, charm, veta, speed, color"
type: task
status: open
priority: 2
created: 2026-02-05
updated: 2026-02-05
parent: options-9
depends-on: options-10
---

# BSM second-order Greeks — vanna, volga, charm, veta, speed, color

Add second-order Greek analytical formulas to the BSM module.

## Branch
`feature/bsm-engine`

## Files to Modify
- `src/options_analyzer/engine/bsm.py` (add functions)
- `tests/test_engine/test_bsm.py` (add tests)

## Functions to Add to `bsm.py`

### Second-Order Greeks
- `vanna(S, K, T, r, sigma, q=0.0) -> float`
  - Formula: `-e^(-qT) * n(d1) * d2 / sigma`
  - Meaning: dDelta/dVol = dVega/dSpot

- `volga(S, K, T, r, sigma, q=0.0) -> float`
  - Formula: `vega * d1 * d2 / sigma`
  - Meaning: dVega/dVol (vol of vol risk, aka vomma)

- `charm(S, K, T, r, sigma, q=0.0, option_type="call") -> float`
  - Call: `-q*e^(-qT)*N(d1) + e^(-qT)*n(d1) * (2*(r-q)*T - d2*sigma*sqrt(T)) / (2*T*sigma*sqrt(T))`
  - Put: `q*e^(-qT)*N(-d1) + e^(-qT)*n(d1) * (2*(r-q)*T - d2*sigma*sqrt(T)) / (2*T*sigma*sqrt(T))`
  - Meaning: dDelta/dTime (delta decay)

- `veta(S, K, T, r, sigma, q=0.0) -> float`
  - Formula: `-S*e^(-qT)*n(d1)*sqrt(T) * [q + (r-q)*d1/(sigma*sqrt(T)) - (1+d1*d2)/(2*T)]`
  - Meaning: dVega/dTime

- `speed(S, K, T, r, sigma, q=0.0) -> float`
  - Formula: `-(gamma/S) * (1 + d1/(sigma*sqrt(T)))`
  - Meaning: dGamma/dSpot

- `color(S, K, T, r, sigma, q=0.0) -> float`
  - Formula: `-e^(-qT) * n(d1) / (2*S*T*sigma*sqrt(T)) * (2*q*T + 1 + d1*(2*(r-q)*T - d2*sigma*sqrt(T)) / (sigma*sqrt(T)))`
  - Meaning: dGamma/dTime

## TDD Approach
1. **Red**: Write tests using **finite-difference verification**:
   - For each second-order Greek, compute it analytically AND numerically:
     - `vanna_numerical = (delta(S, K, T, r, sigma+h) - delta(S, K, T, r, sigma-h)) / (2*h)`
     - `charm_numerical = (delta(S, K, T-h, r, sigma) - delta(S, K, T+h, r, sigma)) / (2*h)`
     - etc.
   - Verify analytical ≈ numerical within tolerance (1e-4 for h=1e-5)
   - Use multiple test points: ATM, ITM, OTM
   - Verify vanna_call == vanna_put (it's the same for calls and puts)
2. **Green**: Implement formulas
3. **Refactor**: Factor out common n(d1), d1, d2 computations

## Edge Cases
- T approaching 0: clamp to small epsilon or return 0
- sigma approaching 0: return 0 for vol-dependent Greeks
- Deep ITM/OTM: verify no NaN/Inf from extreme d1/d2 values

## Notes
- All functions remain pure — same signature pattern as first-order
- Finite-difference tests are the gold standard for verifying analytical derivatives
- Use `pytest.approx` with appropriate tolerance
