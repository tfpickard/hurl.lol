from __future__ import annotations

import asyncio
import contextlib
from collections import defaultdict
from dataclasses import dataclass
from typing import Dict, List

from ..schemas import ShockRequest, TopicSchema
from ..store.memory import get_store
from .topics import ensure_topic_graph


@dataclass
class Shock:
    topic_id: str
    magnitude: float
    half_life_s: float
    created_at: float

    def value_at(self, now: float) -> float:
        elapsed = max(now - self.created_at, 0.0)
        decay = 0.5 ** (elapsed / self.half_life_s)
        return self.magnitude * decay


class TrendEngine:
    def __init__(self) -> None:
        self._graph = ensure_topic_graph()
        self._shocks: List[Shock] = []
        self._lock = asyncio.Lock()
        self._task: asyncio.Task[None] | None = None
        self._running = False

    async def start(self) -> None:
        if not self._task:
            self._running = True
            self._task = asyncio.create_task(self._run())

    async def stop(self) -> None:
        if self._task:
            self._running = False
            self._task.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await self._task
            self._task = None

    async def _run(self) -> None:
        while self._running:
            await self.tick()
            await asyncio.sleep(3.0)

    async def tick(self) -> None:
        store = get_store()
        now = asyncio.get_event_loop().time()
        shocks = [shock for shock in self._shocks if shock.value_at(now) > 0.01]
        self._shocks = shocks

        posts = store.recent_posts(limit=500)
        persona_influence: Dict[str, float] = defaultdict(float)
        for post in posts:
            persona_influence[post.persona_id] += post.metrics.impressions / 1000 + 1

        for topic in store.get_topics():
            base = topic.trend_score * 0.92
            peer = 0.0
            for post in posts:
                if topic.id in post.topics:
                    persona_score = persona_influence.get(post.persona_id, 1.0)
                    peer += persona_score * 0.05
            shock_value = sum(shock.value_at(now) for shock in shocks if shock.topic_id == topic.id)
            trend = max(base + peer + shock_value, 0.01)
            topic.trend_score = min(trend, 10.0)
            store.upsert_topic(topic)

    async def inject_shock(self, request: ShockRequest) -> None:
        now = asyncio.get_event_loop().time()
        self._shocks.append(
            Shock(
                topic_id=request.topic_id,
                magnitude=request.magnitude,
                half_life_s=request.half_life_s,
                created_at=now,
            )
        )

    def trend_snapshot(self) -> List[TopicSchema]:
        return get_store().get_topics()


_engine = TrendEngine()


def get_trend_engine() -> TrendEngine:
    return _engine
