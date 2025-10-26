#!/usr/bin/env python
"""Pydantic schemas for Hurl API."""

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


# ============================================================================
# Post schemas
# ============================================================================


class StyleMetrics(BaseModel):
    """Style metrics for a post."""

    emojis: int = 0
    hashtags: int = 0
    links: int = 0
    caps: float = 0.0  # proportion of caps


class PostLineage(BaseModel):
    """Post lineage tracking influences."""

    template: str | None = None
    influences: list[str] = Field(default_factory=list)  # post IDs


class PostMetrics(BaseModel):
    """Simulated engagement metrics."""

    likes: int = 0
    replies: int = 0
    quotes: int = 0
    impressions: int = 0


class Post(BaseModel):
    """A generated post."""

    id: str
    text: str
    persona_id: str
    created_at: datetime
    mode: Literal["emergent", "pure_random"]
    topics: list[str] = Field(default_factory=list)
    language: str = "en"
    style: StyleMetrics = Field(default_factory=StyleMetrics)
    lineage: PostLineage = Field(default_factory=PostLineage)
    metrics: PostMetrics = Field(default_factory=PostMetrics)
    toxicity: float = 0.0


class GenerateRequest(BaseModel):
    """Request to generate posts."""

    count: int = Field(default=10, ge=1, le=1000)
    mode: Literal["emergent", "pure_random"] = "emergent"
    topics: list[str] = Field(default_factory=list)
    persona_ids: list[str] = Field(default_factory=list)
    language: list[str] = Field(default_factory=lambda: ["en"])
    toxicity_max: float = Field(default=0.3, ge=0.0, le=1.0)
    reading_level: int | None = Field(default=None, ge=1, le=20)
    seed: int | None = None


class GenerateResponse(BaseModel):
    """Response with generated posts."""

    posts: list[Post]
    count: int
    seed: int | None = None


# ============================================================================
# Persona schemas
# ============================================================================


class PersonaStyle(BaseModel):
    """Style markers for a persona."""

    slang_set: list[str] = Field(default_factory=list)
    emoji_preference: float = Field(default=0.5, ge=0.0, le=1.0)
    punctuation_quirks: list[str] = Field(default_factory=list)
    link_propensity: float = Field(default=0.1, ge=0.0, le=1.0)
    hashtag_propensity: float = Field(default=0.2, ge=0.0, le=1.0)
    reading_level: int = Field(default=8, ge=1, le=20)
    cynicism: float = Field(default=0.5, ge=0.0, le=1.0)
    hot_take_factor: float = Field(default=0.3, ge=0.0, le=1.0)


class PersonaBehavior(BaseModel):
    """Behavioral traits for a persona."""

    posting_rate_per_hour: float = Field(default=1.0, ge=0.0)
    burstiness: float = Field(default=0.5, ge=0.0, le=1.0)
    reply_propensity: float = Field(default=0.3, ge=0.0, le=1.0)
    quote_propensity: float = Field(default=0.1, ge=0.0, le=1.0)
    language_distribution: dict[str, float] = Field(
        default_factory=lambda: {"en": 1.0}
    )


class PersonaStances(BaseModel):
    """Opinion vectors for a persona."""

    tech: float = Field(default=0.0, ge=-1.0, le=1.0)
    politics: float = Field(default=0.0, ge=-1.0, le=1.0)
    sports: float = Field(default=0.0, ge=-1.0, le=1.0)
    markets: float = Field(default=0.0, ge=-1.0, le=1.0)
    pop_culture: float = Field(default=0.0, ge=-1.0, le=1.0)
    wellness: float = Field(default=0.0, ge=-1.0, le=1.0)


class Persona(BaseModel):
    """A synthetic user persona."""

    id: str
    display_name: str
    handle: str
    bio: str
    interests: dict[str, float] = Field(
        default_factory=dict
    )  # topic_id -> weight (0-1)
    style: PersonaStyle = Field(default_factory=PersonaStyle)
    behavior: PersonaBehavior = Field(default_factory=PersonaBehavior)
    stances: PersonaStances = Field(default_factory=PersonaStances)
    toxicity: float = Field(default=0.1, ge=0.0, le=1.0)
    influence_score: float = Field(default=0.5, ge=0.0, le=1.0)


class CreatePersonaRequest(BaseModel):
    """Request to create a custom persona."""

    display_name: str
    handle: str
    bio: str = ""
    interests: dict[str, float] = Field(default_factory=dict)
    style: PersonaStyle | None = None
    behavior: PersonaBehavior | None = None
    stances: PersonaStances | None = None
    toxicity: float = Field(default=0.1, ge=0.0, le=1.0)


# ============================================================================
# Topic schemas
# ============================================================================


class Topic(BaseModel):
    """A topic with trend data."""

    id: str
    name: str
    tags: list[str] = Field(default_factory=list)
    related: list[str] = Field(default_factory=list)  # topic IDs
    trend_score: float = 0.0


class TopicListResponse(BaseModel):
    """Response with list of topics."""

    topics: list[Topic]
    count: int


# ============================================================================
# Admin schemas
# ============================================================================


class ShockRequest(BaseModel):
    """Request to inject a trend shock."""

    topic_id: str
    magnitude: float = Field(ge=0.0, le=10.0)
    half_life_s: float = Field(default=300.0, ge=1.0)


class TrendSnapshot(BaseModel):
    """Snapshot of current trend scores."""

    topic_id: str
    trend_score: float
    velocity: float


class SeedRequest(BaseModel):
    """Request to set global RNG seed."""

    seed: int


class SeedResponse(BaseModel):
    """Response after setting seed."""

    seed: int
    message: str


# ============================================================================
# Health schemas
# ============================================================================


class HealthResponse(BaseModel):
    """Health check response."""

    status: Literal["ok", "degraded", "error"]
    version: str = "0.1.0"
    mode: str = "dev"
    llm_enabled: bool = False
    persistence_enabled: bool = False
