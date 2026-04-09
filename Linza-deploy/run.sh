#!/bin/bash
# =============================================================================
#  Linza Detector — запуск Docker-контейнера
#
#  Использование:
#    ./run.sh                         # запуск с настройками по умолчанию
#    ./run.sh --port 8080             # запуск на порту 8080
#    ./run.sh --env-file .env         # запуск с файлом переменных
#    ./run.sh --detach                # запуск в фоне
#    ./run.sh --stop                  # остановка контейнера
#    ./run.sh --logs                  # просмотр логов
#    ./run.sh --status                # статус контейнера и сервисов
# =============================================================================
set -e

# ── Настройки ────────────────────────────────────────────────────────────────
IMAGE_NAME="linza-detector"
IMAGE_TAG="latest"
CONTAINER_NAME="linza"
HOST_PORT=80
ENV_FILE=""
DETACH=false
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

# ── Цвета ────────────────────────────────────────────────────────────────────
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

info()  { echo -e "${BLUE}[linza]${NC} $1"; }
ok()    { echo -e "${GREEN}[linza] ✓${NC} $1"; }
warn()  { echo -e "${YELLOW}[linza] !${NC} $1"; }
fail()  { echo -e "${RED}[linza] ✗${NC} $1"; exit 1; }

# ── Разбор аргументов ────────────────────────────────────────────────────────
ACTION="run"

while [[ $# -gt 0 ]]; do
    case $1 in
        --port)
            HOST_PORT="$2"
            shift 2
            ;;
        --env-file)
            ENV_FILE="$2"
            shift 2
            ;;
        --detach|-d)
            DETACH=true
            shift
            ;;
        --stop)
            ACTION="stop"
            shift
            ;;
        --logs)
            ACTION="logs"
            shift
            ;;
        --status)
            ACTION="status"
            shift
            ;;
        --tag)
            IMAGE_TAG="$2"
            shift 2
            ;;
        --help|-h)
            echo "Linza Detector — запуск Docker-контейнера"
            echo ""
            echo "Использование: ./run.sh [опции]"
            echo ""
            echo "Опции:"
            echo "  --port <port>        Порт на хост-машине (по умолчанию: 80)"
            echo "  --env-file <path>    Файл с переменными окружения"
            echo "  --detach, -d         Запуск в фоновом режиме"
            echo "  --tag <tag>          Тег образа (по умолчанию: latest)"
            echo "  --stop               Остановить контейнер"
            echo "  --logs               Показать логи"
            echo "  --status             Статус контейнера и сервисов"
            echo "  --help, -h           Показать эту справку"
            exit 0
            ;;
        *)
            echo "Неизвестная опция: $1 (используйте --help)"
            exit 1
            ;;
    esac
done

# ── Команда: остановка ───────────────────────────────────────────────────────
if [ "$ACTION" = "stop" ]; then
    if docker ps -q -f name="$CONTAINER_NAME" | grep -q .; then
        info "Остановка контейнера $CONTAINER_NAME..."
        docker stop "$CONTAINER_NAME"
        docker rm "$CONTAINER_NAME"
        ok "Контейнер остановлен"
    else
        warn "Контейнер $CONTAINER_NAME не запущен"
    fi
    exit 0
fi

# ── Команда: логи ────────────────────────────────────────────────────────────
if [ "$ACTION" = "logs" ]; then
    if docker ps -q -f name="$CONTAINER_NAME" | grep -q .; then
        docker logs -f "$CONTAINER_NAME"
    else
        fail "Контейнер $CONTAINER_NAME не запущен"
    fi
    exit 0
fi

