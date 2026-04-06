.PHONY: dev dev-backend dev-frontend build serve test test-backend test-frontend clean

# Development — run backend and frontend in parallel
dev:
	@echo "Starting backend on :8000 and frontend on :5173..."
	@trap 'kill 0' EXIT; \
		uv run uvicorn options_analyzer.api.app:app --reload --host 127.0.0.1 --port 8000 & \
		cd frontend && npm run dev & \
		wait

dev-backend:
	uv run uvicorn options_analyzer.api.app:app --reload --host 127.0.0.1 --port 8000

dev-frontend:
	cd frontend && npm run dev

# Build frontend for production
build:
	cd frontend && npm run build

# Serve production (backend + built SPA)
serve:
	uv run uvicorn options_analyzer.api.app:app --host 0.0.0.0 --port 8000

# Test everything
test: test-backend test-frontend

test-backend:
	uv run pytest -m "not integration" --tb=short -q

test-frontend:
	cd frontend && npm test

# Clean build artifacts
clean:
	rm -rf frontend/dist
