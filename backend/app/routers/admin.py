#!/usr/bin/env python
"""Admin router for trend shocks and seed management."""

from fastapi import APIRouter, HTTPException

from app.schemas import SeedRequest, SeedResponse, ShockRequest, TrendSnapshot
from app.services.rng import rng_manager
from app.services.topics import topic_graph

router = APIRouter(prefix="/v1/admin", tags=["admin"])


@router.post("/shock", status_code=201)
async def inject_shock(request: ShockRequest) -> dict[str, str]:
    """Inject a trend shock to a topic."""
    success = topic_graph.inject_shock(
        request.topic_id, request.magnitude, request.half_life_s
    )

    if not success:
        raise HTTPException(status_code=404, detail="Topic not found")

    return {
        "message": f"Shock injected to {request.topic_id}",
        "topic_id": request.topic_id,
        "magnitude": str(request.magnitude),
        "half_life_s": str(request.half_life_s),
    }


@router.get("/trends", response_model=list[TrendSnapshot])
async def get_trends() -> list[TrendSnapshot]:
    """Get current trend scores and velocities."""
    snapshot_data = topic_graph.get_trend_snapshot()
    return [TrendSnapshot(**item) for item in snapshot_data]


@router.post("/seed", response_model=SeedResponse)
async def set_seed(request: SeedRequest) -> SeedResponse:
    """Set global RNG seed."""
    rng_manager.set_global_seed(request.seed)
    return SeedResponse(seed=request.seed, message=f"Global seed set to {request.seed}")
