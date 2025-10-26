#!/usr/bin/env python
"""Topic graph and management."""

import time
from typing import Any

import networkx as nx

from app.schemas import Topic


# Seed topics covering diverse domains
SEED_TOPICS = [
    # Tech
    {"id": "ai", "name": "Artificial Intelligence", "tags": ["tech", "ai", "ml"]},
    {"id": "crypto", "name": "Cryptocurrency", "tags": ["tech", "crypto", "finance"]},
    {"id": "web3", "name": "Web3", "tags": ["tech", "crypto", "decentralization"]},
    {"id": "cloud", "name": "Cloud Computing", "tags": ["tech", "infrastructure"]},
    {"id": "cybersec", "name": "Cybersecurity", "tags": ["tech", "security"]},
    {"id": "gaming", "name": "Gaming", "tags": ["tech", "entertainment", "gaming"]},
    {"id": "vr_ar", "name": "VR/AR", "tags": ["tech", "vr", "metaverse"]},
    {"id": "quantum", "name": "Quantum Computing", "tags": ["tech", "science"]},
    {"id": "robotics", "name": "Robotics", "tags": ["tech", "automation"]},
    {"id": "open_source", "name": "Open Source", "tags": ["tech", "software", "community"]},
    # Politics & Society
    {"id": "politics", "name": "Politics", "tags": ["politics", "government"]},
    {"id": "climate", "name": "Climate Change", "tags": ["environment", "science", "politics"]},
    {"id": "healthcare", "name": "Healthcare", "tags": ["health", "policy", "society"]},
    {"id": "education", "name": "Education", "tags": ["society", "learning"]},
    {"id": "privacy", "name": "Privacy Rights", "tags": ["politics", "tech", "society"]},
    {"id": "elections", "name": "Elections", "tags": ["politics", "democracy"]},
    # Markets & Finance
    {"id": "stocks", "name": "Stock Market", "tags": ["finance", "markets", "investing"]},
    {"id": "real_estate", "name": "Real Estate", "tags": ["finance", "property", "markets"]},
    {"id": "startups", "name": "Startups", "tags": ["business", "tech", "entrepreneurship"]},
    {"id": "economy", "name": "Economy", "tags": ["finance", "markets", "policy"]},
    {"id": "job_market", "name": "Job Market", "tags": ["employment", "economy", "careers"]},
    # Sports
    {"id": "football", "name": "Football", "tags": ["sports", "football"]},
    {"id": "basketball", "name": "Basketball", "tags": ["sports", "basketball"]},
    {"id": "soccer", "name": "Soccer", "tags": ["sports", "soccer", "football"]},
    {"id": "esports", "name": "Esports", "tags": ["sports", "gaming", "competitive"]},
    {"id": "fitness", "name": "Fitness", "tags": ["sports", "health", "wellness"]},
    # Pop Culture
    {"id": "movies", "name": "Movies", "tags": ["entertainment", "film", "culture"]},
    {"id": "tv", "name": "TV Shows", "tags": ["entertainment", "television", "culture"]},
    {"id": "music", "name": "Music", "tags": ["entertainment", "music", "culture"]},
    {"id": "celebrities", "name": "Celebrities", "tags": ["entertainment", "culture", "gossip"]},
    {"id": "memes", "name": "Memes", "tags": ["internet", "culture", "humor"]},
    {"id": "fashion", "name": "Fashion", "tags": ["culture", "style", "trends"]},
    # Wellness & Lifestyle
    {"id": "mental_health", "name": "Mental Health", "tags": ["wellness", "health", "psychology"]},
    {"id": "nutrition", "name": "Nutrition", "tags": ["wellness", "health", "food"]},
    {"id": "meditation", "name": "Meditation", "tags": ["wellness", "mindfulness", "health"]},
    {"id": "productivity", "name": "Productivity", "tags": ["self-improvement", "work"]},
    {"id": "travel", "name": "Travel", "tags": ["lifestyle", "adventure", "culture"]},
    # Science & Nature
    {"id": "space", "name": "Space Exploration", "tags": ["science", "space", "astronomy"]},
    {"id": "biology", "name": "Biology", "tags": ["science", "nature", "research"]},
    {"id": "physics", "name": "Physics", "tags": ["science", "research"]},
    {"id": "wildlife", "name": "Wildlife", "tags": ["nature", "conservation", "animals"]},
    # Internet & Social
    {"id": "social_media", "name": "Social Media", "tags": ["internet", "culture", "tech"]},
    {"id": "influencers", "name": "Influencers", "tags": ["internet", "culture", "marketing"]},
    {"id": "cancel_culture", "name": "Cancel Culture", "tags": ["internet", "society", "culture"]},
    {"id": "misinformation", "name": "Misinformation", "tags": ["internet", "politics", "media"]},
]

