# Linza Platform — Инструкция администратора (SuperAdmin)

## 1. Роли и права доступа

### Системные роли (legacy)

| Роль | Код | Права |
|------|-----|-------|
| **SuperAdmin** | `superadmin` | Полный доступ. Все операции без ограничений. |
| **Admin** | `admin` | Управление пользователями (своими), настройки. |
| **User** | `user` | Только просмотр и базовая работа. |

### Портальные роли (PRD)

| Роль | Код | Назначение | Автоматический маппинг |
|------|-----|-----------|----------------------|
| Администратор | `administrator` | Org config, пользователи, команды, хранилище | superadmin → ✅, admin → ✅ |
| Оператор | `operator` | Файлы, анализ, очередь | superadmin → ✅, admin → ✅, user → ✅ |
| Юрист | `lawyer` | Рассмотрение эскалированного контента | superadmin → ✅ |
| Главный редактор | `chief_editor` | Метрики, маркировка, команда | superadmin → ✅ |

**SuperAdmin** автоматически получает **все 4 портальные роли**.

### Переключение ролей

- Активная роль определяет контекст интерфейса
- Переключение: `POST /api/auth/switch-role { "active_role": "lawyer" }`
- JWT пересоздаётся с обновлённым полем `ar` (active_role)

---

## 2. JWT-токены

### Структура payload

```json
{
  "sub": "admin",
  "role": "superadmin",
  "pr": ["administrator", "operator", "lawyer", "chief_editor"],
  "ar": "administrator",
  "tid": 1,
  "gid": null,
  "exp": 1744820400
}
```

| Поле | Тип | Описание |
|------|-----|----------|
| `sub` | string | Логин пользователя |
| `role` | string | Legacy-роль (superadmin/admin/user) |
| `pr` | string[] | Портальные роли |
| `ar` | string | Активная портальная роль |
| `tid` | int\|null | ID тенанта |
| `gid` | int\|null | ID команды |
| `exp` | int | Время истечения (Unix timestamp) |

### Параметры

| Параметр | Переменная окружения | По умолчанию |
|----------|---------------------|-------------|
| Секретный ключ | `AUTH_SECRET_KEY` | `linza-board-secret-key-change-in-production` |
| Алгоритм | — | HS256 |
| TTL | `AUTH_TOKEN_EXPIRE_MINUTES` | 480 мин (8 часов) |

**ВАЖНО:** В production ОБЯЗАТЕЛЬНО сменить `AUTH_SECRET_KEY`.

---

## 3. Управление тенантами (организациями)

### Что такое тенант

Тенант — это организация/компания. Все пользователи, команды и проекты привязаны к тенанту. При первом запуске создаётся **Default Organization** (slug: `default`).

### API

| Операция | Метод | Путь | Доступ |
|----------|-------|------|--------|
| Мой тенант | GET | `/api/tenants/my` | Любой авторизованный |
| Список | GET | `/api/tenants/` | Admin+ |
| Создать | POST | `/api/tenants/` | Admin+ |
| Обновить | PATCH | `/api/tenants/{id}` | Admin+ |
| Удалить | DELETE | `/api/tenants/{id}` | **SuperAdmin only** |

### Создание тенанта

```bash
curl -X POST http://localhost:8000/api/tenants/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name": "Новая организация", "slug": "new-org"}'
```

Если `slug` не указан, генерируется автоматически из имени.

---

## 4. Управление пользователями

### Создание пользователя

```bash
curl -X POST http://localhost:8000/api/users/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "first_name": "Иван",
    "last_name": "Петров",
    "login": "ipetrov",
    "password": "SecurePass123!",
    "email": "ivan@company.ru",
    "role": "user",
    "portal_roles": ["operator"]
  }'
```

**Ограничения:**
- Только **SuperAdmin** может создавать пользователей с ролью `admin`
- `password` хешируется bcrypt (усечение до 72 байт)
- `portal_roles` — JSON-массив допустимых ролей: `administrator`, `operator`, `lawyer`, `chief_editor`

