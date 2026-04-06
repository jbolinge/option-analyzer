# Tech Stack

## Languages

| Language | Version | Role |
|----------|---------|------|
| Python | 3.12+ | Backend: domain, engine, visualization, adapters, API |
| TypeScript | 5.x | Frontend: React SPA |

## Backend

| Component | Technology | Version |
|-----------|-----------|---------|
| API Framework | FastAPI | >=0.115 |
| ASGI Server | Uvicorn | >=0.30 |
| Domain Models | Pydantic v2 | >=2.0 |
| Numerical | NumPy + SciPy | >=1.26 / >=1.12 |
| Visualization | Plotly | >=5.18 |
| Broker SDK | TastyTrade | >=12.0.2 |
| Technical Analysis | TA-Lib | >=0.4.28 |
| Candle Fallback | yfinance | >=0.2 |
| Config | PyYAML + python-dotenv | >=6.0 / >=1.0 |
| Package Manager | uv | (exclusively) |

## Frontend

| Component | Technology | Version |
|-----------|-----------|---------|
| Framework | React | 18+ |
| Build Tool | Vite | latest |
| Tiling/Windowing | flexlayout-react | latest |
| Charts | react-plotly.js + plotly.js-cartesian-dist | latest |
| Server State | TanStack Query (React Query) | latest |
| UI State | Zustand | latest |
| Styling | CSS Modules + CSS Custom Properties | — |

## Testing

| Tool | Purpose |
|------|---------|
| pytest | Backend unit + integration tests |
| pytest-asyncio | Async test support |
| hypothesis | Property-based testing (Greeks invariants) |
| Vitest | Frontend unit tests |
| React Testing Library | Frontend component tests |
| ruff | Python linting |
| mypy | Python type checking (strict mode) |

## Database

None — stateless. All data sourced from TastyTrade API in real-time.

## Deployment

Local / self-hosted. Single `uv run uvicorn` command serves both API and SPA.

## Key Dependencies (existing)

- `plotly` — Interactive charting (backend generates figures, frontend renders via plotly.js)
- `tastytrade` — Brokerage API with OAuth + DXLink streaming
- `pydantic` — Immutable domain models, config validation, SecretStr for credentials
- `TA-Lib` — Technical indicator calculations (SMA, HMA, ATR, OBV)
