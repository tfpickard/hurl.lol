# Hurl Frontend

Next.js frontend for the Hurl synthetic social media generator.

## Setup

```bash
npm install
```

## Development

```bash
npm run dev
```

Open http://localhost:4000 in your browser.

## Build

```bash
npm run build
npm start
```

## Environment

The frontend connects to the API at `http://localhost:8000` by default. You can change this in the UI.

## Features

- Real-time SSE streaming of posts
- Mode toggle (Emergent / Pure Random)
- Topic filtering
- Seed control for reproducibility
- Impact panel showing post influences
- Infinite scroll feed
