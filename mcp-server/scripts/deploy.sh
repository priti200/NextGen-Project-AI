#!/bin/bash

# Deployment script for MCP Server
# Usage: ./deploy.sh [environment]

set -e

ENVIRONMENT=${1:-production}
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

echo "================================================"
echo "Deploying MCP Server to $ENVIRONMENT"
echo "================================================"

cd "$PROJECT_ROOT"

# Load environment variables
if [ -f ".env.$ENVIRONMENT" ]; then
    echo "Loading environment from .env.$ENVIRONMENT"
    export $(cat ".env.$ENVIRONMENT" | xargs)
else
    echo "Warning: .env.$ENVIRONMENT not found, using .env"
    if [ -f ".env" ]; then
        export $(cat ".env" | xargs)
    fi
fi

# Pull latest changes (if applicable)
if [ "$ENVIRONMENT" = "production" ]; then
    echo "Pulling latest code..."
    git pull origin main
fi

# Build Docker image
echo "Building Docker image..."
docker-compose build mcp-server

# Stop existing containers
echo "Stopping existing containers..."
docker-compose down

# Start new containers
echo "Starting new containers..."
docker-compose up -d

# Wait for health check
echo "Waiting for service to be healthy..."
sleep 10

MAX_RETRIES=30
RETRY_COUNT=0

while [ $RETRY_COUNT -lt $MAX_RETRIES ]; do
    if curl -f http://localhost:8080/health > /dev/null 2>&1; then
        echo "✓ Service is healthy!"
        break
    fi
    
    echo "Waiting for service... ($RETRY_COUNT/$MAX_RETRIES)"
    sleep 2
    RETRY_COUNT=$((RETRY_COUNT + 1))
done

if [ $RETRY_COUNT -eq $MAX_RETRIES ]; then
    echo "✗ Service failed to become healthy"
    docker-compose logs mcp-server
    exit 1
fi

# Show status
echo ""
echo "================================================"
echo "Deployment completed successfully!"
echo "================================================"
echo ""
echo "Service status:"
docker-compose ps

echo ""
echo "Recent logs:"
docker-compose logs --tail=20 mcp-server

echo ""
echo "Endpoints:"
echo "  - Health: http://localhost:8080/health"
echo "  - Ready: http://localhost:8080/ready"
echo "  - Metrics: http://localhost:8080/metrics"
echo "  - Docs: http://localhost:8080/docs"
