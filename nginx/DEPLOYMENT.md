# Nginx Deployment Guide for hurl.lol and yodo.lol

This guide explains how to configure nginx to route requests for multiple domains on a single server.

## Overview

The nginx configuration routes requests based on the domain name:

- **hurl.lol** → Hurl application (backend: port 8000, frontend: port 4000)
- **yodo.lol** → Your existing application (configure as needed)

## Prerequisites

1. nginx installed on your server
2. Backend and frontend services running on their respective ports
3. Domain names (hurl.lol and yodo.lol) pointing to your server's IP address

## Installation Steps

### 1. Install nginx (if not already installed)

```bash
# Ubuntu/Debian
sudo apt update
sudo apt install nginx

# CentOS/RHEL
sudo yum install nginx

# macOS
brew install nginx
```

### 2. Copy Configuration Files

```bash
# Copy the hurl.lol configuration
sudo cp nginx/hurl.lol.conf /etc/nginx/sites-available/hurl.lol.conf

# Copy the yodo.lol configuration (and customize it)
sudo cp nginx/yodo.lol.conf.template /etc/nginx/sites-available/yodo.lol.conf
sudo nano /etc/nginx/sites-available/yodo.lol.conf  # Edit as needed
```

### 3. Enable the Configurations

```bash
# Create symbolic links to enable the sites
sudo ln -s /etc/nginx/sites-available/hurl.lol.conf /etc/nginx/sites-enabled/
sudo ln -s /etc/nginx/sites-available/yodo.lol.conf /etc/nginx/sites-enabled/
```

### 4. Test nginx Configuration

```bash
# Test for syntax errors
sudo nginx -t

# If successful, you should see:
# nginx: configuration file /etc/nginx/nginx.conf test is successful
```

### 5. Start Your Applications

Make sure both backend and frontend are running on their configured ports:

```bash
# For hurl.lol - start backend on port 8000
cd /path/to/hurl.lol/backend
source .venv/bin/activate
python -m backend.app.main

# In another terminal - start frontend on port 4000
cd /path/to/hurl.lol/frontend
npm run dev

# Or use Docker Compose:
cd /path/to/hurl.lol
docker compose up -d
```

### 6. Reload nginx

```bash
# Reload nginx to apply the new configuration
sudo systemctl reload nginx

# Or restart if reload doesn't work
sudo systemctl restart nginx

# Check status
sudo systemctl status nginx
```

## Verifying the Setup

Test that the routing is working correctly:

```bash
# Test hurl.lol (replace with your server IP or domain)
curl -H "Host: hurl.lol" http://localhost/
curl -H "Host: hurl.lol" http://localhost/v1/healthz

# Test yodo.lol
curl -H "Host: yodo.lol" http://localhost/
```

## Setting Up SSL/HTTPS with Let's Encrypt

Once the HTTP configuration is working, add SSL certificates:

### 1. Install Certbot

```bash
# Ubuntu/Debian
sudo apt install certbot python3-certbot-nginx

# CentOS/RHEL
sudo yum install certbot python3-certbot-nginx

# macOS
brew install certbot
```

### 2. Obtain Certificates

```bash
# For hurl.lol
sudo certbot --nginx -d hurl.lol -d www.hurl.lol

# For yodo.lol
sudo certbot --nginx -d yodo.lol -d www.yodo.lol
```

### 3. Uncomment HTTPS Blocks

After obtaining certificates, uncomment the HTTPS server blocks in the nginx configuration files and reload:

```bash
sudo nano /etc/nginx/sites-available/hurl.lol.conf
# Uncomment the server block starting with "listen 443 ssl http2"

sudo nginx -t
sudo systemctl reload nginx
```

### 4. Set Up Auto-Renewal

Certbot automatically creates a renewal timer. Verify it:

```bash
sudo systemctl status certbot.timer

# Or test renewal
sudo certbot renew --dry-run
```

## Port Configuration

### Current Port Mapping

- **Port 8000**: Backend API (FastAPI)
- **Port 4000**: Frontend (Next.js)
- **Port 80**: nginx HTTP
- **Port 443**: nginx HTTPS (after SSL setup)

### If You Need to Change Ports

If ports 8000 or 4000 are already in use by another application:

1. **Change the backend port** by editing `backend/.env`:
   ```bash
   PORT=8001  # Or any available port
   ```

2. **Update nginx configuration** in `nginx/hurl.lol.conf`:
   ```nginx
   upstream hurl_backend {
       server localhost:8001;  # Match the new port
   }
   ```

