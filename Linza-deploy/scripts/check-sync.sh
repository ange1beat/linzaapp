#!/usr/bin/env bash
# Check that Linza-start/ files are identical to their root counterparts.
# Exit code 0 = all in sync, 1 = drift detected.

set -euo pipefail

PAIRS=(
    "Dockerfile                    Linza-start/Dockerfile"
    "entrypoint.sh                 Linza-start/entrypoint.sh"
    "docker-compose.yml            Linza-start/docker-compose.yml"
    "nginx/nginx.conf              Linza-start/nginx/nginx.conf"
    "nginx/nginx-standalone.conf   Linza-start/nginx-standalone.conf"
    ".env.example                  Linza-start/.env.example"
)

errors=0

for pair in "${PAIRS[@]}"; do
    read -r src dst <<< "$pair"
    if [ ! -f "$src" ]; then
        echo "MISSING: $src"
        errors=$((errors + 1))
        continue
    fi
    if [ ! -f "$dst" ]; then
        echo "MISSING: $dst"
        errors=$((errors + 1))
        continue
    fi
    if ! diff -q "$src" "$dst" > /dev/null 2>&1; then
        echo "OUT OF SYNC: $src ↔ $dst"
        diff --unified=3 "$src" "$dst" || true
        echo ""
        errors=$((errors + 1))
    else
        echo "OK: $src ↔ $dst"
    fi
done

if [ "$errors" -gt 0 ]; then
    echo ""
    echo "ERROR: $errors file(s) out of sync. Run: cp <root-file> <Linza-start-file>"
    exit 1
else
    echo ""
    echo "All files in sync."
fi
