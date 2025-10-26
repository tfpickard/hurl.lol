# Hurl

Synthetic social-media simulator powering [hurl.lol](https://hurl.lol) and the Hurl REST API.

## Project layout

```
hurl/
  backend/    # FastAPI service and generator core
  frontend/   # Next.js demo client for hurl.lol
```

## Backend (FastAPI)

```bash
cd backend
make venv
make install
make run
```

API served at http://localhost:8000 (OpenAPI docs at `/docs`).

Example:

```bash
curl -X POST http://localhost:8000/v1/generate \
  -H 'content-type: application/json' \
  -d '{"count": 25, "mode": "emergent"}'
```

## Frontend (Next.js)

```bash
cd frontend
npm install
npm run dev
```

Visit http://localhost:3000. Override backend origin with `NEXT_PUBLIC_HURL_API`.

## Testing

```bash
cd backend
pytest
```

## License

[MIT](LICENSE)
