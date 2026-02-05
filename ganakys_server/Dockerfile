# Build stage
FROM dart:3.7 AS build
WORKDIR /app

# Copy dependency files first for caching
COPY ganakys_server/pubspec.* ./ganakys_server/
COPY ganakys_client/pubspec.* ./ganakys_client/

# Copy full source
COPY ganakys_server/ ./ganakys_server/
COPY ganakys_client/ ./ganakys_client/

WORKDIR /app/ganakys_server

# Install dependencies and compile
RUN dart pub get
RUN dart compile exe bin/main.dart -o bin/server

# Final stage - use Debian slim (dart compile exe needs glibc)
FROM debian:bookworm-slim

# Install minimal runtime deps (curl for healthcheck)
RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN groupadd -r academy && useradd -r -g academy academy

# Environment variables
ENV runmode=production
ENV serverid=default
ENV logging=normal
ENV role=monolith

# Copy compiled server executable
COPY --from=build /app/ganakys_server/bin/server /app/server

# Copy configuration files and resources
COPY --from=build /app/ganakys_server/config/ /app/config/
COPY --from=build /app/ganakys_server/web/ /app/web/
COPY --from=build /app/ganakys_server/migrations/ /app/migrations/

# Protocol file for Insights
COPY --from=build /app/ganakys_server/lib/src/generated/protocol.yaml /app/lib/src/generated/protocol.yaml

# Create storage directories
RUN mkdir -p /app/storage/videos /app/storage/thumbnails /app/storage/audio \
    /app/storage/certificates /app/storage/receipts /app/storage/backups \
    && chown -R academy:academy /app

WORKDIR /app

# Switch to non-root user
USER academy

# Expose ports
EXPOSE 8080
EXPOSE 8081
EXPOSE 8082

# Health check
HEALTHCHECK --interval=30s --timeout=10s --retries=3 --start-period=60s \
    CMD curl -f http://localhost:8080/ || exit 1

# Run migrations on startup, then start server
ENTRYPOINT ["sh", "-c", "./server --apply-migrations --mode=$runmode --server-id=$serverid --logging=$logging --role=$role"]
