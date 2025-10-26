from __future__ import annotations

import random
from typing import List

from ..schemas import PersonaSchema
from ..store.memory import get_store


STANCE_AXES = [
    "tech",
    "politics",
    "sports",
    "markets",
    "pop_culture",
    "wellness",
]


TOPIC_IDS = [
    "ai",
    "startups",
    "governance",
    "climate",
    "sportsball",
    "markets",
    "memes",
    "food",
    "music",
    "crypto",
    "space",
]


def _random_curve(rand: random.Random) -> List[float]:
    base = [max(rand.gauss(0.5, 0.2), 0.05) for _ in range(24)]
    total = sum(base)
    return [round(x / total, 4) for x in base]


def _persona_from_index(idx: int) -> PersonaSchema:
    rand = random.Random(10_000 + idx)
    names = [
        "Alex Rivers",
        "Jordan Vega",
        "Riley Chen",
        "Morgan Drift",
        "Sky Patel",
        "Dak Harper",
        "Reese Calder",
        "Quinn Solaris",
        "Jules Evergreen",
        "Hayes Orbit",
    ]
    bios = [
        "Plotting the future of vibes and hardware hacks.",
        "Certified chaos wrangler with a caffeine subscription.",
        "Synthwave playlists, long walks through algorithm forests.",
        "Hot takes on cold brew and quantum markets.",
        "Trying to live, laugh, and lasso latency spikes.",
    ]
    name = names[idx % len(names)]
    handle = f"{name.split()[0].lower()}_{idx:03d}"
    interests = {topic: round(rand.random(), 3) for topic in TOPIC_IDS}
    total_interest = sum(interests.values()) or 1.0
    interests = {k: v / total_interest for k, v in interests.items()}
    stances = {axis: round(rand.uniform(-1, 1), 3) for axis in STANCE_AXES}
    emoji_pool = ["🔥", "😂", "🤖", "🌱", "🚀", "💼", "🎧", "🏀", "🧠", "✨"]
    emoji_preference = rand.sample(emoji_pool, k=rand.randint(2, 5))
    slang = rand.sample(
        ["lol", "sheesh", "ngl", "big yikes", "chef's kiss", "bet", "fax"],
        k=rand.randint(1, 4),
    )
    languages = ["en"]
    if rand.random() < 0.25:
        languages.append(rand.choice(["es", "fr", "de", "pt"]))
    toxicity = round(rand.uniform(0.02, 0.35), 3)
    return PersonaSchema(
        id=f"persona_{idx:03d}",
        display_name=name,
        handle=f"@{handle}",
        bio=bios[idx % len(bios)],
        interests=interests,
        slang=slang,
        emoji_preference=emoji_preference,
        punctuation=rand.choice(["minimal", "balanced", "exuberant"]),
        link_propensity=round(rand.uniform(0.05, 0.35), 3),
        hashtag_propensity=round(rand.uniform(0.05, 0.45), 3),
        reading_level=rand.choice(["low", "medium", "high"]),
        cynicism=round(rand.random(), 3),
        hot_take=round(rand.random(), 3),
        posting_curve=_random_curve(rand),
        burstiness=round(rand.uniform(0.1, 0.7), 3),
        reply_propensity=round(rand.uniform(0.05, 0.4), 3),
        quote_propensity=round(rand.uniform(0.02, 0.3), 3),
        languages=languages,
        stances=stances,
        toxicity=toxicity,
        profanity_mask=[],
        influence=round(rand.uniform(0.1, 0.9), 3),
    )


def ensure_seed_personas(count: int = 100) -> List[PersonaSchema]:
    store = get_store()
    personas = store.get_personas()
    if len(personas) >= count:
        return personas
    generated = [_persona_from_index(i) for i in range(count)]
    for persona in generated:
        store.upsert_persona(persona)
    return store.get_personas()


def list_personas() -> List[PersonaSchema]:
    return get_store().get_personas()


def add_persona(persona: PersonaSchema) -> None:
    get_store().upsert_persona(persona)