# ── Команда: статус ──────────────────────────────────────────────────────────
if [ "$ACTION" = "status" ]; then
    echo ""
    echo "============================================="
    echo "  Linza Detector — статус"
    echo "============================================="

    if ! docker ps -q -f name="$CONTAINER_NAME" | grep -q .; then
        warn "Контейнер $CONTAINER_NAME не запущен"
        exit 0
    fi

    CONTAINER_PORT=$(docker port "$CONTAINER_NAME" 80 2>/dev/null | head -1 | cut -d: -f2)
    BASE_URL="http://localhost:${CONTAINER_PORT:-80}"

    ok "Контейнер запущен (порт: ${CONTAINER_PORT:-?})"
    echo ""

    check_service() {
        local name="$1"
        local url="$2"
        if curl -sf "$url" > /dev/null 2>&1; then
            echo -e "  ${GREEN}✓${NC} $name"
        else
            echo -e "  ${RED}✗${NC} $name"
        fi
    }

    check_service "Nginx Gateway      ($BASE_URL)"           "$BASE_URL/"
    check_service "Board (Auth + UI)  ($BASE_URL/health)" "$BASE_URL/health"
    check_service "Storage Service    ($BASE_URL/api/files)"  "$BASE_URL/api/files"
    check_service "Analytics Service  ($BASE_URL/api/classifier)" "$BASE_URL/api/classifier"
    check_service "VPleer Service     ($BASE_URL/api/vpleer)" "$BASE_URL/api/vpleer/files"

    echo ""
    echo "  Логи: ./run.sh --logs"
    echo "  Стоп: ./run.sh --stop"
    echo "============================================="
    exit 0
fi

# ── Команда: запуск ──────────────────────────────────────────────────────────

# Проверка образа
if ! docker image inspect "${IMAGE_NAME}:${IMAGE_TAG}" > /dev/null 2>&1; then
    fail "Образ ${IMAGE_NAME}:${IMAGE_TAG} не найден. Сначала выполните ./build.sh"
fi

# Остановка предыдущего контейнера
if docker ps -aq -f name="$CONTAINER_NAME" | grep -q .; then
    warn "Контейнер $CONTAINER_NAME уже существует, удаляем..."
    docker rm -f "$CONTAINER_NAME" > /dev/null 2>&1
fi

# Формирование команды запуска
DOCKER_ARGS=(
    run
    --name "$CONTAINER_NAME"
    -p "${HOST_PORT}:80"
    -v "linza-analytics-data:/app/data"
)

if [ "$DETACH" = true ]; then
    DOCKER_ARGS+=(-d)
fi

# Env-файл
if [ -n "$ENV_FILE" ]; then
    if [ ! -f "$ENV_FILE" ]; then
        fail "Файл $ENV_FILE не найден"
    fi
    DOCKER_ARGS+=(--env-file "$ENV_FILE")
elif [ -f "$SCRIPT_DIR/.env" ]; then
    DOCKER_ARGS+=(--env-file "$SCRIPT_DIR/.env")
    info "Используется файл .env"
fi

DOCKER_ARGS+=("${IMAGE_NAME}:${IMAGE_TAG}")

echo ""
echo "============================================="
echo "  Linza Detector — запуск"
echo "============================================="
echo "  Образ:     ${IMAGE_NAME}:${IMAGE_TAG}"
echo "  Контейнер: ${CONTAINER_NAME}"
echo "  Порт:      ${HOST_PORT} → 80"
echo "  Режим:     $([ "$DETACH" = true ] && echo "фоновый" || echo "интерактивный")"
echo "============================================="
echo ""

docker "${DOCKER_ARGS[@]}"

if [ "$DETACH" = true ]; then
    echo ""
    # Ждём запуска
    info "Ожидание запуска..."
    sleep 3

    if docker ps -q -f name="$CONTAINER_NAME" | grep -q .; then
        ok "Контейнер запущен"
        echo ""
        echo "  Платформа: http://localhost:${HOST_PORT}"
        echo "  Логи:      ./run.sh --logs"
        echo "  Статус:    ./run.sh --status"
        echo "  Остановка: ./run.sh --stop"
    else
        fail "Контейнер не запустился. Проверьте логи: docker logs $CONTAINER_NAME"
    fi
fi
