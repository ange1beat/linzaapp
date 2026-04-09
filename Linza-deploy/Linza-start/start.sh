#!/bin/bash
# =============================================================================
#  Linza-start — сборка и запуск всей платформы одной командой
#
#  Использование:
#    ./start.sh                      # клонировать, собрать, запустить
#    ./start.sh --build-only         # только собрать образ
#    ./start.sh --run-only           # только запустить (если образ уже собран)
#    ./start.sh --compose            # запуск через docker-compose (для разработки)
#    ./start.sh --stop               # остановить контейнер
#    ./start.sh --status             # проверить статус
# =============================================================================
set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
BUILD_DIR=""
cleanup() { [ -n "$BUILD_DIR" ] && [ -d "$BUILD_DIR" ] && rm -rf "$BUILD_DIR"; }
trap cleanup EXIT
IMAGE_NAME="linza-detector"
IMAGE_TAG="latest"
CONTAINER_NAME="linza"
HOST_PORT=80
GITHUB_ORG="BigDataQueen"
BRANCH="main"

# ── Цвета ─────────────────────────────────────────────────────────────────────
RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'
BLUE='\033[0;34m'; NC='\033[0m'
info()  { echo -e "${BLUE}[linza]${NC} $1"; }
ok()    { echo -e "${GREEN}[linza] ✓${NC} $1"; }
warn()  { echo -e "${YELLOW}[linza] !${NC} $1"; }
fail()  { echo -e "${RED}[linza] ✗${NC} $1"; exit 1; }

# ── Репозитории ────────────────────────────────────────────────────────────────
# Все сервисы платформы, включая Linza-debug (error-tracker)
REPOS=("linza-board" "Linza-storage-service" "linza-analytics" "linza-vpleer" "Linza-debug")

# ── Разбор аргументов ──────────────────────────────────────────────────────────
ACTION="full"
while [[ $# -gt 0 ]]; do
    case $1 in
        --build-only)  ACTION="build"; shift ;;
        --run-only)    ACTION="run"; shift ;;
        --compose)     ACTION="compose"; shift ;;
        --stop)        ACTION="stop"; shift ;;
        --status)      ACTION="status"; shift ;;
        --port)        HOST_PORT="$2"; shift 2 ;;
        --branch)      BRANCH="$2"; shift 2 ;;
        --help|-h)
            echo "Linza-start — сборка и запуск платформы видеоаналитики"
            echo ""
            echo "Использование: ./start.sh [опции]"
            echo ""
            echo "Действия:"
            echo "  (без опций)       Клонировать, собрать и запустить"
            echo "  --build-only      Только собрать Docker-образ"
            echo "  --run-only        Только запустить (образ должен быть собран)"
            echo "  --compose         Запустить через docker-compose (для разработки)"
            echo "  --stop            Остановить контейнер"
            echo "  --status          Проверить статус сервисов"
            echo ""
            echo "Опции:"
            echo "  --port <port>     Порт (по умолчанию: 80)"
            echo "  --branch <name>   Git-ветка (по умолчанию: main)"
            echo "  --help, -h        Эта справка"
            exit 0
            ;;
        *) fail "Неизвестная опция: $1 (--help для справки)" ;;
    esac
done

# ── Команда: stop ──────────────────────────────────────────────────────────────
if [ "$ACTION" = "stop" ]; then
    if docker ps -q -f name="$CONTAINER_NAME" | grep -q .; then
        info "Остановка контейнера..."
        docker stop "$CONTAINER_NAME" && docker rm "$CONTAINER_NAME"
        ok "Контейнер остановлен"
    else
        warn "Контейнер не запущен"
    fi
    exit 0
fi

