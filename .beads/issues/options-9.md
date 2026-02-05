---
id: options-9
title: "BSM Engine & Computation"
type: epic
status: open
priority: 2
created: 2026-02-05
updated: 2026-02-05
depends-on: options-1
---

# BSM Engine & Computation

Pure computation phase: Black-Scholes-Merton analytical formulas, Greeks calculator, payoff diagrams, and position-level analysis. No API calls — everything uses numpy/scipy and is fully testable with known textbook values.

## Scope
- BSM pure functions: d1, d2, all first-order Greeks (delta, gamma, theta, vega, rho)
- BSM second-order Greeks (vanna, volga, charm, veta, speed, color)
- Comprehensive BSM test suite with known values and finite-difference verification
- Hypothesis property-based tests (put-call parity, delta bounds, etc.)
- GreeksCalculator class wrapping pure functions with config defaults
- PayoffCalculator for expiration P&L, theoretical P&L, P&L surfaces
- PositionAnalyzer for multi-leg aggregation and risk profiles

## Acceptance Criteria
- [ ] All BSM formulas match textbook values to 6 decimal places
- [ ] Finite-difference verification confirms analytical second-order Greeks
- [ ] Put-call parity holds for all generated inputs (hypothesis)
- [ ] PayoffCalculator produces correct shapes for standard strategies
- [ ] PositionAnalyzer correctly aggregates Greeks across legs with signed quantities
- [ ] Edge cases handled: T→0, sigma→0, deep ITM/OTM
