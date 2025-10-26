from __future__ import annotations

import asyncio
import json
from contextlib import AbstractContextManager
from typing import Any, Dict, Iterator, List, Optional

from .. import FastAPI, ResponseContainer, call_route


class _StreamContext(AbstractContextManager):
    def __init__(self, response: ResponseContainer) -> None:
        self._response = response
        self._body = response.body

    def __enter__(self) -> "_StreamContext":
        return self

    def __exit__(self, *args) -> Optional[bool]:
        return None

    def iter_lines(self) -> Iterator[str]:
        body = self._body
        if hasattr(body, "__aiter__"):
            async def get_next() -> Optional[str]:
                agen = body.__aiter__()
                try:
                    chunk = await agen.__anext__()
                except StopAsyncIteration:
                    return None
                return chunk.decode() if isinstance(chunk, bytes) else str(chunk)

            chunk = asyncio.get_event_loop().run_until_complete(get_next())
            if chunk is not None:
                yield chunk
        elif body:
            iterator = iter(body)
            try:
                chunk = next(iterator)
            except StopIteration:
                return
            yield chunk.decode() if isinstance(chunk, bytes) else str(chunk)


class _ClientResponse:
    def __init__(self, container: ResponseContainer) -> None:
        self._container = container
        self.status_code = container.status_code
        self.headers = container.headers

    def json(self) -> Any:
        return self._container.json()

    @property
    def text(self) -> str:
        return json.dumps(self.json())


class TestClient:
    def __init__(self, app: FastAPI) -> None:
        self.app = app
        asyncio.get_event_loop().run_until_complete(app._run_startup())

    def request(self, method: str, path: str, *, json: Any | None = None, params: Dict[str, str] | None = None) -> _ClientResponse:
        query = {key: [value] for key, value in (params or {}).items()}
        response = asyncio.get_event_loop().run_until_complete(
            call_route(self.app, method.upper(), path, headers={}, query=query, body=json)
        )
        return _ClientResponse(response)

    def get(self, path: str, *, params: Dict[str, str] | None = None) -> _ClientResponse:
        return self.request("GET", path, params=params)

    def post(self, path: str, *, json: Any | None = None) -> _ClientResponse:
        return self.request("POST", path, json=json)

    def stream(self, method: str, path: str, *, params: Dict[str, str] | None = None, timeout: float | None = None) -> _StreamContext:
        query = {key: [value] for key, value in (params or {}).items()}
        response = asyncio.get_event_loop().run_until_complete(
            call_route(self.app, method.upper(), path, headers={}, query=query, body=None)
        )
        return _StreamContext(response)
