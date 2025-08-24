#!/bin/bash

# Deployment script for Nature App with HTTPS reverse proxy
# Run this script on your server (130.226.56.134)

set -e

DOMAIN="natureapp.duckdns.org"
EMAIL="tobiasmayn@gmail.com"  # Update this with your email
VERCEL_URL="nature-app-ten.vercel.app"  # Update this with your Vercel app URL

echo "🌿 Nature App Deployment Script"
echo "================================"

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check prerequisites
echo "Checking prerequisites..."
if ! command_exists lxd; then
    echo "❌ LXD is not installed. Please install LXD first."
    echo "   sudo snap install lxd"
    echo "   sudo lxd init"
    exit 1
fi

if ! command_exists docker; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

if ! command_exists docker-compose; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

echo "✅ Prerequisites check passed"

# Update nginx configuration with Vercel URL
echo "📝 Updating nginx configuration..."
if [ "$VERCEL_URL" = "your-vercel-app.vercel.app" ]; then
    echo "⚠️  Please update VERCEL_URL in this script with your actual Vercel app URL"
    read -p "Enter your Vercel app URL (e.g., my-app.vercel.app): " VERCEL_URL
fi

# Update CORS origin in nginx config
sed -i "s|https://your-vercel-app.vercel.app|https://$VERCEL_URL|g" nginx/nginx.conf

# Update email in LXD setup script
if [ "$EMAIL" = "your-email@example.com" ]; then
    read -p "Enter your email for Let's Encrypt: " EMAIL
fi
sed -i "s/your-email@example.com/$EMAIL/g" lxd/setup-container.sh

echo "🚀 Starting deployment..."

# Stop any existing containers
echo "🛑 Stopping existing containers..."
docker-compose down || true

# Build and start backend services
echo "🏗️  Building and starting backend services..."
docker-compose up -d

# Wait for services to be ready
echo "⏳ Waiting for backend services to start..."
sleep 30

# Test backend health
echo "🔍 Testing backend health..."
if curl -f http://localhost:8080/health > /dev/null 2>&1; then
    echo "✅ Backend is healthy"
else
    echo "⚠️  Backend health check failed, but continuing..."
fi

# Set up LXD container
echo "📦 Setting up LXD container..."
cd lxd
chmod +x setup-container.sh
./setup-container.sh

echo "🎉 Deployment complete!"
echo ""
echo "Your setup:"
echo "- Backend API: https://$DOMAIN/api/"
echo "- Frontend: Deploy to Vercel and set API URL to https://$DOMAIN/api"
echo "- SSL Certificate: Automatically managed by Let's Encrypt"
echo ""
echo "Next steps:"
echo "1. Deploy your frontend to Vercel"
echo "2. Update your frontend's API base URL to: https://$DOMAIN/api"
echo "3. Test the complete setup"
echo ""
echo "Useful commands:"
echo "- Check nginx logs: lxc exec nginx-proxy -- tail -f /var/log/nginx/access.log"
echo "- Check SSL certificate: lxc exec nginx-proxy -- certbot certificates"
echo "- Restart nginx: lxc exec nginx-proxy -- systemctl restart nginx"