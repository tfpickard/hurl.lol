#!/usr/bin/env python
"""Style decorators: emojis, hashtags, links, markdown."""

import re

from app.schemas import Persona, StyleMetrics
from app.services.rng import rng_manager


# Emoji sets
EMOJIS = {
    "positive": ["😊", "😃", "🔥", "💯", "✨", "🎉", "👏", "❤️", "🙌", "💪"],
    "negative": ["😤", "😠", "💀", "😭", "😩", "🤦", "😑", "🙄", "😬"],
    "neutral": ["🤔", "👀", "📈", "📊", "💰", "🚀", "🎯", "⚡", "🌟", "✅"],
    "tech": ["💻", "🤖", "🔧", "⚙️", "📱", "🖥️", "🌐", "🔌"],
    "celebration": ["🎊", "🥳", "🍾", "🏆", "🎁"],
}

# Common hashtags by topic
HASHTAG_TEMPLATES = {
    "ai": ["AI", "MachineLearning", "ArtificialIntelligence", "ML", "DeepLearning"],
    "crypto": ["Crypto", "Bitcoin", "Web3", "Blockchain", "DeFi"],
    "gaming": ["Gaming", "Gamer", "Esports", "GamerLife", "VideoGames"],
    "fitness": ["Fitness", "Workout", "FitnessMotivation", "GymLife", "Gains"],
    "climate": ["ClimateChange", "ClimateAction", "Environment", "Sustainability"],
    "politics": ["Politics", "Election", "Vote", "Democracy"],
    "stocks": ["Stocks", "Investing", "StockMarket", "Trading", "Finance"],
}

# Sample URLs for link injection
SAMPLE_URLS = [
    "example.com/article",
    "site.io/post",
    "blog.net/read",
    "news.com/breaking",
    "media.org/story",
]


