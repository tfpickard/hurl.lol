# Hurl Backend

FastAPI-based backend for Hurl synthetic social media post generator.

## Features

- **REST API** with OpenAPI docs
- **SSE streaming** for real-time post feed
- **100+ seed personas** with diverse traits
- **40+ topics** with dynamic trend propagation
- **Emergent dynamics** modeling social contagion
- **Deterministic generation** with seed control
- **Optional LLM integration** (OpenAI, Ollama, local)
- **Prometheus metrics** for monitoring
- **In-memory storage** with optional SQLite persistence

## Quick Start

```bash
# Create virtual environment
make venv
source .venv/bin/activate

# Install dependencies
make install

# Run development server
make dev

# API now available at http://localhost:8000
# Docs at http://localhost:8000/docs
```

## API Endpoints

### Core Endpoints

- `GET /v1/healthz` - Health check
- `POST /v1/generate` - Generate batch of posts
- `GET /v1/stream` - SSE stream of posts
- `GET /v1/sample` - Sample posts (convenience)

### Personas

- `GET /v1/personas` - List all personas
- `GET /v1/personas/{id}` - Get specific persona
- `POST /v1/personas` - Create custom persona

### Topics

- `GET /v1/topics` - List all topics
- `GET /v1/topics/{id}` - Get specific topic

### Admin

- `POST /v1/admin/shock` - Inject trend shock
- `GET /v1/admin/trends` - View current trends
- `POST /v1/admin/seed` - Set global RNG seed

### Monitoring

- `GET /metrics` - Prometheus metrics

## Development

### Running Tests

```bash
# Run all tests with coverage
make test

# Run tests without coverage (faster)
make test-fast
```

### Code Quality

```bash
# Format code with black
make fmt

# Run linters (ruff, mypy)
make lint
```

### CLI Tool

```bash
# Generate posts from CLI
make hurlgen ARGS="--count 50 --mode emergent --output text"

# Or directly
python scripts/hurlgen.py --count 100 --topic ai --seed 42 > posts.ndjson
```

## Configuration

Environment variables (create `.env` file):

```bash
HURL_ENV=dev
HOST=0.0.0.0
PORT=8000
HURL_REQUIRE_AUTH=0
HURL_PERSIST=0
HURL_LLM_PROVIDER=none
HURL_LLM_API_KEY=
HURL_ALLOW_ORIGINS=https://hurl.lol,http://localhost:4000
HURL_DEFAULT_SEED=
HURL_MAX_BATCH_SIZE=1000
HURL_TREND_TICK_INTERVAL=5.0
```

## Architecture

### Services

- **generator/core.py** - Template-based text generation with Markov chains
- **generator/llm.py** - Optional LLM adapter (provider-agnostic)
- **generator/styles.py** - Style decorators (emojis, hashtags, links)
- **generator/metrics.py** - Engagement metrics simulation
- **personas.py** - 100+ seed personas with traits and behaviors
- **topics.py** - Topic graph with 40+ topics and relationships
- **trends.py** - Trend engine with emergent dynamics
- **rng.py** - Deterministic RNG with PCG64

### Storage

- **store/memory.py** - In-memory sliding window (default)
- **store/sqlite.py** - Optional SQLite persistence (HURL_PERSIST=1)

### Routers

- **posts.py** - Post generation and streaming
- **personas.py** - Persona CRUD
- **topics.py** - Topic listing
- **admin.py** - Trend shocks and seed management
- **health.py** - Health checks

## Adding Features

### Add a New Topic

Edit `app/services/topics.py`:

```python
SEED_TOPICS.append({
    "id": "my_topic",
    "name": "My Topic",
    "tags": ["category"],
})

TOPIC_EDGES.append(("my_topic", "related_topic", 0.7))
```

### Add Custom Templates

Edit `app/services/generator/core.py`:

```python
TEMPLATES["my_category"] = [
    "New template: {topic} {verb}",
    "Another template about {topic}",
]
```

### Enable LLM

```bash
# OpenAI
export HURL_LLM_PROVIDER=openai
export HURL_LLM_API_KEY=sk-...

# Ollama (local)
export HURL_LLM_PROVIDER=ollama

# Restart server
make dev
```

## Docker

```bash
# Build image
docker build -t hurl-backend .

# Run container
docker run -p 8000:8000 \
  -e HURL_ENV=prod \
  -e HURL_LLM_PROVIDER=none \
  hurl-backend
```

## Testing

### Unit Tests

```bash
pytest tests/test_generator.py -v
```

### API Tests

```bash
pytest tests/test_api.py -v
```

### Load Testing

```bash
# Generate 1000 posts
curl -X POST http://localhost:8000/v1/generate \
  -H 'Content-Type: application/json' \
  -d '{"count": 1000, "seed": 42}'
```

## Performance

- **Batch generation**: ~100-500 posts/sec (without LLM)
- **SSE streaming**: Configurable interval (default 1 post/sec)
- **Memory footprint**: ~50MB baseline + ~10KB per stored post
- **LLM mode**: ~20% overhead when enabled (150ms budget per post)

## License

MIT
