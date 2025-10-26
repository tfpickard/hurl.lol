from __future__ import annotations

from app.services.generator.core import generator_service
from app.services.rng import get_rng
from app.store.memory import get_store


def test_generator_determinism() -> None:
    generator = generator_service()
    store = get_store()
    store.clear_posts()
    get_rng().reseed(1234)
    posts_a = generator.generate(
        count=3,
        mode="pure_random",
        topics=[],
        persona_ids=[],
        languages=[],
        toxicity_max=1.0,
        reading_level=None,
        seed=42,
    )
    store.clear_posts()
    get_rng().reseed(1234)
    posts_b = generator.generate(
        count=3,
        mode="pure_random",
        topics=[],
        persona_ids=[],
        languages=[],
        toxicity_max=1.0,
        reading_level=None,
        seed=42,
    )

    signature_a = [(post.persona_id, post.text) for post in posts_a]
    signature_b = [(post.persona_id, post.text) for post in posts_b]
    assert signature_a == signature_b
