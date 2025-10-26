#!/usr/bin/env python
"""Trend engine with emergent dynamics."""

import asyncio
import math
from typing import Any

import numpy as np
from scipy.special import expit  # sigmoid

from app.services.rng import rng_manager
from app.services.topics import topic_graph


class TrendEngine:
    """
    Manages emergent topic adoption dynamics.

    Computes adoption probability per persona:
    p = σ(α*trend + β*peer_influence + γ*interest_match + δ*recency_decay + ε*shock)
    """

    def __init__(self, tick_interval: float = 5.0):
        self.tick_interval = tick_interval
        self._task: asyncio.Task | None = None
        self._running = False

        # Coefficients for adoption probability
        self.alpha = 0.3  # trend weight
        self.beta = 0.4  # peer influence weight
        self.gamma = 0.5  # interest match weight
        self.delta = -0.2  # recency decay weight
        self.epsilon = 0.6  # shock weight

    async def start(self) -> None:
        """Start the trend engine background task."""
        if self._running:
            return

        self._running = True
        self._task = asyncio.create_task(self._tick_loop())

    async def stop(self) -> None:
        """Stop the trend engine."""
        self._running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass

    async def _tick_loop(self) -> None:
        """Background loop that updates trends."""
        while self._running:
            try:
                topic_graph.tick()
                await asyncio.sleep(self.tick_interval)
            except asyncio.CancelledError:
                break
            except Exception as e:
                # Log error but keep running
                print(f"Trend tick error: {e}")
                await asyncio.sleep(self.tick_interval)

    def compute_topic_adoption_prob(
        self,
        persona_interests: dict[str, float],
        peer_influence_scores: dict[str, float],
        recent_topics: list[str],
        seed: int | None = None,
    ) -> dict[str, float]:
        """
        Compute adoption probability for each topic given persona state.

        Args:
            persona_interests: dict of topic_id -> interest weight (0-1)
            peer_influence_scores: dict of topic_id -> peer influence (0-1)
            recent_topics: list of recently used topic IDs (for recency decay)
            seed: RNG seed

        Returns:
            dict of topic_id -> adoption probability (0-1)
        """
        rng = rng_manager.get_rng(seed)
        probs = {}

        for topic_id in topic_graph.graph.nodes:
            trend_score = topic_graph.get_trend_score(topic_id)
            interest = persona_interests.get(topic_id, 0.0)
            peer_influence = peer_influence_scores.get(topic_id, 0.0)

            # Recency decay: penalize if topic was used recently
            recency_penalty = 0.0
            if topic_id in recent_topics:
                # exponential decay based on position
                idx = recent_topics.index(topic_id)
                recency_penalty = math.exp(-idx / 3.0)

            # Combined logit
            logit = (
                self.alpha * trend_score
                + self.beta * peer_influence
                + self.gamma * interest
                - self.delta * recency_penalty
            )

            # Sigmoid to probability
            prob = float(expit(logit))
            probs[topic_id] = prob

        return probs

    def sample_topics(
        self,
        adoption_probs: dict[str, float],
        count: int = 1,
        seed: int | None = None,
    ) -> list[str]:
        """
        Sample topics based on adoption probabilities.

        Args:
            adoption_probs: dict of topic_id -> prob
            count: number of topics to sample
            seed: RNG seed

        Returns:
            list of topic IDs
        """
        if not adoption_probs:
            return []

        topic_ids = list(adoption_probs.keys())
        probs = np.array([adoption_probs[tid] for tid in topic_ids])

        # Normalize
        prob_sum = probs.sum()
        if prob_sum > 0:
            probs = probs / prob_sum
        else:
            probs = np.ones(len(probs)) / len(probs)

        rng = rng_manager.get_rng(seed)
        sampled = rng.choice(topic_ids, size=min(count, len(topic_ids)), replace=False, p=probs)

        return sampled.tolist() if isinstance(sampled, np.ndarray) else [sampled]


# Global trend engine instance
trend_engine = TrendEngine()
