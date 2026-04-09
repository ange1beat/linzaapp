# Linza Storage Service

Сервис хранения файлов и управления доступом к ним для платформы **Linza Detector** — системы видеоаналитики.

Обеспечивает загрузку файлов по URL в S3-совместимое хранилище, отслеживание прогресса через Server-Sent Events и управление доступом к файлам.

## Общая архитектура платформы

| Репозиторий | Назначение | Порт |
|-------------|-----------|------|
| [linza-board](https://github.com/BigDataQueen/linza-board) | UI, авторизация, роли пользователей | 8000 |
| **Linza-storage-service** (этот) | Работа с файлами, S3-хранилище | 8001 |
| [linza-analytics](https://github.com/BigDataQueen/linza-analytics) | Классификатор нарушений, отчёты | 8002 |
| [linza-vpleer](https://github.com/BigDataQueen/linza-vpleer) | Видеоплеер | 8003 |
| [Linza-deploy](https://github.com/BigDataQueen/Linza-deploy) | Сборка и развёртывание | — |

## Функционал

### Загрузка файлов по URL
- Приём URL через REST API, запуск фоновой задачи загрузки
- **Фаза 1 — Скачивание**: файл скачивается во временное хранилище с отслеживанием прогресса
- **Фаза 2 — Загрузка в S3**: файл загружается в S3-совместимое хранилище с multipart-upload и callback-прогрессом
- Автоматическое определение имени файла из URL или заголовка `Content-Disposition`
- Очистка временных файлов после завершения

### Отслеживание прогресса (SSE)
- Server-Sent Events (text/event-stream) для мониторинга в реальном времени
- Статусы задачи: `pending` → `downloading` → `uploading` → `completed` / `error`
- Передача: текущий прогресс (байты), общий размер, статус, имя файла
- Интервал обновления: 400 мс

### Управление файлами
- Получение списка файлов из S3-бакета (имя, размер, дата изменения)
- Совмещённый ответ: файлы в хранилище + активные задачи загрузки
- Персистентное хранение задач (SQLite write-back cache)
- TTL автоочистка: completed 1ч, error 24ч

### Надёжность
- **Crash recovery**: задачи выживают перезапуск, in-flight задачи → error ("interrupted by restart")
- **Orphan cleanup**: при старте очищается `/tmp/linza-storage/` от файлов предыдущего крэша
- **Path traversal**: validate_s3_key() запрещает `..`, абсолютные пути, ограничивает `uploads/` и `sources/`

### S3-интеграция
- Совместимость с любым S3-совместимым хранилищем (MinIO, Yandex Cloud, SberCloud и др.)
- Подпись запросов s3v4
- Конфигурация через переменные окружения (без хардкода ключей)

## Структура проекта

```
Linza-storage-service/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI-приложение, lifespan, middleware
│   ├── s3_client.py         # Boto3 S3-клиент, hot-reload конфигурация
│   ├── tasks.py             # Персистентный менеджер задач (SQLite + memory cache)
│   ├── task_db.py           # SQLite persistence layer (WAL mode)
│   └── routes/
│       ├── __init__.py
│       ├── files.py         # Эндпоинты: список, загрузка, прогресс, удаление
│       └── config.py        # Горячее обновление S3-конфигурации
├── tests/                    # Pytest тесты (54 теста)
├── requirements.txt          # Python-зависимости
├── Dockerfile                # Python 3.12-slim, порт 8001
├── CLAUDE.md                 # Архитектурные правила
└── README.md
```

## Реализация

### `app/main.py` — Точка входа
FastAPI-приложение с CORS-middleware и единственным роутером `/api/files`. CORS-источники настраиваются через переменную окружения.

### `app/s3_client.py` — S3-клиент
Инициализация boto3-клиента с параметрами из переменных окружения:
- Эндпоинт, ключи доступа, регион, имя бакета
- Подпись s3v4 для совместимости с S3-совместимыми хранилищами

### `app/tasks.py` + `app/task_db.py` — Менеджер задач
Персистентное хранение задач с SQLite write-back cache:
- **Hot path** (`update_task`): запись только в memory (~200 вызовов/сек при загрузке)
- **Background flush**: batch-запись dirty задач в SQLite каждые 2 сек
- **Terminal states**: `completed`/`error` сохраняются в SQLite немедленно
- **Crash recovery**: при старте downloading/uploading → error ("interrupted by restart")
- **TTL cleanup**: completed 1ч, error 24ч (настраивается через env)

### `app/routes/files.py` — API-эндпоинты

**`GET /api/files`** — Список файлов и активных задач
- Вызывает `s3.list_objects_v2()` для получения содержимого бакета
- Возвращает объединённый ответ: `{ files: [...], tasks: [...] }`

**`POST /api/files/upload-from-url`** — Запуск загрузки
- Принимает `{ url: "https://..." }`
- Определяет имя файла из URL-пути
- Создаёт задачу и запускает фоновый процесс через `BackgroundTasks`
- Возвращает `{ task_id, filename }`

**`GET /api/files/progress/{task_id}`** — SSE-поток
- Отправляет JSON-события каждые 400 мс
- Поля события: `status`, `filename`, `progress`, `total`, `error`
- Закрывает поток при статусе `completed` или `error`

Фоновая задача `_upload_task()`:
1. Скачивает файл через `httpx.Client.stream()` с `follow_redirects=True`
2. Сохраняет во временный файл (`tempfile.mkstemp`)
3. Загружает в S3 через `s3.upload_file()` с `Callback` для отслеживания прогресса
4. Удаляет временный файл в блоке `finally`

## Стек технологий

| Компонент | Технология | Версия |
|-----------|-----------|--------|
| Фреймворк | FastAPI | 0.115.5 |
| ASGI-сервер | Uvicorn | 0.32.1 |
| S3-клиент | Boto3 | 1.35.85 |
| HTTP-клиент | httpx | 0.27.2 |
| Runtime | Python | 3.12 |

## Переменные окружения

| Переменная | Описание | По умолчанию |
|-----------|----------|-------------|
| `S3_ACCESS_KEY_ID` | Ключ доступа S3 | — |
| `S3_SECRET_ACCESS_KEY` | Секретный ключ S3 | — |
| `S3_ENDPOINT_URL` | URL S3-эндпоинта | `https://s3.cloud.ru` |
| `S3_BUCKET_NAME` | Имя бакета | `linzadata` |
| `S3_REGION` | Регион | `ru-central-1` |
| `CORS_ORIGINS` | Разрешённые CORS-источники (через запятую) | `http://localhost:5173` |
| `SERVICE_API_KEY` | Ключ межсервисной аутентификации | — |
| `ERROR_TRACKER_URL` | URL error-tracker сервиса | `http://localhost:8004` |
| `TASK_DB_PATH` | Путь к SQLite БД задач | `/app/data/tasks.db` |
| `TASK_TTL_COMPLETED` | TTL для completed задач (сек) | `3600` |
| `TASK_TTL_ERROR` | TTL для error задач (сек) | `86400` |

## Запуск

### Разработка

```bash
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8001
```

### Docker

```bash
docker build -t linza-storage-service .
docker run -p 8001:8001 \
  -e S3_ACCESS_KEY_ID=your-key \
  -e S3_SECRET_ACCESS_KEY=your-secret \
  -e S3_ENDPOINT_URL=https://s3.cloud.ru \
  -e S3_BUCKET_NAME=linzadata \
  linza-storage-service
```

## API

| Метод | Endpoint | Описание |
|-------|----------|----------|
| GET | `/api/files` | Список файлов в хранилище и активных задач |
| POST | `/api/files/upload-from-url` | Запуск загрузки файла по URL |
| GET | `/api/files/progress/{task_id}` | SSE-поток прогресса загрузки |
| GET | `/health` | Проверка состояния сервиса |

### Пример запроса — загрузка файла

```bash
curl -X POST http://localhost:8001/api/files/upload-from-url \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com/video.mp4"}'
```

Ответ:
```json
{
  "task_id": "a1b2c3d4e5f6...",
  "filename": "video.mp4"
}
```

### Пример SSE-потока

```bash
curl http://localhost:8001/api/files/progress/a1b2c3d4e5f6
```

```
data: {"status": "downloading", "filename": "video.mp4", "progress": 5242880, "total": 104857600}
data: {"status": "uploading", "filename": "video.mp4", "progress": 3145728, "total": 104857600}
data: {"status": "completed", "filename": "video.mp4", "progress": 104857600, "total": 104857600}
```
