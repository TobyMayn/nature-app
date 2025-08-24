# Nature App Deployment Guide

## Architecture Overview

- **Frontend**: Hosted on Vercel
- **Backend**: Docker containers on your server (130.226.56.134)
- **Reverse Proxy**: LXD container running nginx with Let's Encrypt SSL
- **Domain**: natureapp.duckdns.org

## Setup Instructions

### 1. Server Prerequisites

Ensure your server has:
- LXD installed and initialized
- Docker and Docker Compose installed
- Port 80 and 443 accessible from the internet
- Domain `natureapp.duckdns.org` pointing to your server IP

### 2. Deploy Backend with HTTPS

```bash
# Clone/upload your code to the server
cd /path/to/nature-app

# Update email and Vercel URL in deploy.sh
vim deploy.sh

# Run deployment script
./deploy.sh
```

### 3. Deploy Frontend to Vercel

1. Push your code to GitHub
2. Connect GitHub repo to Vercel
3. Set environment variable in Vercel:
   ```
   NEXT_PUBLIC_API_URL=https://natureapp.duckdns.org/api
   ```
4. Deploy to Vercel

### 4. Update CORS Settings

After deploying to Vercel, update the nginx configuration with your Vercel URL:

```bash
# Edit nginx config
lxc exec nginx-proxy -- nano /etc/nginx/nginx.conf

# Replace "your-vercel-app.vercel.app" with your actual Vercel URL
# Then restart nginx
lxc exec nginx-proxy -- systemctl restart nginx
```

## Configuration Files

- `nginx/nginx.conf`: Nginx reverse proxy configuration
- `lxd/setup-container.sh`: LXD container setup script
- `docker-compose.yml`: Updated to expose backend on port 8080
- `deploy.sh`: Main deployment script

## API Endpoints

Your API will be available at:
- `https://natureapp.duckdns.org/api/users`
- `https://natureapp.duckdns.org/api/results`
- `https://natureapp.duckdns.org/api/auth`

## Monitoring and Maintenance

### Check nginx logs
```bash
lxc exec nginx-proxy -- tail -f /var/log/nginx/access.log
lxc exec nginx-proxy -- tail -f /var/log/nginx/error.log
```

### Check SSL certificate
```bash
lxc exec nginx-proxy -- certbot certificates
```

### Restart services
```bash
# Restart nginx
lxc exec nginx-proxy -- systemctl restart nginx

# Restart backend
docker-compose restart backend

# Check container status
lxc list nginx-proxy
docker-compose ps
```

### Certificate Renewal

Let's Encrypt certificates auto-renew via cron job. To manually renew:
```bash
lxc exec nginx-proxy -- certbot renew --dry-run
```

## Security Features

- HTTPS with Let's Encrypt SSL certificates
- Security headers (HSTS, CSP, etc.)
- Rate limiting on API endpoints
- CORS configured for your Vercel domain
- Modern TLS configuration (TLS 1.2 and 1.3)

## Troubleshooting

### Backend not accessible
1. Check if docker containers are running: `docker-compose ps`
2. Check if port 8080 is accessible: `curl http://localhost:8080/health`
3. Check nginx logs for errors

### SSL certificate issues
1. Ensure domain points to your server
2. Check Let's Encrypt logs: `lxc exec nginx-proxy -- journalctl -u certbot`
3. Manually test certificate: `lxc exec nginx-proxy -- certbot renew --dry-run`

### CORS issues
1. Verify Vercel URL in nginx config
2. Check browser developer tools for CORS errors
3. Update nginx config and restart: `lxc exec nginx-proxy -- systemctl restart nginx`