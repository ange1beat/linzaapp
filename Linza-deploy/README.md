# Linza Deploy

Конфигурация развёртывания платформы **Linza Detector** — системы видеоаналитики для обнаружения нарушений в видеоконтенте.

Содержит скрипты для сборки единого Docker-контейнера, его запуска, экспорта и переноса на локальную или виртуальную машину.

## Общая архитектура платформы

| Репозиторий | Назначение | Порт |
|-------------|-----------|------|
| [linza-board](https://github.com/BigDataQueen/linza-board) | UI, авторизация, роли пользователей | 8000 |
| [Linza-storage-service](https://github.com/BigDataQueen/Linza-storage-service) | Работа с файлами, S3-хранилище | 8001 |
| [linza-analytics](https://github.com/BigDataQueen/linza-analytics) | Классификатор нарушений, отчёты | 8002 |
| [linza-vpleer](https://github.com/BigDataQueen/linza-vpleer) | Видеоплеер | 8003 |
| **Linza-deploy** (этот) | Сборка и развёртывание | 80 |

## Архитектурная схема

```
┌─────────────────────────────────────────────────────────────────┐
│                     Клиент (браузер)                             │
└─────────────────────────┬───────────────────────────────────────┘
                          │ HTTP :80
┌─────────────────────────▼───────────────────────────────────────┐
│                    Nginx (API Gateway)                           │
│                                                                  │
│  /api/auth/*            → board:8000                            │
│  /api/users/*           → board:8000                            │
│  /api/settings/*        → board:8000                            │
│  /api/files/*           → storage:8001                          │
│  /api/config/*          → storage:8001                          │
│  /api/classifier/*      → analytics:8002                        │
│  /api/vpleer/*          → vpleer:8003                           │
│  /* (SPA)               → board:8000                            │
└──────┬──────────┬───────────────┬─────────────┬─────────────────┘
       │          │               │             │
┌──────▼────┐ ┌───▼─────────┐ ┌──▼───────┐ ┌───▼──────┐
│ Board     │ │ Storage     │ │ Analytics│ │ VPleer   │
│ :8000     │ │ :8001       │ │ :8002    │ │ :8003    │
│           │ │             │ │          │ │          │
│ Vue.js    │ │ S3/MinIO    │ │ SQLite   │ │ Video    │
│ SPA       │ │ boto3       │ │ 21 тип   │ │ Streaming│
│ JWT Auth  │ │ httpx       │ │ нарушений│ │ ffmpeg   │
│ Роли      │ │ SSE         │ │ Отчёты   │ │          │
│ Профили   │ │ Hot-reload  │ │          │ │          │
│ хранилищ  │ │ конфиг      │ │          │ │          │
└─────┬─────┘ └─────────────┘ └──────────┘ └────┬─────┘
      │                                          │
      │  PUT /api/config/s3                      │ GET /api/files/download/*
      │  (горячее обновление)                    │ GET /api/classifier
      └──────────► Storage ◄─────────────────────┘
                    │                      VPleer → Storage
                    ▼                      VPleer → Analytics
              ┌───────────┐
              │ S3 / MinIO │
              └───────────┘
```

### Межсервисное взаимодействие (REST API)

| Кто вызывает | Кого вызывает | Метод | Эндпоинт | Описание |
|---|---|---|---|---|
| VPleer | Storage | `GET` | `/api/files` | Список файлов |
| VPleer | Storage | `HEAD` | `/api/files/download/{file}` | Размер файла |
| VPleer | Storage | `GET` | `/api/files/download/{file}` | Потоковое чтение файла |
| VPleer | Analytics | `GET` | `/api/classifier` | Конфигурация категорий |
| Board | Storage | `PUT` | `/api/config/s3` | Обновление S3-кредов (горячее) |
| Board | Storage | `POST` | `/api/config/s3/test` | Тест подключения к S3 |

## Быстрый старт — единый контейнер

### 1. Сборка

```bash
# Вариант A: из локальных репозиториев (должны лежать рядом)
./build.sh

# Вариант B: автоматическое клонирование с GitHub
./build.sh --clone

# Вариант C: клонирование конкретной ветки
./build.sh --clone --branch main --tag v1.0.0
```

### 2. Настройка

```bash
cp .env.example .env
# Отредактировать .env — указать S3-ключи и пароль администратора
```

### 3. Запуск

```bash
# Запуск в фоне
./run.sh -d

# Или с указанием порта
./run.sh -d --port 8080

# Или напрямую через docker
docker run -d -p 80:80 --env-file .env --name linza linza-detector
```

### 4. Использование

Откройте `http://localhost` в браузере. Логин: `admin` / `admin` (по умолчанию).

```bash
# Проверка статуса
./run.sh --status

# Просмотр логов
./run.sh --logs

# Остановка
./run.sh --stop
```

### 5. Перенос на другую машину

```bash
# На машине-источнике: экспорт образа
./export.sh
# → linza-detector.tar.gz

# Копирование на целевую машину
scp linza-detector.tar.gz user@server:~/

# На целевой машине: загрузка и запуск
./export.sh --import linza-detector.tar.gz
./run.sh -d
```

## Структура проекта

```
Linza-deploy/
├── build.sh                 # Скрипт сборки Docker-образа
├── run.sh                   # Скрипт запуска/остановки/логов
├── export.sh                # Экспорт/импорт образа для переноса
├── Dockerfile               # Multi-stage сборка единого контейнера
├── entrypoint.sh            # Запуск Nginx + 4 uvicorn-процессов
├── docker-compose.yml       # Оркестрация: 4 сервиса + MinIO + Nginx
├── nginx/
│   ├── nginx.conf           # Nginx для Docker Compose (имена сервисов)
│   └── nginx-standalone.conf # Nginx для единого контейнера (localhost)
├── .env.example             # Шаблон переменных окружения
└── README.md
```

## Скрипты

### `build.sh` — Сборка Docker-образа

Собирает все 4 сервиса в один Docker-образ `linza-detector`.

**Что делает:**
1. Проверяет наличие всех репозиториев (или клонирует с GitHub при `--clone`)
2. Готовит контекст сборки: копирует код без `.git`, `node_modules`, `__pycache__`
3. Запускает `docker build` с multi-stage Dockerfile
4. Выводит информацию о собранном образе и команды для запуска

**Опции:**

| Опция | Описание |
|-------|----------|
| `--clone` | Клонировать репозитории из GitHub |
| `--branch <name>` | Ветка для клонирования (по умолчанию: `main`) |
| `--tag <tag>` | Тег Docker-образа (по умолчанию: `latest`) |

**Ожидаемая структура директорий (без `--clone`):**
```
parent-dir/
├── linza-board/
├── Linza-storage-service/
├── linza-analytics/
├── linza-vpleer/
└── Linza-deploy/          ← вы здесь
```

### `run.sh` — Управление контейнером

**Опции:**

| Опция | Описание |
|-------|----------|
| `--port <port>` | Порт на хост-машине (по умолчанию: `80`) |
| `--env-file <path>` | Файл с переменными окружения |
| `-d`, `--detach` | Запуск в фоновом режиме |
| `--stop` | Остановить и удалить контейнер |
| `--logs` | Показать логи контейнера |
| `--status` | Проверить статус контейнера и всех сервисов |
| `--tag <tag>` | Тег образа (по умолчанию: `latest`) |

### `export.sh` — Экспорт/импорт образа

Для переноса собранного образа на машину без доступа к исходному коду или GitHub.

| Опция | Описание |
|-------|----------|
| (без опций) | Экспорт в `linza-detector.tar.gz` |
| `--output <file>` | Экспорт в указанный файл |
| `--import <file>` | Импорт образа из архива |

## Реализация единого контейнера

### `Dockerfile` — Multi-stage сборка

**Stage 1** — `node:20-alpine` (сборка фронтенда):
- `npm ci` — установка Node.js зависимостей
- `npm run build` — Vite собирает Vue.js SPA в `dist/`

**Stage 2** — `python:3.12-slim` (рабочий образ):
- Установка Nginx и curl
- Установка Python-зависимостей из 4 файлов `requirements.txt`
- Копирование кода каждого сервиса в `/app/services/{name}/`
- Копирование собранного SPA в `/app/services/board/dist/`
- Копирование `nginx-standalone.conf` в `/etc/nginx/nginx.conf`
- `HEALTHCHECK` проверяет доступность сервисов каждые 30 секунд

### `entrypoint.sh` — Запуск процессов

Порядок запуска:
1. Запускает 4 uvicorn-процесса в фоне (привязаны к `127.0.0.1`, не видны снаружи)
2. Ожидает готовности каждого сервиса через `GET /health` (до 30 секунд)
3. Проверяет конфигурацию Nginx (`nginx -t`)
4. Запускает Nginx в foreground-режиме (`nginx -g 'daemon off'`)

Nginx остаётся главным процессом контейнера — при его завершении контейнер останавливается. Логи каждого сервиса пишутся в `/var/log/linza/{name}.log`.

### `nginx/nginx-standalone.conf` — API Gateway (единый контейнер)

Все upstream-ы указывают на `127.0.0.1` (внутри одного контейнера):

| URL-паттерн | Upstream | Назначение |
|-------------|----------|-----------|
| `/api/files*` | `127.0.0.1:8001` | Файловые операции (SSE, загрузка) |
| `/api/classifier*` | `127.0.0.1:8002` | Классификатор нарушений |
| `/api/vpleer*` | `127.0.0.1:8003` | Видеоплеер |
| `/*` | `127.0.0.1:8000` | Auth API + Vue.js SPA (fallback) |

Особенности:
- `client_max_body_size 10G` — загрузка больших видеофайлов
- `proxy_buffering off` + `proxy_http_version 1.1` для `/api/files` — SSE
- `proxy_read_timeout 600s` — долгие операции загрузки

### `nginx/nginx.conf` — API Gateway (Docker Compose)

Аналогичная конфигурация, но upstream-ы указывают на имена сервисов Docker Compose (`linza-board:8000`, `storage-service:8001` и т.д.).

## Docker Compose (альтернативный вариант)

Для разработки или когда нужны отдельные контейнеры.

```bash
cd Linza-deploy
cp .env.example .env
docker compose up --build
```

Запускает 6 контейнеров:

| Сервис | Образ | Порт |
|--------|-------|------|
| `linza-board` | Из `../linza-board` | 8000 |
| `storage-service` | Из `../Linza-storage-service` | 8001 |
| `analytics-service` | Из `../linza-analytics` | 8002 |
| `vpleer-service` | Из `../linza-vpleer` | 8003 |
| `minio` | `minio/minio:latest` | 9000/9001 |
| `nginx` | `nginx:alpine` | 80 |

## Переменные окружения

| Переменная | Описание | По умолчанию |
|-----------|----------|-------------|
| `AUTH_SECRET_KEY` | Секретный ключ JWT | `linza-secret-change-in-production` |
| `AUTH_ADMIN_LOGIN` | Логин администратора | `admin` |
| `AUTH_ADMIN_PASSWORD` | Пароль администратора | `admin` |
| `S3_ACCESS_KEY_ID` | Ключ доступа S3 | — |
| `S3_SECRET_ACCESS_KEY` | Секретный ключ S3 | — |
| `S3_ENDPOINT_URL` | URL S3-эндпоинта | `https://s3.cloud.ru` |
| `S3_BUCKET_NAME` | Имя бакета | `linzadata` |
| `S3_REGION` | Регион | `ru-central-1` |
| `MINIO_ROOT_USER` | Логин MinIO | `minioadmin` |
| `MINIO_ROOT_PASSWORD` | Пароль MinIO | `minioadmin` |
| `CORS_ORIGINS` | CORS-источники | `http://localhost,http://localhost:80` |

## Маршрутизация

```
Браузер → :80 (Nginx)
  ├── /api/auth/*        → board:8000
  ├── /api/files/*       → storage:8001   (SSE, proxy_buffering off)
  ├── /api/classifier/*  → analytics:8002
  ├── /api/vpleer/*      → vpleer:8003
  └── /* (SPA fallback)  → board:8000 → index.html
```
