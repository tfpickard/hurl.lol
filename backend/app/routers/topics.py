from __future__ import annotations

from fastapi import APIRouter

from ..schemas import TopicSchema
from ..services.topics import list_topics

router = APIRouter(tags=["topics"])


@router.get("/topics", response_model=list[TopicSchema])
async def get_topics() -> list[TopicSchema]:
    return list_topics()
