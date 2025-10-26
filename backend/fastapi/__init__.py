from __future__ import annotations

import asyncio
import inspect
from dataclasses import asdict, is_dataclass
from typing import Any, Awaitable, Callable, Dict, List, Optional, get_type_hints

from .responses import JSONResponse, Response, StreamingResponse


class HTTPException(Exception):
    def __init__(self, status_code: int, detail: str) -> None:
        self.status_code = status_code
        self.detail = detail
        super().__init__(detail)


class Depends:
    def __init__(self, dependency: Callable[..., Any]) -> None:
        self.dependency = dependency


class Request:
    def __init__(self, method: str, url: str, headers: Dict[str, str], query_params: Dict[str, List[str]], body: Any | None = None) -> None:
        self.method = method
        self.url = url
        self.headers = {k.lower(): v for k, v in headers.items()}
        self._query_params = QueryParams(query_params)
        self._body = body

    @property
    def query_params(self) -> "QueryParams":
        return self._query_params

    async def is_disconnected(self) -> bool:
        return False

    @property
    def headers(self) -> Dict[str, str]:
        return self._headers

    @headers.setter
    def headers(self, value: Dict[str, str]) -> None:
        self._headers = value


class QueryParams:
    def __init__(self, mapping: Dict[str, List[str]]) -> None:
        self._mapping = mapping

    def get(self, key: str, default: Optional[str] = None) -> Optional[str]:
        values = self._mapping.get(key)
        if not values:
            return default
        return values[0]

    def getlist(self, key: str) -> List[str]:
        return list(self._mapping.get(key, []))

    def __iter__(self):
        return iter(self._mapping.items())


class Route:
    def __init__(
        self,
        path: str,
        methods: List[str],
        endpoint: Callable[..., Any],
        *,
        response_model: Any = None,
        status_code: int = 200,
        dependencies: Optional[List[Depends]] = None,
    ) -> None:
        self.path = path
        self.methods = methods
        self.endpoint = endpoint
        self.response_model = response_model
        self.status_code = status_code
        self.dependencies = dependencies or []


class APIRouter:
    def __init__(self, *, tags: Optional[List[str]] = None) -> None:
        self.routes: List[Route] = []

    def add_api_route(
        self,
        path: str,
        endpoint: Callable[..., Any],
        *,
        methods: List[str],
        response_model: Any = None,
        status_code: int = 200,
        dependencies: Optional[List[Depends]] = None,
    ) -> None:
        self.routes.append(Route(path, methods, endpoint, response_model=response_model, status_code=status_code, dependencies=dependencies))

    def get(self, path: str, *, response_model: Any = None, status_code: int = 200):
        def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
            self.add_api_route(path, func, methods=["GET"], response_model=response_model, status_code=status_code)
            return func

        return decorator

    def post(self, path: str, *, response_model: Any = None, status_code: int = 200):
        def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
            self.add_api_route(path, func, methods=["POST"], response_model=response_model, status_code=status_code)
            return func

        return decorator


class FastAPI:
    def __init__(self, *, title: str = "FastAPI", version: str = "0.1.0") -> None:
        self.title = title
        self.version = version
        self.routes: List[Route] = []
        self._startup_events: List[Callable[[], Awaitable[None] | None]] = []
        self._shutdown_events: List[Callable[[], Awaitable[None] | None]] = []

    def include_router(self, router: APIRouter, *, prefix: str = "") -> None:
        for route in router.routes:
            path = prefix.rstrip("/") + route.path
            self.routes.append(Route(path or "/", route.methods, route.endpoint, response_model=route.response_model, status_code=route.status_code, dependencies=route.dependencies))

    def add_middleware(self, middleware, **kwargs) -> None:  # pragma: no cover - middleware ignored
        pass

    def add_api_route(
        self,
        path: str,
        endpoint: Callable[..., Any],
        *,
        methods: List[str],
        response_model: Any = None,
        status_code: int = 200,
    ) -> None:
        self.routes.append(Route(path, methods, endpoint, response_model=response_model, status_code=status_code))

    def get(self, path: str, *, response_model: Any = None, status_code: int = 200, **kwargs):
        def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
            self.add_api_route(path, func, methods=["GET"], response_model=response_model, status_code=status_code)
            return func

        return decorator

    def post(self, path: str, *, response_model: Any = None, status_code: int = 200, **kwargs):
        def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
            self.add_api_route(path, func, methods=["POST"], response_model=response_model, status_code=status_code)
            return func

        return decorator

    def on_event(self, event_type: str) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
        def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
            if event_type == "startup":
                self._startup_events.append(func)
            elif event_type == "shutdown":
                self._shutdown_events.append(func)
            return func

        return decorator

    async def _run_startup(self) -> None:
        for handler in self._startup_events:
            result = handler()
            if inspect.isawaitable(result):
                await result

    async def _run_shutdown(self) -> None:
        for handler in self._shutdown_events:
            result = handler()
            if inspect.isawaitable(result):
                await result


