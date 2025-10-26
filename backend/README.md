# Hurl Backend

Synthetic social-media generator powering **Hurl**.

## Quick start

```bash
make venv
make install
make run
```

The API is available at http://localhost:8000 with docs at http://localhost:8000/docs.

### Example requests

```bash
curl -X POST http://localhost:8000/v1/generate \
  -H 'content-type: application/json' \
  -d '{"count": 5, "mode": "emergent"}'

curl http://localhost:8000/v1/personas | jq '.[:2]'
```

### CLI generator

```bash
python backend/scripts/hurlgen.py --count 20 --mode emergent --seed 42 > posts.ndjson
```

### Docker

```bash
docker build -t hurl-backend backend
```
