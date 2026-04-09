# CLAUDE.md — Linza Board

## Описание сервиса
Linza Board — клиентское приложение Linza Detector. Vue.js SPA + FastAPI backend.
Порт: 8000. Роль: UI, авторизация, управление пользователями, настройки хранилищ, аналитика, отслеживание ошибок.

## Критические правила
- **НЕ удалять и НЕ менять** существующие компоненты при добавлении новых
- **НЕ менять** API-контракты существующих эндпоинтов без обновления всех клиентов
- **bcrypt==4.0.1** — обязательно, passlib 1.7.4 несовместим с bcrypt>=4.1
- **password[:72]** — обязательно в hash_password/verify_password
- Всегда проверять что ВСЕ imports в router/index.js указывают на существующие файлы
- **Все цвета через CSS-переменные** — никогда не использовать хардкод цветов в компонентах

## Дизайн-система

### Тёмная тема (по умолчанию, `:root` в App.vue)

| Токен | Значение | Назначение |
|-------|----------|-----------|
| `--sidebar-w` | `240px` | Ширина сайдбара |
| `--c-sidebar` | `#0D1B2A` | Фон сайдбара |
| `--c-sidebar-hover` | `#1B2838` | Hover элементов сайдбара |
| `--c-sidebar-active` | `rgba(10,111,255,0.15)` | Активный элемент сайдбара |
| `--c-sidebar-border` | `#1C2D3F` | Разделители сайдбара |
| `--c-bg` | `#0A0F1A` | Фон страницы |
| `--c-surface` | `#111827` | Фон карточек/таблиц |
| `--c-surface-2` | `#1A2332` | Вторичный фон (заголовки таблиц, хедеры) |
| `--c-border` | `#1E293B` | Общие границы |
| `--c-blue` | `#0A6FFF` | Основной акцент |
| `--c-blue-dim` | `rgba(10,111,255,0.12)` | Фон акцента (badge-blue, user-badge) |
| `--c-blue-hover` | `#0855CC` | Hover акцента |
| `--c-teal` | `#14B8A6` | Акцент действий (btn-primary) |
| `--c-teal-bg` | `rgba(20,184,166,0.12)` | Фон акцента действий |
| `--c-txt` | `#F1F5F9` | Основной текст |
| `--c-txt-2` | `#94A3B8` | Вторичный текст |
| `--c-txt-3` | `#475569` | Приглушённый текст |
| `--c-err` | `#F87171` | Ошибки/опасность |
| `--c-err-bg` | `rgba(220,38,38,0.08)` | Фон ошибок |
| `--c-ok` | `#34D399` | Успех |
| `--c-ok-bg` | `rgba(52,211,153,0.08)` | Фон успеха |
| `--c-warn` | `#FBBF24` | Предупреждения |
| `--c-warn-bg` | `rgba(251,191,36,0.08)` | Фон предупреждений |

### Светлая тема (спецификация, `@media (prefers-color-scheme: light)`)

> **Статус:** НЕ реализована в коде. Ниже — спецификация для будущей реализации.

| Токен | Значение | Назначение |
|-------|----------|-----------|
| `--c-sidebar` | `#FFFFFF` | Фон сайдбара |
| `--c-sidebar-hover` | `#F0F0F2` | Hover элементов |
| `--c-sidebar-active` | `rgba(10,111,255,0.08)` | Активный элемент |
| `--c-sidebar-border` | `#E5E7EB` | Разделители |
| `--c-bg` | `#F5F5F7` | Фон страницы |
| `--c-surface` | `#FFFFFF` | Фон карточек/таблиц |
| `--c-surface-2` | `#F0F0F2` | Вторичный фон |
| `--c-border` | `#E5E7EB` | Общие границы |
| `--c-blue` | `#0A6FFF` | Основной акцент (без изменений) |
| `--c-blue-dim` | `rgba(10,111,255,0.06)` | Фон акцента |
| `--c-blue-hover` | `#0855CC` | Hover акцента (без изменений) |
| `--c-teal` | `#0D9488` | Акцент действий |
| `--c-teal-bg` | `rgba(13,148,136,0.08)` | Фон акцента действий |
| `--c-txt` | `#111827` | Основной текст |
| `--c-txt-2` | `#6B7280` | Вторичный текст |
| `--c-txt-3` | `#9CA3AF` | Приглушённый текст |
| `--c-err` | `#DC2626` | Ошибки |
| `--c-err-bg` | `rgba(220,38,38,0.06)` | Фон ошибок |
| `--c-ok` | `#059669` | Успех |
| `--c-ok-bg` | `rgba(5,150,105,0.06)` | Фон успеха |
| `--c-warn` | `#D97706` | Предупреждения |
| `--c-warn-bg` | `rgba(217,119,6,0.06)` | Фон предупреждений |

