#!/bin/bash
# =============================================================================
#  Linza Detector — entrypoint для единого контейнера
#  Запускает 4 сервиса (uvicorn) + Nginx (API Gateway)
# =============================================================================
set -e

LOG_DIR="/var/log/linza"
mkdir -p "$LOG_DIR"

echo "============================================="
echo "  LINZA DETECTOR — запуск платформы"
echo "============================================="

# До любых uvicorn: чтобы board (и vpleer) видели URL в os.environ при импорте backend.main
export STORAGE_SERVICE_URL="${STORAGE_SERVICE_URL:-http://127.0.0.1:8001}"
export ANALYTICS_SERVICE_URL="${ANALYTICS_SERVICE_URL:-http://127.0.0.1:8002}"
export ERROR_TRACKER_URL="${ERROR_TRACKER_URL:-http://127.0.0.1:8004}"

# ── Функция запуска сервиса ──────────────────────────────────────────────────
start_service() {
    local name="$1"
    local dir="$2"
    local module="$3"
    local port="$4"

    echo "[linza] Запуск $name (порт $port)..."
    cd "/app/services/$dir"
    uvicorn "$module" \
        --host 127.0.0.1 \
        --port "$port" \
        --log-level info \
        --access-log \
        >> "$LOG_DIR/${name}.log" 2>&1 &
    echo "[linza] $name PID=$!"
}

# ── Запуск сервисов ──────────────────────────────────────────────────────────
start_service "board"     "board"     "backend.main:app" 8000
start_service "storage"   "storage"   "app.main:app"     8001
start_service "analytics" "analytics" "app.main:app"     8002
export TEMP_DIR="${TEMP_DIR:-/tmp/vpleer}"
mkdir -p "$TEMP_DIR"
start_service "vpleer"    "vpleer"    "app.main:app"     8003

# Error Tracker — сбор ошибок со всех сервисов
start_service "tracker"   "tracker"   "app.main:app"     8004

# ── Ожидание готовности сервисов ─────────────────────────────────────────────
echo "[linza] Ожидание готовности сервисов..."
wait_for_service() {
    local name="$1"
    local port="$2"
    local retries=30
    local i=0
    while [ $i -lt $retries ]; do
        if curl -sf "http://127.0.0.1:${port}/health" > /dev/null 2>&1; then
            echo "[linza] ✓ $name готов"
            return 0
        fi
        i=$((i + 1))
        sleep 1
    done
    echo "[linza] ✗ $name не ответил за ${retries}с"
    echo "[linza]   Последние строки лога:"
    tail -5 "$LOG_DIR/${name}.log" 2>/dev/null || true
    return 1
}

wait_for_service "board"     8000
wait_for_service "storage"   8001
wait_for_service "analytics" 8002
wait_for_service "vpleer"    8003
wait_for_service "tracker"   8004

# ── Запуск Nginx ─────────────────────────────────────────────────────────────
echo "[linza] Запуск Nginx (порт 80)..."
nginx -t 2>&1 && echo "[linza] ✓ Конфигурация Nginx валидна" || {
    echo "[linza] ✗ Ошибка конфигурации Nginx"
    exit 1
}

echo ""
echo "============================================="
echo "  Linza Detector запущен!"
echo "  Откройте http://localhost в браузере"
echo "============================================="
echo "  Сервисы:"
echo "    Board (UI + Auth)  → :8000"
echo "    Storage Service    → :8001"
echo "    Analytics Service  → :8002"
echo "    VPleer Service     → :8003"
echo "    Error Tracker      → :8004"
echo "    Nginx Gateway      → :80"
echo "============================================="
echo ""

# Nginx в foreground — держит контейнер живым
# При завершении nginx контейнер остановится
exec nginx -g 'daemon off;'