# ── Команда: status ────────────────────────────────────────────────────────────
if [ "$ACTION" = "status" ]; then
    echo ""
    echo "============================================="
    echo "  Linza Detector — статус"
    echo "============================================="
    if ! docker ps -q -f name="$CONTAINER_NAME" | grep -q .; then
        warn "Контейнер не запущен"
        exit 0
    fi
    PORT=$(docker port "$CONTAINER_NAME" 80 2>/dev/null | head -1 | cut -d: -f2)
    BASE="http://localhost:${PORT:-80}"
    ok "Контейнер запущен (порт: ${PORT:-?})"
    echo ""
    for svc in "Board:${BASE}/health" "Storage:${BASE}/api/files" "Analytics:${BASE}/api/classifier" "VPleer:${BASE}/api/vpleer/files" "ErrorTracker:${BASE}/api/errors/health"; do
        name="${svc%%:*}"; url="${svc#*:}"
        if curl -sf "$url" >/dev/null 2>&1; then
            echo -e "  ${GREEN}✓${NC} $name"
        else
            echo -e "  ${RED}✗${NC} $name"
        fi
    done
    echo ""
    echo "  Плеер: ${BASE}/api/vpleer/player"
    echo "  Ошибки: ${BASE}/settings/error-tracking (UI)"
    echo "============================================="
    exit 0
fi

# ── Проверка Docker ────────────────────────────────────────────────────────────
command -v docker >/dev/null 2>&1 || fail "Docker не установлен"

# ── Подготовка .env ────────────────────────────────────────────────────────────
if [ ! -f "$SCRIPT_DIR/.env" ]; then
    if [ -f "$SCRIPT_DIR/.env.example" ]; then
        cp "$SCRIPT_DIR/.env.example" "$SCRIPT_DIR/.env"
        warn "Создан .env из .env.example — настройте S3 ключи!"
    fi
fi

# ── Docker Compose ─────────────────────────────────────────────────────────────
if [ "$ACTION" = "compose" ]; then
    info "Запуск через docker-compose..."
    # Клонируем рядом если нет
    for repo in "${REPOS[@]}"; do
        if [ ! -d "$SCRIPT_DIR/../$repo" ] && [ ! -d "$SCRIPT_DIR/$repo" ]; then
            info "Клонирование $repo..."
            git clone --depth 1 --branch "$BRANCH" \
                "https://github.com/${GITHUB_ORG}/${repo}.git" \
                "$SCRIPT_DIR/../$repo"
        fi
    done
    cd "$SCRIPT_DIR"
    docker compose --env-file .env up --build -d
    ok "Сервисы запущены"
    echo ""
    echo "  Платформа:      http://localhost"
    echo "  Плеер:          http://localhost/api/vpleer/player"
    echo "  Ошибки (UI):    http://localhost → Настройки → Отслеживание ошибок"
    echo "  MinIO:          http://localhost:9001"
    echo ""
    echo "  Логи:           docker compose logs -f"
    echo "  Остановка:      docker compose down"
    exit 0
fi

# ── Клонирование (если нужно) ──────────────────────────────────────────────────
BUILD_DIR="$(mktemp -d)"
CONTEXT_DIR="$BUILD_DIR/context"
mkdir -p "$CONTEXT_DIR"

clone_or_copy() {
    local repo="$1"
    # Проверяем наличие локально (рядом с Linza-start или выше)
    if [ -d "$SCRIPT_DIR/../$repo" ]; then
        info "Копирование $repo (локально)..."
        rsync -a --exclude='.git' --exclude='node_modules' --exclude='__pycache__' \
            "$SCRIPT_DIR/../$repo/" "$CONTEXT_DIR/$repo/" 2>/dev/null || \
            cp -r "$SCRIPT_DIR/../$repo" "$CONTEXT_DIR/$repo"
    elif [ -d "$SCRIPT_DIR/../../$repo" ]; then
        info "Копирование $repo (локально)..."
        rsync -a --exclude='.git' --exclude='node_modules' --exclude='__pycache__' \
            "$SCRIPT_DIR/../../$repo/" "$CONTEXT_DIR/$repo/" 2>/dev/null || \
            cp -r "$SCRIPT_DIR/../../$repo" "$CONTEXT_DIR/$repo"
    else
        info "Клонирование $repo из GitHub..."
        git clone --depth 1 --branch "$BRANCH" \
            "https://github.com/${GITHUB_ORG}/${repo}.git" \
            "$CONTEXT_DIR/$repo" 2>&1 | tail -1
    fi
    rm -rf "$CONTEXT_DIR/$repo/.git" "$CONTEXT_DIR/$repo/node_modules"
    find "$CONTEXT_DIR/$repo" -type d -name '__pycache__' -exec rm -rf {} + 2>/dev/null || true
    ok "  $repo"
}

