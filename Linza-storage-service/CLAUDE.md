# CLAUDE.md — Linza Storage Service

## Описание сервиса
Сервис хранения файлов Linza Detector. Работа с S3/MinIO через boto3.
Порт: 8001. Роль: файловые операции, загрузка по URL, потоковая отдача, SSE-прогресс.

## Критические правила
- **get_s3() и get_bucket()** — вызывать как функции, НЕ как переменные (синглтон убран для hot-reload)
- **НЕ импортировать** `s3` или `BUCKET_NAME` напрямую из s3_client — только get_s3()/get_bucket()
- Range-заголовок: всегда проверять bytes= prefix, start <= end, start < total_size
- Content-Disposition: только через _safe_content_disposition (RFC 5987)
- **validate_s3_key()** для всех user-supplied S3 ключей — запрет .., абсолютных путей, только uploads/ и sources/

## Реестр функционала

### Файлы (app/routes/files.py)
- [x] GET /api/files/ — список файлов S3 + активные задачи загрузки
- [x] POST /api/files/upload-from-url — фоновая загрузка файла по URL → S3
- [x] GET /api/files/download/{filename:path} — потоковая отдача из S3 с Range-запросами
- [x] GET /api/files/progress/{task_id} — SSE-стрим прогресса загрузки

### Конфигурация (app/routes/config.py)
- [x] GET /api/config/s3 — текущая конфигурация S3 (ключи замаскированы)
- [x] PUT /api/config/s3 — горячее обновление S3-кредов (пересоздание boto3-клиента)
- [x] POST /api/config/s3/test — тест подключения к S3

### S3-клиент (app/s3_client.py)
- [x] get_s3() — получить текущий boto3-клиент
- [x] get_bucket() — получить имя текущего бакета
- [x] get_config() — конфигурация без секретов
- [x] reconfigure() — горячая замена с thread lock

### Health
- [x] GET /health — {"status": "ok", "service": "storage-service"}

## Смена S3-хранилища

### Через .env (при запуске)
```
S3_ACCESS_KEY_ID=ваш-ключ
S3_SECRET_ACCESS_KEY=ваш-секрет
S3_ENDPOINT_URL=https://s3.cloud.ru    # без /bucket на конце!
S3_BUCKET_NAME=linzadata
S3_REGION=ru-central-1
```

### Горячее обновление (без рестарта)
```bash
curl -X PUT http://localhost:8001/api/config/s3 \
  -H "Content-Type: application/json" \
  -d '{"endpoint_url":"https://new-s3.example.com","access_key_id":"NEW_KEY","secret_access_key":"NEW_SECRET","bucket_name":"new-bucket","region":"us-east-1"}'
```

### Тест подключения
```bash
curl -X POST http://localhost:8001/api/config/s3/test
```

## Персистентное хранение задач (storage#9)

### Архитектура: SQLite + write-back cache

- **SQLite** (`app/task_db.py`): персистентное хранилище, WAL mode
- **In-memory dict** (`app/tasks.py`): кэш для горячего пути
- **Flush thread**: каждые 2 сек сбрасывает dirty задачи в SQLite + TTL cleanup
- **Lifespan** (`app/main.py`): `init_task_store()` при старте, `shutdown_task_store()` при остановке

### Публичный API tasks.py (не изменился)

| Функция | Описание |
|---|---|
| `set_task(task_id, data)` | Создать/заменить задачу (memory + SQLite) |
| `update_task(task_id, **kw)` | Частичное обновление (memory only, кроме terminal states) |
| `get_task(task_id)` | Получить задачу (memory → SQLite fallback) |
| `get_active_tasks()` | Список незавершённых задач |
| `init_task_store()` | Инициализация при старте |
| `shutdown_task_store()` | Финальный flush при остановке |
| `clear_tasks()` | Сброс (для тестов) |

### Очистка orphaned temp-файлов (storage#11)

- Все temp-файлы создаются в `/tmp/linza-storage/` (TEMP_DIR в files.py и main.py)
- `mkstemp(prefix="storage-", dir=TEMP_DIR)` — 3 места в files.py
- При старте `_cleanup_temp_dir()` удаляет всё в TEMP_DIR и логирует количество
- Порядок в lifespan: `_cleanup_temp_dir()` → `init_task_store()` (диск → состояние)

### Crash recovery

При рестарте `init_task_store()`:
- Загружает активные задачи из SQLite
- Помечает downloading/uploading → error ("interrupted by restart")
- Temp файлы потеряны, возобновление невозможно

### Переменные окружения

| Переменная | Default | Описание |
|---|---|---|
| `TASK_DB_PATH` | `/app/data/tasks.db` | Путь к SQLite БД задач |
| `TASK_TTL_COMPLETED` | `3600` (1ч) | TTL для completed задач |
| `TASK_TTL_ERROR` | `86400` (24ч) | TTL для error задач |

## Тестовое покрытие (storage#12)

98 тестов в 12 файлах. Ключевые области:

| Файл | Тестов | Область |
|---|---|---|
| `test_range_headers.py` | 8 | Malformed Range, boundary clamping, 206/200 |
| `test_s3_failures.py` | 6 | ClientError (404/403), partial delete, sources/ partition |
| `test_upload_edge_cases.py` | 9 | upload-local, URL parsing, content-type |
| `test_remote_s3.py` | 7 | remote-s3/list+import, validation |
| `test_concurrent.py` | 3 | 10 потоков × 100 updates, read/write isolation |
| `test_sse_stream.py` | 5 | SSE progress: not_found, completed, error, headers |
| `test_s3_client.py` | 6 | reconfigure() concurrency, secret masking |
| `test_temp_cleanup.py` | 5 | Orphan cleanup, dir creation, logging |
| `test_tasks.py` | 12 | Persistence, TTL, crash recovery |

**Bugfix**: `_db_lock` (threading.Lock) в task_db.py — serialization concurrent SQLite access.

## Зависимости
- fastapi==0.115.5
- uvicorn[standard]==0.32.1
- boto3==1.35.85
- httpx==0.27.2
- python-multipart==0.0.20
- sqlite3 (stdlib, не в requirements)

## Чеклист перед коммитом
1. Все вызовы S3 используют get_s3()/get_bucket(), не синглтоны
2. _safe_content_disposition для всех Content-Disposition заголовков
3. Range validation: bytes= prefix, start/end bounds check
4. config router подключён в main.py на /api/config
5. Task API: set_task/update_task/get_task/get_active_tasks — сигнатуры не менять
6. init_task_store() вызывается в lifespan main.py
7. Все tempfile.mkstemp() используют dir=TEMP_DIR, prefix="storage-"
