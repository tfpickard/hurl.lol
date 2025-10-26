#!/usr/bin/env python
"""Server-Sent Events (SSE) helpers."""

import asyncio
from typing import AsyncGenerator

import orjson
from starlette.responses import StreamingResponse


class SSEResponse(StreamingResponse):
    """SSE streaming response."""

    def __init__(self, generator: AsyncGenerator, **kwargs):
        super().__init__(
            generator,
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no",  # Disable nginx buffering
            },
            **kwargs,
        )


def format_sse(data: dict | str, event: str | None = None) -> str:
    """
    Format data as SSE message.

    Args:
        data: Data to send (dict will be JSON-encoded)
        event: Optional event type

    Returns:
        Formatted SSE string
    """
    lines = []

    if event:
        lines.append(f"event: {event}")

    if isinstance(data, dict):
        data_str = orjson.dumps(data).decode("utf-8")
    else:
        data_str = str(data)

    lines.append(f"data: {data_str}")
    lines.append("")  # Empty line to end message

    return "\n".join(lines) + "\n"


async def heartbeat_generator(interval: float = 15.0) -> AsyncGenerator[str, None]:
    """Generate SSE heartbeat messages."""
    while True:
        await asyncio.sleep(interval)
        yield format_sse({"type": "heartbeat"}, event="heartbeat")
