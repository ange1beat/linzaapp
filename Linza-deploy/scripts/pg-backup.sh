#!/usr/bin/env bash
# ------------------------------------------------------------------
# pg-backup.sh — Dump internal PostgreSQL → restore to cloud PostgreSQL
#
# Usage:
#   ./scripts/pg-backup.sh                    # one-shot backup
#   ./scripts/pg-backup.sh --schedule 6h      # run every 6 hours (foreground)
#
# Environment variables (required):
#   POSTGRES_USER, POSTGRES_PASSWORD, POSTGRES_DB  — internal PostgreSQL
#   POSTGRES_HOST                                   — internal host (default: postgres)
#   CLOUD_DATABASE_URL                              — cloud PostgreSQL connection string
#                                                     e.g. postgresql://user:pass@cloud-host:5432/linza
#
# How it works:
#   1. pg_dump (internal) → compressed SQL file in /tmp
#   2. psql (cloud) ← restore from dump
#   3. Cleanup temp file
#
# Requirements:
#   - pg_dump and psql available (postgres:16-alpine image has them)
#   - Network access from this container to cloud PostgreSQL
# ------------------------------------------------------------------
set -euo pipefail

POSTGRES_HOST="${POSTGRES_HOST:-postgres}"
POSTGRES_PORT="${POSTGRES_PORT:-5432}"
BACKUP_DIR="${BACKUP_DIR:-/tmp/pg-backups}"

log() { echo "[$(date -u +%Y-%m-%dT%H:%M:%SZ)] $*"; }

do_backup() {
    log "Starting backup: ${POSTGRES_HOST}:${POSTGRES_PORT}/${POSTGRES_DB} → cloud"

    # Validate env
    if [ -z "${CLOUD_DATABASE_URL:-}" ]; then
        log "ERROR: CLOUD_DATABASE_URL is not set. Skipping."
        return 1
    fi
    if [ -z "${POSTGRES_USER:-}" ] || [ -z "${POSTGRES_DB:-}" ]; then
        log "ERROR: POSTGRES_USER or POSTGRES_DB is not set."
        return 1
    fi

    mkdir -p "$BACKUP_DIR"
    local dump_file="${BACKUP_DIR}/linza_$(date -u +%Y%m%d_%H%M%S).sql.gz"

    # Step 1: Dump internal PostgreSQL
    log "pg_dump → ${dump_file}"
    PGPASSWORD="${POSTGRES_PASSWORD}" pg_dump \
        -h "$POSTGRES_HOST" \
        -p "$POSTGRES_PORT" \
        -U "$POSTGRES_USER" \
        -d "$POSTGRES_DB" \
        --no-owner \
        --no-privileges \
        --clean \
        --if-exists \
        | gzip > "$dump_file"

    local dump_size
    dump_size=$(du -sh "$dump_file" | cut -f1)
    log "Dump complete: ${dump_size}"

    # Step 2: Restore to cloud PostgreSQL
    log "Restoring to cloud..."
    gunzip -c "$dump_file" | psql "$CLOUD_DATABASE_URL" --quiet --no-psqlrc 2>&1 | \
        grep -v "^NOTICE:" || true

    log "Restore complete"

    # Step 3: Cleanup (keep last 3 dumps)
    local count
    count=$(find "$BACKUP_DIR" -name "linza_*.sql.gz" | wc -l)
    if [ "$count" -gt 3 ]; then
        find "$BACKUP_DIR" -name "linza_*.sql.gz" -printf '%T+ %p\n' | \
            sort | head -n -3 | awk '{print $2}' | xargs rm -f
        log "Cleaned old dumps, kept last 3"
    fi

    log "Backup finished successfully"
}

# --- Main ---
if [ "${1:-}" = "--schedule" ]; then
    interval="${2:-6h}"
    # Convert to seconds
    case "$interval" in
        *h) seconds=$(( ${interval%h} * 3600 )) ;;
        *m) seconds=$(( ${interval%m} * 60 )) ;;
        *s) seconds="${interval%s}" ;;
        *)  seconds="$interval" ;;
    esac
    log "Scheduled mode: backup every ${interval} (${seconds}s)"
    while true; do
        do_backup || log "Backup failed, will retry next cycle"
        sleep "$seconds"
    done
else
    do_backup
fi
