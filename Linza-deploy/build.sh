#!/bin/bash
# =============================================================================
#  Linza Detector — скрипт сборки единого Docker-образа
#
#  Использование:
#    ./build.sh                    # сборка из локальных репозиториев
#    ./build.sh --clone            # клонировать репозитории и собрать
#    ./build.sh --clone --branch main  # клонировать ветку main
#    ./build.sh --tag v1.0.0       # собрать с тегом linza-detector:v1.0.0
# =============================================================================
set -e

# ── Настройки ────────────────────────────────────────────────────────────────
IMAGE_NAME="linza-detector"
IMAGE_TAG="latest"
GITHUB_ORG="BigDataQueen"
BRANCH="main"
DO_CLONE=false
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
BUILD_DIR="$(mktemp -d)"

# ── Репозитории ──────────────────────────────────────────────────────────────
REPOS=(
    "linza-board"
    "Linza-storage-service"
    "linza-analytics"
    "linza-vpleer"
)

# ── Разбор аргументов ────────────────────────────────────────────────────────
while [[ $# -gt 0 ]]; do
    case $1 in
        --clone)
            DO_CLONE=true
            shift
            ;;
        --branch)
            BRANCH="$2"
            shift 2
            ;;
        --tag)
            IMAGE_TAG="$2"
            shift 2
            ;;
        --help|-h)
            echo "Linza Detector — сборка единого Docker-образа"
            echo ""
            echo "Использование: ./build.sh [опции]"
            echo ""
            echo "Опции:"
            echo "  --clone           Клонировать репозитории из GitHub"
            echo "  --branch <name>   Ветка для клонирования (по умолчанию: main)"
            echo "  --tag <tag>       Тег Docker-образа (по умолчанию: latest)"
            echo "  --help, -h        Показать эту справку"
            echo ""
            echo "Без --clone скрипт ожидает, что все репозитории"
            echo "расположены рядом с директорией Linza-deploy:"
            echo ""
            echo "  parent-dir/"
            echo "  ├── linza-board/"
            echo "  ├── Linza-storage-service/"
            echo "  ├── linza-analytics/"
            echo "  ├── linza-vpleer/"
            echo "  └── Linza-deploy/        ← вы здесь"
            exit 0
            ;;
        *)
            echo "Неизвестная опция: $1 (используйте --help)"
            exit 1
            ;;
    esac
done

PARENT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

# ── Цвета для вывода ────────────────────────────────────────────────────────
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

info()  { echo -e "${BLUE}[linza]${NC} $1"; }
ok()    { echo -e "${GREEN}[linza] ✓${NC} $1"; }
warn()  { echo -e "${YELLOW}[linza] !${NC} $1"; }
fail()  { echo -e "${RED}[linza] ✗${NC} $1"; exit 1; }

# ── Клонирование репозиториев ────────────────────────────────────────────────
if [ "$DO_CLONE" = true ]; then
    info "Клонирование репозиториев (ветка: $BRANCH)..."
    CLONE_DIR="$BUILD_DIR/repos"
    mkdir -p "$CLONE_DIR"

    for repo in "${REPOS[@]}"; do
        info "  Клонирование $repo..."
        git clone --depth 1 --branch "$BRANCH" \
            "https://github.com/${GITHUB_ORG}/${repo}.git" \
            "$CLONE_DIR/$repo" 2>&1 | tail -1
        ok "  $repo"
    done

    SOURCE_DIR="$CLONE_DIR"
else
    SOURCE_DIR="$PARENT_DIR"
fi

# ── Проверка наличия репозиториев ────────────────────────────────────────────
info "Проверка репозиториев..."
for repo in "${REPOS[@]}"; do
    if [ ! -d "$SOURCE_DIR/$repo" ]; then
        fail "Репозиторий $repo не найден в $SOURCE_DIR"
    fi
    ok "  $repo"
done

# ── Подготовка контекста сборки ──────────────────────────────────────────────
info "Подготовка контекста сборки..."
CONTEXT_DIR="$BUILD_DIR/context"
mkdir -p "$CONTEXT_DIR"

# Копируем каждый репозиторий (без .git для уменьшения размера)
for repo in "${REPOS[@]}"; do
    info "  Копирование $repo..."
    rsync -a --exclude='.git' --exclude='node_modules' --exclude='__pycache__' \
        "$SOURCE_DIR/$repo/" "$CONTEXT_DIR/$repo/" 2>/dev/null || \
    cp -r "$SOURCE_DIR/$repo" "$CONTEXT_DIR/$repo"
    # Удаляем .git если rsync не использовался
    rm -rf "$CONTEXT_DIR/$repo/.git"
    rm -rf "$CONTEXT_DIR/$repo/node_modules"
    find "$CONTEXT_DIR/$repo" -type d -name '__pycache__' -exec rm -rf {} + 2>/dev/null || true
done

# Копируем файлы сборки из Linza-deploy
cp "$SCRIPT_DIR/Dockerfile"                    "$CONTEXT_DIR/"
cp "$SCRIPT_DIR/entrypoint.sh"                 "$CONTEXT_DIR/"
mkdir -p "$CONTEXT_DIR/nginx"
cp "$SCRIPT_DIR/nginx/nginx-standalone.conf"   "$CONTEXT_DIR/nginx/"

ok "Контекст сборки подготовлен"

# ── Вывод структуры ──────────────────────────────────────────────────────────
info "Структура контекста:"
echo "  $CONTEXT_DIR/"
for repo in "${REPOS[@]}"; do
    echo "  ├── $repo/"
done
echo "  ├── Dockerfile"
echo "  ├── entrypoint.sh"
echo "  └── nginx/nginx-standalone.conf"
echo ""

# ── Сборка Docker-образа ────────────────────────────────────────────────────
info "Сборка Docker-образа ${IMAGE_NAME}:${IMAGE_TAG}..."
echo ""

docker build \
    -t "${IMAGE_NAME}:${IMAGE_TAG}" \
    -f "$CONTEXT_DIR/Dockerfile" \
    "$CONTEXT_DIR"

echo ""
ok "Docker-образ собран: ${IMAGE_NAME}:${IMAGE_TAG}"

# ── Информация об образе ────────────────────────────────────────────────────
IMAGE_SIZE=$(docker image inspect "${IMAGE_NAME}:${IMAGE_TAG}" \
    --format='{{.Size}}' 2>/dev/null | awk '{printf "%.0f", $1/1048576}')

echo ""
echo "============================================="
echo "  Linza Detector — образ собран!"
echo "============================================="
echo "  Образ:  ${IMAGE_NAME}:${IMAGE_TAG}"
echo "  Размер: ~${IMAGE_SIZE} МБ"
echo ""
echo "  Запуск:"
echo "    ./run.sh"
echo ""
echo "  Или вручную:"
echo "    docker run -d -p 80:80 \\"
echo "      -e AUTH_ADMIN_PASSWORD=your-password \\"
echo "      -e S3_ACCESS_KEY_ID=your-key \\"
echo "      -e S3_SECRET_ACCESS_KEY=your-secret \\"
echo "      --name linza \\"
echo "      ${IMAGE_NAME}:${IMAGE_TAG}"
echo ""
echo "  Экспорт образа для переноса:"
echo "    docker save ${IMAGE_NAME}:${IMAGE_TAG} | gzip > linza-detector.tar.gz"
echo ""
echo "  Загрузка на другой машине:"
echo "    docker load < linza-detector.tar.gz"
echo "============================================="

# ── Очистка ──────────────────────────────────────────────────────────────────
rm -rf "$BUILD_DIR"
ok "Временные файлы удалены"
