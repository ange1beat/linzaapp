# CLAUDE.md — Linza Analytics Service

## Описание сервиса
Сервис аналитики Linza Detector. Классификатор нарушений, 21 подкласс, 3 категории.
Порт: 8002. Роль: хранение и управление конфигурацией классификатора.

## Критические правила
- **SQLite WAL + timeout=10** — обязательно в _get_conn()
- **НЕ вкладывать транзакции** — _seed_defaults вызывается внутри `with conn:`, который уже управляет BEGIN/COMMIT
- **Dockerfile: non-root user** — appuser обязателен
- **Конфигурация через app/config.py** — все env vars централизованы, не разбрасывать os.getenv() по модулям
- Subclass валидация: только из VALID_SUBCLASSES (21 значение из DEFAULT_CONFIG)
- **Audit log транзакционный** — audit INSERT обязательно в том же `with conn:` что и мутация config

## Реестр функционала

### API (app/routes/classifier.py)
- [x] GET /api/classifier/ — список всех 21 подклассов с категориями
- [x] PUT /api/classifier/ — обновить маппинг (макс 100 items, валидация subclass + category)
- [x] PUT /api/classifier/reset — сброс к дефолтным значениям
- [x] GET /api/classifier/audit — лог изменений (фильтры: subclass, action, limit, offset)

### Health
- [x] GET /health — {"status": "ok", "service": "analytics-service"}

### База данных (app/db.py)
- [x] SQLite с WAL mode и timeout=10
- [x] Таблица classifier_config: subclass (PK), category (CHECK: prohibited/18+/16+)
- [x] 21 дефолтный подкласс (NUDE, SEX, KIDSPORN, ALCOHOL, SMOKING, etc.)
- [x] Автосидирование при пустой таблице на старте
- [x] Таблица classifier_audit: id (PK autoincrement), timestamp, request_id, action, subclass, old/new_category
- [x] Audit INSERT в той же транзакции (`with conn:`) что и мутация конфигурации

## Подклассы нарушений (DEFAULT_CONFIG)
| Подкласс | Категория по умолчанию |
|---|---|
| NUDE, SEX | 18+ |
| KIDSPORN, DRUGS, DRUGS2KIDS, SUICIDE, KIDSSUICIDE | prohibited |
| TERROR, EXTREMISM, TERRORCONTENT, LGBT | prohibited |
| ALCOHOL, SMOKING, VANDALISM, VIOLENCE, OBSCENE_LANGUAGE | 16+ |
| CHILDFREE, INOAGENT, INOAGENTCONTENT, ANTIWAR, LUDOMANIA | 18+ |

## Зависимости
- fastapi==0.115.5
- uvicorn[standard]==0.32.1
- python-multipart==0.0.20

## Чеклист перед коммитом
1. PRAGMA journal_mode=WAL и timeout=10 в _get_conn()
2. _seed_defaults НЕ содержит явный BEGIN/COMMIT (context manager управляет)
3. VALID_SUBCLASSES генерируется из DEFAULT_CONFIG
4. Field(min_length=1, max_length=50) на subclass в ClassifierItem
5. Dockerfile содержит USER appuser
