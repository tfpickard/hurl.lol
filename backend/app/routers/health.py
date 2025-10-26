from __future__ import annotations

from fastapi import APIRouter

router = APIRouter(tags=["health"])


@router.get("/v1/healthz")
async def healthz() -> dict[str, str]:
    return {"status": "ok"}
