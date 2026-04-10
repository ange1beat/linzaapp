# Linza Board

Основное клиентское приложение платформы **Linza Detector** — системы видеоаналитики для обнаружения и классификации нарушений в видеоконтенте.

Репозиторий содержит **Vue.js SPA** (интерфейс проекта), **сервис авторизации** (JWT) и **управление ролями пользователей**.

## Общая архитектура платформы

Linza Detector разделена на независимые сервисы, каждый в своём репозитории:

| Репозиторий | Назначение | Порт |
|-------------|-----------|------|
| **linza-board** (этот) | UI, авторизация, роли пользователей | 8000 |
| [Linza-storage-service](https://github.com/BigDataQueen/Linza-storage-service) | Работа с файлами, S3-хранилище | 8001 |
| [linza-analytics](https://github.com/BigDataQueen/linza-analytics) | Классификатор нарушений, отчёты | 8002 |
| [linza-vpleer](https://github.com/BigDataQueen/linza-vpleer) | Видеоплеер | 8003 |
| [Linza-deploy](https://github.com/BigDataQueen/Linza-deploy) | Сборка и развёртывание | — |

## Функционал

### Авторизация и роли
- JWT-аутентификация с настраиваемым временем жизни токена (по умолчанию 8 часов)
- Суперадмин с конфигурируемыми через переменные окружения учётными данными
- OAuth2 Bearer-схема с автоматическим обновлением
- Route guards — защита маршрутов от неавторизованного доступа
- Хеширование паролей через bcrypt

### Интерфейс — страница «Аналитика» (`/`)
- Загрузка JSON-отчётов с результатами детекции нарушений
- Метаданные видео: длительность, время обработки, дата анализа
- Таблица нарушений с сортировкой по типу, времени, уверенности, категории
- Фильтрация по трём категориям: Запрещённый / 18+ / 16+
- Верификация детекций: подтверждено / требует проверки / ложное срабатывание
- Экспорт в Excel (XLSX) — подтверждённые нарушения или все, если ничего не выбрано

### Интерфейс — страница «Файлы» (`/files`)
- Таблица файлов из S3-хранилища (данные от Linza-storage-service)
- Загрузка файлов по URL с прогрессом в реальном времени (SSE)
- Двухфазная загрузка: скачивание → загрузка в S3
- Отображение статуса: ожидание → скачивание → загрузка → готово/ошибка

### Интерфейс — страница «Вход» (`/login`)
- Форма авторизации с логином и паролем
- Переключение видимости пароля
- Адаптивная вёрстка (мобильная/десктопная)

### Общий UI
- Тёмная и светлая тема (автоопределение через `prefers-color-scheme`)
- Навигационная панель с логотипом LINZA DETECTOR
- Шрифты Inter (интерфейс) и Barlow Condensed (логотип)

## Структура проекта

```
linza-board/
├── src/                          # Vue.js 3 SPA
│   ├── App.vue                  # Корневой компонент с навигацией
│   ├── main.js                  # Инициализация приложения
│   ├── router/index.js          # Маршруты и route guards
│   ├── views/
│   │   ├── LoginPage.vue        # Страница авторизации
│   │   ├── AnalyticsPage.vue    # Страница аналитики
│   │   └── FilesPage.vue        # Страница управления файлами
│   ├── components/
│   │   ├── FileUpload.vue       # Загрузка JSON-отчёта
│   │   ├── FilterPanel.vue      # Фильтры категорий + экспорт
│   │   ├── ViolationsTable.vue  # Таблица нарушений с верификацией
│   │   ├── ClassifierModal.vue  # Настройка категорий нарушений
│   │   └── UploadFromUrlModal.vue # Загрузка файла по ссылке
│   ├── composables/
│   │   ├── useAuth.js           # Логика авторизации, токены
│   │   ├── useClassifier.js     # Классификатор нарушений (20+ типов)
│   │   └── useDetections.js     # Данные детекций, фильтрация, сортировка
│   └── utils/
│       └── exportExcel.js       # Генерация XLSX-отчётов
├── backend/                      # FastAPI бэкенд
│   ├── main.py                  # Инициализация FastAPI, CORS, SPA
│   ├── auth.py                  # JWT-токены, проверка паролей
│   └── routes/
│       └── auth.py              # POST /login, GET /me
├── services/                     # Микросервисы (заглушки)
│   ├── auth-service/            # Сервис авторизации (порт 8001)
│   ├── license-service/         # Сервис лицензий (порт 8002)
│   └── license-check/           # Проверка лицензий (порт 8003)
├── docs/architecture/
│   └── ARCHITECTURE.md          # Архитектурная документация
├── Dockerfile                    # Multi-stage: Node.js → Python
├── docker-compose.yml            # Запуск linza-board
├── docker-compose.services.yml   # Инфраструктура (Postgres, Redis)
├── package.json                  # Vue 3, Vite, vue-router, xlsx
├── requirements.txt              # FastAPI, uvicorn, python-jose, passlib
└── vite.config.js               # Прокси к микросервисам
```

## Стек технологий

| Компонент | Технология | Версия |
|-----------|-----------|--------|
| Фронтенд | Vue.js 3 (Composition API) | 3.5.0 |
| Сборка | Vite | 6.0.0 |
| Маршрутизация | Vue Router | 4.4.0 |
| Excel-экспорт | SheetJS (xlsx) | 0.18.5 |
| Бэкенд | FastAPI | 0.115.5 |
| ASGI-сервер | Uvicorn | 0.32.1 |
| JWT | python-jose | 3.3.0 |
| Хеширование | passlib + bcrypt | 1.7.4 |

## Переменные окружения

| Переменная | Описание | По умолчанию |
|-----------|----------|-------------|
| `CORS_ORIGINS` | Разрешённые CORS-источники (через запятую) | `http://localhost:5173` |
| `AUTH_SECRET_KEY` | Секретный ключ для подписи JWT | `linza-board-secret-key-change-in-production` |
| `AUTH_TOKEN_EXPIRE_MINUTES` | Время жизни токена (минуты) | `480` (8 часов) |
| `AUTH_ADMIN_LOGIN` | Логин администратора | `admin` |
| `AUTH_ADMIN_PASSWORD` | Пароль администратора (plain text) | `admin` |
| `AUTH_ADMIN_PASSWORD_HASH` | Bcrypt-хеш пароля (приоритет над plain text) | — |

## Запуск

### Разработка

```bash
# Установка зависимостей
npm install
pip install -r requirements.txt

# Запуск фронтенда (порт 5173) и бэкенда (порт 8000)
npm run dev:all

# Или по отдельности
npm run dev              # Vite dev server
npm run dev:backend      # FastAPI
```

### Docker

```bash
docker build -t linza-board .
docker run -p 8000:8000 \
  -e AUTH_SECRET_KEY=your-secret \
  -e AUTH_ADMIN_PASSWORD=your-password \
  linza-board
```

## API

| Метод | Endpoint | Описание |
|-------|----------|----------|
| POST | `/api/auth/login` | Авторизация (возвращает JWT-токен) |
| GET | `/api/auth/me` | Информация о текущем пользователе |
| GET | `/health` | Проверка состояния сервиса |

## Классификатор нарушений

Система поддерживает 20+ типов нарушений, сгруппированных по 7 классам:

| Класс | Подклассы |
|-------|----------|
| Сексуальный контент | NUDE, SEX, KIDSPORN |
| Наркотики и вредные вещества | ALCOHOL, SMOKING, DRUGS, DRUGS2KIDS |
| Девиантное поведение | VANDALISM, VIOLENCE, SUICIDE, KIDSSUICIDE, OBSCENE_LANGUAGE |
| Терроризм и экстремизм | TERROR, EXTREMISM, TERRORCONTENT |
| Антитрадиционные ценности | LGBT, CHILDFREE |
| Антипатриотический контент | INOAGENT, INOAGENTCONTENT, ANTIWAR |
| Лудомания | LUDOMANIA |

Каждый подкласс имеет настраиваемую категорию: **Запрещённый**, **18+** или **16+**.