### Правила дизайна

1. **Все цвета через CSS-переменные** — никогда не использовать хардкод цветов в компонентах
2. **Тема определяется ОС** — при реализации светлой темы использовать `@media (prefers-color-scheme: light)` для переопределения `:root`
3. **Контрастность** — минимум WCAG AA (4.5:1 для текста 13px, 3:1 для крупного текста 18px+)
4. **Шрифты:** `Inter` (основной UI), `Barlow Condensed` (цифры в stat-карточках)
5. **Размеры шрифтов:** 10px (group-title), 11px (badge, label), 12px (secondary), 13px (body), 16px (modal h3), 18px (page-title)
6. **Радиусы скругления:** 3px (user-role badge), 4px (badge, icon-btn, sidebar-logout), 6px (btn, input, alert), 8px (data-table, stat-card), 10px (modal)
7. **Иконки:** Bootstrap Icons SVG, 16x16 (nav), 14x14 (кнопки/footer), `fill="currentColor"`
8. **Badge-классы:** `.badge-ok` (зелёный), `.badge-err` (красный), `.badge-warn` (жёлтый), `.badge-blue` (синий)
9. **Тени:** не используются — дизайн строится на borders (`1px solid var(--c-border)`)
10. **Новые компоненты** обязаны использовать глобальные классы из App.vue: `.btn`, `.btn-primary`, `.btn-danger`, `.btn-sm`, `.data-table`, `.modal`, `.modal-overlay`, `.field`, `.badge`, `.alert`, `.empty-state`, `.page-title`, `.page-toolbar`, `.search-input`

## Реестр функционала (frontend)

### Навигация
- [x] Sidebar с 3 блоками: Рабочий процесс / Настройки / Справка
- [x] Логотип SVG (src/assets/linza-detector-logo.svg)
- [x] Ролевой доступ: Настройки видны только admin/superadmin
- [x] Router guard: managerOnly проверяет роль через /api/auth/me

### Страницы
- [x] LoginPage.vue — авторизация (JWT, localStorage)
- [x] AnalyticsPage.vue — загрузка JSON, таблица нарушений, фильтры, классификатор
- [x] FilesPage.vue — список S3-файлов, загрузка по URL, SSE-прогресс
- [x] ResultsPage.vue — история JSON-отчётов, привязка к файлам, просмотр/удаление
- [x] UsersPage.vue — CRUD пользователей с ролями
- [x] AccessParamsPage.vue — CRUD параметров доступа (домен/логин/пароль)
- [x] SourcesPage.vue — CRUD источников данных (S3/HTTP/SMB)
- [x] StoragePage.vue — профили хранилищ (source/destination), тест подключения
- [x] ErrorTrackingPage.vue — отслеживание ошибок: статистика, фильтры, таблица, отправка в GitHub Issues (Linza-debug)
- [x] InstructionPage.vue — пошаговое руководство
- [x] AboutPage.vue — информация о системе

### Компоненты
- [x] FilterPanel.vue — чекбоксы prohibited/18+/16+, кнопка "Настроить категории", Excel-экспорт
- [x] ClassifierModal.vue — 21 подкласс в 7 группах, маппинг категорий, сброс
- [x] ViolationsTable.vue — сортировка, верификация, цветные бейджи
- [x] FileUpload.vue — загрузка JSON-файлов
- [x] UploadFromUrlModal.vue — загрузка файлов по URL
- [x] VideoPlayer.vue — iframe-интеграция с vpleer, detections base64

### Composables
- [x] useAuth.js — login/logout/fetchMe, getToken, isSuperAdmin, canManageUsers, canAccessSettings
- [x] useDetections.js — loadFromJson, filters, toggleFilter, filteredDetections, categoryCounts, sort
- [x] useClassifier.js — loadConfig/saveConfig/resetConfig, CATEGORIES, SUBCLASS_INFO, CLASS_INFO
- [x] useStorage.js — CRUD профилей хранилищ, testConnection, activateProfile
- [x] useReports.js — CRUD отчётов анализа
- [x] useErrorTracking.js — fetchErrors/fetchStats/clearErrors/submitToGithub/buildGitHubIssueUrl, фильтрация по сервису и серьёзности

