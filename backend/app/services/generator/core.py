#!/usr/bin/env python
"""Core text generation with templates and Markov chains."""

import random
import re
from collections import defaultdict
from typing import Any

from app.schemas import Persona
from app.services.rng import rng_manager
from app.services.topics import topic_graph


# Template categories
TEMPLATES = {
    "hot_take": [
        "Hot take: {topic} is {adjective}",
        "Unpopular opinion: {topic} {verb}",
        "{topic}? More like {negative_prefix}{topic}",
        "Everyone's wrong about {topic}. Here's why:",
        "The problem with {topic} is {complaint}",
    ],
    "observation": [
        "Just noticed that {topic} is {trend_verb}",
        "Is it just me or is {topic} {adjective} lately?",
        "{topic} hitting different today",
        "The {topic} situation is {adjective}",
        "Watching {topic} unfold like",
    ],
    "question": [
        "Why is {topic} {trend_verb}?",
        "What's the deal with {topic}?",
        "Am I the only one who thinks {topic} is {adjective}?",
        "Can someone explain {topic} to me?",
        "Thoughts on {topic}?",
    ],
    "statement": [
        "{topic} is {adjective}",
        "Just {verb} some {topic}",
        "{topic}: a thread",
        "My take on {topic}",
        "{topic} >> {other_topic}",
    ],
    "reaction": [
        "{emotion} about {topic} rn",
        "{topic} got me like",
        "When {topic} {event}",
        "Me watching {topic}:",
        "*{action}* at {topic}",
    ],
    "announcement": [
        "New: {topic} just {event}",
        "BREAKING: {topic} {event}",
        "{topic} update: {news}",
        "This just in: {topic}",
        "PSA: {topic} is {status}",
    ],
}

# Vocabulary for template filling
ADJECTIVES = [
    "wild", "crazy", "insane", "interesting", "weird", "broken", "overrated",
    "underrated", "revolutionary", "outdated", "amazing", "terrible", "mid",
    "peak", "bussin", "sus", "fire", "trash", "iconic", "cringe"
]

VERBS = [
    "slaps", "hits different", "goes hard", "misses", "fails", "succeeds",
    "matters", "sucks", "rocks", "fell off", "came back", "peaked"
]

TREND_VERBS = [
    "trending", "blowing up", "dying", "everywhere", "back", "over",
    "having a moment", "mainstream", "niche"
]

EMOTIONS = [
    "Excited", "Worried", "Confused", "Angry", "Happy", "Disappointed",
    "Shocked", "Impressed", "Frustrated", "Hyped", "Concerned"
]

ACTIONS = [
    "screaming", "crying", "laughing", "dying", "shaking", "sweating"
]

COMPLAINTS = [
    "nobody talks about it", "everyone ignores the real issue",
    "the hype is overblown", "it's too complicated", "it's too simple",
    "the timing is off"
]

NEWS_EVENTS = [
    "changed everything", "broke the internet", "went viral",
    "dropped unexpectedly", "made waves", "caused controversy"
]

STATUS_WORDS = [
    "live", "dead", "back", "canceled", "revived", "trending", "fading"
]


class MarkovChain:
    """Simple Markov chain for text generation."""

    def __init__(self, order: int = 2):
        self.order = order
        self.chain: dict[tuple[str, ...], list[str]] = defaultdict(list)

    def train(self, texts: list[str]) -> None:
        """Train on a corpus of texts."""
        for text in texts:
            words = text.split()
            if len(words) < self.order + 1:
                continue

            for i in range(len(words) - self.order):
                key = tuple(words[i : i + self.order])
                next_word = words[i + self.order]
                self.chain[key].append(next_word)

    def generate(self, seed_words: list[str], max_length: int = 20, rng_seed: int | None = None) -> str:
        """Generate text starting from seed words."""
        if len(seed_words) < self.order:
            return " ".join(seed_words)

        current = tuple(seed_words[-self.order :])
        output = list(seed_words)

        for _ in range(max_length - len(seed_words)):
            if current not in self.chain:
                break

            candidates = self.chain[current]
            next_word = rng_manager.choice(candidates, seed=rng_seed)
            output.append(next_word)

            current = tuple(output[-self.order :])

        return " ".join(output)


