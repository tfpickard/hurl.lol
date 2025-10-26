# Hurl

**The Internet, but synthetic.**

Hurl is a production-ready synthetic social media post generator that creates realistic, slightly chaotic posts from AI-generated personas. Experience an infinite feed of synthetic social media content with emergent dynamics or pure randomness.

## Features

- **Dual Modes**: Emergent (collective dynamics with trend propagation) or Pure Random
- **100+ Diverse Personas**: Each with unique interests, styles, behaviors, and stances
- **Dynamic Topic Graph**: 40+ topics with trend scores, shocks, and network effects
- **Real-Time Streaming**: SSE-based infinite feed
- **Customizable Filters**: Topics, languages, toxicity levels, personas
- **Deterministic Generation**: Reproducible results with seed control
- **Optional LLM Integration**: Feature-flagged support for OpenAI, Ollama, or local models
- **REST API**: Full-featured API at `hurl.rest` (when deployed)
- **CLI Tool**: Bulk generation with NDJSON output
- **Metrics & Monitoring**: Prometheus metrics and rich logging

## Quick Start

### Using Docker Compose (Recommended)

```bash
# Start both backend and frontend
docker compose up

# Backend: http://localhost:8000
# Frontend: http://localhost:3000
# API Docs: http://localhost:8000/docs
```

### Manual Setup

#### Backend

```bash
cd backend

# Create virtual environment (Python 3.12+)
make venv
source .venv/bin/activate

# Install dependencies
make install

# Run development server
make dev

# Backend now running at http://localhost:8000
```

#### Frontend

```bash
cd frontend

# Install dependencies
npm install

# Run development server
npm run dev

# Frontend now running at http://localhost:3000
```

## API Examples

### Generate Posts

```bash
# Generate 25 posts in emergent mode
curl -X POST http://localhost:8000/v1/generate \
  -H 'Content-Type: application/json' \
  -d '{
    "count": 25,
    "mode": "emergent",
    "seed": 42
  }'
```

### Stream Posts (SSE)

```bash
# Stream posts in real-time
curl -N http://localhost:8000/v1/stream?mode=emergent&interval=1.0
```

### Filter by Topics

```bash
# Generate posts about AI and crypto
curl -X POST http://localhost:8000/v1/generate \
  -H 'Content-Type: application/json' \
  -d '{
    "count": 10,
    "mode": "emergent",
    "topics": ["ai", "crypto"]
  }'
```

### List Topics

```bash
curl http://localhost:8000/v1/topics
```

### List Personas

```bash
curl http://localhost:8000/v1/personas
```

### Inject a Trend Shock

```bash
# Inject a shock to boost "ai" trending
curl -X POST http://localhost:8000/v1/admin/shock \
  -H 'Content-Type: application/json' \
  -d '{
    "topic_id": "ai",
    "magnitude": 3.0,
    "half_life_s": 300
  }'
```

### View Current Trends

```bash
curl http://localhost:8000/v1/admin/trends
```

## CLI Usage

```bash
# Generate 100 posts and output as NDJSON
python backend/scripts/hurlgen.py --count 100 --mode emergent --seed 42 > posts.ndjson

# Generate posts about specific topics
python backend/scripts/hurlgen.py --count 50 --topic ai --topic crypto --output text

# Generate with specific personas
python backend/scripts/hurlgen.py --count 20 --persona PERSONA_ID --output json
```

## Project Structure

```
hurl/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI application
│   │   ├── config.py            # Configuration management
│   │   ├── schemas.py           # Pydantic models
│   │   ├── sse.py               # SSE helpers
│   │   ├── routers/             # API endpoints
│   │   │   ├── posts.py         # Post generation & streaming
│   │   │   ├── personas.py      # Persona management
│   │   │   ├── topics.py        # Topic listing
│   │   │   ├── admin.py         # Admin endpoints (shocks, seeds)
│   │   │   └── health.py        # Health check
│   │   ├── services/
│   │   │   ├── generator/
│   │   │   │   ├── core.py      # Text generation (templates, Markov)
│   │   │   │   ├── llm.py       # Optional LLM adapter
│   │   │   │   ├── styles.py    # Style decorators (emoji, hashtags)
│   │   │   │   └── metrics.py   # Engagement simulation
│   │   │   ├── personas.py      # 100+ seed personas
│   │   │   ├── topics.py        # Topic graph (40+ topics)
│   │   │   ├── trends.py        # Trend engine with emergent dynamics
│   │   │   └── rng.py           # Deterministic RNG utilities
│   │   └── store/
│   │       ├── memory.py        # In-memory post storage
│   │       └── sqlite.py        # Optional SQLite persistence
│   ├── scripts/
│   │   └── hurlgen.py           # CLI tool
│   ├── tests/
│   │   ├── test_api.py
│   │   └── test_generator.py
│   ├── Makefile
│   ├── Dockerfile
│   ├── requirements.txt
│   └── pyproject.toml
├── frontend/
│   ├── pages/
│   │   ├── index.tsx            # Main feed UI
│   │   └── _app.tsx
│   ├── lib/
│   │   └── sse.ts               # SSE client library
│   ├── package.json
│   └── README.md
├── docker-compose.yml
└── README.md
```