# Topic relationships (edges in the graph)
TOPIC_EDGES = [
    ("ai", "tech", 0.9),
    ("ai", "quantum", 0.3),
    ("ai", "robotics", 0.6),
    ("crypto", "web3", 0.8),
    ("crypto", "stocks", 0.4),
    ("crypto", "privacy", 0.5),
    ("gaming", "esports", 0.9),
    ("gaming", "vr_ar", 0.6),
    ("climate", "politics", 0.7),
    ("climate", "wildlife", 0.5),
    ("healthcare", "mental_health", 0.6),
    ("healthcare", "nutrition", 0.5),
    ("stocks", "economy", 0.8),
    ("startups", "open_source", 0.4),
    ("startups", "ai", 0.6),
    ("fitness", "nutrition", 0.7),
    ("fitness", "wellness", 0.6),
    ("movies", "celebrities", 0.7),
    ("tv", "celebrities", 0.6),
    ("memes", "social_media", 0.8),
    ("influencers", "social_media", 0.9),
    ("cancel_culture", "social_media", 0.7),
    ("misinformation", "social_media", 0.6),
    ("misinformation", "politics", 0.5),
    ("space", "physics", 0.6),
    ("privacy", "cybersec", 0.7),
    ("education", "productivity", 0.4),
    ("job_market", "economy", 0.6),
    ("fashion", "influencers", 0.5),
]


class TopicGraph:
    """Topic graph with trend dynamics."""

    def __init__(self):
        self.graph = nx.DiGraph()
        self._trend_scores: dict[str, float] = {}
        self._velocities: dict[str, float] = {}
        self._shocks: list[dict[str, Any]] = []  # active shocks
        self._last_tick = time.time()

        # Build initial graph
        self._initialize_graph()

    def _initialize_graph(self) -> None:
        """Initialize graph with seed topics and edges."""
        for topic_data in SEED_TOPICS:
            self.graph.add_node(
                topic_data["id"],
                name=topic_data["name"],
                tags=topic_data["tags"],
            )
            self._trend_scores[topic_data["id"]] = 0.1  # baseline

        for source, target, weight in TOPIC_EDGES:
            if source in self.graph and target in self.graph:
                self.graph.add_edge(source, target, weight=weight)

    def get_topic(self, topic_id: str) -> Topic | None:
        """Get a topic by ID."""
        if topic_id not in self.graph:
            return None

        node_data = self.graph.nodes[topic_id]
        related = [
            edge[1] for edge in self.graph.out_edges(topic_id)
        ]

        return Topic(
            id=topic_id,
            name=node_data["name"],
            tags=node_data["tags"],
            related=related,
            trend_score=self._trend_scores.get(topic_id, 0.0),
        )

    def get_all_topics(self) -> list[Topic]:
        """Get all topics."""
        return [
            self.get_topic(topic_id)
            for topic_id in self.graph.nodes
            if self.get_topic(topic_id) is not None
        ]

    def inject_shock(self, topic_id: str, magnitude: float, half_life_s: float) -> bool:
        """Inject a trend shock."""
        if topic_id not in self.graph:
            return False

        self._shocks.append(
            {
                "topic_id": topic_id,
                "magnitude": magnitude,
                "half_life_s": half_life_s,
                "created_at": time.time(),
            }
        )
        return True

    def tick(self, alpha: float = 0.2, beta: float = 0.3, recency_decay: float = 0.95) -> None:
        """
        Update trend scores via dynamics.

        Simple model:
        - Shocks add impulse
        - Neighbor influence spreads through edges
        - Recency decay pulls scores toward baseline
        """
        now = time.time()
        dt = now - self._last_tick
        self._last_tick = now

        # Apply shocks
        shock_contributions: dict[str, float] = {}
        for shock in self._shocks[:]:
            age = now - shock["created_at"]
            decay_factor = 0.5 ** (age / shock["half_life_s"])

            if decay_factor < 0.01:
                self._shocks.remove(shock)
                continue

            topic_id = shock["topic_id"]
            shock_contributions[topic_id] = (
                shock_contributions.get(topic_id, 0.0)
                + shock["magnitude"] * decay_factor
            )

        # Update each topic
        new_scores = {}
        for topic_id in self.graph.nodes:
            current = self._trend_scores.get(topic_id, 0.1)

            # Shock contribution
            shock_boost = shock_contributions.get(topic_id, 0.0)

            # Neighbor influence
            neighbor_influence = 0.0
            in_edges = list(self.graph.in_edges(topic_id, data=True))
            if in_edges:
                for source, _, edge_data in in_edges:
                    weight = edge_data.get("weight", 0.5)
                    neighbor_score = self._trend_scores.get(source, 0.1)
                    neighbor_influence += weight * neighbor_score
                neighbor_influence /= len(in_edges)

            # Combined update
            new_score = (
                alpha * current
                + beta * neighbor_influence
                + shock_boost
            )

            # Recency decay toward baseline
            baseline = 0.1
            new_score = new_score * recency_decay + baseline * (1 - recency_decay)

            new_scores[topic_id] = max(0.0, min(new_score, 10.0))  # clamp

        # Compute velocities
        for topic_id, new_score in new_scores.items():
            old_score = self._trend_scores.get(topic_id, 0.1)
            self._velocities[topic_id] = (new_score - old_score) / max(dt, 0.1)

        self._trend_scores = new_scores

    def get_trend_snapshot(self) -> list[dict[str, Any]]:
        """Get current trend scores and velocities."""
        return [
            {
                "topic_id": topic_id,
                "trend_score": self._trend_scores.get(topic_id, 0.0),
                "velocity": self._velocities.get(topic_id, 0.0),
            }
            for topic_id in self.graph.nodes
        ]

    def get_trend_score(self, topic_id: str) -> float:
        """Get trend score for a topic."""
        return self._trend_scores.get(topic_id, 0.0)


# Global topic graph instance
topic_graph = TopicGraph()
