# Linza VPleer

Сервис видеоплеера платформы **Linza Detector** — системы видеоаналитики для обнаружения нарушений в видеоконтенте.

Обеспечивает воспроизведение видеофайлов, навигацию по временным меткам нарушений и просмотр фрагментов видео с привязкой к результатам анализа.

## Общая архитектура платформы

| Репозиторий | Назначение | Порт |
|-------------|-----------|------|
| [linza-board](https://github.com/BigDataQueen/linza-board) | UI, авторизация, роли пользователей | 8000 |
| [Linza-storage-service](https://github.com/BigDataQueen/Linza-storage-service) | Работа с файлами, S3-хранилище | 8001 |
| [linza-analytics](https://github.com/BigDataQueen/linza-analytics) | Классификатор нарушений, отчёты | 8002 |
| **linza-vpleer** (этот) | Видеоплеер | 8003 |
| [Linza-deploy](https://github.com/BigDataQueen/Linza-deploy) | Сборка и развёртывание | — |

## Схема взаимодействия с внешними сервисами

```
                         ┌──────────────────────┐
                         │    Браузер / UI       │
                         │  (HTML5 + hls.js)     │
                         └──────────┬───────────┘
                                    │
                    HTTP (Range / HLS)
                                    │
                         ┌──────────▼───────────┐
                         │   linza-vpleer :8003  │
                         │                       │
                         │  /stream/{file}       │──── Progressive (MP4, WebM, MOV)
                         │  /hls/{file}/*.m3u8   │──── HLS transcode (AVI, MKV, MXF...)
                         │  /playback-info/{file}│──── Выбор стратегии
                         │  /metadata/{file}     │──── ffprobe по URL
                         │  /timeline            │──── Маркеры нарушений
                         │  /player/{file}       │──── HTML-плеер + панель детекций
                         └──┬──────────┬────────┘
                            │          │
                  ┌─────────▼──┐  ┌────▼────────────┐
                  │  Storage   │  │   Analytics      │
                  │   :8001    │  │     :8002        │
                  │            │  │                   │
                  │ /api/files │  │ /api/classifier   │
                  │ /download  │  │ (категории        │
                  │            │  │  нарушений)       │
                  └─────┬──────┘  └──────────────────┘
                        │
                  ┌─────▼──────┐
                  │  S3 / MinIO │
                  │  (видеофайлы)│
                  └────────────┘
```

**Потоки данных:**
- **Progressive стриминг**: Браузер → VPleer → Storage → S3 (HTTP Range, 1MB chunks)
- **HLS транскодирование**: VPleer запускает ffmpeg, который читает из Storage по URL и генерирует .ts сегменты
- **Метаданные**: ffprobe читает заголовки файла по URL через Storage (без скачивания)
- **Детекции**: Браузер передаёт JSON → VPleer обогащает через Analytics → маркеры на таймлайне

## Функционал

### Потоковое воспроизведение видео
- Проксирование видеофайлов из S3-хранилища через Linza-storage-service
- Поддержка HTTP Range requests для перемотки в больших файлах
- Автоматический выбор стратегии: progressive (MP4, WebM, MOV) или HLS transcode (AVI, MKV, MXF, HEVC, MPEG)

### Поддерживаемые форматы

| Формат | Стратегия | Оптимизация |
|--------|-----------|-------------|
| MP4 (H.264) | Progressive | Мгновенный старт |
| M4V | Progressive | Как MP4 |
| WebM (VP8/VP9) | Progressive | Нативная поддержка браузера |
| MOV (H.264) | Progressive + fallback | HLS если браузер не поддерживает |
| MKV (H.264) | HLS (stream copy) | Переупаковка за секунды |
| MKV (другие кодеки) | HLS (transcode) | ultrafast перекодирование |
| AVI | HLS (transcode) | `-seekable 1` для HTTP |
| MPEG/MPG | HLS (transcode) | Линейное чтение |
| MXF | HLS (transcode) | ProRes/DNxHD → H.264 |
| HEVC (H.265) | HLS (transcode) | Safari: progressive |

### Панель детекций (рецензирование результатов анализа)
- Двухколоночная раскладка: видео (слева) + панель детекций (справа)
- Карточки с таймкодами, subclass, category, confidence
- Подсветка активной детекции при воспроизведении
- Навигация Prev/Next между детекциями (hotkeys `[` `]`)
- Загрузка JSON с детекциями через модальное окно (вставка текста / файл .json)
- Воспроизведение фрагмента интервала (in-player + скачивание)

### Фрагменты видео
- Вырезка фрагмента по временному интервалу `start_time` — `end_time` (через ffmpeg)
- Быстрое извлечение без перекодирования (`-c copy`)

### Превью и метаданные
- Генерация JPEG-превью из произвольного момента видео
- Метаданные через URL (ffprobe читает по HTTP, без скачивания файла)
- Метаданные: длительность, разрешение, кодеки, FPS, битрейт

### Временная шкала нарушений
- Интеграция с linza-analytics для получения конфигурации классификатора
- Обогащение детекций категориями и цветовой кодировкой
- Цвета: запрещённый (красный `#dc3545`), 18+ (оранжевый `#fd7e14`), 16+ (жёлтый `#ffc107`)
- Tooltips при наведении на маркер: subclass, category, confidence, таймкоды

### Дизайн-система и темизация (Фаза C)

Интерфейс плеера построен на CSS custom properties (36 токенов) с поддержкой тёмной и светлой темы. Переключение через кнопку ☾/☀ в заголовке, сохранение в `localStorage`.

**Текущая версия интерфейса (v1 — реализовано):**

| Компонент | Статус | Описание |
|-----------|--------|----------|
| Дизайн-токены | ✅ | 36 CSS custom properties, dark + light |
| Переключение тем | ✅ | ☾/☀ кнопка, localStorage, prefers-color-scheme |
| Двойная дорожка таймлайна | ✅ | 🎬 video (9px) + 🔊 audio (9px), маршрутизация по `source` |
| Группировка мультикласса | ✅ | Перекрывающиеся детекции → групповая карточка с gradient border |
| Обратная связь | ✅ | ✓ confirm / ✗ reject / ↻ reclassify, SVG-иконки Bootstrap Icons |
| Undo / Batch confirm | ✅ | Отмена review + «✓ Все» для массового подтверждения |
| Keyboard shortcuts | ✅ | `[`/`]` навигация, `Y`/`N`/`R` review, `T` тема |

**Цветовая палитра (токены):**

```
Категории (severity):        Фидбек (review):           Источники (резерв):
--cat-prohibited: #dc3545    --feedback-confirm: #22c55e  --source-video: #53c0f0
--cat-18:         #fd7e14    --feedback-reject:  #ef4444  --source-audio: #a855f7
--cat-16:         #ffc107    --feedback-reclass: #f59e0b  --source-both:  #ec4899
```

**Резерв для следующего этапа (v2 — после интеграции сторонних сервисов):**

| Компонент | Токены / API | Что нужно для мержа |
|-----------|-------------|---------------------|
| Цветовая маркировка источников | CSS: `--source-video/audio/both` (заложены в dark + light)<br>API: `source_colors` в ответе `/timeline` | Сторонний сервис начинает передавать `source` в детекциях |
| Панель фильтров (C-6) | — | Достаточный объём данных для фильтрации (>20 детекций) |
| Сводка-статбар (C-7) | — | Реализация C-6 |
| Экспорт с рецензией (C-8) | `review` поле в localStorage | Эндпоинт для сохранения review на бэкенде |

> **Принцип**: CSS-токены и API-поля закладываются заранее, даже если UI-привязка ещё не реализована. Это позволяет сторонним сервисам уже ориентироваться на контракт, а UI-изменения мержить без координации с бэкендом.

### Буферизация и кэширование
- Shared HTTP client с connection pooling (lifespan)
- Таймауты: 30s connect / 3600s read (для файлов 20ГБ+)
- HLS-сегменты кэшируются в /tmp/vpleer/hls/
- Фоновая очистка кэша: TTL 1 час, лимит 50ГБ

## API

| Метод | Endpoint | Описание |
|-------|----------|----------|
| GET | `/health` | Проверка состояния сервиса |
| GET | `/api/vpleer/player` | HTML-страница списка файлов |
| GET | `/api/vpleer/player/{filename}` | HTML-видеоплеер с панелью детекций |
| GET | `/api/vpleer/files` | JSON-список файлов из хранилища |
| GET | `/api/vpleer/stream/{filename}` | Потоковое воспроизведение (Range support) |
| GET | `/api/vpleer/playback-info/{filename}` | Определение стратегии воспроизведения |
| GET | `/api/vpleer/hls/{filename}/playlist.m3u8` | HLS-плейлист (on-demand transcode) |
| GET | `/api/vpleer/hls/{filename}/{segment}` | HLS-сегмент (.ts) |
| GET | `/api/vpleer/fragment?filename=&start=&end=` | Фрагмент видео по интервалу |
| GET | `/api/vpleer/thumbnail/{filename}?time=` | Превью-кадр (JPEG) |
| GET | `/api/vpleer/metadata/{filename}` | Метаданные видеофайла |
| GET | `/api/vpleer/timeline?filename=&detections=` | Временная шкала нарушений (+ `source_colors`) |

### Примеры запросов

```bash
# Открыть плеер в браузере
open http://localhost:8003/api/vpleer/player

# Определить стратегию воспроизведения
curl http://localhost:8003/api/vpleer/playback-info/video.mkv

# Потоковое воспроизведение
curl http://localhost:8003/api/vpleer/stream/video.mp4

# HLS-плейлист для не-MP4 форматов
curl http://localhost:8003/api/vpleer/hls/video.mkv/playlist.m3u8

# Фрагмент с 15.5 по 25.8 секунду
curl "http://localhost:8003/api/vpleer/fragment?filename=video.mp4&start=15.5&end=25.8" -o fragment.mp4

# Превью на 10-й секунде
curl "http://localhost:8003/api/vpleer/thumbnail/video.mp4?time=10" -o thumb.jpg

# Метаданные
curl http://localhost:8003/api/vpleer/metadata/video.mp4

# Временная шкала с детекциями
curl "http://localhost:8003/api/vpleer/timeline?filename=video.mp4&detections=[{\"subclass\":\"NUDE\",\"start_time\":\"00:00:15.500\",\"end_time\":\"00:00:25.800\",\"confidence\":0.95}]"
```

## Структура проекта

```
linza-vpleer/
├── app/
│   ├── __init__.py
│   ├── main.py                  # FastAPI, lifespan (shared client), фоновая очистка
│   ├── config.py                # Конфигурация (URL, таймауты, кэш)
│   ├── routes/
│   │   ├── stream.py            # Стриминг, playback-info, HLS
│   │   ├── metadata.py          # Метаданные и превью
│   │   ├── timeline.py          # Временная шкала нарушений
│   │   └── player.py            # HTML-плеер, панель детекций, hls.js
│   └── services/
│       └── ffmpeg.py            # ffmpeg/ffprobe, HLS генерация
├── tests/
│   ├── conftest.py
│   ├── test_health.py
│   ├── test_player.py
│   ├── test_stream.py
│   └── test_timeline.py
├── devplan.md                   # План разработки
├── requirements.txt
├── Dockerfile
├── CLAUDE.md
└── README.md
```

## Стек технологий

| Компонент | Технология | Версия |
|-----------|-----------|--------|
| Фреймворк | FastAPI | 0.115.5 |
| ASGI-сервер | Uvicorn | 0.32.1 |
| HTTP-клиент | httpx | 0.27.2 |
| Видео | ffmpeg / ffprobe | системный |
| HLS-плеер | hls.js | CDN (latest) |
| Runtime | Python | 3.12 |

## Переменные окружения

| Переменная | Описание | По умолчанию |
|-----------|----------|-------------|
| `CORS_ORIGINS` | Разрешённые CORS-источники (через запятую) | `http://localhost:5173` |
| `STORAGE_SERVICE_URL` | URL сервиса хранения | `http://localhost:8001` |
| `ANALYTICS_SERVICE_URL` | URL сервиса аналитики | `http://localhost:8002` |
| `TEMP_DIR` | Директория для временных файлов и HLS-кэша | `/tmp/vpleer` |
| `ERROR_TRACKER_URL` | URL сервиса отслеживания ошибок | `http://localhost:8004` |

## Запуск

### Разработка

```bash
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8003
```

### Docker

```bash
docker build -t linza-vpleer .
docker run -p 8003:8003 \
  -e STORAGE_SERVICE_URL=http://storage:8001 \
  -e ANALYTICS_SERVICE_URL=http://analytics:8002 \
  linza-vpleer
```

## План тестирования интерфейса по типам файлов

### Чеклист для каждого формата

| Формат | playback-info | Воспроизведение | Seek | Детекции | Фрагмент |
|--------|--------------|-----------------|------|----------|----------|
| **MP4 (H.264)** | `progressive` | Мгновенно | Range seek | Маркеры на таймлайне | ffmpeg `-c copy` |
| **M4V** | `progressive` | Мгновенно | Range seek | Маркеры на таймлайне | ffmpeg `-c copy` |
| **WebM** | `progressive` | Мгновенно | Range seek | Маркеры на таймлайне | ffmpeg transcode |
| **MOV** | `progressive` | Мгновенно (macOS), fallback HLS (Windows) | Range / HLS | Маркеры на таймлайне | ffmpeg `-c copy` |
| **MKV (H.264)** | `transcode` | HLS, stream copy, старт ~5с | По сегментам | Маркеры на таймлайне | ffmpeg `-c copy` |
| **MKV (HEVC)** | `transcode` | HLS, transcode, старт ~10с | По сегментам | Маркеры на таймлайне | ffmpeg transcode |
| **AVI** | `transcode` + warning | HLS, transcode | По сегментам | Маркеры на таймлайне | ffmpeg transcode |
| **MPEG/MPG** | `transcode` | HLS, transcode | По сегментам | Маркеры на таймлайне | ffmpeg transcode |
| **MXF** | `transcode` + warning (большой) | HLS, transcode, долго | По сегментам | Маркеры на таймлайне | ffmpeg transcode |
| **HEVC (.hevc)** | `transcode` | HLS, transcode | По сегментам | Маркеры на таймлайне | ffmpeg transcode |

### Сценарии ручного тестирования

1. **Progressive MP4**: Открыть `/player/video.mp4` → видео запускается мгновенно, бейдж "MP4 (H264)", seek работает
2. **MKV с H.264**: Открыть `/player/video.mkv` → бейдж "MKV (H264)", spinner "Подготовка...", через 3-5с видео воспроизводится через HLS
3. **AVI**: Открыть `/player/video.avi` → бейдж "AVI (?)" (если ffprobe timeout), warning в overlay, HLS transcode запускается
4. **Загрузка детекций**: Кнопка "Загрузить JSON" → вставить JSON → карточки появляются, клик → seek
5. **Навигация**: `[` / `]` hotkeys → перемотка между детекциями
6. **Фрагмент**: Кнопка "Фрагмент" на карточке → видео играет интервал с паузой на end
7. **Responsive**: Сузить окно <1024px → панель детекций перемещается под видео
