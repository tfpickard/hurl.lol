from __future__ import annotations

import random
from typing import Dict, List

from ..schemas import TopicSchema
from ..store.memory import get_store


TOPIC_DEFINITIONS = [
    ("ai", "AI Futures", ["ml", "automation", "agents"], ["startups", "ethics", "markets"]),
    ("startups", "Founder Grind", ["funding", "pitch", "demo"], ["ai", "markets", "product"]),
    ("governance", "Governance", ["policy", "civic", "regulation"], ["climate", "markets", "ai"]),
    ("climate", "Climate Pulse", ["energy", "carbon", "weather"], ["governance", "wellness"]),
    ("sportsball", "Sportsball", ["nba", "world cup", "stats"], ["markets", "memes"]),
    ("markets", "Markets", ["stonks", "macro", "rates"], ["ai", "crypto", "startups"]),
    ("memes", "Meme Frenzy", ["viral", "lol", "trend"], ["pop_culture", "gaming"]),
    ("food", "Food", ["recipe", "snack", "chef"], ["wellness", "travel"]),
    ("music", "Music", ["playlist", "gig", "vibe"], ["pop_culture", "memes"]),
    ("crypto", "Crypto", ["chain", "defi", "token"], ["markets", "ai"]),
    ("space", "Space", ["launch", "orbit", "mars"], ["ai", "startups"]),
    ("wellness", "Wellness", ["meditation", "sleep", "balance"], ["food", "climate"]),
]


def ensure_topic_graph() -> Dict[str, TopicSchema]:
    store = get_store()
    topics = {topic.id: topic for topic in store.get_topics()}
    if topics:
        return topics

    for topic_id, name, tags, related in TOPIC_DEFINITIONS:
        topic = TopicSchema(id=topic_id, name=name, tags=tags, trend_score=0.1)
        topic.related = {
            target: round(random.Random(hash((topic_id, target)) & 0xFFFFFFFF).uniform(0.1, 0.9), 3)
            for target in related
        }
        store.upsert_topic(topic)
        topics[topic_id] = topic
    return topics


def list_topics() -> List[TopicSchema]:
    return get_store().get_topics()


def update_topic_score(topic_id: str, delta: float) -> TopicSchema | None:
    store = get_store()
    topic = store.get_topic(topic_id)
    if topic is None:
        return None
    topic.trend_score = max(topic.trend_score + delta, 0.0)
    store.upsert_topic(topic)
    return topic
