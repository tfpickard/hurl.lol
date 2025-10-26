from __future__ import annotations

import asyncio
import json
from typing import Any, AsyncGenerator, AsyncIterable, Awaitable, Callable, Dict

from fastapi.responses import StreamingResponse

JsonDict = Dict[str, Any]


async def _heartbeat(queue: "asyncio.Queue[bytes]", interval: float) -> None:
    try:
        while True:
            await asyncio.sleep(interval)
            await queue.put(b"data: {\"event\": \"ping\"}\n\n")
    except asyncio.CancelledError:
        pass


async def stream_events(source: AsyncIterable[JsonDict], *, ping_interval: float = 15.0) -> AsyncGenerator[bytes, None]:
    queue: "asyncio.Queue[bytes]" = asyncio.Queue()
    producer_done = asyncio.Event()

    async def produce() -> None:
        try:
            async for payload in source:
                text = json.dumps(payload, ensure_ascii=False)
                await queue.put(f"data: {text}\n\n".encode("utf-8"))
        finally:
            producer_done.set()

    producer_task = asyncio.create_task(produce())
    heartbeat_task = asyncio.create_task(_heartbeat(queue, ping_interval))

    try:
        while True:
            if producer_done.is_set() and queue.empty():
                break
            chunk = await queue.get()
            yield chunk
    finally:
        producer_task.cancel()
        heartbeat_task.cancel()

    yield b"event: close\n\n"


async def sse_response(
    generator: AsyncIterable[JsonDict] | Callable[[], AsyncIterable[JsonDict]],
    *,
    headers: Dict[str, str] | None = None,
    ping_interval: float = 15.0,
) -> StreamingResponse:
    source = generator() if callable(generator) else generator
    return StreamingResponse(
        stream_events(source, ping_interval=ping_interval),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            **(headers or {}),
        },
    )