### Поиск пользователей

```bash
curl -X POST http://localhost:8000/api/users/search \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "searchTerm": "Иван",
    "pageSize": 10,
    "pageNumber": 1,
    "excludeIds": ["1"]
  }'
```

Ответ: `{ "users": [...], "total": 15 }`

### Смена роли пользователя

```bash
curl -X PATCH http://localhost:8000/api/users/5/roles \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"isSupervisor": true}'
```

Маппинг: `isSupervisor: true` → portal_roles `["administrator", "operator"]`

### Удаление пользователя

```bash
curl -X DELETE http://localhost:8000/api/users/5 \
  -H "Authorization: Bearer $TOKEN"
```

**Нельзя удалить SuperAdmin.**

---

## 5. Управление командами

### Создание

```bash
curl -X POST http://localhost:8000/api/teams/ \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"name": "Отдел аналитики"}'
```

Команда автоматически привязывается к тенанту текущего пользователя.

### Добавление участников

```bash
curl -X POST http://localhost:8000/api/teams/1/members \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"user_ids": [2, 3, 5]}'
```

Пользователь должен принадлежать тому же тенанту.

### Удаление команды

При удалении команды все пользователи отвязываются (team_id → null), но не удаляются.

---

## 6. Управление проектами

### Создание

```bash
curl -X POST http://localhost:8000/api/projects/ \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"name": "Анализ Q1 2026"}'
```

Создатель автоматически становится **owner**.

### Иерархия доступа

Доступ к проекту проверяется в следующем порядке:
1. **SuperAdmin** → доступ ко всем проектам
2. **Владелец** (created_by) → полный доступ
3. **Участник** (project_members) → по роли (owner/editor/viewer)
4. **Шеринг с пользователем** (project_shares type=user)
5. **Шеринг с командой** (project_shares type=team)
6. **Шеринг с организацией** (project_shares type=tenant)
7. **Тот же тенант** → доступ на чтение

### Шеринг проекта

```bash
# Поделиться с пользователем
curl -X POST http://localhost:8000/api/projects/1/share \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"share_type": "user", "share_target_id": 5, "permission": "edit"}'

# Поделиться с командой
curl -X POST http://localhost:8000/api/projects/1/share \
  -d '{"share_type": "team", "share_target_id": 2, "permission": "view"}'

# Поделиться с организацией
curl -X POST http://localhost:8000/api/projects/1/share \
  -d '{"share_type": "tenant", "share_target_id": 1, "permission": "view"}'
```

---

## 7. Квоты хранилища

### Иерархия

```
Организация (tenant) → Команда (team) → Пользователь (user)
       10 GB              5 GB              1 GB
```

При загрузке файла проверяются **все три уровня**. Если хотя бы один исчерпан — upload отклоняется (HTTP 413).

### Установка квоты

```bash
# Квота для организации: 10 GB
curl -X POST http://localhost:8000/api/storage/quotas \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"scope_type": "tenant", "scope_id": 1, "quota_bytes": 10737418240}'

# Квота для команды: 5 GB
curl -X POST http://localhost:8000/api/storage/quotas \
  -d '{"scope_type": "team", "scope_id": 1, "quota_bytes": 5368709120}'

# Квота для пользователя: 1 GB
curl -X POST http://localhost:8000/api/storage/quotas \
  -d '{"scope_type": "user", "scope_id": 5, "quota_bytes": 1073741824}'
```

### Просмотр использования

```bash
curl http://localhost:8000/api/storage/usage \
  -H "Authorization: Bearer $TOKEN"
```

Ответ:
```json
{
  "user": {"id": 1, "scope_type": "user", "scope_id": 5, "quota_bytes": 1073741824, "used_bytes": 524288000},
  "team": {"id": 2, "scope_type": "team", "scope_id": 1, "quota_bytes": 5368709120, "used_bytes": 2147483648},
  "tenant": {"id": 3, "scope_type": "tenant", "scope_id": 1, "quota_bytes": 10737418240, "used_bytes": 4294967296}
}
```