## Реестр функционала (backend)

### Модели (backend/models.py)
- [x] User — id, login, password_hash, role (superadmin/admin/user), created_by
- [x] StorageProfile — id, name, profile_type, s3_*, is_active, created_by
- [x] AccessCredential — id, name, domain, login, password_encrypted, workspace
- [x] DataSource — id, name, path_type, path_url, file_extensions, priority, access_credential_id
- [x] AnalysisReport — id, filename, report_name, source, status, report_json, created_by
- [x] ErrorRecord — id, service, severity, category, message, traceback, endpoint, method, status_code, request_id, extra, github_issue_url, status (new/submitted)

### API эндпоинты
- [x] POST /api/auth/login — авторизация
- [x] GET /api/auth/me — текущий пользователь
- [x] GET/POST/DELETE /api/users/ — CRUD пользователей
- [x] GET/POST/PUT/DELETE /api/settings/storage — профили хранилищ
- [x] POST /api/settings/storage/{id}/activate — активация профиля
- [x] POST /api/settings/storage/{id}/test — тест подключения S3
- [x] GET/POST/PUT/DELETE /api/settings/access — параметры доступа
- [x] GET/POST/PUT/DELETE /api/settings/sources — источники данных
- [x] GET/POST/GET/{id}/DELETE /api/reports — отчёты анализа
- [x] GET /api/errors/ — список ошибок с фильтрами (service, severity, limit, offset)
- [x] GET /api/errors/stats — статистика ошибок (total, last_hour, by_service, by_severity)
- [x] POST /api/errors/report — приём ошибок от middleware (без авторизации)
- [x] POST /api/errors/manual — ручное создание отчёта об ошибке (admin+)
- [x] POST /api/errors/{id}/submit-issue — отправка ошибки в GitHub Issues (Linza-debug)
- [x] DELETE /api/errors/ — очистка ошибок (опционально по сервису)

### Middleware
- [x] ErrorReporterMiddleware — перехват HTTP 4xx/5xx и unhandled exceptions, сохранение в локальную БД (error_records) и опциональная отправка во внешний трекер (Linza Debug)

### Зависимости (requirements.txt)
- fastapi==0.115.5
- uvicorn[standard]==0.32.1
- python-jose[cryptography]==3.3.0
- passlib[bcrypt]==1.7.4
- bcrypt==4.0.1
- python-multipart==0.0.20
- sqlalchemy==2.0.36
- alembic>=1.13
- psycopg2-binary>=2.9
- boto3==1.35.85
- httpx>=0.27.0
- python-json-logger>=3.0
- slowapi>=0.1.9

## Взаимодействие сервисов (API)

### Linza Board → Linza Debug (error-tracker)
- **Канал:** ErrorReporterMiddleware → POST {ERROR_TRACKER_URL}/api/errors/report
- **Когда:** при каждом HTTP 4xx/5xx ответе или unhandled exception
- **Payload:** { service, severity, message, traceback, endpoint, method, status_code, request_id, extra }
- **Переменная окружения:** ERROR_TRACKER_URL (опционально, если не задана — только локальная БД)

### Linza Board UI → GitHub Issues (Linza-debug)
- **Канал:** кнопка "GitHub Issue" на странице Отслеживание ошибок → window.open() с pre-filled URL
- **Репозиторий:** BigDataQueen/Linza-debug
- **Формат:** title = "[service] message", body = structured markdown с деталями ошибки
- **После создания:** POST /api/errors/{id}/submit-issue сохраняет URL и меняет статус на "submitted"

## База данных

### Гибридный подход (board#27)

**Production (PostgreSQL):** Alembic миграции (`alembic upgrade head`).
**Dev/Test (SQLite):** `Base.metadata.create_all()` — быстро, без зависимости от PostgreSQL.

Логика выбора в `backend/database.py → run_migrations()`:
- `DATABASE_URL` начинается с `postgresql` → Alembic
- Иначе (sqlite, по умолчанию) → create_all()

### Alembic: создание новой миграции

