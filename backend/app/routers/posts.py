#!/usr/bin/env python
"""Posts router for generation and streaming."""

import asyncio
import time
from datetime import datetime, timezone
from typing import AsyncGenerator

from fastapi import APIRouter, Query
from ulid import ULID

from app.config import settings
from app.schemas import GenerateRequest, GenerateResponse, Post, PostLineage
from app.services.generator.core import text_generator
from app.services.generator.llm import llm_adapter
from app.services.generator.metrics import metrics_simulator
from app.services.generator.styles import style_decorator
from app.services.personas import persona_registry
from app.services.rng import rng_manager
from app.services.topics import topic_graph
from app.services.trends import trend_engine
from app.sse import SSEResponse, format_sse
from app.store.memory import memory_store

router = APIRouter(prefix="/v1", tags=["posts"])


async def generate_single_post(
    persona_id: str | None,
    mode: str,
    topic_filter: list[str],
    language_filter: list[str],
    toxicity_max: float,
    seed: int | None,
) -> Post:
    """Generate a single post."""
    # Select persona
    if persona_id:
        persona = persona_registry.get_persona(persona_id)
        if not persona:
            # Fall back to random
            persona = persona_registry.get_random_personas(1, seed=seed)[0]
    else:
        persona = persona_registry.get_random_personas(1, seed=seed)[0]

    # Select topics based on mode
    if mode == "emergent":
        # Use trend engine to compute adoption probabilities
        recent_posts = memory_store.get_posts_by_persona(persona.id, limit=10)
        recent_topics = [topic for post in recent_posts for topic in post.topics]

        # Compute peer influence (simplified: assume small random influence)
        peer_influence = {
            topic_id: rng_manager.random(seed=seed) * 0.3
            for topic_id in topic_graph.graph.nodes
        }

        adoption_probs = trend_engine.compute_topic_adoption_prob(
            persona.interests, peer_influence, recent_topics, seed=seed
        )

        # Filter by topic_filter if provided
        if topic_filter:
            adoption_probs = {
                k: v for k, v in adoption_probs.items() if k in topic_filter
            }

        if not adoption_probs:
            # Fallback to interests
            adoption_probs = persona.interests

        topics = trend_engine.sample_topics(adoption_probs, count=rng_manager.randint(1, 3, seed=seed), seed=seed)
    else:
        # Pure random mode
        all_topics = list(topic_graph.graph.nodes)
        if topic_filter:
            all_topics = [t for t in all_topics if t in topic_filter]

        num_topics = rng_manager.randint(1, 3, seed=seed)
        topics = rng_manager.choice(all_topics, size=min(num_topics, len(all_topics)), seed=seed)
        topics = topics.tolist() if hasattr(topics, 'tolist') else list(topics)

    # Select language
    if language_filter:
        language = rng_manager.choice(language_filter, seed=seed)
    else:
        # Use persona's language distribution
        langs = list(persona.behavior.language_distribution.keys())
        probs = list(persona.behavior.language_distribution.values())
        total = sum(probs)
        probs = [p / total for p in probs]
        language = rng_manager.choice(langs, p=probs, seed=seed)

    # Generate base text
    base_text, template_name = text_generator.generate(persona, topics, seed=seed)

    # Optionally enhance with LLM
    if llm_adapter.is_enabled() and rng_manager.random(seed=seed) < 0.2:  # 20% chance
        persona_context = f"cynicism={persona.style.cynicism}, reading_level={persona.style.reading_level}"
        base_text = await llm_adapter.enhance_text(base_text, persona_context, seed=seed)

    # Apply style decorations
    final_text, style_metrics = style_decorator.decorate(base_text, persona, topics, seed=seed)

    # Simulate metrics
    post_metrics = metrics_simulator.simulate_metrics(persona, topics, final_text, mode, seed=seed)

    # Compute toxicity (simplified: use persona's base toxicity + small noise)
    toxicity = min(
        persona.toxicity + rng_manager.random(seed=seed) * 0.1,
        1.0,
    )

    # Filter by toxicity
    if toxicity > toxicity_max:
        # Regenerate with different seed (simple retry)
        seed_retry = seed + 1 if seed is not None else None
        return await generate_single_post(
            persona_id, mode, topic_filter, language_filter, toxicity_max, seed_retry
        )

    # Find influences (recent posts from similar personas or topics)
    influences = []
    recent_all = memory_store.get_recent_posts(limit=50)
    if recent_all:
        # Sample up to 3 influences
        num_influences = min(rng_manager.randint(0, 4, seed=seed), len(recent_all))
        if num_influences > 0:
            sampled = rng_manager.choice(recent_all, size=num_influences, seed=seed)
            influences = [p.id for p in (sampled if hasattr(sampled, '__iter__') else [sampled])]

    lineage = PostLineage(template=template_name, influences=influences)

    # Create post
    post = Post(
        id=str(ULID()),
        text=final_text,
        persona_id=persona.id,
        created_at=datetime.now(timezone.utc),
        mode=mode,
        topics=topics,
        language=language,
        style=style_metrics,
        lineage=lineage,
        metrics=post_metrics,
        toxicity=toxicity,
    )

    # Store post
    memory_store.add_post(post)

    return post