class StyleDecorator:
    """Applies style decorations to generated text."""

    def __init__(self):
        pass

    def add_emojis(self, text: str, persona: Persona, seed: int | None = None) -> tuple[str, int]:
        """
        Add emojis based on persona preference.

        Returns:
            (decorated_text, emoji_count)
        """
        emoji_pref = persona.style.emoji_preference
        if emoji_pref < 0.1:
            return text, 0

        # Determine how many emojis to add
        max_emojis = int(emoji_pref * 5)  # 0-5 emojis
        num_emojis = rng_manager.randint(0, max_emojis + 1, seed=seed)

        if num_emojis == 0:
            return text, 0

        # Select emoji category based on text sentiment (simple heuristic)
        positive_words = {"good", "great", "amazing", "love", "awesome", "best", "fire", "peak"}
        negative_words = {"bad", "terrible", "worst", "hate", "awful", "trash", "mid"}

        text_lower = text.lower()
        has_positive = any(word in text_lower for word in positive_words)
        has_negative = any(word in text_lower for word in negative_words)

        if has_positive:
            emoji_pool = EMOJIS["positive"] + EMOJIS["celebration"]
        elif has_negative:
            emoji_pool = EMOJIS["negative"]
        else:
            emoji_pool = EMOJIS["neutral"]

        selected_emojis = [
            rng_manager.choice(emoji_pool, seed=seed) for _ in range(num_emojis)
        ]

        # Add emojis (50% at end, 50% sprinkled)
        if rng_manager.random(seed=seed) < 0.5:
            # Append at end
            text = text + " " + " ".join(selected_emojis)
        else:
            # Sprinkle throughout
            words = text.split()
            for emoji in selected_emojis:
                if words:
                    pos = rng_manager.randint(0, len(words), seed=seed)
                    words.insert(pos, emoji)
            text = " ".join(words)

        return text, num_emojis

    def add_hashtags(
        self, text: str, persona: Persona, topics: list[str], seed: int | None = None
    ) -> tuple[str, int]:
        """
        Add hashtags based on persona and topics.

        Returns:
            (decorated_text, hashtag_count)
        """
        hashtag_pref = persona.style.hashtag_propensity
        if hashtag_pref < 0.1:
            return text, 0

        max_hashtags = int(hashtag_pref * 4)  # 0-4 hashtags
        num_hashtags = rng_manager.randint(0, max_hashtags + 1, seed=seed)

        if num_hashtags == 0:
            return text, 0

        # Collect possible hashtags
        hashtag_pool = []
        for topic in topics:
            if topic in HASHTAG_TEMPLATES:
                hashtag_pool.extend(HASHTAG_TEMPLATES[topic])

        if not hashtag_pool:
            hashtag_pool = ["Trending", "Viral", "Thoughts", "Update", "News"]

        # Sample hashtags
        selected = [
            rng_manager.choice(hashtag_pool, seed=seed) for _ in range(num_hashtags)
        ]
        hashtags = [f"#{tag}" for tag in selected]

        # Append at end
        text = text + " " + " ".join(hashtags)

        return text, num_hashtags

    def add_links(self, text: str, persona: Persona, seed: int | None = None) -> tuple[str, int]:
        """
        Add URLs based on persona.

        Returns:
            (decorated_text, link_count)
        """
        link_pref = persona.style.link_propensity
        if rng_manager.random(seed=seed) > link_pref:
            return text, 0

        url = rng_manager.choice(SAMPLE_URLS, seed=seed)
        text = text + f" {url}"

        return text, 1

    def apply_caps(self, text: str, persona: Persona, seed: int | None = None) -> tuple[str, float]:
        """
        Apply random CAPS based on persona excitement.

        Returns:
            (decorated_text, caps_ratio)
        """
        # High emoji users tend to use more caps
        caps_prob = persona.style.emoji_preference * 0.3

        if rng_manager.random(seed=seed) > caps_prob:
            return text, 0.0

        words = text.split()
        caps_count = 0

        for i in range(len(words)):
            # Don't cap hashtags or URLs
            if words[i].startswith("#") or words[i].startswith("http"):
                continue

            if rng_manager.random(seed=seed) < 0.3:  # 30% of words
                words[i] = words[i].upper()
                caps_count += 1

        caps_ratio = caps_count / len(words) if words else 0.0
        return " ".join(words), caps_ratio

    def apply_punctuation_quirks(self, text: str, persona: Persona, seed: int | None = None) -> str:
        """Apply persona-specific punctuation quirks."""
        quirks = persona.style.punctuation_quirks

        if not quirks:
            return text

        # Apply quirks (e.g., "..." or "!!" or "?!")
        for quirk in quirks:
            if rng_manager.random(seed=seed) < 0.4:  # 40% chance
                text = text + quirk

        return text

    def sanitize_toxicity(self, text: str, persona: Persona) -> str:
        """
        Basic profanity masking based on toxicity setting.

        This is a simple placeholder. In production, use a real profanity filter.
        """
        if persona.toxicity > 0.7:
            return text  # Allow everything

        # Simple blocklist
        blocklist = ["fuck", "shit", "damn", "ass", "bitch"]
        pattern = re.compile(r"\b(" + "|".join(blocklist) + r")\b", re.IGNORECASE)

        def mask(match):
            word = match.group(0)
            return word[0] + "*" * (len(word) - 1)

        return pattern.sub(mask, text)

    def decorate(
        self,
        text: str,
        persona: Persona,
        topics: list[str],
        seed: int | None = None,
    ) -> tuple[str, StyleMetrics]:
        """
        Apply all decorations to text.

        Returns:
            (decorated_text, style_metrics)
        """
        # Apply decorations in sequence
        text, emoji_count = self.add_emojis(text, persona, seed=seed)
        text, hashtag_count = self.add_hashtags(text, persona, topics, seed=seed)
        text, link_count = self.add_links(text, persona, seed=seed)
        text, caps_ratio = self.apply_caps(text, persona, seed=seed)
        text = self.apply_punctuation_quirks(text, persona, seed=seed)
        text = self.sanitize_toxicity(text, persona)

        metrics = StyleMetrics(
            emojis=emoji_count,
            hashtags=hashtag_count,
            links=link_count,
            caps=caps_ratio,
        )

        return text, metrics


# Global style decorator instance
style_decorator = StyleDecorator()
