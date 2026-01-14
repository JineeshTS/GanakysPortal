#!/bin/bash
# DEP-005: GanaPortal Health Check Script
# Comprehensive health check for all services

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

BACKEND_URL=${BACKEND_URL:-"http://localhost:8000"}
FRONTEND_URL=${FRONTEND_URL:-"http://localhost:3000"}
DB_HOST=${DB_HOST:-"localhost"}
REDIS_HOST=${REDIS_HOST:-"localhost"}

echo ""
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║           GanaPortal Health Check                            ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""

check_status() {
    local name=$1
    local status=$2
    if [[ $status -eq 0 ]]; then
        echo -e "${GREEN}[PASS]${NC} $name"
        return 0
    else
        echo -e "${RED}[FAIL]${NC} $name"
        return 1
    fi
}

FAILED=0

# Backend API
echo "Checking Backend API..."
curl -sf "${BACKEND_URL}/health" > /dev/null 2>&1
check_status "Backend API (${BACKEND_URL}/health)" $? || FAILED=1

# Backend Docs
curl -sf "${BACKEND_URL}/docs" > /dev/null 2>&1
check_status "API Documentation (${BACKEND_URL}/docs)" $? || FAILED=1

# Frontend
echo ""
echo "Checking Frontend..."
curl -sf "${FRONTEND_URL}" > /dev/null 2>&1
check_status "Frontend (${FRONTEND_URL})" $? || FAILED=1

# Database
echo ""
echo "Checking Database..."
docker exec ganaportal-db pg_isready -U ganaportal > /dev/null 2>&1
check_status "PostgreSQL Database" $? || FAILED=1

# Redis
echo ""
echo "Checking Redis..."
docker exec ganaportal-redis redis-cli ping > /dev/null 2>&1
check_status "Redis Cache" $? || FAILED=1

# Docker Containers
echo ""
echo "Checking Docker Containers..."
for container in ganaportal-backend ganaportal-frontend ganaportal-db ganaportal-redis ganaportal-nginx; do
    docker ps --format '{{.Names}}' | grep -q "^${container}$"
    check_status "Container: ${container}" $? || FAILED=1
done

# Disk Space
echo ""
echo "Checking Disk Space..."
DISK_USAGE=$(df / | tail -1 | awk '{print $5}' | sed 's/%//')
if [[ $DISK_USAGE -lt 90 ]]; then
    echo -e "${GREEN}[PASS]${NC} Disk usage: ${DISK_USAGE}%"
else
    echo -e "${YELLOW}[WARN]${NC} Disk usage high: ${DISK_USAGE}%"
fi

# Memory
echo ""
echo "Checking Memory..."
FREE_MEM=$(free -m | awk '/^Mem:/{printf "%.0f", $7/$2*100}')
if [[ $FREE_MEM -gt 10 ]]; then
    echo -e "${GREEN}[PASS]${NC} Free memory: ${FREE_MEM}%"
else
    echo -e "${YELLOW}[WARN]${NC} Low memory: ${FREE_MEM}% free"
fi

# Summary
echo ""
echo "════════════════════════════════════════════════════════════════"
if [[ $FAILED -eq 0 ]]; then
    echo -e "${GREEN}All health checks passed!${NC}"
    exit 0
else
    echo -e "${RED}Some health checks failed!${NC}"
    exit 1
fi
