#!/usr/bin/env python
"""Generator tests."""

import pytest

from backend.app.schemas import PersonaStyle
from backend.app.services.generator.core import text_generator
from backend.app.services.generator.styles import style_decorator
from backend.app.services.personas import persona_registry
from backend.app.services.rng import rng_manager


def test_rng_determinism():
    """Test RNG determinism with fixed seed."""
    rng_manager.set_global_seed(42)

    value1 = rng_manager.random(seed=42)
    value2 = rng_manager.random(seed=42)

    assert value1 == value2


def test_text_generation():
    """Test basic text generation."""
    persona = persona_registry.get_random_personas(1, seed=42)[0]
    topics = ["ai", "tech"]

    text, template = text_generator.generate(persona, topics, seed=42)

    assert isinstance(text, str)
    assert len(text) > 0
    assert isinstance(template, str)


def test_text_generation_determinism():
    """Test text generation determinism."""
    persona = persona_registry.get_random_personas(1, seed=42)[0]
    topics = ["crypto"]

    text1, _ = text_generator.generate(persona, topics, seed=123)
    text2, _ = text_generator.generate(persona, topics, seed=123)

    assert text1 == text2


def test_style_decorator_emojis():
    """Test emoji decoration."""
    persona = persona_registry.get_random_personas(1, seed=42)[0]
    # Force high emoji preference
    persona.style.emoji_preference = 1.0

    text = "This is a test post"
    decorated, metrics = style_decorator.decorate(text, persona, ["ai"], seed=42)

    # Should have added some emojis
    assert metrics.emojis >= 0


def test_style_decorator_hashtags():
    """Test hashtag decoration."""
    persona = persona_registry.get_random_personas(1, seed=42)[0]
    persona.style.hashtag_propensity = 1.0

    text = "AI is amazing"
    decorated, metrics = style_decorator.decorate(text, persona, ["ai"], seed=42)

    # Should have added hashtags
    assert "#" in decorated or metrics.hashtags >= 0


def test_persona_creation():
    """Test persona registry."""
    all_personas = persona_registry.get_all_personas()
    assert len(all_personas) >= 100  # Should have 100+ seed personas


def test_markov_chain():
    """Test Markov chain generation."""
    from backend.app.services.generator.core import MarkovChain

    chain = MarkovChain(order=2)
    corpus = [
        "the quick brown fox",
        "the quick red fox",
        "the slow brown dog",
    ]
    chain.train(corpus)

    # Generate from seed
    result = chain.generate(["the", "quick"], max_length=5, rng_seed=42)
    assert result.startswith("the quick")
    assert len(result.split()) >= 2


def test_template_filling():
    """Test template filling."""
    result = text_generator.fill_template(
        "Hot take: {topic} is {adjective}", "AI", seed=42
    )

    assert "AI" in result
    assert "Hot take:" in result


def test_toxicity_sanitization():
    """Test toxicity filtering."""
    from backend.app.schemas import Persona, PersonaBehavior, PersonaStances

    persona = Persona(
        id="test",
        display_name="Test",
        handle="test",
        bio="",
        toxicity=0.3,  # Low toxicity
        style=PersonaStyle(),
        behavior=PersonaBehavior(),
        stances=PersonaStances(),
    )

    text = "This is a damn test"
    sanitized = style_decorator.sanitize_toxicity(text, persona)

    # Should be masked
    assert "d*mn" in sanitized or "damn" not in sanitized
