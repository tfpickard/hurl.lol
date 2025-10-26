from __future__ import annotations

import random
from typing import Dict


def simulate_metrics(rng: random.Random, influence: float, mode: str) -> Dict[str, int]:
    base = 5 if mode == "emergent" else 2
    likes = int(rng.gammavariate(1.5 + influence, 2.0)) + base
    replies = max(0, int(rng.gauss(influence, 1)))
    quotes = max(0, int(rng.random() * influence * 2))
    impressions = int((likes + 1) * rng.uniform(30, 80))
    return {
        "likes": likes,
        "replies": replies,
        "quotes": quotes,
        "impressions": impressions,
    }
