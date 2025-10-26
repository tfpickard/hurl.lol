# Nginx Configuration for Hurl

This directory contains nginx configuration files for deploying Hurl alongside other applications on the same server.

## Files

- **hurl.lol.conf**: Production-ready nginx configuration for hurl.lol
- **yodo.lol.conf.template**: Template configuration for yodo.lol (customize as needed)
- **DEPLOYMENT.md**: Comprehensive deployment guide with step-by-step instructions

## Quick Start

1. Read [DEPLOYMENT.md](./DEPLOYMENT.md) for detailed instructions
2. Copy `hurl.lol.conf` to `/etc/nginx/sites-available/`
3. Create a symlink in `/etc/nginx/sites-enabled/`
4. Test the configuration with `sudo nginx -t`
5. Reload nginx with `sudo systemctl reload nginx`

## Configuration Overview

The nginx setup routes traffic based on domain names:

```
hurl.lol → Backend (port 8000) + Frontend (port 4000)
yodo.lol → Your existing application (configure as needed)
```

### Key Features

- Domain-based routing for multiple applications
- SSE (Server-Sent Events) support for real-time streaming
- WebSocket support for Next.js hot reload
- Static asset caching for better performance
- Ready-to-use SSL/HTTPS configuration (commented out)
- Proper proxy headers and timeouts

## Port Requirements

Make sure these ports are available and services are running:

- **8000**: Hurl backend (FastAPI)
- **4000**: Hurl frontend (Next.js)
- **80**: nginx HTTP
- **443**: nginx HTTPS (optional, for SSL)

## Next Steps

1. **Test locally**: Start your backend and frontend services
2. **Configure nginx**: Follow the deployment guide
3. **Set up SSL**: Use certbot for free HTTPS certificates
4. **Monitor**: Check logs in `/var/log/nginx/`

For detailed instructions, see [DEPLOYMENT.md](./DEPLOYMENT.md).
