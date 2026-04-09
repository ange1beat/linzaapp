# CLAUDE.md — Linza Deploy

## Описание
Конфигурация развёртывания Linza Detector. Docker, nginx, start.sh.
Порт: 80 (nginx gateway). Роль: сборка и запуск единого контейнера.

## Критические правила
- **Dockerfile COPY пути case-sensitive**: `Linza-storage-service` (с большой L)
- **Linza-start/ копии ДОЛЖНЫ быть идентичны** корневым файлам (Dockerfile, entrypoint.sh, nginx configs)
- **ffmpeg** обязателен в Dockerfile (apt-get install)
- **entrypoint.sh**: env vars STORAGE_SERVICE_URL/ANALYTICS_SERVICE_URL экспортировать ДО запуска vpleer
- **start.sh**: REPOS array case-sensitive: ("linza-board" "Linza-storage-service" "linza-analytics" "linza-vpleer")
- **НЕ запускать docker build напрямую** — только через start.sh

## Реестр файлов

### Корневые
- [x] Dockerfile — multi-stage: node:20 (Vue build) + python:3.12 (runtime) + nginx + ffmpeg
- [x] entrypoint.sh — запуск 4 uvicorn + nginx, healthcheck wait
- [x] docker-compose.yml — 8 сервисов: postgres, minio, board, storage, analytics, vpleer, error-tracker, nginx
- [x] nginx/nginx.conf — API gateway (compose, DNS имена сервисов)
- [x] nginx/nginx-ssl.conf — HTTPS/TLS версия nginx.conf (443 ssl http2, HSTS, OCSP)
- [x] nginx/nginx-standalone.conf — API gateway (единый контейнер, 127.0.0.1)

### Linza-start/
- [x] start.sh — клонирование, сборка, запуск. Trap cleanup. --branch, --port, --compose
- [x] Dockerfile — идентичен корневому
- [x] entrypoint.sh — идентичен корневому
- [x] docker-compose.yml — идентичен корневому
- [x] nginx-standalone.conf — идентичен корневому nginx/nginx-standalone.conf
- [x] nginx/nginx.conf — идентичен корневому nginx/nginx.conf
- [x] .env.example — шаблон переменных окружения
- [x] README.md — инструкция

## Nginx маршрутизация
| Паттерн | Upstream | Порт |
|---|---|---|
| /api/auth/*, /api/users/*, /api/settings/*, /api/reports/* | board | 8000 |
| /api/files/* | storage | 8001 |
| /api/config/* | storage | 8001 |
| /api/classifier/* | analytics | 8002 |
| /api/vpleer/* | vpleer | 8003 |
| /* (SPA fallback) | board | 8000 |

## Синхронизация Linza-start/
- **Проверка:** `bash scripts/check-sync.sh` — CI запускает автоматически
- **Файлы:** Dockerfile, entrypoint.sh, docker-compose.yml, nginx/nginx.conf, nginx-standalone.conf, .env.example
- **При изменении корневого файла:** скопировать в Linza-start/ (root = source of truth)

## PostgreSQL (board#27)

- **Сервис:** `postgres` (postgres:16-alpine) в docker-compose.yml
- **Healthcheck:** `pg_isready` — board ждёт готовности PostgreSQL перед стартом
- **Volume:** `postgres-data` — данные PostgreSQL персистентны
- **Переменные:** `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB` в .env.example
- **Board подключается через:** `DATABASE_URL=postgresql://$USER:$PASS@postgres:5432/$DB`
- **Миграции:** Alembic (`alembic upgrade head`) запускается автоматически в lifespan board при старте

### Air-gapped деплой

Всё внутри образов. PostgreSQL image (`postgres:16-alpine`) нужен в локальном registry. Alembic миграции — Python-файлы внутри образа board, интернет не нужен.

## Резервное копирование в облачный PostgreSQL (board#27)

### Инфраструктура

- **Скрипт:** `scripts/pg-backup.sh` — pg_dump внутреннего PG → psql restore в облачный
- **Сервис:** `pg-backup` (закомментирован в docker-compose.yml, раскомментировать для включения)
- **Переменные:** `CLOUD_DATABASE_URL`, `BACKUP_INTERVAL` в .env

### Включение

1. Задать `CLOUD_DATABASE_URL=postgresql://user:pass@cloud-host:5432/linza_board` в `.env`
2. Раскомментировать секцию `pg-backup` в `docker-compose.yml`
3. Добавить volume `pg-backup-data` в секцию volumes
4. `docker-compose up -d pg-backup`

### Два подхода к репликации (backlog)

| Подход | Когда использовать | Задача |
|---|---|---|
| **pg_dump по расписанию** | Есть прямой доступ к внутреннему PG (VPN/SSH-туннель). Полная копия, быстро, консистентно. | Скрипт готов: `scripts/pg-backup.sh` |
| **App-level экспорт** | Нет доступа к БД напрямую, только HTTP API. Работает через API Gateway. Нужен отдельный Python-сервис. | Бэклог: требует реализации API-эндпоинтов экспорта |

### Скрипты
- [x] scripts/check-sync.sh — проверка синхронизации корневых файлов и Linza-start/
- [x] scripts/pg-backup.sh — pg_dump → облачный PostgreSQL
- [x] scripts/smoke-test.sh — cross-service smoke test (docker compose up → health checks → cleanup)
  - Запуск: `bash scripts/smoke-test.sh`
  - Проверяет: health endpoints через nginx и напрямую, X-Request-ID, CORS
  - Требует: Docker, docker compose, все 5 репозиториев сервисов

## HTTPS/TLS (deploy#13)

- **nginx-ssl.conf** — HTTPS-версия nginx.conf (443 ssl http2, redirect 80->443, modern TLS)
- **SSL сертификаты** в `ssl/` директории (gitignored, только `.gitkeep` в репозитории)
- **Документация:** `docs/ssl-setup.md` — Let's Encrypt и self-signed инструкции
- **Включение:** заменить volume mount `nginx.conf` на `nginx-ssl.conf` в docker-compose.yml

## Чеклист перед коммитом
1. `bash scripts/check-sync.sh` проходит без ошибок
2. nginx configs содержат location /api/config → storage
3. entrypoint.sh экспортирует STORAGE_SERVICE_URL и ANALYTICS_SERVICE_URL ДО vpleer
4. start.sh содержит trap cleanup EXIT
5. Dockerfile устанавливает ffmpeg
6. docker-compose.yml содержит postgres service с healthcheck
7. scripts/pg-backup.sh имеет chmod +x
