# CLAUDE.md — Linza Debug (Error Tracker)

## Описание сервиса
Централизованный трекер ошибок для платформы Linza. Принимает отчёты от всех микросервисов.
Порт: 8004. Роль: сбор, хранение, фильтрация и статистика ошибок.

## Критические правила
- **category** определяется через `infer_category()` — auto-inference по service name, explicit override при наличии
- **SQLite: check_same_thread=False** — обязательно в connect_args
- **ALTER TABLE миграция** при добавлении колонок — `create_all` не добавляет к существующим таблицам
- Все сервисы шлют ошибки на POST /api/errors/report — backward-compatible (category optional)

## Реестр функционала

### API (error-tracker/app/main.py)
- [x] POST /api/errors/report — приём ошибок от микросервисов (auto-category inference)
- [x] GET /api/errors — список ошибок с фильтрами (service, severity, category)
- [x] GET /api/dashboard — статистика (total, last_hour, by_service, by_severity, by_category)
- [x] GET /health — health check

### Модель ErrorRecord
- id, service, severity, category, message, traceback, endpoint, method, status_code, request_id, extra, created_at

## Категории ошибок
| service → category |
|---|
| vpleer → player |
| storage-service → storage |
| analytics-service → analytics |
| linza-board → api |
| unknown → api (default) |

## Чеклист перед коммитом
1. infer_category() используется при создании ErrorRecord
2. SERVICE_CATEGORY_MAP содержит все известные сервисы
3. category присутствует в response GET /api/errors
4. by_category присутствует в GET /api/dashboard
