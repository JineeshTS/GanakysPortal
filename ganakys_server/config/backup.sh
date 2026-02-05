#!/bin/sh
# Daily PostgreSQL backup script with GPG encryption
# Runs via cron at 3 AM UTC

set -e

BACKUP_DIR="/backups"
DATE=$(date +%Y%m%d_%H%M%S)
FILENAME="ganakys_${DATE}.sql.gz.gpg"
RETENTION_DAYS=30

# Read DB password from Docker secret
export PGPASSWORD=$(cat /run/secrets/db_password)

echo "[$(date)] Starting backup..."

# Dump, compress, and encrypt in one pipeline
pg_dump -h "$PGHOST" -p "$PGPORT" -U "$PGUSER" -d "$PGDATABASE" \
    --format=custom --compress=9 \
    | gpg --batch --yes --symmetric --cipher-algo AES256 \
           --passphrase-file /run/secrets/encryption_key \
           --output "${BACKUP_DIR}/${FILENAME}"

# Generate checksum
sha256sum "${BACKUP_DIR}/${FILENAME}" > "${BACKUP_DIR}/${FILENAME}.sha256"

echo "[$(date)] Backup created: ${FILENAME}"
echo "[$(date)] Size: $(du -h "${BACKUP_DIR}/${FILENAME}" | cut -f1)"

# Clean up old backups (keep last N days)
find "$BACKUP_DIR" -name "ganakys_*.sql.gz.gpg" -mtime +$RETENTION_DAYS -delete 2>/dev/null || true
find "$BACKUP_DIR" -name "ganakys_*.sha256" -mtime +$RETENTION_DAYS -delete 2>/dev/null || true

echo "[$(date)] Cleanup complete. Backups retained: $(ls -1 ${BACKUP_DIR}/ganakys_*.sql.gz.gpg 2>/dev/null | wc -l)"
echo "[$(date)] Backup finished successfully."
