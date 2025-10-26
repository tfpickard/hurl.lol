from __future__ import annotations

from contextlib import contextmanager
from dataclasses import dataclass
from threading import RLock
from typing import Iterator

import random


@dataclass
class RNGState:
    seed: int


class RNGService:
    """Centralised RNG service based on :class:`random.Random`."""

    def __init__(self, seed: int = 12345) -> None:
        self._seed = seed
        self._lock = RLock()
        self._generator = random.Random(seed)

    @property
    def seed(self) -> int:
        return self._seed

    def reseed(self, seed: int) -> None:
        with self._lock:
            self._seed = int(seed)
            self._generator = random.Random(self._seed)

    def generator(self) -> random.Random:
        with self._lock:
            return self._generator

    @contextmanager
    def using_seed(self, seed: int | None) -> Iterator[random.Random]:
        if seed is None:
            yield self.generator()
            return
        local = random.Random(seed)
        yield local


_global_rng = RNGService()


def get_rng() -> RNGService:
    return _global_rng
