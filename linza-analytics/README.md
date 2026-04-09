# Linza Analytics

Сервис аналитики платформы **Linza Detector** — системы видеоаналитики для обнаружения нарушений в видеоконтенте.

Обеспечивает классификацию нарушений (20+ типов), управление категориями, анализ результатов обработки видео-файлов и создание отчётов.

## Общая архитектура платформы

| Репозиторий | Назначение | Порт |
|-------------|-----------|------|
| [linza-board](https://github.com/BigDataQueen/linza-board) | UI, авторизация, роли пользователей | 8000 |
| [Linza-storage-service](https://github.com/BigDataQueen/Linza-storage-service) | Работа с файлами, S3-хранилище | 8001 |
| **linza-analytics** (этот) | Классификатор нарушений, отчёты | 8002 |
| [linza-vpleer](https://github.com/BigDataQueen/linza-vpleer) | Видеоплеер | 8003 |
| [Linza-deploy](https://github.com/BigDataQueen/Linza-deploy) | Сборка и развёртывание | — |

## Функционал

### Классификатор нарушений
Система классифицирует 21 тип нарушений по трём уровням возрастных ограничений:

| Категория | Описание | Типы нарушений |
|-----------|----------|----------------|
| **Запрещённый** | Полностью запрещённый контент | KIDSPORN, DRUGS, DRUGS2KIDS, SUICIDE, KIDSSUICIDE, TERROR, EXTREMISM, TERRORCONTENT, LGBT |
| **18+** | Контент для совершеннолетних | NUDE, SEX, CHILDFREE, INOAGENT, INOAGENTCONTENT, ANTIWAR, LUDOMANIA |
| **16+** | Ограничения 16+ | ALCOHOL, SMOKING, VANDALISM, VIOLENCE, OBSCENE_LANGUAGE |

### Иерархия нарушений

Подклассы группируются по 7 родительским классам:

| Родительский класс | Название | Подклассы |
|-------------------|----------|----------|
| SEX | Сексуальный контент | NUDE, SEX, KIDSPORN |
| DRUGS | Наркотики и вредные вещества | ALCOHOL, SMOKING, DRUGS, DRUGS2KIDS |
| DEVIANT | Девиантное поведение | VANDALISM, VIOLENCE, SUICIDE, KIDSSUICIDE, OBSCENE_LANGUAGE |
| TERRORISM | Терроризм и экстремизм | TERROR, EXTREMISM, TERRORCONTENT |
| ANTITRADITIONAL | Антитрадиционные ценности | LGBT, CHILDFREE |
| ANTIPATRIOTIC | Антипатриотический контент | INOAGENT, INOAGENTCONTENT, ANTIWAR |
| LUDOMANIA | Лудомания | LUDOMANIA |

### Управление конфигурацией
- Получение текущей конфигурации категорий
- Обновление привязки подклассов к категориям (bulk update с upsert)
- Сброс к значениям по умолчанию (21 предустановленная запись)
- Валидация: допустимые категории — `prohibited`, `18+`, `16+`

## Структура проекта

```
linza-analytics/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI-приложение, lifespan, CORS
│   ├── db.py                # SQLite: схема, CRUD, значения по умолчанию
│   └── routes/
│       ├── __init__.py
│       └── classifier.py    # REST API классификатора
├── data/
│   └── linza.db             # SQLite-база (создаётся автоматически)
├── requirements.txt          # Python-зависимости
├── Dockerfile                # Python 3.12-slim, порт 8002
└── README.md
```

## Реализация

### `app/main.py` — Точка входа
FastAPI-приложение с `lifespan`-контекстом, который инициализирует базу данных при запуске. Подключает CORS-middleware и роутер `/api/classifier`.

### `app/db.py` — Слой данных (SQLite)

**Схема базы данных:**
```sql
CREATE TABLE classifier_config (
    subclass TEXT PRIMARY KEY,
    category TEXT NOT NULL CHECK(category IN ('prohibited', '18+', '16+'))
)
```

**Функции:**
- `init_db()` — создание таблицы и засеивание значений по умолчанию (если таблица пуста)
- `get_all()` — получение всех записей, отсортированных по `subclass`
- `update_all(items)` — массовое обновление с `INSERT ... ON CONFLICT DO UPDATE` (upsert)
- `seed_defaults()` — пересоздание 21 записи по умолчанию

**Путь к базе данных** настраивается через переменную `DATABASE_PATH`. По умолчанию — `./data/linza.db`. Директория создаётся автоматически при первом запуске.

### `app/routes/classifier.py` — REST API

**`GET /api/classifier`** — Получение конфигурации
- Возвращает массив объектов `{ subclass, category }`
- Данные отсортированы по имени подкласса

**`PUT /api/classifier`** — Обновление конфигурации
- Принимает массив `[{ subclass: "NUDE", category: "18+" }, ...]`
- Валидация: категория должна быть `prohibited`, `18+` или `16+`
- При ошибке возвращает `400` с описанием невалидной записи
- Upsert: если подкласс существует — обновляет, если нет — создаёт

**`PUT /api/classifier/reset`** — Сброс к умолчаниям
- Удаляет все записи и создаёт 21 запись по умолчанию
- Возвращает обновлённую конфигурацию

**`GET /api/classifier/audit`** — Аудит-лог изменений
- Возвращает историю изменений конфигурации (newest first)
- Query-параметры: `subclass`, `action` (`update`/`reset`), `limit` (1–500, default 50), `offset`
- Каждая запись: `{ id, timestamp, request_id, action, subclass, old_category, new_category }`
- Записываются только реальные изменения (no-op PUT не создаёт записей)
- Audit пишется в одной транзакции с мутацией конфигурации

## Стек технологий

| Компонент | Технология | Версия |
|-----------|-----------|--------|
| Фреймворк | FastAPI | 0.115.5 |
| ASGI-сервер | Uvicorn | 0.32.1 |
| База данных | SQLite 3 | встроенная |
| Runtime | Python | 3.12 |

## Переменные окружения

| Переменная | Описание | По умолчанию |
|-----------|----------|-------------|
| `DATABASE_PATH` | Путь к файлу базы данных SQLite | `./data/linza.db` |
| `ERROR_TRACKER_URL` | URL error-tracker сервиса | `http://localhost:8004` |
| `CORS_ORIGINS` | Разрешённые CORS-источники (через запятую) | `http://localhost:5173` |
| `SERVICE_API_KEY` | Ключ межсервисной аутентификации | — |

## Запуск

### Разработка

```bash
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8002
```

### Docker

```bash
docker build -t linza-analytics .
docker run -p 8002:8002 -v linza-analytics-data:/app/data linza-analytics
```

## API

| Метод | Endpoint | Описание |
|-------|----------|----------|
| GET | `/api/classifier` | Получить конфигурацию категорий |
| PUT | `/api/classifier` | Обновить привязку подклассов к категориям |
| PUT | `/api/classifier/reset` | Сбросить к значениям по умолчанию |
| GET | `/api/classifier/audit` | Аудит-лог изменений (фильтры: subclass, action, limit, offset) |
| GET | `/health` | Проверка состояния сервиса |

### Пример — получение конфигурации

```bash
curl http://localhost:8002/api/classifier
```

Ответ:
```json
[
  { "subclass": "ALCOHOL", "category": "16+" },
  { "subclass": "ANTIWAR", "category": "18+" },
  { "subclass": "CHILDFREE", "category": "18+" },
  { "subclass": "DRUGS", "category": "prohibited" },
  ...
]
```

### Пример — обновление категорий

```bash
curl -X PUT http://localhost:8002/api/classifier \
  -H "Content-Type: application/json" \
  -d '[
    { "subclass": "NUDE", "category": "prohibited" },
    { "subclass": "ALCOHOL", "category": "18+" }
  ]'
```

### Пример — сброс к значениям по умолчанию

```bash
curl -X PUT http://localhost:8002/api/classifier/reset
```

### Пример — просмотр аудит-лога

```bash
# Все изменения (последние 50)
curl http://localhost:8002/api/classifier/audit

# Фильтр по подклассу
curl "http://localhost:8002/api/classifier/audit?subclass=NUDE&limit=10"
```

Ответ:
```json
[
  {
    "id": 3,
    "timestamp": "2026-04-03T15:30:01.123Z",
    "request_id": "abc12345",
    "action": "update",
    "subclass": "NUDE",
    "old_category": "18+",
    "new_category": "prohibited"
  }
]
```