@router.post("/generate", response_model=GenerateResponse)
async def generate_posts(request: GenerateRequest) -> GenerateResponse:
    """Generate a batch of posts synchronously."""
    count = min(request.count, settings.max_batch_size)
    seed = request.seed or rng_manager.get_global_seed()

    posts = []
    for i in range(count):
        # Increment seed per post for determinism
        post_seed = (seed + i) if seed is not None else None

        # Select persona if specified
        persona_id = None
        if request.persona_ids:
            persona_id = rng_manager.choice(request.persona_ids, seed=post_seed)

        post = await generate_single_post(
            persona_id=persona_id,
            mode=request.mode,
            topic_filter=request.topics,
            language_filter=request.language,
            toxicity_max=request.toxicity_max,
            seed=post_seed,
        )
        posts.append(post)

    return GenerateResponse(posts=posts, count=len(posts), seed=seed)


@router.get("/sample", response_model=GenerateResponse)
async def sample_posts(
    count: int = Query(default=10, ge=1, le=100),
    mode: str = Query(default="emergent"),
    seed: int | None = None,
) -> GenerateResponse:
    """Convenience endpoint to sample posts."""
    request = GenerateRequest(count=count, mode=mode, seed=seed)
    return await generate_posts(request)


async def stream_posts_generator(
    mode: str,
    topics: list[str],
    persona_ids: list[str],
    language: list[str],
    toxicity_max: float,
    seed: int | None,
    interval: float = 1.0,
) -> AsyncGenerator[str, None]:
    """
    Generate SSE stream of posts.

    Args:
        interval: Time between posts in seconds
    """
    counter = 0
    base_seed = seed or int(time.time())

    try:
        while True:
            post_seed = base_seed + counter

            # Select persona if specified
            persona_id = None
            if persona_ids:
                persona_id = rng_manager.choice(persona_ids, seed=post_seed)

            post = await generate_single_post(
                persona_id=persona_id,
                mode=mode,
                topic_filter=topics,
                language_filter=language,
                toxicity_max=toxicity_max,
                seed=post_seed,
            )

            # Send post as SSE event
            yield format_sse(post.model_dump(mode="json"), event="post")

            counter += 1

            # Wait before next post
            await asyncio.sleep(interval)

    except asyncio.CancelledError:
        # Client disconnected
        pass


@router.get("/stream")
async def stream_posts(
    mode: str = Query(default="emergent"),
    topics: str = Query(default=""),  # comma-separated
    persona_ids: str = Query(default=""),  # comma-separated
    language: str = Query(default="en"),  # comma-separated
    toxicity_max: float = Query(default=0.3, ge=0.0, le=1.0),
    seed: int | None = Query(default=None),
    interval: float = Query(default=1.0, ge=0.1, le=10.0),
) -> SSEResponse:
    """Stream posts via Server-Sent Events."""
    # Parse comma-separated filters
    topic_list = [t.strip() for t in topics.split(",") if t.strip()]
    persona_list = [p.strip() for p in persona_ids.split(",") if p.strip()]
    language_list = [lang.strip() for lang in language.split(",") if lang.strip()]

    generator = stream_posts_generator(
        mode=mode,
        topics=topic_list,
        persona_ids=persona_list,
        language=language_list,
        toxicity_max=toxicity_max,
        seed=seed,
        interval=interval,
    )

    return SSEResponse(generator)