```bash
# 1. Измени модель в backend/models.py
# 2. Сгенерируй миграцию:
cd linza-board
python -m alembic revision --autogenerate -m "описание изменения"
# 3. Проверь сгенерированный файл в alembic/versions/
# 4. Тест: python -m pytest tests/ -v
# 5. Коммит: миграцию + модель вместе
```

### Alembic: откат миграции

```bash
python -m alembic downgrade -1    # откатить на 1 шаг
python -m alembic current         # текущая версия
python -m alembic history          # история миграций
```

### Docker deployment

PostgreSQL разворачивается как сервис в Linza-deploy. Board подключается через `DATABASE_URL`:
```
DATABASE_URL=postgresql://linza:linza@postgres:5432/linza_board
```

Контейнер board зависит от postgres (healthcheck: `pg_isready`). Миграции применяются автоматически в lifespan при старте приложения.

### Переменные окружения БД

| Переменная | По умолчанию | Описание |
|---|---|---|
| `DATABASE_URL` | `sqlite:///./linza_board.db` | Connection string (SQLite для dev, PostgreSQL для prod) |
| `POSTGRES_USER` | `linza` | PostgreSQL user (docker-compose) |
| `POSTGRES_PASSWORD` | `linza` | PostgreSQL password (docker-compose) |
| `POSTGRES_DB` | `linza_board` | PostgreSQL database name (docker-compose) |
| `CLOUD_DATABASE_URL` | — | Облачный PostgreSQL для резервного копирования (Linza-deploy) |
| `BACKUP_INTERVAL` | `6h` | Интервал резервного копирования (Linza-deploy) |

### Резервное копирование в облачный PostgreSQL

Настройка в `Linza-deploy`:
- `scripts/pg-backup.sh` — pg_dump внутреннего PG → psql restore в облачный
- Сервис `pg-backup` в docker-compose.yml (закомментирован, раскомментировать для включения)
- Подробнее: `Linza-deploy/CLAUDE.md` → "Резервное копирование"

## Прогресс спринтов (актуально на 03.04.2026)

| Спринт | Тема | Статус | Ключевые PR (board) |
|---|---|---|---|
| Sprint 1 | Security Hardening | **DONE** ✅ | #33 (rate limit), #34 (encryption) |
| Sprint 2 | Service Quality | **DONE** ✅ | #35 (lifespan) |
| Sprint 3 | Cross-Service Infra | **DONE** ✅ | #36 (service key), #37 (request-id), #41 (JSON log) |
| Sprint 4 | Data & Storage | **DONE** ✅ | #42 (Alembic/PG), #43 (backup docs) |
| Sprint 5 | Observability | **DONE** ✅ | #44 (uvicorn JSON + request_id + ErrorTrackerHandler) |
| Sprint 6 | Polish & Deploy | **IN PROGRESS** | #46 (light theme + board#40 Variant C) |

Полный roadmap: [board#32](https://github.com/BigDataQueen/linza-board/issues/32)

## Известные ограничения
- ~~SQLite: check_same_thread=False (не работает с PostgreSQL)~~ (решено: условный connect_args в database.py)
- ~~Нет rate-limiting на login~~ (добавлен: slowapi, 5/minute на /api/auth/login)
- ~~Пароли в AccessCredential хранятся plaintext~~ (добавлено: Fernet AES-128 шифрование, env CREDENTIAL_ENCRYPTION_KEY)
- Тесты работают на SQLite (create_all), не на PostgreSQL — при добавлении PostgreSQL-специфичных фич нужно учитывать различия
- **НЕ переопределять filter() на logging.Handler** — ломает addFilter() chain (RequestIDFilter не выполнится)

## Чеклист перед коммитом
1. Все Vue-файлы из router/index.js существуют на диске
2. Все backend routes из main.py существуют в backend/routes/
3. requirements.txt содержит bcrypt==4.0.1
4. FilterPanel + ClassifierModal не удалены из AnalyticsPage
5. useDetections.js содержит toggleFilter и filteredDetections
6. password[:72] в auth.py hash_password/verify_password
7. ErrorRecord модель импортируется в routes/errors.py и доступна для create_all
8. Роутер errors зарегистрирован в main.py с prefix="/api/errors"
9. Все цвета в новых компонентах используют CSS-переменные из дизайн-системы
10. При изменении моделей — сгенерировать Alembic миграцию (`alembic revision --autogenerate`)
11. Миграция и модель коммитятся вместе (никогда не коммитить модель без миграции)