if [ "$ACTION" = "full" ] || [ "$ACTION" = "build" ]; then
    echo ""
    echo "============================================="
    echo "  Linza Detector — сборка"
    echo "============================================="
    echo ""

    info "Подготовка исходного кода..."
    for repo in "${REPOS[@]}"; do
        clone_or_copy "$repo"
    done

    # Копируем файлы сборки
    cp "$SCRIPT_DIR/Dockerfile"                  "$CONTEXT_DIR/"
    cp "$SCRIPT_DIR/entrypoint.sh"               "$CONTEXT_DIR/"
    mkdir -p "$CONTEXT_DIR/nginx"
    cp "$SCRIPT_DIR/nginx-standalone.conf"        "$CONTEXT_DIR/nginx/"

    # ── Сборка Docker-образа ──────────────────────────────────────────
    echo ""
    info "Сборка Docker-образа ${IMAGE_NAME}:${IMAGE_TAG}..."
    docker build -t "${IMAGE_NAME}:${IMAGE_TAG}" \
        -f "$CONTEXT_DIR/Dockerfile" "$CONTEXT_DIR"

    IMAGE_SIZE=$(docker image inspect "${IMAGE_NAME}:${IMAGE_TAG}" \
        --format='{{.Size}}' 2>/dev/null | awk '{printf "%.0f", $1/1048576}')

    echo ""
    ok "Образ собран: ${IMAGE_NAME}:${IMAGE_TAG} (~${IMAGE_SIZE} МБ)"

    # Очистка (trap EXIT тоже подхватит)
    rm -rf "$BUILD_DIR"
    BUILD_DIR=""
fi

# ── Запуск ─────────────────────────────────────────────────────────────────────
if [ "$ACTION" = "full" ] || [ "$ACTION" = "run" ]; then
    if ! docker image inspect "${IMAGE_NAME}:${IMAGE_TAG}" >/dev/null 2>&1; then
        fail "Образ не найден. Сначала выполните: ./start.sh --build-only"
    fi

    # Остановить предыдущий
    if docker ps -aq -f name="$CONTAINER_NAME" | grep -q .; then
        warn "Удаление предыдущего контейнера..."
        docker rm -f "$CONTAINER_NAME" >/dev/null 2>&1
    fi

    DOCKER_ARGS=(run -d --name "$CONTAINER_NAME" -p "${HOST_PORT}:80"
                 -v "linza-analytics-data:/app/data"
                 -v "linza-errors-data:/app/services/board")
    [ -f "$SCRIPT_DIR/.env" ] && DOCKER_ARGS+=(--env-file "$SCRIPT_DIR/.env")
    DOCKER_ARGS+=("${IMAGE_NAME}:${IMAGE_TAG}")

    docker "${DOCKER_ARGS[@]}"

    info "Ожидание запуска сервисов..."
    sleep 4

    if docker ps -q -f name="$CONTAINER_NAME" | grep -q .; then
        echo ""
        echo "============================================="
        echo "  Linza Detector запущен!"
        echo "============================================="
        echo "  Платформа:       http://localhost:${HOST_PORT}"
        echo "  Видеоплеер:      http://localhost:${HOST_PORT}/api/vpleer/player"
        echo "  API docs:        http://localhost:${HOST_PORT}/api/vpleer/docs"
        echo "  Ошибки (UI):     http://localhost:${HOST_PORT} → Настройки → Отслеживание ошибок"
        echo ""
        echo "  Логин:           admin / admin"
        echo ""
        echo "  Статус:          ./start.sh --status"
        echo "  Остановка:       ./start.sh --stop"
        echo "  Логи:            docker logs -f ${CONTAINER_NAME}"
        echo ""
        echo "  Экспорт:         docker save ${IMAGE_NAME}:${IMAGE_TAG} | gzip > linza-detector.tar.gz"
        echo "============================================="
    else
        fail "Контейнер не запустился. Логи: docker logs $CONTAINER_NAME"
    fi
fi