class ResponseContainer:
    def __init__(self, status_code: int, headers: Dict[str, str], body: Any) -> None:
        self.status_code = status_code
        self.headers = headers
        self.body = body

    def json(self) -> Any:
        return self.body


def _match_path(route_path: str, request_path: str) -> Optional[Dict[str, str]]:
    route_parts = [part for part in route_path.strip("/").split("/") if part]
    request_parts = [part for part in request_path.strip("/").split("/") if part]
    if len(route_parts) != len(request_parts):
        return None
    params: Dict[str, str] = {}
    for route_part, request_part in zip(route_parts, request_parts):
        if route_part.startswith("{") and route_part.endswith("}"):
            params[route_part[1:-1]] = request_part
        elif route_part != request_part:
            return None
    return params


async def _execute(endpoint: Callable[..., Any], kwargs: Dict[str, Any]) -> Any:
    result = endpoint(**kwargs)
    if inspect.isawaitable(result):
        return await result
    return result


def _build_arguments(route: Route, request: Request, path_params: Dict[str, str], body: Any) -> Dict[str, Any]:
    sig = inspect.signature(route.endpoint)
    type_hints = get_type_hints(route.endpoint)
    arguments: Dict[str, Any] = {}
    for name, param in sig.parameters.items():
        annotation = type_hints.get(name, param.annotation)
        if isinstance(param.default, Depends):
            dep = param.default.dependency
            dep_value = _resolve_dependency(dep, request)
            arguments[name] = dep_value
        elif annotation is Request or annotation == Request:
            arguments[name] = request
        elif name in path_params:
            arguments[name] = path_params[name]
        elif is_dataclass(annotation) and isinstance(body, dict):
            arguments[name] = annotation(**body)
        elif body is not None and param.default is inspect._empty:
            arguments[name] = body
        else:
            arguments[name] = param.default if param.default is not inspect._empty else None
    return arguments


def _resolve_dependency(func: Callable[..., Any], request: Request) -> Any:
    sig = inspect.signature(func)
    type_hints = get_type_hints(func)
    kwargs: Dict[str, Any] = {}
    for name, param in sig.parameters.items():
        annotation = type_hints.get(name, param.annotation)
        if isinstance(param.default, Depends):
            kwargs[name] = _resolve_dependency(param.default.dependency, request)
        elif annotation is Request or annotation == Request:
            kwargs[name] = request
        else:
            kwargs[name] = param.default if param.default is not inspect._empty else None
    result = func(**kwargs)
    if inspect.isawaitable(result):
        return asyncio.get_event_loop().run_until_complete(result)
    return result


def _serialize(value: Any) -> Any:
    if hasattr(value, "dict") and callable(getattr(value, "dict")):
        return value.dict()
    if is_dataclass(value):
        return asdict(value)
    if isinstance(value, list):
        return [_serialize(item) for item in value]
    if isinstance(value, dict):
        return {key: _serialize(val) for key, val in value.items()}
    return value


async def call_route(app: FastAPI, method: str, path: str, headers: Dict[str, str], query: Dict[str, List[str]], body: Any | None) -> ResponseContainer:
    for route in app.routes:
        if method not in route.methods:
            continue
        params = _match_path(route.path, path)
        if params is None:
            continue
        request = Request(method, path, headers, query, body)
        try:
            kwargs = _build_arguments(route, request, params, body)
            result = await _execute(route.endpoint, kwargs)
        except HTTPException as exc:
            return ResponseContainer(exc.status_code, {}, {"detail": exc.detail})

        if isinstance(result, StreamingResponse):
            return ResponseContainer(route.status_code, result.headers, result.body)
        if isinstance(result, JSONResponse):
            return ResponseContainer(result.status_code, result.headers, result.content)
        if isinstance(result, Response):
            return ResponseContainer(result.status_code, result.headers, result.body)
        return ResponseContainer(route.status_code, {}, _serialize(result))
    return ResponseContainer(404, {}, {"detail": "Not Found"})


__all__ = [
    "APIRouter",
    "Depends",
    "FastAPI",
    "HTTPException",
    "JSONResponse",
    "Request",
    "StreamingResponse",
]
