#!/bin/bash
# Build script for Ganakys Academy production deployment
set -e

ACADEMY_DIR="/var/academy"
FLUTTER_DIR="${ACADEMY_DIR}/ganakys_flutter"
SERVER_DIR="${ACADEMY_DIR}/ganakys_server"

echo "=== Ganakys Academy Production Build ==="
echo ""

# Step 1: Generate Serverpod client
echo "[1/4] Generating Serverpod client..."
cd "${SERVER_DIR}"
serverpod generate
echo "  Client generated successfully."

# Step 2: Analyze server code
echo "[2/4] Analyzing server code..."
dart analyze lib/src/endpoints/
echo "  Server analysis passed."

# Step 3: Build Flutter Web
echo "[3/4] Building Flutter web app..."
cd "${FLUTTER_DIR}"
flutter pub get
flutter build web \
  --release \
  --web-renderer html \
  --dart-define=SERVER_URL=https://academy.ganakys.com/api/ \
  --dart-define=FLUTTER_WEB_AUTO_DETECT=true
echo "  Flutter web build complete."

# Step 4: Build Docker containers
echo "[4/4] Building Docker containers..."
cd "${ACADEMY_DIR}"
docker compose build --no-cache
echo "  Docker build complete."

echo ""
echo "=== Build Complete ==="
echo "To deploy: docker compose up -d"
echo "To check: docker compose ps"
