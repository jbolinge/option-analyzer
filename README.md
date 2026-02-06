# options-analyzer

Options position analyzer with first and second-order Greeks, TastyTrade integration, and Bloomberg-themed visualization.

## Features

- **Complete Greeks engine** — Black-Scholes-Merton with all first-order (delta, gamma, theta, vega, rho) and second-order Greeks (vanna, volga, charm, veta, speed, color)
- **TastyTrade integration** — Live market data, option chains, account positions, and real-time streaming via DXLink
- **Bloomberg-themed charts** — Dark theme with orange/cyan palette across payoff diagrams, Greeks profiles, decay charts, vol surfaces, and 3D surfaces
- **Jupyter notebooks** — Four ready-to-use notebooks for connection, position analysis, Greeks dashboards, and vol surfaces
- **Provider-agnostic architecture** — Hexagonal design with ports and adapters; swap TastyTrade for any broker

## Prerequisites

- Python 3.12+
- [uv](https://docs.astral.sh/uv/) package manager
- TastyTrade account (paper trading works)

## Quick Start

```bash
# Clone and install
git clone <repo-url>
cd options-analyzer
uv sync --all-extras

# Set up credentials
cp .env.example .env
# Edit .env with your TastyTrade username and password

# Set up config
cp config/config.yaml.example config/config.yaml

# Launch notebooks
uv run jupyter lab
```

## Running Tests

```bash
# Unit tests (no credentials needed)
uv run pytest -m "not integration"

# All tests including TastyTrade integration
uv run pytest

# With coverage
uv run pytest --cov=src/options_analyzer
```

## Architecture

```
Presentation  (Jupyter / future web app)
     |
Visualization (plotly + Bloomberg theme)
     |
Engine        (BSM Greeks, Payoff, Position Analyzer)
     |
Domain        (OptionContract, Leg, Position, Greeks)
     |
Ports (ABCs)  <-->  Adapters (TastyTrade)
```

See [CLAUDE.md](CLAUDE.md) for full developer documentation, project structure, and testing strategy.
