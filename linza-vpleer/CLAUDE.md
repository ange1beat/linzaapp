# CLAUDE.md — Linza VPleer Service

## Описание сервиса
Видеоплеер Linza Detector. Потоковое воспроизведение, ffmpeg, timeline с разметкой.
Порт: 8003. Роль: видеоплеер, метаданные, фрагменты, timeline нарушений.

## Критические правила
- **json.dumps(filename)** для JS-контекста в player.py (НЕ html.escape в `<script>`)
- **_safe_content_disposition** (RFC 5987) для всех Content-Disposition
- **quote(safe="/")** для URL с поддиректориями
- Range validation: bytes= prefix, start/end bounds

## Реестр функционала

### Player (app/routes/player.py)
- [x] GET /api/vpleer/files — JSON-список файлов из storage
- [x] GET /api/vpleer/player — HTML-страница списка файлов
- [x] GET /api/vpleer/player/{filename} — HTML-видеоплеер с timeline
- [x] ?detections=base64_json — приём детекций через query param
- [x] Timeline маркеры: загрузка через /api/vpleer/timeline, рендер цветных блоков
- [x] Клик по маркеру → seek видео к start_time
- [x] Клик по timeline → seek к позиции (по проценту)
- [x] Контролы скорости: 0.25x, 0.5x, 1x, 1.5x, 2x
- [x] Загрузка метаданных из /api/vpleer/metadata/{filename}
- [x] Двухколоночная раскладка: видео (слева) + панель детекций (справа)
- [x] Панель детекций: карточки с таймкодами, subclass, category, confidence
- [x] Подсветка активной детекции при воспроизведении (timeupdate)
- [x] Навигация Prev/Next между детекциями + hotkeys [ ]
- [x] Модальное окно загрузки JSON (вставка текста + файл .json)
- [x] Воспроизведение фрагмента интервала (in-player + скачивание)
- [x] Timeline tooltips: subclass, category, confidence, таймкоды при hover
- [x] Responsive: панель складывается на экранах <1024px

### Stream (app/routes/stream.py)
- [x] GET /api/vpleer/stream/{filename} — потоковое воспроизведение с Range
- [x] GET /api/vpleer/fragment — вырезка фрагмента по времени (ffmpeg)
- [x] GET /api/vpleer/playback-info/{filename} — определение стратегии (progressive/transcode)
- [x] GET /api/vpleer/hls/{filename}/playlist.m3u8 — HLS on-demand транскодирование
- [x] GET /api/vpleer/hls/{filename}/{segment} — отдача HLS-сегментов
- [x] 10 форматов: MP4, M4V, AVI, MKV, MOV, WebM, MPEG, MPG, MXF, HEVC

### Metadata (app/routes/metadata.py)
- [x] GET /api/vpleer/metadata/{filename} — метаданные видео (ffprobe через URL, без скачивания)
- [x] GET /api/vpleer/thumbnail/{filename} — JPEG-превью (ffmpeg)

### Буферизация и форматы
- [x] get_metadata_from_url() — ffprobe по URL без скачивания файла
- [x] get_stream_info() — определение кодека и контейнера
- [x] generate_hls() — транскодирование в HLS с stream copy для H.264
- [x] Shared HTTP client (lifespan) — connection pooling, таймауты 30s/3600s
- [x] Фоновая очистка кэша /tmp (LRU, TTL 1ч, лимит 50ГБ)
- [x] hls.js интеграция на фронтенде
- [x] Бейдж формата и индикатор транскодирования в UI

### Timeline (app/routes/timeline.py)
- [x] GET /api/vpleer/timeline — маркеры нарушений с цветовой кодировкой
  - Цвета категорий: prohibited=#dc3545, 18+=#fd7e14, 16+=#ffc107
  - Цвета источников (резерв): SOURCE_COLORS video=#53c0f0, audio=#a855f7, both=#ec4899
  - Обогащение детекций категориями из analytics-service
  - Проброс поля `source` (video/audio/both, default "both")

