#!/usr/bin/env python
"""In-memory post storage with sliding window."""

from collections import deque
from typing import Any

from app.schemas import Post


class MemoryStore:
    """In-memory store for posts with sliding window."""

    def __init__(self, max_size: int = 10000):
        self.max_size = max_size
        self._posts: deque[Post] = deque(maxlen=max_size)
        self._index: dict[str, Post] = {}

    def add_post(self, post: Post) -> None:
        """Add a post to the store."""
        # If at capacity, remove oldest from index
        if len(self._posts) >= self.max_size and self._posts:
            oldest = self._posts[0]
            self._index.pop(oldest.id, None)

        self._posts.append(post)
        self._index[post.id] = post

    def get_post(self, post_id: str) -> Post | None:
        """Get a post by ID."""
        return self._index.get(post_id)

    def get_recent_posts(self, limit: int = 100) -> list[Post]:
        """Get the most recent posts."""
        return list(self._posts)[-limit:]

    def get_all_posts(self) -> list[Post]:
        """Get all stored posts."""
        return list(self._posts)

    def get_posts_by_persona(self, persona_id: str, limit: int = 50) -> list[Post]:
        """Get recent posts by a persona."""
        persona_posts = [p for p in self._posts if p.persona_id == persona_id]
        return persona_posts[-limit:]

    def get_posts_by_topic(self, topic_id: str, limit: int = 50) -> list[Post]:
        """Get recent posts about a topic."""
        topic_posts = [p for p in self._posts if topic_id in p.topics]
        return topic_posts[-limit:]

    def count(self) -> int:
        """Count total posts in store."""
        return len(self._posts)

    def clear(self) -> None:
        """Clear all posts."""
        self._posts.clear()
        self._index.clear()


# Global memory store instance
memory_store = MemoryStore()