### scope_type

| Тип | scope_id | Описание |
|-----|----------|----------|
| `tenant` | tenants.id | Квота организации |
| `team` | teams.id | Квота команды |
| `user` | users.id | Квота пользователя |

---

## 8. OTP-авторизация (2FA)

### Параметры

| Параметр | Значение |
|----------|----------|
| Длина кода | 6 цифр |
| TTL | 10 минут |
| Хеширование | bcrypt (как пароль) |
| Rate limit | 5 challenge/мин, 10 verify/мин |

### Flow

```
POST /api/auth { login, password }
  → Проверка credentials (bcrypt)
  → Генерация OTP (secrets.randbelow)
  → Хеширование OTP (bcrypt)
  → Сохранение в otp_challenges
  → Response: { user, stateToken }

POST /api/auth/factors/otp/verify { stateToken, passcode }
  → Загрузка challenge по stateToken
  → Проверка expiry
  → Верификация OTP (bcrypt verify)
  → verified = True
  → Response: { user, stateToken }

POST /api/auth/sign-in { stateToken }
  → Проверка verified = True
  → Генерация JWT
  → Удаление challenge из БД
  → Response: { accessToken }
```

### Мониторинг

OTP-коды логируются в dev-режиме:
```
INFO linza.auth: OTP for user@example.com: 123456 (dev only)
```

**В production необходимо подключить email/SMS-сервис.**

---

## 9. Переменные окружения

| Переменная | По умолчанию | Описание |
|-----------|-------------|----------|
| `AUTH_SECRET_KEY` | `linza-board-secret-key-change-in-production` | JWT секретный ключ |
| `AUTH_TOKEN_EXPIRE_MINUTES` | `480` | TTL токена (минуты) |
| `AUTH_ADMIN_LOGIN` | `admin` | Логин SuperAdmin |
| `AUTH_ADMIN_PASSWORD` | `admin` | Пароль SuperAdmin |
| `AUTH_ADMIN_EMAIL` | `admin@linza.local` | Email SuperAdmin |
| `DATABASE_URL` | `sqlite:///./linza_board.db` | БД (sqlite/postgresql) |
| `CORS_ORIGINS` | `http://localhost:5173` | Разрешённые CORS origins |
| `ERROR_TRACKER_URL` | — | URL Linza Debug (опционально) |
| `SERVICE_API_KEY` | — | Ключ межсервисной авторизации |
| `CREDENTIAL_ENCRYPTION_KEY` | auto | Fernet ключ шифрования credentials |
| `STORAGE_SERVICE_URL` | auto | URL storage-service |
| `ANALYTICS_SERVICE_URL` | auto | URL analytics-service |
| `VPLEER_SERVICE_URL` | auto | URL vpleer-service |

---

## 10. База данных

### Миграции

**PostgreSQL (production):**
```bash
cd linza-board
python -m alembic upgrade head
```

**SQLite (development):**
Миграции применяются автоматически при запуске (`Base.metadata.create_all()`).

### Откат

```bash
python -m alembic downgrade -1     # откатить на 1 шаг
python -m alembic current          # текущая версия
python -m alembic history          # история
```

### Таблицы (полный список)