# Simple corpus for Markov training
MARKOV_CORPUS = [
    "the quick brown fox jumps over the lazy dog",
    "artificial intelligence is changing the world",
    "cryptocurrency has revolutionized finance",
    "social media connects people across the globe",
    "climate change requires urgent action",
    "technology advances at an exponential rate",
    "education shapes the future generation",
    "healthcare innovation saves lives every day",
    "sports bring communities together",
    "music transcends cultural boundaries",
    "movies tell stories that inspire us",
    "gaming has become mainstream entertainment",
    "productivity tools help us work smarter",
    "wellness practices improve mental health",
    "science explores the unknown frontiers",
]


class TextGenerator:
    """Rule-based text generator with templates and Markov chains."""

    def __init__(self):
        self.markov = MarkovChain(order=2)
        self.markov.train(MARKOV_CORPUS)

    def fill_template(self, template: str, topic_name: str, seed: int | None = None) -> str:
        """Fill a template with random vocabulary."""
        replacements = {
            "topic": topic_name,
            "adjective": rng_manager.choice(ADJECTIVES, seed=seed),
            "verb": rng_manager.choice(VERBS, seed=seed),
            "trend_verb": rng_manager.choice(TREND_VERBS, seed=seed),
            "emotion": rng_manager.choice(EMOTIONS, seed=seed),
            "action": rng_manager.choice(ACTIONS, seed=seed),
            "complaint": rng_manager.choice(COMPLAINTS, seed=seed),
            "negative_prefix": rng_manager.choice(["not-", "un-", "anti-"], seed=seed),
            "event": rng_manager.choice(NEWS_EVENTS, seed=seed),
            "news": rng_manager.choice(STATUS_WORDS, seed=seed),
            "status": rng_manager.choice(STATUS_WORDS, seed=seed),
            "other_topic": rng_manager.choice(["everything", "the rest", "alternatives"], seed=seed),
        }

        # Replace placeholders
        result = template
        for key, value in replacements.items():
            result = result.replace(f"{{{key}}}", str(value))

        return result

    def select_template_category(self, persona: Persona, seed: int | None = None) -> str:
        """Select a template category based on persona traits."""
        # Weight by persona style
        weights = {
            "hot_take": persona.style.hot_take_factor,
            "observation": 0.3,
            "question": 0.2,
            "statement": 0.3,
            "reaction": persona.style.emoji_preference * 0.4,
            "announcement": 0.1,
        }

        categories = list(weights.keys())
        probs = [weights[c] for c in categories]
        total = sum(probs)
        probs = [p / total for p in probs]

        return rng_manager.choice(categories, p=probs, seed=seed)

    def generate_base_text(
        self,
        persona: Persona,
        topics: list[str],
        seed: int | None = None,
    ) -> tuple[str, str]:
        """
        Generate base text from templates.

        Returns:
            (text, template_name)
        """
        # Pick a topic
        if not topics:
            topics = ["everything"]

        topic_id = rng_manager.choice(topics, seed=seed)
        topic_obj = topic_graph.get_topic(topic_id)
        topic_name = topic_obj.name if topic_obj else topic_id

        # Select template category
        category = self.select_template_category(persona, seed=seed)
        templates = TEMPLATES[category]
        template = rng_manager.choice(templates, seed=seed)

        # Fill template
        text = self.fill_template(template, topic_name, seed=seed)

        # Optionally extend with Markov
        if rng_manager.random(seed=seed) < 0.3:  # 30% chance
            seed_words = text.split()[-2:]
            extension = self.markov.generate(seed_words, max_length=10, rng_seed=seed)
            # Take only the new words
            new_words = extension.split()[len(seed_words):]
            if new_words:
                text += " " + " ".join(new_words[:5])

        template_name = f"{category}_v1"
        return text, template_name

    def generate(
        self,
        persona: Persona,
        topics: list[str],
        seed: int | None = None,
    ) -> tuple[str, str]:
        """
        Generate text for a persona and topics.

        Returns:
            (text, template_name)
        """
        return self.generate_base_text(persona, topics, seed=seed)


# Global text generator instance
text_generator = TextGenerator()
