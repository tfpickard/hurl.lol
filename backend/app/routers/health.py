#!/usr/bin/env python
"""Health check router."""

from fastapi import APIRouter

from backend.app.config import settings
from backend.app.schemas import HealthResponse

router = APIRouter()


@router.get("/healthz", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    """Health check endpoint."""
    return HealthResponse(
        status="ok",
        version="0.1.0",
        mode=settings.hurl_env,
        llm_enabled=settings.llm_enabled,
        persistence_enabled=settings.persist,
    )