| Таблица | Модуль | Описание |
|---------|--------|----------|
| `tenants` | multi-tenancy | Организации/компании |
| `teams` | multi-tenancy | Команды внутри организации |
| `users` | auth | Пользователи (расширена: tenant, team, storage, profile) |
| `projects` | projects | Проекты с tenant scope |
| `project_members` | projects | Участники проекта (owner/editor/viewer) |
| `project_shares` | projects | Полиморфный шеринг (user/team/tenant) |
| `report_shares` | projects | Шеринг отчётов |
| `user_favorite_projects` | projects | Избранные проекты |
| `storage_quotas` | storage | Иерархические квоты (scope_type + scope_id) |
| `otp_challenges` | auth | OTP-коды для 2FA |
| `storage_profiles` | storage | S3 профили подключения |
| `access_credentials` | settings | Шифрованные credentials (Fernet) |
| `data_sources` | settings | Источники данных (S3/HTTP/SMB) |
| `analysis_reports` | reports | Результаты видеоанализа |
| `video_analysis_queue` | analysis | Очередь анализа |
| `error_records` | errors | Централизованные ошибки |
| `app_settings` | portal | Key-value настройки приложения |
| `yandex_oauth_states` | oauth | Yandex OAuth state |
| `user_yandex_disk_tokens` | oauth | Yandex Disk токены |
| `google_oauth_states` | oauth | Google OAuth state |
| `user_google_drive_tokens` | oauth | Google Drive токены |

### Seed-данные

При первом запуске автоматически:
1. Создаётся Default Organization (tenant slug: `default`)
2. Создаётся SuperAdmin пользователь (из env vars)
3. SuperAdmin привязывается к Default Organization

---

## 11. API-справочник

### Аутентификация

| Метод | Путь | Описание | Доступ |
|-------|------|----------|--------|
| POST | `/api/auth` | Login → stateToken (compat) | Public |
| POST | `/api/auth/login` | Login → access_token (direct) | Public |
| POST | `/api/auth/factors/otp/challenge/email` | Resend OTP email | Public |
| POST | `/api/auth/factors/otp/challenge/sms` | Resend OTP SMS | Public |
| POST | `/api/auth/factors/otp/verify` | Verify OTP | Public |
| POST | `/api/auth/sign-in` | stateToken → accessToken | Public |
| POST | `/api/auth/token` | Refresh token | Auth |
| POST | `/api/auth/sign-out` | Logout | Auth |
| POST | `/api/auth/switch-role` | Switch portal role | Auth |
| GET | `/api/auth/me` | Current user profile | Auth |

### Пользователи

| Метод | Путь | Описание | Доступ |
|-------|------|----------|--------|
| GET | `/api/users/` | Список пользователей | Admin+ |
| POST | `/api/users/` | Создать пользователя | Admin+ |
| POST | `/api/users/search` | Поиск с пагинацией | Auth |
| GET | `/api/users/me` | Мой профиль | Auth |
| GET | `/api/users/{id}` | Профиль по ID | Auth |
| PATCH | `/api/users/{id}` | Обновить | Admin+ |
| DELETE | `/api/users/{id}` | Удалить | Admin+ |
| PUT | `/api/users/me/name` | Изменить имя | Auth |
| PUT | `/api/users/me/password` | Изменить пароль | Auth |
| PUT | `/api/users/me/telegram` | Изменить Telegram | Auth |
| PUT | `/api/users/me/avatar` | Загрузить аватар | Auth |
| PATCH | `/api/users/{id}/roles` | Смена роли | Admin+ |

### Тенанты / Команды / Проекты / Хранилище

Полный список: см. HTML-документацию (`linza-admin-dashboard-update.html`).

---

## 12. Безопасность: чеклист для production

- [ ] Сменить `AUTH_SECRET_KEY` на случайную строку ≥ 32 символа
- [ ] Сменить `AUTH_ADMIN_PASSWORD` на сложный пароль
- [ ] Установить `DATABASE_URL` на PostgreSQL
- [ ] Настроить `CORS_ORIGINS` (убрать localhost)
- [ ] Включить HTTPS (через reverse proxy)
- [ ] Настроить `CREDENTIAL_ENCRYPTION_KEY` (для AccessCredential)
- [ ] Подключить email/SMS-сервис для OTP
- [ ] Настроить `ERROR_TRACKER_URL` для Linza Debug
- [ ] Настроить `SERVICE_API_KEY` для межсервисной авторизации
- [ ] Проверить bcrypt==4.0.1 в requirements.txt