## Configuration

Create a `.env` file in the backend directory:

```bash
HURL_ENV=dev
HURL_REQUIRE_AUTH=0
HURL_PERSIST=0
HURL_LLM_PROVIDER=none
HURL_LLM_API_KEY=
HURL_ALLOW_ORIGINS=https://hurl.lol,http://localhost:3000
HOST=0.0.0.0
PORT=8000
```

### Optional LLM Integration

To enable LLM enhancement (20% of posts):

```bash
# For OpenAI
HURL_LLM_PROVIDER=openai
HURL_LLM_API_KEY=sk-...

# For Ollama (local)
HURL_LLM_PROVIDER=ollama

# For custom local model
HURL_LLM_PROVIDER=local
```

## How It Works

### Emergent Mode

In emergent mode, topic adoption follows network dynamics:

```
p = σ(α*trend + β*peer_influence + γ*interest_match + δ*recency_decay + ε*shock)
```

- **Trend scores** propagate through the topic graph
- **Shocks** inject exogenous spikes (e.g., breaking news)
- **Peer influence** simulates social contagion
- **Recency decay** prevents topic repetition
- **Bandwagon effects** create viral cascades

### Pure Random Mode

Bypasses all dynamics and samples topics uniformly (weighted by persona interests).

### Text Generation Pipeline

1. **Topic Selection**: Emergent dynamics or random sampling
2. **Template Selection**: Based on persona style (hot takes, observations, questions, etc.)
3. **Text Generation**: Templates + Markov chain texture
4. **Optional LLM Enhancement**: 20% of posts pass through LLM (if enabled)
5. **Style Decoration**: Emojis, hashtags, links, caps, punctuation quirks
6. **Toxicity Sanitization**: Profanity masking based on persona settings

## Development

### Running Tests

```bash
cd backend
make test

# Or faster without coverage
make test-fast
```

### Code Quality

```bash
# Format code
make fmt

# Run linters
make lint
```

### Adding a New Topic

Edit `backend/app/services/topics.py`:

```python
SEED_TOPICS.append({
    "id": "new_topic",
    "name": "New Topic",
    "tags": ["category", "tag"],
})

# Add edges to related topics
TOPIC_EDGES.append(("new_topic", "related_topic", 0.7))
```

### Adding a Custom Persona

```bash
curl -X POST http://localhost:8000/v1/personas \
  -H 'Content-Type: application/json' \
  -d '{
    "display_name": "Custom User",
    "handle": "customuser",
    "bio": "A custom persona",
    "interests": {"ai": 0.9, "crypto": 0.7}
  }'
```

## Deployment

### Backend (FastAPI)

```bash
# Build Docker image
docker build -t hurl-backend ./backend

# Run container
docker run -p 8000:8000 -e HURL_ENV=prod hurl-backend
```

### Frontend (Next.js)

```bash
cd frontend
npm run build
npm start
```

Or deploy to Vercel/Netlify with environment variable:
```
NEXT_PUBLIC_API_URL=https://hurl.rest
```

## Monitoring

Prometheus metrics available at `/metrics`:

- `hurl_requests_total`: Total request count
- `hurl_request_duration_seconds`: Request latency
- `hurl_posts_generated_total`: Total posts generated by mode

## License

MIT License - see LICENSE file for details.

## Disclaimer

All posts are synthetic. No real users, opinions, or data. Hurl responsibly.

---

© Hurl. Made with synthetic chaos.
