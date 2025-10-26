from __future__ import annotations

from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_healthcheck() -> None:
    response = client.get("/v1/healthz")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_generate_endpoint() -> None:
    response = client.post("/v1/generate", json={"count": 2, "mode": "pure_random"})
    assert response.status_code == 200
    payload = response.json()
    assert isinstance(payload, list)
    assert len(payload) == 2
    assert {"id", "text", "persona_id"}.issubset(payload[0])


def test_seed_endpoint() -> None:
    response = client.post("/v1/seed", json={"seed": 99})
    assert response.status_code == 200
    assert response.json()["seed"] == 99


def test_stream_endpoint() -> None:
    with client.stream("GET", "/v1/stream", timeout=3) as stream:
        first = next(stream.iter_lines())
        assert first is not None
