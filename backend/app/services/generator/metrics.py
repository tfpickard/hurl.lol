#!/usr/bin/env python
"""Simulated engagement metrics and influence calculation."""

from app.schemas import Persona, PostMetrics
from app.services.rng import rng_manager


class MetricsSimulator:
    """Simulates engagement metrics for posts."""

    def __init__(self):
        pass

    def compute_base_reach(self, persona: Persona) -> float:
        """Compute base reach multiplier from persona influence."""
        # Influence score (0-1) maps to reach multiplier (1-100)
        return 1.0 + persona.influence_score * 99.0

    def simulate_metrics(
        self,
        persona: Persona,
        topics: list[str],
        text: str,
        mode: str,
        seed: int | None = None,
    ) -> PostMetrics:
        """
        Simulate engagement metrics.

        Factors:
        - Persona influence
        - Topic trend scores
        - Text length and style
        - Mode (emergent has more variance)
        """
        base_reach = self.compute_base_reach(persona)

        # Topic boost (higher trend = more impressions)
        topic_boost = 1.0
        if topics:
            # For simplicity, use a fixed boost
            # In full implementation, query topic trend scores
            topic_boost = 1.0 + rng_manager.random(seed=seed) * 0.5

        # Text length factor (longer = slightly more engagement)
        word_count = len(text.split())
        length_factor = min(1.0 + word_count / 100.0, 2.0)

        # Impressions
        impressions_mean = base_reach * topic_boost * length_factor * 50
        impressions = max(
            int(rng_manager.exponential(scale=impressions_mean, seed=seed)), 1
        )

        # Engagement rate (likes, replies, quotes as % of impressions)
        like_rate = rng_manager.beta(2, 10, seed=seed)  # ~10-20%
        reply_rate = rng_manager.beta(1, 20, seed=seed)  # ~2-5%
        quote_rate = rng_manager.beta(1, 50, seed=seed)  # ~1-2%

        likes = int(impressions * like_rate)
        replies = int(impressions * reply_rate)
        quotes = int(impressions * quote_rate)

        return PostMetrics(
            likes=likes,
            replies=replies,
            quotes=quotes,
            impressions=impressions,
        )


# Global metrics simulator instance
metrics_simulator = MetricsSimulator()
