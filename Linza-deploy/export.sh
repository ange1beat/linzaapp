#!/bin/bash
# =============================================================================
#  Linza Detector — экспорт Docker-образа для переноса на другую машину
#
#  Использование:
#    ./export.sh                        # экспорт в linza-detector.tar.gz
#    ./export.sh --output /path/to/out  # экспорт в указанный файл
#    ./export.sh --import file.tar.gz   # импорт образа из архива
# =============================================================================
set -e

IMAGE_NAME="linza-detector"
IMAGE_TAG="latest"
OUTPUT_FILE="linza-detector.tar.gz"
ACTION="export"

# ── Цвета ────────────────────────────────────────────────────────────────────
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

info()  { echo -e "${BLUE}[linza]${NC} $1"; }
ok()    { echo -e "${GREEN}[linza] ✓${NC} $1"; }
fail()  { echo -e "${RED}[linza] ✗${NC} $1"; exit 1; }

# ── Разбор аргументов ────────────────────────────────────────────────────────
while [[ $# -gt 0 ]]; do
    case $1 in
        --output|-o)
            OUTPUT_FILE="$2"
            shift 2
            ;;
        --tag)
            IMAGE_TAG="$2"
            shift 2
            ;;
        --import)
            ACTION="import"
            OUTPUT_FILE="$2"
            shift 2
            ;;
        --help|-h)
            echo "Linza Detector — экспорт/импорт Docker-образа"
            echo ""
            echo "Использование:"
            echo "  ./export.sh                        Экспорт образа"
            echo "  ./export.sh --output <file>        Экспорт в указанный файл"
            echo "  ./export.sh --import <file>        Импорт образа из архива"
            echo "  ./export.sh --tag <tag>            Тег образа (по умолчанию: latest)"
            echo ""
            echo "Перенос на другую машину:"
            echo "  1. На машине-источнике:  ./export.sh"
            echo "  2. Скопировать файл:     scp linza-detector.tar.gz user@host:~/"
            echo "  3. На целевой машине:    ./export.sh --import linza-detector.tar.gz"
            echo "  4. Запустить:            ./run.sh -d"
            exit 0
            ;;
        *)
            echo "Неизвестная опция: $1 (используйте --help)"
            exit 1
            ;;
    esac
done

# ── Импорт ───────────────────────────────────────────────────────────────────
if [ "$ACTION" = "import" ]; then
    if [ ! -f "$OUTPUT_FILE" ]; then
        fail "Файл $OUTPUT_FILE не найден"
    fi

    FILE_SIZE=$(du -h "$OUTPUT_FILE" | cut -f1)
    info "Загрузка образа из $OUTPUT_FILE ($FILE_SIZE)..."
    docker load < "$OUTPUT_FILE"
    ok "Образ загружен"
    echo ""
    echo "  Запуск: ./run.sh -d"
    exit 0
fi

# ── Экспорт ──────────────────────────────────────────────────────────────────
if ! docker image inspect "${IMAGE_NAME}:${IMAGE_TAG}" > /dev/null 2>&1; then
    fail "Образ ${IMAGE_NAME}:${IMAGE_TAG} не найден. Сначала выполните ./build.sh"
fi

IMAGE_SIZE=$(docker image inspect "${IMAGE_NAME}:${IMAGE_TAG}" \
    --format='{{.Size}}' 2>/dev/null | awk '{printf "%.0f", $1/1048576}')

info "Экспорт образа ${IMAGE_NAME}:${IMAGE_TAG} (~${IMAGE_SIZE} МБ)..."
info "Это может занять несколько минут..."

docker save "${IMAGE_NAME}:${IMAGE_TAG}" | gzip > "$OUTPUT_FILE"

ARCHIVE_SIZE=$(du -h "$OUTPUT_FILE" | cut -f1)
ok "Образ сохранён: $OUTPUT_FILE ($ARCHIVE_SIZE)"
echo ""
echo "  Перенос на другую машину:"
echo "    scp $OUTPUT_FILE user@host:~/"
echo ""
echo "  Загрузка на целевой машине:"
echo "    ./export.sh --import $OUTPUT_FILE"
echo "    ./run.sh -d"
