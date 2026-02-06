# options-analyzer

Options position analyzer with first and second-order Greeks, TastyTrade integration, and Bloomberg-themed visualization.

## Project Overview

A standalone tool for tracking and visualizing options positions (any multi-leg strategy) with complete Greeks analysis. Uses the TastyTrade API with a provider-agnostic data layer. The initial interface is Jupyter Notebooks, with architecture designed for a future Bloomberg-style web application.

## Technology Stack

- **Python 3.12+** with modern type hints
- **uv** for package management (exclusively — no pip, no poetry)
- **Pydantic v2** for domain models and configuration
- **numpy + scipy** for numerical computation
- **plotly** for interactive visualization
- **tastytrade SDK** for brokerage data
- **pytest + hypothesis** for TDD
- **jupyterlab** for notebook interface

## Architecture — Hexagonal (Ports & Adapters)

```
+---------------------------------------------------+
|  Presentation (Jupyter / future Dash web app)     |
+---------------------------------------------------+
|  Visualization (plotly figures + Bloomberg theme)  |
+---------------------------------------------------+
|  Engine (BSM Greeks, Payoff, Position Analyzer)    |
+---------------------------------------------------+
|  Domain (OptionContract, Leg, Position, Greeks)    |
+----------------+----------------------------------+
|  Ports (ABCs)  |  Adapters (TastyTrade, future...) |
+----------------+----------------------------------+
```

Engine + Visualization depend only on Domain. Adapters implement Ports. Presentation consumes Engine + Visualization. Nothing depends on a specific data provider.

## Project Structure

```
src/options_analyzer/
├── config/
│   └── schema.py              # AppConfig, ProviderConfig (Pydantic v2, SecretStr)
├── domain/
│   ├── enums.py               # OptionType, PositionSide, ExerciseStyle
│   ├── models.py              # OptionContract, Leg, Position
│   └── greeks.py              # FirstOrderGreeks, SecondOrderGreeks, FullGreeks, PositionGreeks
├── ports/
│   ├── market_data.py         # MarketDataProvider ABC
│   └── account.py             # AccountProvider ABC
├── adapters/tastytrade/
│   ├── session.py             # Session lifecycle (paper vs live via is_test)
│   ├── mapping.py             # SDK ↔ domain models (ONLY file importing SDK types)
│   ├── market_data.py         # TastyTradeMarketDataProvider
│   ├── account.py             # TastyTradeAccountProvider
│   └── streaming.py           # DXLink streamer wrapper
├── engine/
│   ├── bsm.py                 # Pure BSM functions: d1, d2, all 1st + 2nd order Greeks
│   ├── greeks_calculator.py   # GreeksCalculator wrapping BSM with config defaults
│   ├── payoff.py              # PayoffCalculator: expiration payoff, theoretical P&L, surfaces
│   └── position_analyzer.py   # PositionAnalyzer: aggregate Greeks, risk profiles
└── visualization/
    ├── theme.py               # Bloomberg dark theme (black bg, orange/cyan, monospace)
    ├── payoff_charts.py       # P&L at expiration, theoretical P&L, 3D surface
    ├── greeks_charts.py       # Greeks vs price profiles, position summary
    ├── decay_charts.py        # Theta/charm/veta decay over time
    ├── vol_charts.py          # Vanna/volga profiles
    └── surface_charts.py      # 3D surfaces (Greeks vs price vs vol/time)

tests/
├── conftest.py
├── factories.py               # Reusable test object builders
├── test_domain/
├── test_engine/
├── test_adapters/
└── test_visualization/

notebooks/
├── 01_connect_and_explore.ipynb
├── 02_position_analysis.ipynb
├── 03_greeks_dashboard.ipynb
└── 04_vol_surfaces.ipynb
```

## Key Concepts

- **OptionContract**: Immutable model for a single option (symbol, underlying, strike, expiration, type)
- **Leg**: A contract + side (long/short) + quantity + open price
- **Position**: Named collection of legs (e.g., "AAPL 150/160/170 BWB")
- **FirstOrderGreeks**: delta, gamma, theta, vega, rho, iv — sourced from data provider
- **SecondOrderGreeks**: vanna, volga, charm, veta, speed, color — computed via BSM engine
- **BSM**: Black-Scholes-Merton analytical formulas implemented as pure functions
- **Port**: Abstract interface (ABC) that adapters implement
- **Adapter**: Concrete implementation for a specific provider (TastyTrade)

## BSM Second-Order Greeks Reference

| Greek | Formula | Meaning |
|-------|---------|---------|
| Vanna | `-e^(-qT) * n(d1) * d2 / sigma` | dDelta/dVol = dVega/dS |
| Volga | `vega * d1 * d2 / sigma` | dVega/dVol (vol of vol risk) |
| Charm | call/put specific with n(d1), d2 terms | dDelta/dTime (delta decay) |
| Veta | `-S*e^(-qT)*n(d1)*sqrt(T) * [...]` | dVega/dTime |
| Speed | `-(gamma/S) * (1 + d1/(sigma*sqrt(T)))` | dGamma/dS |
| Color | complex with n(d1), d1, d2, T, sigma | dGamma/dTime |

## Development Workflow

1. **TDD**: Write tests first (red), then implementation (green), then refactor
2. **Beads tracking**: Use `/bd` commands to track issues in `.beads/`
3. **Feature branches**: `feature/<epic-name>` merged to main when complete
4. **Frequent commits**: Small, focused commits with clear messages
5. **Context7 MCP**: Use for up-to-date API docs (tastytrade SDK, plotly, Pydantic v2)

## Running Commands

```bash
# Run tests (skip integration)
uv run pytest -m "not integration"

# Run all tests including integration (requires TastyTrade credentials)
uv run pytest -m integration

# Run specific test file
uv run pytest tests/test_engine/test_bsm.py

# Run with coverage
uv run pytest --cov=src/options_analyzer

# Type checking
uv run mypy src/

# Linting
uv run ruff check src/

# Jupyter notebooks
uv run jupyter lab
```

## Configuration

Main config file: `config/config.yaml`

```yaml
provider:
  name: tastytrade
  username: "${TASTYTRADE_USERNAME}"
  password: "${TASTYTRADE_PASSWORD}"
  is_paper: true

engine:
  risk_free_rate: 0.05
  dividend_yield: 0.0

visualization:
  theme: bloomberg
```

Credentials use `pydantic.SecretStr` — never logged or displayed in repr.

## Testing Strategy

- **BSM formulas**: Known textbook values (Hull 10th ed.) + finite-difference verification of 2nd-order Greeks
- **Property-based (hypothesis)**: Put-call parity, delta bounds, gamma/vega non-negative, Greek symmetries
- **Payoff shapes**: Verify standard strategies — butterfly tent shape, vertical capped P&L, etc.
- **Aggregation**: signed_quantity * multiplier applied correctly across multi-leg positions
- **Integration** (`@pytest.mark.integration`): Connect to TastyTrade paper, fetch chain, stream Greeks — skipped by default
- **Visualization**: Verify figure structure (trace count, axis labels, theme applied) — no visual regression

## Dependencies

### Core
- pydantic>=2.0
- numpy>=1.26
- scipy>=1.12
- plotly>=5.18
- pyyaml>=6.0
- tastytrade>=11.1

### Dev
- pytest>=8.0
- pytest-asyncio>=0.23
- pytest-cov
- hypothesis>=6.0
- ruff
- mypy

### Jupyter (optional group)
- jupyterlab>=4.0
- ipywidgets>=8.0
