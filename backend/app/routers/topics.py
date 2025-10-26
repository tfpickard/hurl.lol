#!/usr/bin/env python
"""Topics router."""

from fastapi import APIRouter, HTTPException

from app.schemas import Topic, TopicListResponse
from app.services.topics import topic_graph

router = APIRouter(prefix="/v1/topics", tags=["topics"])


@router.get("", response_model=TopicListResponse)
async def list_topics() -> TopicListResponse:
    """List all topics."""
    topics = topic_graph.get_all_topics()
    return TopicListResponse(topics=topics, count=len(topics))


@router.get("/{topic_id}", response_model=Topic)
async def get_topic(topic_id: str) -> Topic:
    """Get a specific topic."""
    topic = topic_graph.get_topic(topic_id)
    if not topic:
        raise HTTPException(status_code=404, detail="Topic not found")
    return topic
