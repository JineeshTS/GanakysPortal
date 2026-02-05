#!/bin/bash
# Deploy script for Ganakys Academy
set -e

ACADEMY_DIR="/var/academy"

echo "=== Ganakys Academy Deployment ==="

# Check secrets exist
echo "[1/5] Checking secrets..."
SECRETS_DIR="${ACADEMY_DIR}/secrets"
REQUIRED_SECRETS="db_password redis_password jwt_private_key jwt_public_key gemini_api_key encryption_key video_signing_secret"
for secret in $REQUIRED_SECRETS; do
    if [ ! -f "${SECRETS_DIR}/${secret}" ]; then
        echo "  ERROR: Missing secret: ${secret}"
        exit 1
    fi
done
echo "  All required secrets present."

# Check Flutter web build exists
echo "[2/5] Checking Flutter web build..."
if [ ! -f "${ACADEMY_DIR}/ganakys_flutter/build/web/index.html" ]; then
    echo "  ERROR: Flutter web build not found. Run scripts/build.sh first."
    exit 1
fi
echo "  Flutter web build found."

# Create required directories
echo "[3/5] Creating directories..."
mkdir -p "${ACADEMY_DIR}/storage/videos"
mkdir -p "${ACADEMY_DIR}/storage/thumbnails"
mkdir -p "${ACADEMY_DIR}/storage/audio"
mkdir -p "${ACADEMY_DIR}/storage/certificates"
mkdir -p "${ACADEMY_DIR}/storage/receipts"
mkdir -p "${ACADEMY_DIR}/storage/backups"
mkdir -p "${ACADEMY_DIR}/nginx/ssl"
echo "  Directories ready."

# Start/restart services
echo "[4/5] Starting services..."
cd "${ACADEMY_DIR}"
docker compose up -d --build
echo "  Services starting..."

# Wait for health checks
echo "[5/5] Waiting for services to be healthy..."
sleep 10
docker compose ps

echo ""
echo "=== Deployment Complete ==="
echo "Site: https://academy.ganakys.com"
echo ""
echo "Check logs: docker compose logs -f"
echo "Check health: curl -s http://localhost:8080/health"
