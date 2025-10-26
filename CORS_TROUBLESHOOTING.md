# CORS and Mixed Content Troubleshooting

## Common Issue: Connecting from https://hurl.lol to localhost

### The Problem

When visiting the production site `https://hurl.lol` and trying to connect to a local backend at `http://localhost:8000`, you'll encounter two browser security errors:

1. **Mixed Content Error** (Primary Issue)
   ```
   [blocked] The page at https://hurl.lol/ requested insecure content from http://localhost:8000/v1/stream
   ```

2. **CORS Error** (Secondary Issue)
   ```
   EventSource cannot load http://localhost:8000/v1/stream due to access control checks.
   ```

### Why This Happens

**Mixed Content Policy**: Modern browsers block HTTP requests from HTTPS pages for security reasons. This prevents attackers from injecting insecure content into secure pages.

**CORS (Cross-Origin Resource Sharing)**: Even if mixed content wasn't an issue, CORS headers must be configured to allow the production domain to access your local backend.

## Solutions

### Solution 1: Run Frontend Locally (Recommended for Development)

Instead of using the production site, run the frontend locally:

```bash
cd frontend
npm install
npm run dev
```

Then visit `http://localhost:4000` and connect to `http://localhost:8000`. Both are HTTP, so no mixed content issue.

### Solution 2: Use HTTPS for Local Backend

Run your local backend with HTTPS using a self-signed certificate:

1. Generate a self-signed certificate:
   ```bash
   openssl req -x509 -newkey rsa:4096 -keyout key.pem -out cert.pem -days 365 -nodes
   ```

2. Run the backend with SSL:
   ```bash
   cd backend
   uvicorn app.main:app --host 0.0.0.0 --port 8000 --ssl-keyfile=../key.pem --ssl-certfile=../cert.pem
   ```

3. Accept the browser's security warning for the self-signed certificate

4. Connect from `https://hurl.lol` to `https://localhost:8000`

### Solution 3: Browser Flags (Not Recommended)

You can temporarily disable mixed content blocking in your browser, but this is NOT recommended for security reasons:

**Chrome/Edge:**
```
--allow-running-insecure-content --disable-web-security --user-data-dir=/tmp/chrome-dev
```

**Note**: Only use this for testing, never for regular browsing.

### Solution 4: Use a Reverse Proxy

Set up a local reverse proxy (nginx, Caddy) that:
- Listens on HTTPS
- Forwards to your HTTP backend
- Provides a valid SSL certificate (via Let's Encrypt or self-signed)

## CORS Configuration

The backend is configured to allow the following origins by default:

- `https://hurl.lol` (production)
- `http://localhost:4000` (local frontend)
- `http://localhost:8000` (local backend)
- `https://localhost:8000` (local HTTPS backend)
- `http://127.0.0.1:4000` (alternative localhost)
- `http://127.0.0.1:8000` (alternative localhost)

### Customizing CORS Origins

You can override the allowed origins via environment variable:

```bash
export HURL_ALLOW_ORIGINS="https://hurl.lol,http://localhost:4000,http://localhost:8000"
```

Or in your `.env` file:

```
HURL_ALLOW_ORIGINS=https://hurl.lol,http://localhost:4000,http://localhost:8000
```

### Verifying CORS Configuration

When the backend starts, it will log the allowed origins:

```
INFO:     Allowed CORS origins: ['https://hurl.lol', 'http://localhost:4000', ...]
```

You can also check the CORS headers in your browser's network tab:

```
Access-Control-Allow-Origin: https://hurl.lol
Access-Control-Allow-Credentials: true
Access-Control-Allow-Methods: *
Access-Control-Allow-Headers: *
```

## Testing Your Setup

1. **Start the backend:**
   ```bash
   cd backend
   python -m app.main
   ```

2. **Verify CORS headers:**
   ```bash
   curl -H "Origin: https://hurl.lol" -H "Access-Control-Request-Method: GET" \
        -H "Access-Control-Request-Headers: X-Requested-With" \
        -X OPTIONS http://localhost:8000/v1/healthz -v
   ```

   Look for `Access-Control-Allow-Origin: https://hurl.lol` in the response.

3. **Test the stream endpoint:**
   ```bash
   curl -H "Origin: https://hurl.lol" http://localhost:8000/v1/stream\?mode=emergent\&interval=1 -v
   ```

## Production Deployment

In production, CORS is automatically configured via Docker Compose:

```yaml
environment:
  - HURL_ALLOW_ORIGINS=https://hurl.lol,http://localhost:4000,...
```

Make sure your production environment has the correct origins configured.

## Still Having Issues?

1. **Check browser console**: Look for specific error messages
2. **Check backend logs**: Verify the CORS configuration on startup
3. **Test with curl**: Eliminate browser-specific issues
4. **Verify network**: Ensure localhost:8000 is accessible
5. **Check firewall**: Ensure port 8000 is not blocked

## Security Note

CORS allows controlled access to your API from different origins. Be careful when adding origins to the allowed list, especially in production. Only add origins you trust.

For development, it's safe to allow localhost origins. For production, only allow your actual production domains.
