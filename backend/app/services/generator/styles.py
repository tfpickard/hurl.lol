from __future__ import annotations

import random
from typing import Dict, List


EMOJI_BANK = ["😂", "🔥", "🤖", "🌱", "💥", "🌀", "🏀", "🎧", "💤", "📈", "🚀", "🥲"]
HASHTAG_BANK = [
    "#Hurl",
    "#SyntheticVibes",
    "#AI",
    "#LateStageInternet",
    "#Vibes",
    "#Markets",
    "#Sportsball",
    "#Wellness",
]
LINK_BANK = [
    "https://hurl.lol",
    "https://hurl.rest",
    "https://example.com/hurl",
]


def apply_decorators(
    text: str,
    *,
    persona_emojis: List[str],
    hashtag_propensity: float,
    link_propensity: float,
    rng: random.Random,
) -> Dict[str, object]:
    tokens = text.split()
    emojis_used: List[str] = []
    hashtags_used: List[str] = []
    links_used: List[str] = []

    if rng.random() < hashtag_propensity:
        tag = rng.choice(HASHTAG_BANK)
        tokens.append(tag)
        hashtags_used.append(tag)

    if rng.random() < link_propensity:
        link = rng.choice(LINK_BANK)
        tokens.append(link)
        links_used.append(link)

    emoji_count = rng.randint(0, min(3, len(persona_emojis)))
    for _ in range(emoji_count):
        emoji = rng.choice(persona_emojis or EMOJI_BANK)
        emojis_used.append(emoji)
        tokens.append(emoji)

    mutated = " ".join(tokens)
    style_metrics = {
        "emojis": len(emojis_used),
        "hashtags": len(hashtags_used),
        "links": len(links_used),
        "caps": round(min(1.0, rng.random() * 0.2), 3),
    }
    return {"text": mutated, "style": style_metrics}
