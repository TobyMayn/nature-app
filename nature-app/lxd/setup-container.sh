#!/bin/bash

# LXD Container Setup Script for Nginx Reverse Proxy with Let's Encrypt
# Run this script on your server to create and configure the LXD container

set -e

CONTAINER_NAME="nginx-proxy"
DOMAIN="natureapp.duckdns.org"
EMAIL="tobiasmayn@gmail.com"  # Replace with your email for Let's Encrypt

echo "Setting up LXD container for nginx reverse proxy..."

# Create LXD container
echo "Creating LXD container..."
lxc launch ubuntu:22.04 $CONTAINER_NAME

# Wait for container to start
echo "Waiting for container to start..."
sleep 10

# Update container
echo "Updating container packages..."
lxc exec $CONTAINER_NAME -- apt update
lxc exec $CONTAINER_NAME -- apt upgrade -y

# Install nginx and certbot
echo "Installing nginx and certbot..."
lxc exec $CONTAINER_NAME -- apt install -y nginx certbot python3-certbot-nginx

# Create certbot directory
lxc exec $CONTAINER_NAME -- mkdir -p /var/www/certbot

# Copy nginx configuration
echo "Copying nginx configuration..."
lxc file push ./nginx/nginx.conf $CONTAINER_NAME/etc/nginx/nginx.conf

# Create temporary nginx config for initial certificate request
echo "Creating temporary nginx config for Let's Encrypt..."
lxc exec $CONTAINER_NAME -- tee /etc/nginx/sites-available/temp > /dev/null <<EOF
server {
    listen 80;
    server_name $DOMAIN;
    
    location /.well-known/acme-challenge/ {
        root /var/www/certbot;
    }
    
    location / {
        return 200 'OK';
        add_header Content-Type text/plain;
    }
}
EOF

# Enable temporary config
lxc exec $CONTAINER_NAME -- ln -sf /etc/nginx/sites-available/temp /etc/nginx/sites-enabled/default
lxc exec $CONTAINER_NAME -- nginx -t
lxc exec $CONTAINER_NAME -- systemctl restart nginx

# Configure port forwarding for HTTP (port 80)
echo "Configuring port forwarding..."
lxc config device add $CONTAINER_NAME http proxy listen=tcp:0.0.0.0:80 connect=tcp:127.0.0.1:80

# Configure port forwarding for HTTPS (port 443)
lxc config device add $CONTAINER_NAME https proxy listen=tcp:0.0.0.0:443 connect=tcp:127.0.0.1:443

# Wait a moment for nginx to be ready
sleep 5

# Request SSL certificate
echo "Requesting SSL certificate from Let's Encrypt..."
lxc exec $CONTAINER_NAME -- certbot certonly --webroot -w /var/www/certbot -d $DOMAIN --email $EMAIL --agree-tos --non-interactive

# Copy the final nginx configuration
echo "Installing final nginx configuration..."
lxc file push ./nginx/nginx.conf $CONTAINER_NAME/etc/nginx/nginx.conf

# Test nginx configuration
lxc exec $CONTAINER_NAME -- nginx -t

# Restart nginx with SSL configuration
lxc exec $CONTAINER_NAME -- systemctl restart nginx

# Enable nginx to start on boot
lxc exec $CONTAINER_NAME -- systemctl enable nginx

# Set up automatic certificate renewal
echo "Setting up automatic certificate renewal..."
lxc exec $CONTAINER_NAME -- tee /etc/cron.d/certbot > /dev/null <<EOF
0 12 * * * root test -x /usr/bin/certbot -a \! -d /run/systemd/system && perl -e 'sleep int(rand(43200))' && certbot renew --quiet --post-hook "systemctl reload nginx"
EOF

# Make container start on boot
lxc config set $CONTAINER_NAME boot.autostart true

echo "LXD container setup complete!"
echo "Your nginx reverse proxy is now running with SSL on https://$DOMAIN"
echo ""
echo "Next steps:"
echo "1. Update your backend docker-compose.yml to expose on port 8080"
echo "2. Update the CORS origin in nginx.conf with your Vercel app URL"
echo "3. Test the setup"

# Show container status
lxc list $CONTAINER_NAME