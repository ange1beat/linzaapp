# Linza-start

Единый архив для сборки и развёртывания платформы **Linza Detector** на локальной машине.

## Требования

- **Docker** (Desktop или Engine) — версия 20+
- **Git** — для клонирования исходного кода
- ~2 ГБ свободного места на диске

## Быстрый старт (3 команды)

```bash
# 1. Скачать
git clone https://github.com/BigDataQueen/Linza-deploy.git
cd Linza-deploy/Linza-start

# 2. Создать .env с вашими S3-ключами (одна команда)
cat > .env << 'EOF'
AUTH_SECRET_KEY=linza-secret-change-in-production
AUTH_ADMIN_LOGIN=admin
AUTH_ADMIN_PASSWORD=admin
S3_ACCESS_KEY_ID=ваш-ключ-доступа
S3_SECRET_ACCESS_KEY=ваш-секретный-ключ
S3_ENDPOINT_URL=https://s3.cloud.ru
S3_BUCKET_NAME=linzadata
S3_REGION=ru-central-1
EOF

# 3. Собрать и запустить
chmod +x start.sh
./start.sh
```

Скрипт автоматически:
1. Клонирует 5 репозиториев (linza-board, Linza-storage-service, linza-analytics, linza-vpleer, Linza-debug)
2. Собирает единый Docker-образ `linza-detector:latest` (~3-5 минут)
3. Запускает контейнер на порту 80

После запуска:
- Откройте http://localhost
- Логин: `admin` / `admin`

> **Важно:** `docker run linza-detector` и `docker build .` напрямую НЕ работают!
> Образ собирается из исходников 5 репозиториев. Только `start.sh` корректно
> формирует build context (клонирует репозитории → собирает → запускает).

## Альтернативный способ создания .env

Если предпочитаете редактор:
```bash
cp .env.example .env
nano .env   # или vim .env — заменить S3_ACCESS_KEY_ID и S3_SECRET_ACCESS_KEY
```

Или через `sed`:
```bash
cp .env.example .env && sed -i \
  -e 's/^S3_ACCESS_KEY_ID=.*/S3_ACCESS_KEY_ID=ваш-ключ/' \
  -e 's/^S3_SECRET_ACCESS_KEY=.*/S3_SECRET_ACCESS_KEY=ваш-секрет/' \
  .env
```

## URL-адреса

| Страница | URL |
|---|---|
| Платформа (UI) | http://localhost |
| Видеоплеер | http://localhost/api/vpleer/player |
| API документация | http://localhost/api/vpleer/docs |
| Отслеживание ошибок | http://localhost → Настройки → Отслеживание ошибок |

## Команды

```bash
./start.sh                    # Полная сборка и запуск
./start.sh --build-only       # Только собрать Docker-образ
./start.sh --run-only         # Только запустить (образ уже собран)
./start.sh --compose          # Запуск через docker-compose (для разработки)
./start.sh --stop             # Остановить
./start.sh --status           # Проверить статус сервисов
./start.sh --port 8080        # Запустить на порту 8080
./start.sh --branch develop   # Собрать из ветки develop
```

## Подробная инструкция по развёртыванию

### Вариант 1: Единый контейнер (рекомендуется)

Все 5 сервисов + Nginx API Gateway в одном Docker-контейнере.

#### Шаг 1. Установите Docker

**macOS:**
```bash
brew install --cask docker
# или скачайте Docker Desktop: https://www.docker.com/products/docker-desktop
```

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install -y docker.io docker-compose-plugin
sudo usermod -aG docker $USER
# Перезайдите в терминал после добавления в группу
```

**Windows:**
Скачайте и установите [Docker Desktop](https://www.docker.com/products/docker-desktop).

#### Шаг 2. Клонируйте и настройте

```bash
git clone https://github.com/BigDataQueen/Linza-deploy.git
cd Linza-deploy/Linza-start

# Создать .env одной командой (замените ключи на свои):
cat > .env << 'EOF'
AUTH_SECRET_KEY=linza-secret-change-in-production
AUTH_ADMIN_LOGIN=admin
AUTH_ADMIN_PASSWORD=admin
S3_ACCESS_KEY_ID=ваш-ключ-доступа
S3_SECRET_ACCESS_KEY=ваш-секретный-ключ
S3_ENDPOINT_URL=https://s3.cloud.ru
S3_BUCKET_NAME=linzadata
S3_REGION=ru-central-1
EOF
```

#### Шаг 3. Соберите и запустите

```bash
chmod +x start.sh
./start.sh
```

Вывод после успешного запуска:
```
=============================================
  Linza Detector запущен!
=============================================
  Платформа:       http://localhost
  Видеоплеер:      http://localhost/api/vpleer/player
  Ошибки (UI):     http://localhost → Настройки → Отслеживание ошибок

  Логин:           admin / admin

  Статус:          ./start.sh --status
  Остановка:       ./start.sh --stop
  Логи:            docker logs -f linza
=============================================
```

### Вариант 2: Docker Compose (для разработки)

Каждый сервис в отдельном контейнере + MinIO (локальный S3).

```bash
cd Linza-deploy/Linza-start
cat > .env << 'EOF'
S3_ACCESS_KEY_ID=minioadmin
S3_SECRET_ACCESS_KEY=minioadmin
S3_ENDPOINT_URL=http://minio:9000
S3_BUCKET_NAME=linzadata
S3_REGION=ru-central-1
MINIO_ROOT_USER=minioadmin
MINIO_ROOT_PASSWORD=minioadmin
EOF

