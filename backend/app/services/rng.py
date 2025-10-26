#!/usr/bin/env python
"""Global RNG utilities for deterministic generation."""

import threading
from typing import Any

import numpy as np


class RNGManager:
    """Thread-safe RNG manager with global and per-request seeds."""

    def __init__(self, default_seed: int | None = None):
        self._lock = threading.Lock()
        self._global_seed = default_seed
        self._global_rng = self._make_rng(default_seed)

    def _make_rng(self, seed: int | None) -> np.random.Generator:
        """Create a new RNG with PCG64 bit generator."""
        return np.random.Generator(np.random.PCG64(seed))

    def set_global_seed(self, seed: int) -> None:
        """Set the global seed and reset global RNG."""
        with self._lock:
            self._global_seed = seed
            self._global_rng = self._make_rng(seed)

    def get_global_seed(self) -> int | None:
        """Get the current global seed."""
        return self._global_seed

    def get_rng(self, seed: int | None = None) -> np.random.Generator:
        """
        Get an RNG instance.

        If seed is provided, returns a new RNG with that seed.
        Otherwise returns the global RNG (not thread-safe).
        """
        if seed is not None:
            return self._make_rng(seed)

        with self._lock:
            return self._global_rng

    def choice(
        self,
        arr: list[Any] | np.ndarray,
        size: int | None = None,
        p: list[float] | np.ndarray | None = None,
        seed: int | None = None,
    ) -> Any:
        """Weighted choice from array."""
        rng = self.get_rng(seed)
        return rng.choice(arr, size=size, p=p)

    def randint(
        self, low: int, high: int, size: int | None = None, seed: int | None = None
    ) -> int | np.ndarray:
        """Random integer(s) in [low, high)."""
        rng = self.get_rng(seed)
        return rng.integers(low, high, size=size)

    def random(self, size: int | None = None, seed: int | None = None) -> float | np.ndarray:
        """Random float(s) in [0, 1)."""
        rng = self.get_rng(seed)
        return rng.random(size=size)

    def normal(
        self,
        loc: float = 0.0,
        scale: float = 1.0,
        size: int | None = None,
        seed: int | None = None,
    ) -> float | np.ndarray:
        """Random normal distribution."""
        rng = self.get_rng(seed)
        return rng.normal(loc, scale, size=size)

    def shuffle(self, arr: list[Any], seed: int | None = None) -> None:
        """In-place shuffle."""
        rng = self.get_rng(seed)
        rng.shuffle(arr)

    def beta(
        self, a: float, b: float, size: int | None = None, seed: int | None = None
    ) -> float | np.ndarray:
        """Random beta distribution."""
        rng = self.get_rng(seed)
        return rng.beta(a, b, size=size)

    def exponential(
        self, scale: float = 1.0, size: int | None = None, seed: int | None = None
    ) -> float | np.ndarray:
        """Random exponential distribution."""
        rng = self.get_rng(seed)
        return rng.exponential(scale, size=size)


# Global RNG manager instance
rng_manager = RNGManager()
