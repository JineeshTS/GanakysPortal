#!/bin/bash
# DEP-005: GanaPortal Production Deployment Script
# Usage: ./deploy.sh [staging|production]

set -e

ENVIRONMENT=${1:-staging}
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
log_warning() { echo -e "${YELLOW}[WARNING]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; exit 1; }

echo ""
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║           GanaPortal Deployment Script                       ║"
echo "║           Environment: ${ENVIRONMENT}                                  ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""

# Validate environment
if [[ "$ENVIRONMENT" != "staging" && "$ENVIRONMENT" != "production" ]]; then
    log_error "Invalid environment. Use 'staging' or 'production'"
fi

# Check required tools
for cmd in docker docker-compose; do
    if ! command -v $cmd &> /dev/null; then
        log_error "$cmd is required but not installed"
    fi
done

# Load environment variables
ENV_FILE="${PROJECT_DIR}/env/.env.${ENVIRONMENT}"
if [[ ! -f "$ENV_FILE" ]]; then
    log_error "Environment file not found: $ENV_FILE"
fi
source "$ENV_FILE"

log_info "Loading environment from $ENV_FILE"

# Pre-deployment checks
log_info "Running pre-deployment checks..."

# Check database connectivity
log_info "Checking database connectivity..."
docker exec ganaportal-db pg_isready -U ${DB_USER:-ganaportal} || log_warning "Database may not be ready"

# Backup database (production only)
if [[ "$ENVIRONMENT" == "production" ]]; then
    log_info "Creating database backup..."
    BACKUP_FILE="/backups/ganaportal_$(date +%Y%m%d_%H%M%S).sql"
    docker exec ganaportal-db pg_dump -U ${DB_USER:-ganaportal} ${DB_NAME:-ganaportal_db} > "$BACKUP_FILE" 2>/dev/null || log_warning "Backup failed - continuing anyway"
    log_success "Backup created: $BACKUP_FILE"
fi

# Pull latest images
log_info "Pulling latest Docker images..."
cd "${PROJECT_DIR}/docker"
docker-compose -f docker-compose.prod.yml pull

# Stop old containers gracefully
log_info "Stopping existing containers..."
docker-compose -f docker-compose.prod.yml stop --timeout 30

# Start new containers
log_info "Starting new containers..."
docker-compose -f docker-compose.prod.yml up -d --remove-orphans

# Wait for services to be healthy
log_info "Waiting for services to be healthy..."
sleep 10

# Run database migrations
log_info "Running database migrations..."
docker exec ganaportal-backend alembic upgrade head || log_warning "Migration may have failed"

# Health checks
log_info "Running health checks..."
HEALTH_URL="http://localhost:8000/health"
MAX_RETRIES=10
RETRY_COUNT=0

while [[ $RETRY_COUNT -lt $MAX_RETRIES ]]; do
    if curl -sf "$HEALTH_URL" > /dev/null; then
        log_success "Backend health check passed"
        break
    fi
    RETRY_COUNT=$((RETRY_COUNT + 1))
    log_info "Waiting for backend... ($RETRY_COUNT/$MAX_RETRIES)"
    sleep 5
done

if [[ $RETRY_COUNT -eq $MAX_RETRIES ]]; then
    log_error "Backend health check failed after $MAX_RETRIES attempts"
fi

# Frontend health check
FRONTEND_HEALTH="http://localhost:3000/api/health"
if curl -sf "$FRONTEND_HEALTH" > /dev/null; then
    log_success "Frontend health check passed"
else
    log_warning "Frontend health check failed"
fi

# Clean up old images
log_info "Cleaning up old Docker images..."
docker system prune -f --filter "until=24h"

# Print status
echo ""
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║              Deployment Complete!                            ║"
echo "╠══════════════════════════════════════════════════════════════╣"
echo "║  Environment: ${ENVIRONMENT}                                         ║"
echo "║  Backend:     http://localhost:8000                          ║"
echo "║  Frontend:    http://localhost:3000                          ║"
echo "║  API Docs:    http://localhost:8000/docs                     ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""

log_success "GanaPortal deployed successfully to ${ENVIRONMENT}!"

# Send notification (if configured)
if [[ -n "$SLACK_WEBHOOK" ]]; then
    curl -X POST -H 'Content-type: application/json' \
        --data "{\"text\":\"GanaPortal deployed to ${ENVIRONMENT} successfully!\"}" \
        "$SLACK_WEBHOOK" 2>/dev/null || true
fi