./start.sh --compose
```

Дополнительные порты в режиме compose:

| Сервис | Порт | Описание |
|---|---|---|
| MinIO Console | http://localhost:9001 | Локальное S3 хранилище |
| Board | http://localhost:8000 | UI + Auth + Errors API |
| Storage | http://localhost:8001 | Работа с S3 файлами |
| Analytics | http://localhost:8002 | Классификатор нарушений |
| VPleer | http://localhost:8003 | Видеоплеер |
| Error Tracker | http://localhost:8004 | Внешний сервис ошибок |
| Nginx Gateway | http://localhost:80 | API Gateway |

### Вариант 3: Ручная сборка (без start.sh)

```bash
# Клонировать все репозитории в одну директорию
mkdir linza && cd linza
git clone https://github.com/BigDataQueen/linza-board.git
git clone https://github.com/BigDataQueen/Linza-storage-service.git
git clone https://github.com/BigDataQueen/linza-analytics.git
git clone https://github.com/BigDataQueen/linza-vpleer.git
git clone https://github.com/BigDataQueen/Linza-debug.git
git clone https://github.com/BigDataQueen/Linza-deploy.git

# Скопировать файлы сборки
cp Linza-deploy/Linza-start/Dockerfile .
cp Linza-deploy/Linza-start/entrypoint.sh .
mkdir -p nginx
cp Linza-deploy/Linza-start/nginx-standalone.conf nginx/

# Собрать образ
docker build -t linza-detector:latest .

# Запустить (только после сборки!)
docker run -d --name linza -p 80:80 \
  -e AUTH_ADMIN_LOGIN=admin \
  -e AUTH_ADMIN_PASSWORD=admin \
  -e S3_ACCESS_KEY_ID=your-key \
  -e S3_SECRET_ACCESS_KEY=your-secret \
  linza-detector:latest
```

## Отслеживание ошибок

Платформа включает встроенную систему отслеживания ошибок:

1. **Автоматический сбор** — ErrorReporterMiddleware перехватывает HTTP 4xx/5xx ошибки и необработанные исключения
2. **Просмотр в UI** — раздел Настройки → Отслеживание ошибок (требуется роль admin/superadmin)
3. **Ручной отчёт** — кнопка «Создать отчёт» открывает форму с полями: сервис, серьёзность, категория, описание
4. **Отправка в GitHub** — из интерфейса можно отправить ошибку как Issue в [BigDataQueen/Linza-debug](https://github.com/BigDataQueen/Linza-debug/issues)

## Экспорт / импорт образа

```bash
# Экспорт (для переноса на машину без интернета)
docker save linza-detector:latest | gzip > linza-detector.tar.gz

# Импорт на другой машине
docker load < linza-detector.tar.gz
cd Linza-deploy/Linza-start
./start.sh --run-only
```

## Переменные окружения (.env)

| Переменная | Описание | По умолчанию | Обязательная |
|---|---|---|---|
| `S3_ACCESS_KEY_ID` | Ключ доступа S3 | — | да |
| `S3_SECRET_ACCESS_KEY` | Секретный ключ S3 | — | да |
| `S3_ENDPOINT_URL` | URL S3-хранилища | `https://s3.cloud.ru` | нет |
| `S3_BUCKET_NAME` | Имя бакета | `linzadata` | нет |
| `S3_REGION` | Регион S3 | `ru-central-1` | нет |
| `AUTH_SECRET_KEY` | Секрет для JWT токенов | `linza-secret-...` | нет |
| `AUTH_ADMIN_LOGIN` | Логин администратора | `admin` | нет |
| `AUTH_ADMIN_PASSWORD` | Пароль администратора | `admin` | нет |
| `MINIO_ROOT_USER` | MinIO логин (compose) | `minioadmin` | нет |
| `MINIO_ROOT_PASSWORD` | MinIO пароль (compose) | `minioadmin` | нет |

## Архитектура

```
┌──────────────────────────────────────────────────────────┐
│                    Nginx Gateway (:80)                    │
├───────────┬───────────┬───────────┬───────────┬──────────┤
│   Board   │  Storage  │ Analytics │  VPleer   │  Error   │
│  :8000    │  :8001    │  :8002    │  :8003    │ Tracker  │
│  UI+Auth  │  S3 Files │Classifier │  Player   │  :8004   │
│  Vue.js   │  boto3    │  SQLite   │  ffmpeg   │  SQLite  │
│ +ErrorsAPI│           │           │           │          │
└───────────┴─────┬─────┴───────────┴───────────┴──────────┘
                  │
            ┌─────┴─────┐
            │ S3 / MinIO │
            └───────────┘
```

## Содержимое архива

```
Linza-start/
├── start.sh              # Главный скрипт (сборка + запуск)
├── Dockerfile            # Multi-stage Docker build (единый образ)
├── entrypoint.sh         # Запуск 5 uvicorn + nginx внутри контейнера
├── nginx-standalone.conf # Nginx конфиг для единого контейнера
├── docker-compose.yml    # Альтернатива: сервисы по отдельности
├── nginx/nginx.conf      # Nginx конфиг для docker-compose
├── .env.example          # Шаблон переменных окружения
└── README.md             # Этот файл
```

## Устранение неполадок

**Контейнер не запускается:**
```bash
docker logs linza
```

**Сервис не отвечает:**
```bash
./start.sh --status
```

**Пересборка после изменений:**
```bash
./start.sh --stop
./start.sh
```

**Нет доступа к S3:**
Проверьте ключи в `.env` файле. Для локальной разработки используйте MinIO:
```bash
./start.sh --compose  # поднимет MinIO на localhost:9001
```

**`docker run linza-detector` не работает:**
Образ нужно сначала собрать. Используйте `./start.sh` или `./start.sh --build-only`.
`docker run` работает только после сборки образа (см. Вариант 3).
