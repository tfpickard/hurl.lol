#!/usr/bin/env python
"""CLI tool for bulk post generation."""

import argparse
import asyncio
import sys

import orjson
from rich.console import Console
from rich.progress import track

# Add parent directory to path for imports
sys.path.insert(0, "/home/user/hurl.lol")

from app.schemas import GenerateRequest
from app.routers.posts import generate_single_post

console = Console()


async def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Hurl - Generate synthetic social media posts"
    )
    parser.add_argument(
        "--count",
        type=int,
        default=10,
        help="Number of posts to generate (default: 10)",
    )
    parser.add_argument(
        "--mode",
        choices=["emergent", "pure_random"],
        default="emergent",
        help="Generation mode (default: emergent)",
    )
    parser.add_argument(
        "--topic",
        action="append",
        dest="topics",
        help="Filter by topic(s), can be specified multiple times",
    )
    parser.add_argument(
        "--persona",
        action="append",
        dest="personas",
        help="Filter by persona ID(s), can be specified multiple times",
    )
    parser.add_argument(
        "--language",
        action="append",
        dest="languages",
        default=["en"],
        help="Language(s) to generate (default: en)",
    )
    parser.add_argument(
        "--toxicity-max",
        type=float,
        default=0.3,
        help="Maximum toxicity (0-1, default: 0.3)",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=None,
        help="Random seed for reproducibility",
    )
    parser.add_argument(
        "--output",
        choices=["ndjson", "json", "text"],
        default="ndjson",
        help="Output format (default: ndjson)",
    )

    args = parser.parse_args()

    # Generate posts
    console.print(
        f"[bold blue]Hurl[/bold blue] - Generating {args.count} posts in {args.mode} mode...\n"
    )

    posts = []
    for i in track(range(args.count), description="Generating..."):
        post_seed = (args.seed + i) if args.seed is not None else None

        persona_id = None
        if args.personas:
            # Simple round-robin if multiple personas specified
            persona_id = args.personas[i % len(args.personas)]

        post = await generate_single_post(
            persona_id=persona_id,
            mode=args.mode,
            topic_filter=args.topics or [],
            language_filter=args.languages,
            toxicity_max=args.toxicity_max,
            seed=post_seed,
        )
        posts.append(post)

    # Output
    if args.output == "ndjson":
        for post in posts:
            print(orjson.dumps(post.model_dump(mode="json")).decode("utf-8"))

    elif args.output == "json":
        print(
            orjson.dumps(
                [p.model_dump(mode="json") for p in posts], option=orjson.OPT_INDENT_2
            ).decode("utf-8")
        )

    elif args.output == "text":
        for i, post in enumerate(posts, 1):
            console.print(f"\n[bold cyan]Post {i}[/bold cyan]")
            console.print(f"  [dim]ID:[/dim] {post.id}")
            console.print(f"  [dim]Persona:[/dim] {post.persona_id}")
            console.print(f"  [dim]Topics:[/dim] {', '.join(post.topics)}")
            console.print(f"  [dim]Mode:[/dim] {post.mode}")
            console.print(f"\n  [green]{post.text}[/green]")
            console.print(
                f"\n  [dim]Likes: {post.metrics.likes} | Replies: {post.metrics.replies} | Quotes: {post.metrics.quotes}[/dim]"
            )


if __name__ == "__main__":
    asyncio.run(main())
