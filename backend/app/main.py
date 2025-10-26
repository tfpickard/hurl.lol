#!/usr/bin/env python
"""Main FastAPI application for Hurl."""

import time
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from prometheus_client import Counter, Histogram, generate_latest
from starlette.responses import Response

from app.config import settings
from app.routers import admin, health, personas, posts, topics
from app.services.trends import trend_engine

# Prometheus metrics
request_count = Counter(
    "hurl_requests_total",
    "Total request count",
    ["method", "endpoint", "status"],
)
request_duration = Histogram(
    "hurl_request_duration_seconds",
    "Request duration in seconds",
    ["method", "endpoint"],
)
posts_generated = Counter(
    "hurl_posts_generated_total",
    "Total posts generated",
    ["mode"],
)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Lifespan context manager for startup/shutdown."""
    # Startup
    await trend_engine.start()
    yield
    # Shutdown
    await trend_engine.stop()


# Create FastAPI app
app = FastAPI(
    title="Hurl REST API",
    description="Synthetic social media post generator — hurl.rest",
    version="0.1.0",
    lifespan=lifespan,
)

# CORS middleware
allowed_origins = settings.allow_origins
if isinstance(allowed_origins, str):
    allowed_origins = [o.strip() for o in allowed_origins.split(",")]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request timing middleware
@app.middleware("http")
async def add_metrics_middleware(request: Request, call_next):
    """Add request timing and counting."""
    start_time = time.time()

    response = await call_next(request)

    duration = time.time() - start_time
    endpoint = request.url.path
    method = request.method
    status = response.status_code

    request_count.labels(method=method, endpoint=endpoint, status=status).inc()
    request_duration.labels(method=method, endpoint=endpoint).observe(duration)

    return response


# Include routers
app.include_router(health.router)
app.include_router(posts.router)
app.include_router(personas.router)
app.include_router(topics.router)
app.include_router(admin.router)


# Prometheus metrics endpoint
@app.get("/metrics")
async def metrics() -> Response:
    """Prometheus metrics endpoint."""
    return Response(content=generate_latest(), media_type="text/plain")


@app.get("/")
async def root() -> dict[str, str]:
    """Root endpoint."""
    return {
        "service": "Hurl REST API",
        "version": "0.1.0",
        "docs": "/docs",
        "health": "/v1/healthz",
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "backend.app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.is_dev,
    )
