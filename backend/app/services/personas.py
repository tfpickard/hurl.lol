#!/usr/bin/env python
"""Persona factory and registry with seed personas."""

import uuid
from typing import Any

from faker import Faker

from backend.app.schemas import (
    CreatePersonaRequest,
    Persona,
    PersonaBehavior,
    PersonaStances,
    PersonaStyle,
)
from backend.app.services.rng import rng_manager

fake = Faker()


# Seed personas covering a wide spectrum
SEED_PERSONAS_DATA = [
    # Tech enthusiasts
    {
        "display_name": "Alex Chen",
        "handle": "alexc_tech",
        "bio": "AI researcher. Building the future. Opinions are my own.",
        "interests": {"ai": 0.9, "quantum": 0.6, "open_source": 0.7},
        "stances": {"tech": 0.8, "politics": 0.1},
        "style": {"reading_level": 14, "hot_take_factor": 0.4, "cynicism": 0.3},
    },
    {
        "display_name": "crypto_whale_42",
        "handle": "crypto_whale_42",
        "bio": "HODL. Not financial advice. Diamond hands.",
        "interests": {"crypto": 1.0, "web3": 0.9, "stocks": 0.5},
        "stances": {"tech": 0.6, "markets": 0.9},
        "style": {"emoji_preference": 0.9, "hashtag_propensity": 0.8, "cynicism": 0.2},
    },
    {
        "display_name": "Sarah K",
        "handle": "sarahk_codes",
        "bio": "Full-stack dev. Coffee addict. She/her.",
        "interests": {"open_source": 0.8, "cloud": 0.6, "productivity": 0.5},
        "stances": {"tech": 0.7},
        "style": {"reading_level": 10, "hot_take_factor": 0.2},
    },
    {
        "display_name": "hackerman3000",
        "handle": "hackerman3000",
        "bio": "Security researcher. Bug bounties. Ethical hacking.",
        "interests": {"cybersec": 0.95, "privacy": 0.8, "open_source": 0.6},
        "stances": {"tech": 0.5, "politics": 0.3},
        "style": {"reading_level": 12, "cynicism": 0.6, "punctuation": ["..."]},
    },
    {
        "display_name": "VR Visionary",
        "handle": "vr_visionary",
        "bio": "Building the metaverse. VR/AR evangelist.",
        "interests": {"vr_ar": 1.0, "gaming": 0.7, "startups": 0.5},
        "stances": {"tech": 0.9},
        "style": {"hot_take_factor": 0.7, "emoji_preference": 0.6},
    },
    # Politics & society
    {
        "display_name": "PolicyWonk",
        "handle": "policywonk",
        "bio": "Political analyst. Facts over feelings.",
        "interests": {"politics": 0.9, "elections": 0.8, "climate": 0.6},
        "stances": {"politics": 0.7},
        "style": {"reading_level": 15, "cynicism": 0.5, "hot_take_factor": 0.6},
    },
    {
        "display_name": "Climate Activist",
        "handle": "climate_now",
        "bio": "Climate action NOW. Science is real.",
        "interests": {"climate": 1.0, "politics": 0.7, "wildlife": 0.6},
        "stances": {"politics": 0.8},
        "style": {"hot_take_factor": 0.8, "hashtag_propensity": 0.9},
    },
    {
        "display_name": "Dr. Maria Lopez",
        "handle": "dr_maria_lopez",
        "bio": "Public health physician. Advocate for healthcare reform.",
        "interests": {"healthcare": 0.9, "politics": 0.5, "mental_health": 0.7},
        "stances": {"politics": 0.4},
        "style": {"reading_level": 16, "cynicism": 0.2},
    },
    # Finance & markets
    {
        "display_name": "Wall St Wolf",
        "handle": "wallstwolf",
        "bio": "Stocks, options, gains. Let's get this bread.",
        "interests": {"stocks": 0.95, "economy": 0.7, "crypto": 0.4},
        "stances": {"markets": 0.9},
        "style": {"emoji_preference": 0.7, "hot_take_factor": 0.8, "cynicism": 0.6},
    },
    {
        "display_name": "StartupFounder",
        "handle": "startup_founder",
        "bio": "Building in public. Raised Series A. Always be shipping.",
        "interests": {"startups": 1.0, "ai": 0.6, "job_market": 0.4},
        "stances": {"tech": 0.7, "markets": 0.6},
        "style": {"reading_level": 11, "hot_take_factor": 0.5},
    },
    # Sports fans
    {
        "display_name": "SportsJunkie",
        "handle": "sports_junkie",
        "bio": "Live for game day. Stats nerd.",
        "interests": {"football": 0.9, "basketball": 0.8, "esports": 0.3},
        "stances": {"sports": 0.9},
        "style": {"emoji_preference": 0.8, "cynicism": 0.4},
    },
    {
        "display_name": "EsportsKing",
        "handle": "esports_king",
        "bio": "Pro gamer. Streaming 24/7. GG.",
        "interests": {"esports": 1.0, "gaming": 0.9, "social_media": 0.5},
        "stances": {"sports": 0.7},
        "style": {"reading_level": 8, "emoji_preference": 0.9, "slang": ["gg", "ez", "noob"]},
    },
    # Pop culture
    {
        "display_name": "MovieBuff",
        "handle": "movie_buff",
        "bio": "Film critic. Seen everything. Hot takes on cinema.",
        "interests": {"movies": 0.95, "tv": 0.7, "celebrities": 0.5},
        "stances": {"pop_culture": 0.8},
        "style": {"reading_level": 13, "hot_take_factor": 0.9, "cynicism": 0.7},
    },
    {
        "display_name": "pop_stan_forever",
        "handle": "pop_stan_forever",
        "bio": "Stan account. Protecting my fave at all costs.",
        "interests": {"music": 1.0, "celebrities": 0.9, "social_media": 0.8},
        "stances": {"pop_culture": 1.0},
        "style": {"emoji_preference": 1.0, "hashtag_propensity": 1.0, "caps": 0.3},
    },
    {
        "display_name": "MemeL0rd",
        "handle": "memelord",
        "bio": "Curator of chaos. Dank memes only.",
        "interests": {"memes": 1.0, "social_media": 0.9, "gaming": 0.6},
        "stances": {},
        "style": {"emoji_preference": 0.9, "cynicism": 0.8, "reading_level": 7},
    },
    # Wellness & lifestyle
    {
        "display_name": "Wellness Warrior",
        "handle": "wellness_warrior",
        "bio": "Holistic health. Mind, body, spirit. Namaste.",
        "interests": {"meditation": 0.9, "nutrition": 0.8, "mental_health": 0.7},
        "stances": {"wellness": 0.9},
        "style": {"emoji_preference": 0.7, "cynicism": 0.1},
    },
    {
        "display_name": "FitnessFreak",
        "handle": "fitness_freak",
        "bio": "No pain, no gain. Gym rat. Macro tracking.",
        "interests": {"fitness": 1.0, "nutrition": 0.9},
        "stances": {"wellness": 0.8},
        "style": {"emoji_preference": 0.8, "hashtag_propensity": 0.7},
    },
    {
        "display_name": "Therapist Jane",
        "handle": "therapist_jane",
        "bio": "Licensed therapist. Mental health advocate. DMs open.",
        "interests": {"mental_health": 0.95, "wellness": 0.6, "healthcare": 0.5},
        "stances": {},
        "style": {"reading_level": 12, "cynicism": 0.2, "emoji_preference": 0.3},
    },
    # Miscellaneous interesting personas
    {
        "display_name": "Skeptic Sam",
        "handle": "skeptic_sam",
        "bio": "Question everything. Prove it.",
        "interests": {"misinformation": 0.8, "politics": 0.6, "science": 0.7},
        "stances": {},
        "style": {"cynicism": 0.95, "hot_take_factor": 0.8, "reading_level": 14},
    },
    {
        "display_name": "Influencer Ivy",
        "handle": "influencer_ivy",
        "bio": "Brand partnerships: ivy@agency.com. Link in bio.",
        "interests": {"influencers": 1.0, "fashion": 0.8, "social_media": 0.9},
        "stances": {},
        "style": {"emoji_preference": 0.9, "link_propensity": 0.9, "hashtag_propensity": 0.9},
    },
    {
        "display_name": "TeacherTom",
        "handle": "teacher_tom",
        "bio": "High school teacher. Education matters.",
        "interests": {"education": 0.9, "politics": 0.4, "productivity": 0.5},
        "stances": {},
        "style": {"reading_level": 11, "cynicism": 0.3},
    },
]