### Дизайн-система (app/routes/player.py)
- [x] CSS custom properties: 36 токенов (фоны, текст, границы, тени, оверлеи, категории, типографика)
- [x] Тёмная тема: `[data-theme="dark"]` — дефолт, цвета идентичны оригиналу
- [x] Светлая тема: `[data-theme="light"]` — полная палитра
- [x] Кнопка переключения темы: `#themeToggle`, localStorage `linza-theme`
- [x] Типографика: 13 font-size → 6 токенов (--text-xs..--text-xl)
- [x] Обе страницы (player + index) используют общую дизайн-систему
- [x] Двойная дорожка таймлайна: trackVideo (🎬) + trackAudio (🔊), 9px каждая
- [x] Маркеры на треках по полю `source`: "video"/"audio"/"both" (default)
- [x] Иконка источника (🎬/🔊/◉) на карточках детекций
- [x] Группировка перекрытий: groupByOverlap() объединяет пересекающиеся детекции
- [x] Групповые карточки: gradient border, список детекций, group-count badge
- [x] Навигация Prev/Next по группам, playGroupFragment() для фрагментов групп
- [x] Обратная связь: ✓ confirm / ✗ reject / ↻ reclassify на каждой детекции
- [x] 4 состояния карточки: pending/confirmed/rejected/reclassified с визуальной индикацией
- [x] Dropdown переклассификации: 21 subclass
- [x] localStorage: сохранение review-статусов (linza-reviews-{filename})
- [x] Keyboard shortcuts: Y (confirm), N (reject), R (reclassify) — работают на группах
- [x] Bootstrap Icons SVG inline (14-16px, fill="currentColor") для всех кнопок
- [x] Undo-кнопка после review действия (setReview(id, null))
- [x] Batch confirm: "✓ Все" в панели header (confirmAllVisible)
- [x] group-card border-left для индикации review-состояния
- [x] showReclass() через data-det-id атрибут (не onclick.toString)
- [x] Панель фильтров: collapsible, чипы (категория, источник, статус), confidence slider
- [x] Сортировка: по времени / severity / confidence
- [x] Фильтрация применяется к карточкам (display:none) и маркерам (opacity:0.12)
- [x] Тег-бейджи активных фильтров, счётчик результатов, сброс
- [x] Сводка-статбар: counts по категориям (цветные точки) + статусам review
- [x] Клик по элементу статбара → быстрый фильтр, обновляется при изменении фидбека
- [x] Экспорт JSON: кнопка внизу панели, Blob + createObjectURL, поле review в каждой детекции
- [x] beforeunload предупреждение при наличии несохранённых review

### Health
- [x] GET /health — {"status": "ok", "service": "vpleer"}

## Межсервисные вызовы
- GET {STORAGE_SERVICE_URL}/api/files — список файлов
- HEAD/GET {STORAGE_SERVICE_URL}/api/files/download/{filename} — стриминг файлов
- ffprobe {STORAGE_SERVICE_URL}/api/files/download/{filename} — метаданные по URL (Range)
- ffmpeg -i {STORAGE_SERVICE_URL}/api/files/download/{filename} — HLS транскодирование по URL
- GET {ANALYTICS_SERVICE_URL}/api/classifier — конфигурация категорий

## Зависимости
- fastapi==0.115.5
- uvicorn[standard]==0.32.1
- httpx==0.27.2

## Чеклист перед коммитом
1. json.dumps для filename в <script> блоке player.py
2. _safe_content_disposition для Content-Disposition
3. Timeline JS: loadTimeline, parseTime, renderMarkers, applyDetections присутствуют
4. detections query param в player_page signature
5. Панель детекций: detectionsPanel, detectionList, modalOverlay, jsonInput
6. Навигация: btnPrev, btnNext, navPosition
7. Фрагмент: fragmentIndicator, playFragment, stopFragment
8. hls.js CDN подключён в <head>, Hls.isSupported() проверяется
9. playback-info fetch определяет стратегию (progressive/transcode)
10. formatBadge, transcodeOverlay присутствуют
11. Path traversal защита в hls_segment (pathlib.resolve)
12. Shared HTTP client через _get_http_client() с fallback
13. data-theme="dark" на <html>, :root и [data-theme="light"] CSS-блоки
14. themeToggle кнопка и toggleTheme/initTheme JS в обеих страницах
15. Все цвета через var(--token), нет hardcoded hex в CSS правилах
16. trackVideo, trackAudio элементы в #timeline
17. renderMarkers распределяет маркеры по m.source на нужный трек
18. Timeline endpoint передаёт source field (default "both")
