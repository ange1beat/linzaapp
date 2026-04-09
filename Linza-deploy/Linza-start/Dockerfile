# =============================================================================
#  Linza Detector — единый Docker-образ
#  Все сервисы + Nginx API Gateway в одном контейнере
# =============================================================================

# ── Stage 1: Сборка Vue.js SPA ──────────────────────────────────────────────
FROM node:20-alpine AS frontend-build
WORKDIR /build

COPY linza-board/package.json linza-board/package-lock.json ./
RUN npm ci --ignore-scripts

COPY linza-board/ .
RUN npm run build


# ── Stage 2: Рабочий образ ──────────────────────────────────────────────────
FROM python:3.12-slim
LABEL maintainer="BigDataQueen"
LABEL description="Linza Detector — платформа видеоаналитики (единый контейнер)"

WORKDIR /app

# Установка Nginx и утилит
RUN apt-get update && \
    apt-get install -y --no-install-recommends nginx curl ffmpeg && \
    rm -rf /var/lib/apt/lists/*

# Объединённые Python-зависимости (дедупликация через pip)
COPY linza-board/requirements.txt       /tmp/req-board.txt
COPY Linza-storage-service/requirements.txt /tmp/req-storage.txt
COPY linza-analytics/requirements.txt   /tmp/req-analytics.txt
COPY linza-vpleer/requirements.txt      /tmp/req-vpleer.txt
COPY Linza-debug/error-tracker/requirements.txt /tmp/req-tracker.txt

RUN pip install --no-cache-dir \
    -r /tmp/req-board.txt \
    -r /tmp/req-storage.txt \
    -r /tmp/req-analytics.txt \
    -r /tmp/req-vpleer.txt \
    -r /tmp/req-tracker.txt && \
    rm -rf /tmp/req-*.txt

# ── Код сервисов ─────────────────────────────────────────────────────────────
# Board (UI + Auth)
COPY linza-board/backend/           /app/services/board/backend/
COPY --from=frontend-build /build/dist /app/services/board/dist/

# Storage Service
COPY Linza-storage-service/app/     /app/services/storage/app/

# Analytics Service
COPY linza-analytics/app/           /app/services/analytics/app/

# VPleer Service
COPY linza-vpleer/app/              /app/services/vpleer/app/

# Error Tracker Service
COPY Linza-debug/error-tracker/app/ /app/services/tracker/app/

# ── Nginx ────────────────────────────────────────────────────────────────────
COPY nginx/nginx-standalone.conf    /etc/nginx/nginx.conf

# ── Entrypoint ───────────────────────────────────────────────────────────────
COPY entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

# ── Каталоги данных ──────────────────────────────────────────────────────────
RUN mkdir -p /app/data /var/log/linza

# ── Переменные окружения по умолчанию ────────────────────────────────────────
ENV AUTH_SECRET_KEY=linza-secret-change-in-production \
    AUTH_ADMIN_LOGIN=admin \
    AUTH_ADMIN_PASSWORD=admin \
    S3_ACCESS_KEY_ID="" \
    S3_SECRET_ACCESS_KEY="" \
    S3_ENDPOINT_URL=https://s3.twcstorage.ru \
    S3_BUCKET_NAME=5aca33a6-7dff-49cb-8069-3442ccb455c3 \
    S3_REGION=ru-1 \
    CORS_ORIGINS=http://localhost,http://localhost:80

EXPOSE 80

HEALTHCHECK --interval=30s --timeout=5s --start-period=15s --retries=3 \
    CMD curl -sf http://localhost:8000/health >/dev/null 2>&1 || exit 1

CMD ["/app/entrypoint.sh"]
