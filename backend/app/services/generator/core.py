from __future__ import annotations

import random
from datetime import datetime, timezone
from typing import Iterable, List, Sequence

from ...schemas import EngagementMetrics, LineageInfo, PersonaSchema, PostSchema, StyleMetrics
from ...store.memory import get_store
from ..personas import ensure_seed_personas
from ..rng import get_rng
from ..topics import ensure_topic_graph
from ...utils.ids import ulid
from .metrics import simulate_metrics
from .styles import apply_decorators

TEMPLATES = {
    "hot_take_v3": [
        "{hook}! {stance} {topic} is about to {outcome} and nobody is ready.",
        "{hook}. {topic} discourse is {vibe} and I'm {reaction}.",
    ],
    "threadlet_v2": [
        "Thread time 🧵 {hook}. Step 1: {step1}. Step 2: {step2}.", 
        "Quick thread: {hook}. then {step1} / {step2} / {reaction}"
    ],
    "one_liner": [
        "{hook}.", "{topic} {reaction}", "{stance} {topic}? {outcome}!"
    ],
}

HOOKS = [
    "okay hear me out",
    "plot twist",
    "tiny reminder",
    "spicy take",
    "morning brain dump",
    "midnight download",
]
OUTCOMES = ["break", "explode", "change", "reset", "pivot"]
REACTIONS = ["screaming", "unbothered", "hyped", "sleeping", "plotting"]
VIBES = ["feral", "glorious", "messy", "delicate"]
STEP_FRAGMENTS = ["do the reps", "ship the beta", "hydrate", "call your mentor", "touch grass"]


class PostGenerator:
    def __init__(self) -> None:
        self.store = get_store()
        ensure_seed_personas()
        ensure_topic_graph()

    def _persona_pool(self, persona_ids: Sequence[str]) -> List[PersonaSchema]:
        personas = self.store.get_personas()
        if persona_ids:
            personas = [p for p in personas if p.id in persona_ids]
        if not personas:
            raise ValueError("No personas available for generation")
        return personas

    def _choose_persona(
        self,
        personas: Sequence[PersonaSchema],
        rng: random.Random,
        topics: Sequence[str],
    ) -> PersonaSchema:
        weights = []
        for persona in personas:
            if topics:
                score = sum(persona.interests.get(topic, 0.01) for topic in topics)
            else:
                score = 1.0
            weights.append(score + persona.influence * 0.1)
        total = sum(weights)
        probs = [w / total for w in weights]
        return rng.choices(personas, weights=probs, k=1)[0]

    def _choose_topics(self, persona: PersonaSchema, rng: random.Random, request_topics: Sequence[str]) -> List[str]:
        if request_topics:
            return list(request_topics)
        topics = list(persona.interests.keys())
        rng.shuffle(topics)
        count = rng.randint(1, min(3, len(topics)))
        return topics[:count]

    def _choose_language(self, persona: PersonaSchema, rng: random.Random, allowed: Sequence[str]) -> str:
        languages = persona.languages
        if allowed:
            languages = [lang for lang in languages if lang in allowed] or list(allowed)
        return rng.choice(languages)

    def _base_text(self, rng: random.Random, template_key: str, topic_label: str) -> str:
        template = rng.choice(TEMPLATES[template_key])
        text = template.format(
            hook=rng.choice(HOOKS),
            stance=rng.choice(["real talk", "friendly reminder", "micro take"]),
            topic=topic_label,
            outcome=rng.choice(OUTCOMES),
            vibe=rng.choice(VIBES),
            reaction=rng.choice(REACTIONS),
            step1=rng.choice(STEP_FRAGMENTS),
            step2=rng.choice(STEP_FRAGMENTS),
        )
        return text

    def _generate_text(self, persona: PersonaSchema, topics: List[str], rng: random.Random) -> tuple[str, str]:
        template_key = rng.choice(list(TEMPLATES.keys()))
        topic_label = rng.choice(topics)
        text = self._base_text(rng, template_key, topic_label)
        words = text.split()
        target_length = rng.randint(12, 50)
        while len(words) < target_length:
            words.append(rng.choice(words))
        max_len = min(len(words), 120)
        text = " ".join(words[: rng.randint(8, max_len)])
        return text, template_key

    def _sanitize(self, text: str, persona: PersonaSchema, toxicity: float) -> str:
        cleaned = text
        for banned in persona.profanity_mask:
            cleaned = cleaned.replace(banned, "*")
        if toxicity < 0.2:
            cleaned = cleaned.replace("spicy", "spicy-ish")
        return cleaned

    def _choose_influences(self, persona: PersonaSchema, rng: random.Random) -> List[str]:
        recent = self.store.recent_posts(limit=100)
        if not recent:
            return []
        matches = [post for post in recent if post.persona_id != persona.id]
        rng.shuffle(matches)
        return [post.id for post in matches[: rng.randint(0, 3)]]

    def generate(
        self,
        *,
        count: int,
        mode: str,
        topics: Sequence[str],
        persona_ids: Sequence[str],
        languages: Sequence[str],
        toxicity_max: float,
        reading_level: str | None,
        seed: int | None,
    ) -> List[PostSchema]:
        rng_service = get_rng()
        with rng_service.using_seed(seed) as generator:
            base_seed = generator.randint(0, 2**32 - 1)
            rng = random.Random(base_seed)
        personas = self._persona_pool(persona_ids)
        posts: List[PostSchema] = []
        for _ in range(count):
            persona = self._choose_persona(personas, rng, topics)
            chosen_topics = self._choose_topics(persona, rng, topics)
            language = self._choose_language(persona, rng, languages)
            raw_text, template_key = self._generate_text(persona, chosen_topics, rng)
            sanitized = self._sanitize(raw_text, persona, min(persona.toxicity, toxicity_max))
            decoration = apply_decorators(
                sanitized,
                persona_emojis=persona.emoji_preference,
                hashtag_propensity=persona.hashtag_propensity,
                link_propensity=persona.link_propensity,
                rng=rng,
            )
            metrics_data = simulate_metrics(rng, persona.influence, mode)
            influences = self._choose_influences(persona, rng)
            post = PostSchema(
                id=ulid(),
                text=decoration["text"],
                persona_id=persona.id,
                created_at=datetime.now(timezone.utc),
                mode=mode,
                topics=list(chosen_topics),
                language=language,
                style=StyleMetrics(**decoration["style"]),
                lineage=LineageInfo(template=template_key, influences=influences),
                metrics=EngagementMetrics(**metrics_data),
                toxicity=min(persona.toxicity, toxicity_max),
            )
            self.store.add_post(post)
            posts.append(post)
        return posts


_GENERATOR: PostGenerator | None = None


def generator_service() -> PostGenerator:
    global _GENERATOR
    if _GENERATOR is None:
        _GENERATOR = PostGenerator()
    return _GENERATOR
