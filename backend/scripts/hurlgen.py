#!/usr/bin/env python
from __future__ import annotations

import argparse
import json
from typing import List

from app.services.generator.core import generator_service


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate synthetic Hurl posts as NDJSON")
    parser.add_argument("--count", type=int, default=10)
    parser.add_argument("--mode", choices=["pure_random", "emergent"], default="pure_random")
    parser.add_argument("--topic", action="append", default=[])
    parser.add_argument("--persona", action="append", default=[])
    parser.add_argument("--language", action="append", default=[])
    parser.add_argument("--toxicity-max", type=float, default=1.0)
    parser.add_argument("--seed", type=int, default=None)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    generator = generator_service()
    posts = generator.generate(
        count=args.count,
        mode=args.mode,
        topics=args.topic,
        persona_ids=args.persona,
        languages=args.language,
        toxicity_max=args.toxicity_max,
        reading_level=None,
        seed=args.seed,
    )
    for post in posts:
        print(post.json())


if __name__ == "__main__":
    main()
