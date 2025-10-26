from __future__ import annotations

import asyncio
from typing import AsyncIterable

from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from .config import get_settings
from .routers import admin, health, personas, posts, topics
from .services.personas import ensure_seed_personas
from .services.trends import get_trend_engine
from .services.topics import ensure_topic_graph

settings = get_settings()

app = FastAPI(title=settings.app_name, version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allow_origins,
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
)

app.include_router(health.router)
app.include_router(posts.router, prefix="/v1")
app.include_router(personas.router, prefix="/v1")
app.include_router(topics.router, prefix="/v1")
app.include_router(admin.router, prefix="/v1")


@app.on_event("startup")
async def startup_event() -> None:
    ensure_seed_personas()
    ensure_topic_graph()
    await get_trend_engine().start()


@app.on_event("shutdown")
async def shutdown_event() -> None:
    await get_trend_engine().stop()


@app.get("/", include_in_schema=False)
async def root() -> JSONResponse:
    return JSONResponse({"message": "Hurl REST API"})
