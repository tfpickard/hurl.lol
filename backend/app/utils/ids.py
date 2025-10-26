from __future__ import annotations

import os
import time

_ALPHABET = "0123456789ABCDEFGHJKMNPQRSTVWXYZ"


def ulid() -> str:
    timestamp = int(time.time() * 1000)
    time_chars = []
    for _ in range(10):
        timestamp, rem = divmod(timestamp, 32)
        time_chars.append(_ALPHABET[rem])
    random_bits = int.from_bytes(os.urandom(10), "big")
    rand_chars = []
    for _ in range(16):
        random_bits, rem = divmod(random_bits, 32)
        rand_chars.append(_ALPHABET[rem])
    return "".join(reversed(time_chars)) + "".join(reversed(rand_chars))
