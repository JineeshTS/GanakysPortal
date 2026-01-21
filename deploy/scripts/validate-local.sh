#!/bin/bash
# GanaPortal Local Deployment Validation
# Validates all deployment configurations without running containers

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DEPLOY_DIR="$(dirname "$SCRIPT_DIR")"
PROJECT_DIR="$(dirname "$DEPLOY_DIR")"

log_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[PASS]${NC} $1"; }
log_warning() { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error() { echo -e "${RED}[FAIL]${NC} $1"; }

PASSED=0
FAILED=0

check() {
    local name=$1
    local result=$2
    if [[ $result -eq 0 ]]; then
        log_success "$name"
        ((PASSED++))
    else
        log_error "$name"
        ((FAILED++))
    fi
}

echo ""
echo "╔══════════════════════════════════════════════════════════════════════════════╗"
echo "║                                                                              ║"
echo "║     ██████╗  █████╗ ███╗   ██╗ █████╗ ██████╗  ██████╗ ██████╗ ████████╗    ║"
echo "║    ██╔════╝ ██╔══██╗████╗  ██║██╔══██╗██╔══██╗██╔═══██╗██╔══██╗╚══██╔══╝    ║"
echo "║    ██║  ███╗███████║██╔██╗ ██║███████║██████╔╝██║   ██║██████╔╝   ██║       ║"
echo "║    ██║   ██║██╔══██║██║╚██╗██║██╔══██║██╔═══╝ ██║   ██║██╔══██╗   ██║       ║"
echo "║    ╚██████╔╝██║  ██║██║ ╚████║██║  ██║██║     ╚██████╔╝██║  ██║   ██║       ║"
echo "║     ╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═══╝╚═╝  ╚═╝╚═╝      ╚═════╝ ╚═╝  ╚═╝   ╚═╝       ║"
echo "║                                                                              ║"
echo "║              LOCAL DEPLOYMENT VALIDATION                                     ║"
echo "║                                                                              ║"
echo "╚══════════════════════════════════════════════════════════════════════════════╝"
echo ""

# =============================================================================
# Check Prerequisites
# =============================================================================
echo -e "${CYAN}═══ Checking Prerequisites ═══${NC}"
echo ""

# Docker
docker --version > /dev/null 2>&1
check "Docker installed" $?

# Docker Compose
docker-compose --version > /dev/null 2>&1 || docker compose version > /dev/null 2>&1
check "Docker Compose installed" $?

echo ""

# =============================================================================
# Check Docker Files
# =============================================================================
echo -e "${CYAN}═══ Validating Docker Configuration (DEP-001) ═══${NC}"
echo ""

[[ -f "$DEPLOY_DIR/docker/Dockerfile.backend" ]]
check "Dockerfile.backend exists" $?

[[ -f "$DEPLOY_DIR/docker/Dockerfile.frontend" ]]
check "Dockerfile.frontend exists" $?

[[ -f "$DEPLOY_DIR/docker/docker-compose.prod.yml" ]]
check "docker-compose.prod.yml exists" $?

# Validate docker-compose syntax
cd "$DEPLOY_DIR/docker"
docker-compose -f docker-compose.prod.yml config > /dev/null 2>&1
check "docker-compose.prod.yml syntax valid" $?

echo ""

# =============================================================================
# Check CI/CD Pipelines
# =============================================================================
echo -e "${CYAN}═══ Validating CI/CD Pipelines (DEP-002) ═══${NC}"
echo ""

[[ -f "$DEPLOY_DIR/ci-cd/.github/workflows/ci.yml" ]]
check "CI pipeline (ci.yml) exists" $?

[[ -f "$DEPLOY_DIR/ci-cd/.github/workflows/cd.yml" ]]
check "CD pipeline (cd.yml) exists" $?

# Validate YAML syntax
python3 -c "import yaml; yaml.safe_load(open('$DEPLOY_DIR/ci-cd/.github/workflows/ci.yml'))" 2>/dev/null
check "CI pipeline YAML valid" $?

python3 -c "import yaml; yaml.safe_load(open('$DEPLOY_DIR/ci-cd/.github/workflows/cd.yml'))" 2>/dev/null
check "CD pipeline YAML valid" $?

echo ""

# =============================================================================
# Check Environment Configuration
# =============================================================================
echo -e "${CYAN}═══ Validating Environment Configuration (DEP-003) ═══${NC}"
echo ""

[[ -f "$DEPLOY_DIR/env/.env.production" ]]
check "Production env file exists" $?

[[ -f "$DEPLOY_DIR/env/.env.staging" ]]
check "Staging env file exists" $?

[[ -f "$DEPLOY_DIR/env/.env.example" ]]
check "Example env file exists" $?

# Check required variables in production env
grep -q "DATABASE_URL" "$DEPLOY_DIR/env/.env.production" 2>/dev/null
check "DATABASE_URL configured" $?

grep -q "REDIS_URL" "$DEPLOY_DIR/env/.env.production" 2>/dev/null
check "REDIS_URL configured" $?

grep -q "JWT_SECRET_KEY" "$DEPLOY_DIR/env/.env.production" 2>/dev/null
check "JWT_SECRET_KEY configured" $?

echo ""

# =============================================================================
# Check Database Migrations
# =============================================================================
echo -e "${CYAN}═══ Validating Database Migrations (DEP-004) ═══${NC}"
echo ""

[[ -f "$DEPLOY_DIR/migrations/alembic.ini" ]]
check "alembic.ini exists" $?

[[ -f "$DEPLOY_DIR/migrations/env.py" ]]
check "Alembic env.py exists" $?

[[ -f "$DEPLOY_DIR/migrations/versions/001_initial_schema.py" ]]
check "Initial migration exists" $?

# Validate Python syntax
python3 -m py_compile "$DEPLOY_DIR/migrations/env.py" 2>/dev/null
check "Alembic env.py syntax valid" $?

python3 -m py_compile "$DEPLOY_DIR/migrations/versions/001_initial_schema.py" 2>/dev/null
check "Initial migration syntax valid" $?

echo ""

# =============================================================================
# Check Kubernetes Configuration
# =============================================================================
echo -e "${CYAN}═══ Validating Kubernetes Configuration (DEP-005) ═══${NC}"
echo ""

[[ -f "$DEPLOY_DIR/k8s/namespace.yaml" ]]
check "K8s namespace.yaml exists" $?

[[ -f "$DEPLOY_DIR/k8s/backend-deployment.yaml" ]]
check "K8s backend-deployment.yaml exists" $?

[[ -f "$DEPLOY_DIR/k8s/frontend-deployment.yaml" ]]
check "K8s frontend-deployment.yaml exists" $?

[[ -f "$DEPLOY_DIR/k8s/ingress.yaml" ]]
check "K8s ingress.yaml exists" $?

[[ -f "$DEPLOY_DIR/k8s/configmap.yaml" ]]
check "K8s configmap.yaml exists" $?

# Validate YAML syntax
for f in "$DEPLOY_DIR/k8s/"*.yaml; do
    python3 -c "import yaml; yaml.safe_load(open('$f'))" 2>/dev/null
    check "$(basename $f) YAML valid" $?
done

echo ""

# =============================================================================
# Check Nginx Configuration
# =============================================================================
echo -e "${CYAN}═══ Validating Nginx Configuration (DEP-005) ═══${NC}"
echo ""

[[ -f "$DEPLOY_DIR/nginx/nginx.prod.conf" ]]
check "Nginx production config exists" $?

# Check nginx config syntax (if nginx installed)
if command -v nginx &> /dev/null; then
    nginx -t -c "$DEPLOY_DIR/nginx/nginx.prod.conf" 2>/dev/null
    check "Nginx config syntax valid" $?
else
    log_warning "Nginx not installed - skipping syntax check"
fi

echo ""

# =============================================================================
# Check Deployment Scripts
# =============================================================================
echo -e "${CYAN}═══ Validating Deployment Scripts (DEP-005) ═══${NC}"
echo ""

[[ -f "$DEPLOY_DIR/scripts/deploy.sh" ]]
check "deploy.sh exists" $?

[[ -f "$DEPLOY_DIR/scripts/healthcheck.sh" ]]
check "healthcheck.sh exists" $?

[[ -f "$DEPLOY_DIR/scripts/init-db.sql" ]]
check "init-db.sql exists" $?

[[ -x "$DEPLOY_DIR/scripts/deploy.sh" ]]
check "deploy.sh is executable" $?

[[ -x "$DEPLOY_DIR/scripts/healthcheck.sh" ]]
check "healthcheck.sh is executable" $?

# Validate bash syntax
bash -n "$DEPLOY_DIR/scripts/deploy.sh" 2>/dev/null
check "deploy.sh syntax valid" $?

bash -n "$DEPLOY_DIR/scripts/healthcheck.sh" 2>/dev/null
check "healthcheck.sh syntax valid" $?

echo ""

# =============================================================================
# Check Source Code
# =============================================================================
echo -e "${CYAN}═══ Validating Source Code ═══${NC}"
echo ""

[[ -d "$PROJECT_DIR/src/backend" ]]
check "Backend source directory exists" $?

[[ -d "$PROJECT_DIR/src/frontend" ]]
check "Frontend source directory exists" $?

# Count backend files
BACKEND_FILES=$(find "$PROJECT_DIR/src/backend" -name "*.py" 2>/dev/null | wc -l)
[[ $BACKEND_FILES -gt 50 ]]
check "Backend has $BACKEND_FILES Python files" $?

# Count frontend files
FRONTEND_FILES=$(find "$PROJECT_DIR/src/frontend" -name "*.tsx" -o -name "*.ts" 2>/dev/null | wc -l)
[[ $FRONTEND_FILES -gt 30 ]]
check "Frontend has $FRONTEND_FILES TypeScript files" $?

echo ""

# =============================================================================
# Check Global State
# =============================================================================
echo -e "${CYAN}═══ Validating Project State ═══${NC}"
echo ""

[[ -f "$PROJECT_DIR/state/global_state.json" ]]
check "global_state.json exists" $?

# Check completion status
PROGRESS=$(python3 -c "import json; print(json.load(open('$PROJECT_DIR/state/global_state.json'))['progress']['percentage'])" 2>/dev/null)
[[ "$PROGRESS" == "100" ]]
check "Project completion: ${PROGRESS}%" $?

# Check all gates passed
GATES=$(python3 -c "import json; print(len(json.load(open('$PROJECT_DIR/state/global_state.json'))['gates_passed']))" 2>/dev/null)
[[ "$GATES" == "10" ]]
check "Gates passed: ${GATES}/10" $?

echo ""

# =============================================================================
# Summary
# =============================================================================
TOTAL=$((PASSED + FAILED))

echo "╔══════════════════════════════════════════════════════════════════════════════╗"
echo "║                         VALIDATION SUMMARY                                   ║"
echo "╠══════════════════════════════════════════════════════════════════════════════╣"
printf "║   Total Checks: %-60s ║\n" "$TOTAL"
printf "║   ${GREEN}Passed:${NC} %-63s ║\n" "$PASSED"
if [[ $FAILED -gt 0 ]]; then
    printf "║   ${RED}Failed:${NC} %-63s ║\n" "$FAILED"
else
    printf "║   ${GREEN}Failed:${NC} %-63s ║\n" "0"
fi
echo "╠══════════════════════════════════════════════════════════════════════════════╣"

if [[ $FAILED -eq 0 ]]; then
    echo "║                                                                              ║"
    echo "║   ${GREEN}ALL VALIDATIONS PASSED - READY FOR DEPLOYMENT${NC}                            ║"
    echo "║                                                                              ║"
    echo "║   Next Steps:                                                                ║"
    echo "║   1. Configure secrets in production environment                             ║"
    echo "║   2. Set up SSL certificates for portal.ganakys.com                          ║"
    echo "║   3. Run: ./deploy.sh production                                             ║"
    echo "║                                                                              ║"
else
    echo "║                                                                              ║"
    echo "║   ${RED}SOME VALIDATIONS FAILED - FIX BEFORE DEPLOYMENT${NC}                           ║"
    echo "║                                                                              ║"
fi
echo "╚══════════════════════════════════════════════════════════════════════════════╝"
echo ""

exit $FAILED
