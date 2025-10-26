from __future__ import annotations

import asyncio
from typing import AsyncGenerator, Dict, List

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi import status

from ..config import Settings, get_settings
from ..schemas import GenerateRequest, PostSchema, SeedRequest
from ..services.generator.core import generator_service
from ..services.rng import get_rng
from ..sse import sse_response

router = APIRouter(tags=["posts"])


def require_auth(request: Request, settings: Settings = Depends(get_settings)) -> str | None:
    if not settings.require_auth:
        return None
    header = request.headers.get("authorization")
    if not header or not header.lower().startswith("bearer "):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="missing bearer token")
    token = header.split(" ", 1)[1]
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid bearer token")
    return token


_rate_limiter: Dict[str, Dict[str, float]] = {}


def enforce_rate_limit(token: str | None, now: float) -> None:
    if token is None:
        return
    window = _rate_limiter.setdefault(token, {"tokens": 30.0, "updated": now})
    elapsed = now - window["updated"]
    window["tokens"] = min(30.0, window["tokens"] + elapsed * 2)
    window["updated"] = now
    if window["tokens"] < 1.0:
        raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail="rate limit exceeded")
    window["tokens"] -= 1.0


@router.post("/generate", response_model=List[PostSchema])
async def generate_posts(
    payload: GenerateRequest,
    request: Request,
    token: str | None = Depends(require_auth),
) -> List[PostSchema]:
    enforce_rate_limit(token, asyncio.get_event_loop().time())
    generator = generator_service()
    try:
        posts = generator.generate(
            count=payload.count,
            mode=payload.mode,
            topics=payload.topics,
            persona_ids=payload.persona_ids,
            languages=payload.languages,
            toxicity_max=payload.toxicity_max,
            reading_level=payload.reading_level,
            seed=payload.seed,
        )
    except ValueError as exc:  # pragma: no cover - defensive
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return posts


@router.get("/sample", response_model=List[PostSchema])
async def sample_posts(count: int = 5, mode: str = "pure_random") -> List[PostSchema]:
    generator = generator_service()
    posts = generator.generate(
        count=count,
        mode=mode,
        topics=[],
        persona_ids=[],
        languages=[],
        toxicity_max=1.0,
        reading_level=None,
        seed=None,
    )
    return posts


@router.get("/stream")
async def stream_posts(request: Request, token: str | None = Depends(require_auth)):
    enforce_rate_limit(token, asyncio.get_event_loop().time())
    generator = generator_service()

    async def event_generator() -> AsyncGenerator[Dict[str, object], None]:
        while True:
            if await request.is_disconnected():
                break
            posts = generator.generate(
                count=1,
                mode=request.query_params.get("mode", "pure_random"),
                topics=request.query_params.getlist("topic"),
                persona_ids=request.query_params.getlist("persona_id"),
                languages=request.query_params.getlist("language"),
                toxicity_max=float(request.query_params.get("toxicity_max", "1.0")),
                reading_level=request.query_params.get("reading_level"),
                seed=None,
            )
            yield posts[0].dict()
            await asyncio.sleep(0.5)

    return await sse_response(event_generator())


@router.post("/seed")
async def set_seed(payload: SeedRequest) -> dict[str, int]:
    rng = get_rng()
    rng.reseed(payload.seed)
    return {"seed": rng.seed}
