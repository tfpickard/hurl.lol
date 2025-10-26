from __future__ import annotations

from collections import deque
from datetime import datetime
from threading import RLock
from typing import Deque, Dict, Iterable, List, Optional

from ..schemas import PersonaSchema, PostSchema, TopicSchema


class MemoryStore:
    """In-memory storage with a bounded post window."""

    def __init__(self, *, post_window: int = 5000) -> None:
        self._personas: Dict[str, PersonaSchema] = {}
        self._topics: Dict[str, TopicSchema] = {}
        self._posts: Deque[PostSchema] = deque(maxlen=post_window)
        self._lock = RLock()

    # Personas
    def upsert_persona(self, persona: PersonaSchema) -> None:
        with self._lock:
            self._personas[persona.id] = persona

    def get_personas(self) -> List[PersonaSchema]:
        with self._lock:
            return list(self._personas.values())

    def get_persona(self, persona_id: str) -> Optional[PersonaSchema]:
        with self._lock:
            return self._personas.get(persona_id)

    # Topics
    def upsert_topic(self, topic: TopicSchema) -> None:
        with self._lock:
            self._topics[topic.id] = topic

    def get_topics(self) -> List[TopicSchema]:
        with self._lock:
            return list(self._topics.values())

    def get_topic(self, topic_id: str) -> Optional[TopicSchema]:
        with self._lock:
            return self._topics.get(topic_id)

    # Posts
    def add_post(self, post: PostSchema) -> None:
        with self._lock:
            self._posts.append(post)

    def recent_posts(self, limit: int = 200) -> List[PostSchema]:
        with self._lock:
            return list(list(self._posts)[-limit:])

    def posts_by_persona(self, persona_id: str, limit: int = 50) -> List[PostSchema]:
        with self._lock:
            return [post for post in reversed(self._posts) if post.persona_id == persona_id][:limit]

    def clear_posts(self) -> None:
        with self._lock:
            self._posts.clear()


_store = MemoryStore()


def get_store() -> MemoryStore:
    return _store
