from __future__ import annotations

import json
from typing import Any, AsyncGenerator, AsyncIterable, Dict, Iterable


class Response:
    def __init__(self, content: Any, *, status_code: int = 200, headers: Dict[str, str] | None = None) -> None:
        self.content = content
        self.status_code = status_code
        self.headers = headers or {}
        self.body = content

    def json(self) -> Any:
        return self.content


class JSONResponse(Response):
    def __init__(self, content: Any, *, status_code: int = 200, headers: Dict[str, str] | None = None) -> None:
        super().__init__(content, status_code=status_code, headers=headers)


class StreamingResponse(Response):
    def __init__(self, generator: AsyncIterable[bytes] | Iterable[bytes], *, media_type: str = "application/json", headers: Dict[str, str] | None = None) -> None:
        super().__init__(generator, status_code=200, headers=headers or {})
        self.media_type = media_type
        self.headers.setdefault("content-type", media_type)


__all__ = ["JSONResponse", "Response", "StreamingResponse"]
