from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi import status

from ..config import Settings, get_settings
from ..schemas import ShockRequest, TopicSchema
from ..services.trends import get_trend_engine

router = APIRouter(tags=["admin"])


def ensure_admin(request: Request, settings: Settings = Depends(get_settings)) -> None:
    if not settings.admin_token:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="admin disabled")
    header = request.headers.get("authorization")
    if not header or not header.lower().startswith("bearer "):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="missing bearer token")
    token = header.split(" ", 1)[1]
    if token != settings.admin_token:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="invalid admin token")


@router.post("/admin/shock", status_code=202)
async def inject_shock(payload: ShockRequest, _: None = Depends(ensure_admin)) -> dict[str, str]:
    engine = get_trend_engine()
    await engine.inject_shock(payload)
    return {"status": "accepted"}


@router.get("/admin/trends", response_model=list[TopicSchema])
async def get_trends(_: None = Depends(ensure_admin)) -> list[TopicSchema]:
    return get_trend_engine().trend_snapshot()
