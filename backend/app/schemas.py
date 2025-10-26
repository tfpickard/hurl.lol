from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from datetime import datetime
from typing import Dict, List, Optional


def _now() -> datetime:
    return datetime.utcnow()


@dataclass(slots=True)
class StyleMetrics:
    emojis: int = 0
    hashtags: int = 0
    links: int = 0
    caps: float = 0.0


@dataclass(slots=True)
class LineageInfo:
    template: str
    influences: List[str] = field(default_factory=list)


@dataclass(slots=True)
class EngagementMetrics:
    likes: int = 0
    replies: int = 0
    quotes: int = 0
    impressions: int = 0


@dataclass(slots=True)
class PostSchema:
    id: str
    text: str
    persona_id: str
    created_at: datetime
    mode: str
    topics: List[str]
    language: str
    style: StyleMetrics
    lineage: LineageInfo
    metrics: EngagementMetrics
    toxicity: float = 0.0

    def dict(self) -> Dict[str, object]:
        payload = asdict(self)
        payload["created_at"] = self.created_at.isoformat() + "Z"
        return payload

    def json(self) -> str:
        return json.dumps(self.dict())


@dataclass(slots=True)
class PersonaSchema:
    id: str
    display_name: str
    handle: str
    bio: str
    interests: Dict[str, float]
    slang: List[str] = field(default_factory=list)
    emoji_preference: List[str] = field(default_factory=list)
    punctuation: str = "balanced"
    link_propensity: float = 0.1
    hashtag_propensity: float = 0.2
    reading_level: str = "medium"
    cynicism: float = 0.5
    hot_take: float = 0.5
    posting_curve: List[float] = field(default_factory=list)
    burstiness: float = 0.3
    reply_propensity: float = 0.2
    quote_propensity: float = 0.1
    languages: List[str] = field(default_factory=lambda: ["en"])
    stances: Dict[str, float] = field(default_factory=dict)
    toxicity: float = 0.1
    profanity_mask: List[str] = field(default_factory=list)
    influence: float = 0.1

    def dict(self) -> Dict[str, object]:
        return asdict(self)


@dataclass(slots=True)
class TopicSchema:
    id: str
    name: str
    tags: List[str]
    trend_score: float = 0.0
    related: Dict[str, float] = field(default_factory=dict)

    def dict(self) -> Dict[str, object]:
        return asdict(self)


@dataclass(slots=True)
class GenerateRequest:
    count: int = 1
    mode: str = "pure_random"
    topics: List[str] = field(default_factory=list)
    persona_ids: List[str] = field(default_factory=list)
    languages: List[str] = field(default_factory=list)
    toxicity_max: float = 1.0
    reading_level: Optional[str] = None
    seed: Optional[int] = None


@dataclass(slots=True)
class SeedRequest:
    seed: int


@dataclass(slots=True)
class ShockRequest:
    topic_id: str
    magnitude: float
    half_life_s: float = 60.0