3. **Change the frontend port** by editing `frontend/package.json` or starting with:
   ```bash
   PORT=4001 npm run dev
   ```

4. **Update nginx configuration**:
   ```nginx
   upstream hurl_frontend {
       server localhost:4001;  # Match the new port
   }
   ```

## Troubleshooting

### Check nginx Error Logs

```bash
sudo tail -f /var/log/nginx/error.log
sudo tail -f /var/log/nginx/hurl.lol.error.log
```

### Check Application Logs

```bash
# Backend logs (if running via systemd)
journalctl -u hurl-backend -f

# Docker logs
docker compose logs -f
```

### Common Issues

1. **502 Bad Gateway**: Backend/frontend not running or wrong port
   - Check if services are running: `netstat -tlnp | grep -E ':(8000|4000)'`
   - Verify ports in nginx config match running services

2. **Permission Denied**: SELinux blocking nginx connections
   ```bash
   # Allow nginx to make network connections (CentOS/RHEL)
   sudo setsebool -P httpd_can_network_connect 1
   ```

3. **Connection Refused**: Firewall blocking ports
   ```bash
   # Open ports (Ubuntu/Debian)
   sudo ufw allow 'Nginx Full'

   # CentOS/RHEL
   sudo firewall-cmd --permanent --add-service=http
   sudo firewall-cmd --permanent --add-service=https
   sudo firewall-cmd --reload
   ```

## Production Considerations

### 1. Use a Process Manager

Instead of running the backend manually, use systemd or supervisor:

**Example systemd service** (`/etc/systemd/system/hurl-backend.service`):

```ini
[Unit]
Description=Hurl Backend API
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/path/to/hurl.lol/backend
Environment="PATH=/path/to/hurl.lol/backend/.venv/bin"
ExecStart=/path/to/hurl.lol/backend/.venv/bin/python -m backend.app.main
Restart=always

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl enable hurl-backend
sudo systemctl start hurl-backend
```

### 2. Use PM2 for Frontend (Production)

```bash
cd frontend
npm run build
pm2 start npm --name "hurl-frontend" -- start
pm2 save
pm2 startup
```

### 3. Enable nginx Cache (Optional)

Add to nginx configuration for better performance:

```nginx
proxy_cache_path /var/cache/nginx/hurl levels=1:2 keys_zone=hurl_cache:10m max_size=1g inactive=60m;

# In location block:
proxy_cache hurl_cache;
proxy_cache_valid 200 10m;
```

### 4. Rate Limiting

Add to nginx configuration to prevent abuse:

```nginx
limit_req_zone $binary_remote_addr zone=hurl_limit:10m rate=10r/s;

# In server block:
limit_req zone=hurl_limit burst=20 nodelay;
```

## Environment Variables

Make sure to set production environment variables:

**Backend** (`backend/.env`):
```bash
HURL_ENV=prod
HOST=0.0.0.0
PORT=8000
HURL_ALLOW_ORIGINS=https://hurl.lol
HURL_LLM_PROVIDER=none  # or openai/ollama if configured
HURL_PERSIST=1  # Enable SQLite persistence
```

**Frontend** (`frontend/.env.production`):
```bash
NEXT_PUBLIC_API_URL=https://hurl.lol
NODE_ENV=production
```

## Monitoring

Monitor your applications:

```bash
# Check nginx status
sudo systemctl status nginx

# Monitor connections
sudo netstat -an | grep -E ':(80|443|8000|4000)'

# Watch nginx access logs
sudo tail -f /var/log/nginx/hurl.lol.access.log

# Monitor system resources
htop
```

## Security Checklist

- [ ] SSL/HTTPS configured with valid certificates
- [ ] Firewall configured (only ports 80, 443, 22 open)
- [ ] Rate limiting enabled
- [ ] CORS configured correctly in backend
- [ ] Environment variables secured (no secrets in code)
- [ ] nginx running as non-root user
- [ ] Regular security updates enabled
- [ ] Logs monitored for suspicious activity

## Support

For issues with:
- **Nginx**: Check `/var/log/nginx/error.log`
- **Hurl Backend**: Check application logs or use `/v1/healthz`
- **Hurl Frontend**: Check browser console and network tab

## Quick Reference

```bash
# Restart nginx
sudo systemctl restart nginx

# Test nginx config
sudo nginx -t

# View nginx status
sudo systemctl status nginx

# Reload nginx (graceful restart)
sudo systemctl reload nginx

# View logs
sudo tail -f /var/log/nginx/error.log
sudo tail -f /var/log/nginx/hurl.lol.access.log
```