def _generate_additional_personas(count: int = 80) -> list[dict[str, Any]]:
    """Generate additional random personas to reach 100+."""
    personas = []
    topics = ["ai", "crypto", "gaming", "politics", "climate", "stocks", "movies", "music",
              "fitness", "memes", "social_media", "startups", "healthcare", "education"]

    for i in range(count):
        # Random interests
        num_interests = rng_manager.randint(1, 4)
        selected_topics = rng_manager.choice(topics, size=num_interests, seed=None)
        interests = {
            topic: float(rng_manager.beta(2, 2, seed=None))
            for topic in selected_topics
        }

        # Random stances
        stance_keys = ["tech", "politics", "sports", "markets", "pop_culture", "wellness"]
        num_stances = rng_manager.randint(0, 3)
        selected_stances = rng_manager.choice(stance_keys, size=num_stances, seed=None) if num_stances > 0 else []
        stances = {
            key: float(rng_manager.random(seed=None) * 2 - 1)  # -1 to 1
            for key in selected_stances
        }

        # Random style
        reading_level = int(rng_manager.randint(6, 18))
        emoji_pref = float(rng_manager.beta(2, 3, seed=None))
        hashtag_pref = float(rng_manager.beta(1.5, 3, seed=None))
        hot_take = float(rng_manager.beta(2, 4, seed=None))
        cynicism = float(rng_manager.beta(2, 3, seed=None))

        personas.append({
            "display_name": fake.name(),
            "handle": fake.user_name(),
            "bio": fake.sentence(nb_words=8),
            "interests": interests,
            "stances": stances,
            "style": {
                "reading_level": reading_level,
                "emoji_preference": emoji_pref,
                "hashtag_propensity": hashtag_pref,
                "hot_take_factor": hot_take,
                "cynicism": cynicism,
            },
        })

    return personas


