"""Health check endpoint."""

from __future__ import annotations

from fastapi import APIRouter

router = APIRouter()


@router.get("/health")
async def health() -> dict[str, str]:
    """Return API health status."""
    return {
        "status": "ok",
        "api_version": "0.1.0",
    }
