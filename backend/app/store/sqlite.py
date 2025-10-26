#!/usr/bin/env python
"""Optional SQLite persistence (placeholder for future implementation)."""

from backend.app.schemas import Post


class SQLiteStore:
    """SQLite-based persistent store (placeholder)."""

    def __init__(self, db_path: str = "hurl.db"):
        self.db_path = db_path
        # In production with SQLModel:
        # from sqlmodel import create_engine, Session
        # self.engine = create_engine(f"sqlite:///{db_path}")
        # SQLModel.metadata.create_all(self.engine)

    def add_post(self, post: Post) -> None:
        """Add a post to persistent storage."""
        # Placeholder
        pass

    def get_post(self, post_id: str) -> Post | None:
        """Get a post by ID."""
        # Placeholder
        return None

    def get_recent_posts(self, limit: int = 100) -> list[Post]:
        """Get recent posts."""
        # Placeholder
        return []


# Global SQLite store instance (lazy init)
_sqlite_store: SQLiteStore | None = None


def get_sqlite_store() -> SQLiteStore:
    """Get or create SQLite store instance."""
    global _sqlite_store
    if _sqlite_store is None:
        _sqlite_store = SQLiteStore()
    return _sqlite_store