class PersonaRegistry:
    """Registry for managing personas."""

    def __init__(self):
        self._personas: dict[str, Persona] = {}
        self._initialize_seed_personas()

    def _initialize_seed_personas(self) -> None:
        """Initialize with seed personas."""
        all_seed_data = SEED_PERSONAS_DATA + _generate_additional_personas(80)

        for data in all_seed_data:
            persona = self._create_persona_from_data(data)
            self._personas[persona.id] = persona

    def _create_persona_from_data(self, data: dict[str, Any]) -> Persona:
        """Create a Persona from seed data dict."""
        persona_id = str(uuid.uuid4())

        # Extract style data
        style_data = data.get("style", {})
        style = PersonaStyle(
            reading_level=style_data.get("reading_level", 10),
            emoji_preference=style_data.get("emoji_preference", 0.5),
            hashtag_propensity=style_data.get("hashtag_propensity", 0.2),
            link_propensity=style_data.get("link_propensity", 0.1),
            cynicism=style_data.get("cynicism", 0.5),
            hot_take_factor=style_data.get("hot_take_factor", 0.3),
            slang_set=style_data.get("slang", []),
            punctuation_quirks=style_data.get("punctuation", []),
        )

        # Extract stances
        stances_data = data.get("stances", {})
        stances = PersonaStances(**stances_data)

        # Default behavior
        behavior = PersonaBehavior()

        return Persona(
            id=persona_id,
            display_name=data["display_name"],
            handle=data["handle"],
            bio=data.get("bio", ""),
            interests=data.get("interests", {}),
            style=style,
            behavior=behavior,
            stances=stances,
            toxicity=data.get("toxicity", 0.1),
            influence_score=float(rng_manager.beta(2, 5, seed=None)),
        )

    def get_persona(self, persona_id: str) -> Persona | None:
        """Get a persona by ID."""
        return self._personas.get(persona_id)

    def get_all_personas(self) -> list[Persona]:
        """Get all personas."""
        return list(self._personas.values())

    def create_persona(self, request: CreatePersonaRequest) -> Persona:
        """Create a new custom persona."""
        persona_id = str(uuid.uuid4())

        style = request.style or PersonaStyle()
        behavior = request.behavior or PersonaBehavior()
        stances = request.stances or PersonaStances()

        persona = Persona(
            id=persona_id,
            display_name=request.display_name,
            handle=request.handle,
            bio=request.bio,
            interests=request.interests,
            style=style,
            behavior=behavior,
            stances=stances,
            toxicity=request.toxicity,
            influence_score=0.3,  # new personas start with low influence
        )

        self._personas[persona_id] = persona
        return persona

    def get_random_personas(self, count: int, seed: int | None = None) -> list[Persona]:
        """Get random personas."""
        personas = self.get_all_personas()
        if count >= len(personas):
            return personas

        selected = rng_manager.choice(personas, size=count, seed=seed)
        return selected.tolist() if hasattr(selected, 'tolist') else list(selected)


# Global persona registry
persona_registry = PersonaRegistry()
