# План: Видеоплеер Linza — панель таймкодов, буферизация, рецензирование

## Фаза A: Панель просмотра таймкодов ✅
## Фаза B: Буферизация, форматы, HLS ✅

---

# Фаза C: UX/UI редизайн — рецензирование, мультикласс, фидбек

## C1. Экспертная оценка текущего UI

| Аспект | Оценка | Проблема |
|--------|--------|----------|
| Цветовая система | 7/10 | Консистентна, 3 категории различимы |
| Типографика | 6/10 | 16 font-size → свести к 6 |
| Компоновка | 8/10 | Grid 70/30 хорош |
| Интерактивность | 7/10 | Hover/active, hotkeys |
| Responsive | 5/10 | 1 breakpoint |
| Accessibility | 3/10 | Цвет — единственный индикатор (WCAG 1.4.1) |
| Темизация | 2/10 | Только dark |

**Критические проблемы:** нет светлой темы, нет обратной связи, нет группировки перекрытий, нет аудио/видео, нет фильтров.

---

## C2. Цветовые палитры Dark + Light ✅ РЕАЛИЗОВАНО

Все цвета через CSS custom properties `var(--token)`, тема на `<html data-theme="dark|light">`.
36 токенов: 11 фонов, 5 текстовых, 3 границы/тени, 4 категории, 3 feedback, 5 overlay/shadow, 6 типографика.

### Dark (реализовано)
```
--bg-primary:#1a1a2e  --bg-surface:#16213e  --bg-elevated:#0f3460
--bg-hover:#1a5276  --bg-active:#1a3a5e  --bg-input:#2a2a4a
--bg-input-hover:#3a3a5a  --bg-card:#1a2744  --bg-card-hover:#1e3050
--bg-tooltip:#0a0a1a  --bg-video:#000
--text-primary:#e0e0e0  --text-secondary:#a0a0c0  --text-muted:#7a7aa0
--text-accent:#53c0f0  --text-on-accent:#fff
--border:#2a2a4a  --border-focus:#53c0f0
--cat-prohibited:#dc3545  --cat-18:#fd7e14  --cat-16:#ffc107
--status-active:#e94560
--source-video:#53c0f0  --source-audio:#a855f7  --source-both:#ec4899
--feedback-confirm:#22c55e  --feedback-reject:#ef4444  --feedback-reclass:#f59e0b
```

### Light (реализовано)
```
--bg-primary:#f0f2f5  --bg-surface:#ffffff  --bg-elevated:#e3eaf2
--bg-hover:#d0dae5  --bg-active:#c5d5e5  --bg-input:#e8ecf0
--bg-input-hover:#dde2e8  --bg-card:#f5f7fa  --bg-card-hover:#ebeef2
--bg-tooltip:#1a1a2e  --bg-video:#000
--text-primary:#1a1a2e  --text-secondary:#4a5568  --text-muted:#718096
--text-accent:#2b6cb0  --text-on-accent:#fff
--border:#d2d6dc  --border-focus:#2b6cb0
--cat-prohibited:#dc3545  --cat-18:#fd7e14  --cat-16:#ffc107
--status-active:#e94560
--source-video:#0369a1  --source-audio:#7c3aed  --source-both:#db2777
--feedback-confirm:#16a34a  --feedback-reject:#dc2626  --feedback-reclass:#d97706
```

### Решения по цветам (принятые)

- **Feedback-confirm остаётся зелёным (#22c55e / #16a34a)**, а не сдвигается к teal (#10b981). Причина: семантическая зелёность «подтверждено» важнее визуальной гармонии с Linza blue. Пользователь мгновенно считывает зелёный как «ok», а teal размывает границу с accent-цветом.
- **Категории (prohibited/18+/16+) одинаковы в обеих темах** — красный/оранжевый/жёлтый универсально распознаются как severity-уровни, независимо от фона.
- **`--source-video/audio/both` заложены как CSS-токены и API-константы** (`SOURCE_COLORS` в timeline.py, `source_colors` в ответе эндпоинта). Сейчас источник различается иконками (🎬/🔊/◉); цветовая дифференциация — резерв для сторонних сервисов и будущих веток.

---

## C3. CJM — путь рецензента

```
1.ОБЗОР → 2.НАВИГАЦИЯ → 3.ОЦЕНКА → 4.ФИЛЬТРАЦИЯ → 5.ЭКСПОРТ
```

Hotkeys: `]`/`[` nav, `Y` confirm, `N` reject, `R` reclassify, `F` fragment, `T` theme.

---

## C4. Мультикласс — группировка перекрытий

Алгоритм: сортировка по start_time → если start < prev.end → объединить в группу.

```
┌─ градиент из цветов категорий ─────────────────────────────────┐
│ 00:15.500 — 00:25.800                          3 детекции      │
│ 🎬 NUDE       ● prohibited  ████████░░ 95%   [✓] [✗] [↻]     │
│ 🎬 ALCOHOL    ● 16+         █████░░░░░ 71%   [✓] [✗] [↻]     │
│ 🔊 OBSCENE    ● 16+         ███████░░░ 88%   [✓] [✗] [↻]     │
│ [▶ Фрагмент]  [✓ Все верно]  [📥 Скачать]                     │
└─────────────────────────────────────────────────────────────────┘
```

Timeline: маркер с градиентом или стек тонких полосок.

---

## C5. Аудио vs Видео

Новое поле `"source": "video"|"audio"|"both"` (опционально, default "both").

Timeline → 2 дорожки по 9px:
```
🎬 ┊ ████░░░░░░████░░░░░░░░░░   VIDEO track (9px)
🔊 ┊ ░░░░░░███░░░░░░░█████░░░   AUDIO track (9px)
```

Иконки на карточках: 🎬 video, 🔊 audio, ◉ both.

---

## C6. Фильтрация и сортировка

Клиентская (JS). Фильтры: класс, категория, источник, статус рецензии, confidence (slider).

Логика: И-условие. Фильтр применяется к карточкам И маркерам (скрытые = opacity 0.12).

Сортировка: по времени, severity, confidence.

---

## C7. Расширение модели данных

Вход: `+source` (опционально). Выход timeline: `+source`. Рецензия (только клиент):
```json
"review": { "status": "confirmed|rejected|reclassified", "new_subclass": null }
```

---

## C8. Wireframes и план разработки

### Wireframe: полная страница плеера (dark theme)

```
┌─────────────────────────────────────────────────────────────────────────┐
│ ← К списку файлов                                                      │
│ Linza VPleer — video.mp4  [MP4 H264]                        [☀/☾]     │
├──────────────────────────────────────────┬──────────────────────────────┤
│                                          │ Детекции (47)  [⚙ Фильтры] │
│                                          │ ┌────────────────────────┐  │
│          ▶  ВИДЕОПЛЕЕР                   │ │ Сводка:                │  │
│                                          │ │ ● 3 prohibited         │  │
│             (70vh max)                   │ │ ● 12 18+               │  │
│                                          │ │ ● 32 16+               │  │
│                                          │ │ ✓ 15  ✗ 2  ↻ 1       │  │
│                                          │ └────────────────────────┘  │
│                                          │                             │
│ 🎬 ┊ ███░░░██░░░░░░░░░░░░░░░░░░░░░░░░  │ ◀ Пред  12/47  След ▶     │
│ 🔊 ┊ ░░░░░░░░███░░░░░██░░░░░░░░░░░░░░  │ Сорт: [По времени ▼]      │
│                                          │                             │
│ [-5s][+5s] [0.5x][1x][1.5x][2x]        │ Фильтры: [ALCOHOL×][≥70%×] │
│ [Скачать] [Превью]                       │ 47 → 12 результатов        │
│                                          │                             │
├──────────────────────────────────────────┤ ┌────────────────────────┐  │
│ Формат: MPEG-4 (H.264)                  │ │ 00:15.5 — 00:25.8     │  │
│ Длительность: 1:23:45                    │ │ 🎬 NUDE    ●proh  95% │  │
│ Размер: 1.2 ГБ                           │ │ 🎬 ALCOHOL ●16+  71% │  │
│ Видео: h264 1920x1080 @ 25fps           │ │ 🔊 OBSCENE ●16+  88% │  │
│ Аудио: aac 48000 Hz                      │ │ [▶][✓ Все][✗][↻][📥]│  │
│ Битрейт: 5200 kbps                       │ └────────────────────────┘  │
│                                          │ ┌────────────────────────┐  │
│                                          │ │ 00:45.0 — 00:55.0     │  │
│                                          │ │ 🎬 VIOLENCE ●16+ 82%  │  │
│                                          │ │ [▶ Фрагмент][✓][✗][↻]│  │
│                                          │ └────────────────────────┘  │
│                                          │                             │
│                                          │ [📥 Экспорт JSON]          │
└──────────────────────────────────────────┴──────────────────────────────┘
```

### Wireframe: панель фильтров (развёрнутая)

```
┌─ ⚙ Фильтры ──────────────────────────── [Сбросить] ─┐
│                                                       │
│  КЛАСС                                                │
│  [NUDE] [ALCOHOL] [SMOKING] [VIOLENCE] [DRUGS]       │
│  [OBSCENE] [TERROR] [+13 ещё ▼]                     │
│                                                       │
│  КАТЕГОРИЯ                                            │
│  [● prohibited] [● 18+] [● 16+]                     │
│                                                       │
│  ИСТОЧНИК                                             │
│  [🎬 Видео] [🔊 Аудио]                              │
│                                                       │
│  СТАТУС РЕЦЕНЗИИ                                      │
│  [◻ Без ответа] [✓ Подтв.] [✗ Отклон.] [↻ Перекл.]│
│                                                       │
│  CONFIDENCE                                           │
│  0% ━━━━━━━━●━━━━━━━ 100%   ≥ 70%                  │
└───────────────────────────────────────────────────────┘
```

### Wireframe: карточка с фидбеком (3 состояния)

```
Без ответа (default):
┌─ #ffc107 ──────────────────────────┐
│ 00:45.0 — 00:55.0                  │
│ 🎬 ALCOHOL  ● 16+  71%            │
│ [▶ Фрагм] [✓ Верно] [✗] [↻]     │
└────────────────────────────────────┘

Подтверждено:
┌─ #22c55e ──────────────────────────┐   ← зелёная рамка
│ 00:45.0 — 00:55.0          ✓      │   ← галочка справа
│ 🎬 ALCOHOL  ● 16+  71%            │
│ [▶ Фрагм] [Отменить]              │
└────────────────────────────────────┘

Отклонено (false positive):
┌─ #ef4444 ──────────────────────────┐   ← красная рамка
│ 00:45.0 — 00:55.0          ✗      │
│ 🎬 ~~ALCOHOL~~  ● 16+  71%        │   ← strikethrough
│ [▶ Фрагм] [Отменить]              │
└────────────────────────────────────┘

Переклассифицировано:
┌─ #f59e0b ──────────────────────────┐   ← янтарная рамка
│ 00:45.0 — 00:55.0          ↻      │
│ 🎬 ~~ALCOHOL~~ → SMOKING          │   ← старый → новый
│ [▶ Фрагм] [Отменить]              │
└────────────────────────────────────┘
```

### Wireframe: переключатель тем

```
Dark:  [☾]  — иконка луны, подсветка accent
Light: [☀]  — иконка солнца

Расположение: правый верхний угол header, рядом с заголовком.
Размер: 32x32px, border-radius: 50%.
```

### Wireframe: сводка-статбар

```
┌──────────────────────────────────────┐
│ ● 3 запрещ.  ● 12 18+  ● 32 16+    │
│ ✓ 15 подтв.  ✗ 2 отклон.  ↻ 1     │
│ ◻ 27 без ответа                     │
└──────────────────────────────────────┘
```

Цвета точек = категории. Статусы = feedback-цвета.
Клик по элементу сводки → быстрый фильтр.

---

## C9. Спецификация компонентов

### Кнопки действий на карточке

| Кнопка | Иконка | Размер | Стиль default | Стиль hover |
|--------|--------|--------|---------------|-------------|
| Confirm | ✓ | 24x24 | border 1px solid var(--border), transparent bg | bg var(--feedback-confirm), white text |
| Reject | ✗ | 24x24 | border 1px solid var(--border) | bg var(--feedback-reject), white text |
| Reclassify | ↻ | 24x24 | border 1px solid var(--border) | bg var(--feedback-reclass), white text |
| Fragment | ▶ | auto | border 1px solid var(--border) | bg var(--bg-elevated), accent text |

```css
.action-btn {
  width: 24px; height: 24px;
  border: 1px solid var(--border);
  border-radius: 4px;
  background: transparent;
  color: var(--text-muted);
  cursor: pointer;
  font-size: var(--text-xs);
  display: inline-flex;
  align-items: center;
  justify-content: center;
  transition: all 0.15s;
}
.action-btn:hover {
  color: #fff;
}
.action-btn.confirm:hover { background: var(--feedback-confirm); }
.action-btn.reject:hover  { background: var(--feedback-reject); }
.action-btn.reclass:hover { background: var(--feedback-reclass); }

/* Активное состояние (уже нажата) */
.action-btn.confirm.active {
  background: var(--feedback-confirm);
  color: #fff;
  border-color: var(--feedback-confirm);
}
.action-btn.reject.active {
  background: var(--feedback-reject);
  color: #fff;
  border-color: var(--feedback-reject);
}
```

### Dropdown переклассификации

```css
.reclass-dropdown {
  position: absolute;
  right: 0; top: 100%;
  background: var(--bg-surface);
  border: 1px solid var(--border);
  border-radius: 8px;
  box-shadow: var(--shadow);
  z-index: 30;
  max-height: 200px;
  overflow-y: auto;
  min-width: 180px;
}
.reclass-option {
  padding: 6px 12px;
  font-size: var(--text-sm);
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 8px;
}
.reclass-option:hover {
  background: var(--bg-hover);
}
.reclass-option .cat-dot {
  width: 8px; height: 8px;
  border-radius: 50%;
}
```

### Экспорт-кнопка

```css
.export-btn {
  width: 100%;
  padding: 10px;
  margin-top: 8px;
  background: var(--bg-elevated);
  color: var(--text-accent);
  border: 1px solid var(--border);
  border-radius: 8px;
  font-size: var(--text-base);
  cursor: pointer;
  text-align: center;
  transition: all 0.15s;
}
.export-btn:hover {
  background: var(--bg-hover);
  border-color: var(--text-accent);
}
```

---

## C10. Пошаговый план разработки Фазы C

### Порядок реализации

```
C-1 → C-2 → C-3 → C-4 → C-5 → C-6 → C-7 → C-8
```

### C-1: Дизайн-токены и темизация (1-2 дня)

**Файлы:** `player.py`

1. Заменить все hardcoded цвета на CSS custom properties `var(--token)`
2. Добавить `[data-theme="dark"]` и `[data-theme="light"]` блоки
3. Свести font-size к 6 токенам
4. Добавить кнопку переключения темы (☀/☾) в header
5. JS: читать/сохранять тему в localStorage, default от prefers-color-scheme
6. Тесты: проверить наличие `data-theme`, `localStorage`

### C-2: Двойная дорожка таймлайна (1 день)

**Файлы:** `player.py`

1. Заменить `#timeline` на flex-контейнер с 2 `.timeline-track` (video/audio)
2. При рендере маркеров — размещать по `source` на соответствующую дорожку
3. Лейблы 🎬/🔊 слева
4. Обратная совместимость: если `source` отсутствует → обе дорожки

### C-3: Расширение модели данных (0.5 дня)

**Файлы:** `timeline.py`, `player.py`

1. В `timeline.py`: пробросить `source` из входных данных
2. В `player.py` JS: добавить `source` в `applyDetections()`
3. Обновить пример JSON в модальном окне

### C-4: Группировка мультикласса (1-2 дня)

**Файлы:** `player.py`

1. JS-функция `groupByOverlap(markers)` — алгоритм группировки
2. Новый компонент `renderGroupedCard(group)` — групповая карточка
3. Timeline: маркер с градиентом для групп
4. Навигация Prev/Next — по группам, не по отдельным детекциям

### C-5: Механизм обратной связи (1-2 дня)

**Файлы:** `player.py`

1. Кнопки ✓/✗/↻ на каждой карточке (inline, без модалок)
2. Dropdown для переклассификации (21 subclass)
3. Состояния карточки: pending/confirmed/rejected/reclassified
4. Визуальная индикация (рамка + иконка + strikethrough)
5. localStorage: сохранение review-статусов
6. Keyboard shortcuts: Y/N/R
7. Batch: "Подтвердить все видимые"

### C-6: Панель фильтров (1-2 дня)

**Файлы:** `player.py`

1. Collapsible панель фильтров над списком карточек
2. Фильтры-чипы: класс, категория, источник, статус
3. Confidence slider (range input)
4. Тег-бейджи активных фильтров
5. Применение к карточкам + opacity маркеров на таймлайне
6. Сортировка: dropdown (время, severity, confidence)

### C-7: Сводка-статбар (0.5 дня)

**Файлы:** `player.py`

1. Блок сводки вверху панели (counts по категориям + статусам)
2. Клик по элементу → быстрый фильтр
3. Обновление при изменении фидбека

### C-8: Экспорт JSON с рецензией (0.5 дня)

**Файлы:** `player.py`

1. Кнопка "📥 Экспорт JSON" внизу панели
2. Генерация JSON с полями `review`
3. Скачивание через `Blob` + `URL.createObjectURL`
4. Предупреждение при уходе со страницы (`beforeunload`)

---

## C11. Затрагиваемые файлы

| Файл | Шаги | Изменения |
|------|------|-----------|
| `app/routes/player.py` | C-1..C-8 | CSS токены, темы, timeline 2 дорожки, группировка, фидбек, фильтры, экспорт |
| `app/routes/timeline.py` | C-3 | Проброс `source` |
| `tests/test_player.py` | C-1..C-8 | Тесты на data-theme, фильтры, фидбек-кнопки, экспорт |
| `CLAUDE.md` | C-8 | Обновить реестр |

## C12. Верификация

1. `pytest tests/ -v` — все тесты проходят
2. Переключение темы: dark ↔ light, сохранение в localStorage
3. Двойная дорожка: маркеры video сверху, audio снизу
4. Мультикласс: 3 детекции в одном таймкоде → 1 группированная карточка
5. Фидбек: ✓ → зелёная рамка, ✗ → красная + strikethrough, ↻ → dropdown
6. Фильтры: "ALCOHOL + video" → только matching карточки и маркеры
7. Экспорт: JSON с полями review.status
8. Keyboard: Y/N/R работают на активной карточке
9. Responsive: <1024px — панель под видео
10. WCAG: цветная точка + текстовый лейбл категории на каждой карточке

## Оценка трудозатрат

| Шаг | Описание | Дней |
|-----|----------|------|
| C-1 | Дизайн-токены + темизация | ✅ РЕАЛИЗОВАНО |
| C-2 | Двойная дорожка таймлайна | ✅ РЕАЛИЗОВАНО |
| C-3 | Расширение модели данных | ✅ РЕАЛИЗОВАНО |
| C-4 | Группировка мультикласса | ✅ РЕАЛИЗОВАНО |
| C-5 | Механизм обратной связи | ✅ РЕАЛИЗОВАНО |
| C-6 | Панель фильтров | ✅ РЕАЛИЗОВАНО |
| C-7 | Сводка-статбар | ✅ РЕАЛИЗОВАНО |
| C-8 | Экспорт с рецензией | ✅ РЕАЛИЗОВАНО |
| **Итого** | | **7-10 дней** |

---

# Архитектура платформы (as-is после Фазы C)

## Сервисы

| Сервис | Порт | Стек | БД | Роль |
|--------|------|------|----|------|
| linza-board | 8000 | FastAPI + Vue 3 SPA | SQLite (SQLAlchemy) | UI, авторизация, управление, отчёты |
| linza-storage-service | 8001 | FastAPI | — (S3/MinIO) | Файловые операции, стриминг |
| linza-analytics | 8002 | FastAPI | SQLite | Конфигурация классификатора (21 subclass) |
| linza-vpleer | 8003 | FastAPI | — (stateless) | Видеоплеер, timeline, рецензирование |
| linza-debug | 8004 | FastAPI | — | Агрегация ошибок |
| nginx | 80 | Nginx | — | API Gateway, SPA routing |
| minio | 9000/9001 | MinIO | — | S3-совместимое хранилище |

## Межсервисное взаимодействие

```
board ──→ storage (файлы, скачивание)
board ──→ analytics (конфиг классификатора)
vpleer ──→ storage (стриминг, ffprobe по URL)
vpleer ──→ analytics (обогащение категориями)
все ──→ debug (ErrorReporter middleware)
nginx ──→ все (reverse proxy)
```

## Модель данных linza-board

| Таблица | Ключевые поля | Назначение |
|---------|---------------|-----------|
| User | login, password_hash (bcrypt), role (superadmin/admin/user) | Авторизация |
| StorageProfile | s3_endpoint_url, s3_access_key_id, s3_secret_access_key, s3_bucket_name | Профили хранилищ |
| AccessCredential | domain, login, password_encrypted (**plaintext!**) | Доступ к источникам |
| DataSource | path_type (s3/http/smb), path_url, file_extensions | Источники данных |
| AnalysisReport | filename, status, match_count, report_json (Text) | Отчёты анализа |
| ErrorRecord | service, severity, category, message, traceback, github_issue_url | Ошибки |

## Критические пробелы (production readiness)

| # | Проблема | Влияние | Статус |
|---|----------|---------|--------|
| 1 | Review хранится только в localStorage браузера | Потеря данных при очистке/смене устройства | Не решено |
| 2 | AccessCredential.password хранится plaintext | Критическая уязвимость безопасности | Не решено |
| 3 | Нет rate limiting на /api/auth/login | Brute-force атака | Не решено |
| 4 | Нет межсервисной авторизации (mTLS/API keys) | Сетевая безопасность | Не решено |
| 5 | Нет API versioning | Несовместимые изменения | Не решено |
| 6 | Нет circuit breaker/retry | Каскадные отказы | Не решено |
| 7 | Нет OpenTelemetry/метрик | Сложность отладки | Не решено |
| 8 | Нет CI/CD pipeline | Ручной деплой | Не решено |
| 9 | SQLite — single-node only | Масштабирование | By design |
| 10 | Нет accuracy metrics / model versioning | Нет обратной связи для ML | Не решено |

---

# Фаза D: Персистентность рецензий

## D1. Проблема

Review-данные (confirmed/rejected/reclassified) хранятся в `localStorage` браузера (`linza-reviews-{filename}`). Это означает:
- Потеря при очистке кэша / смене браузера / другого устройства
- Невозможность агрегации по нескольким рецензентам
- Невозможность экспорта для обучения моделей
- Нет аудита кто/когда/что рецензировал

## D2. Целевая архитектура

```
vpleer (frontend JS)
  │ POST /api/reports/{report_id}/reviews
  │ GET  /api/reports/{report_id}/reviews
  ▼
linza-board (FastAPI)
  │ ReviewRecord таблица
  ▼
SQLite / PostgreSQL
```

## D3. Пошаговый план

### D-1: Модель ReviewRecord (1 день)

**Репо:** linza-board
**Файлы:** `app/models.py`, `app/database.py`

Новая таблица:
```python
class ReviewRecord(Base):
    __tablename__ = "review_records"
    id = Column(Integer, primary_key=True)
    report_id = Column(Integer, ForeignKey("analysis_reports.id"), nullable=False)
    detection_index = Column(Integer, nullable=False)  # индекс детекции в report_json
    subclass = Column(String, nullable=False)           # NUDE, ALCOHOL, ...
    original_category = Column(String)                   # prohibited, 18+, 16+
    status = Column(String, nullable=False)              # confirmed / rejected / reclassified
    new_subclass = Column(String, nullable=True)         # только для reclassified
    reviewed_by = Column(Integer, ForeignKey("users.id"))
    reviewed_at = Column(DateTime, default=func.now())
    __table_args__ = (UniqueConstraint("report_id", "detection_index"),)
```

### D-2: API эндпоинты рецензий (1-2 дня)

**Репо:** linza-board
**Файлы:** `app/routes/reports.py` (расширение существующего роутера)

| Метод | Путь | Описание |
|-------|------|----------|
| GET | `/api/reports/{id}/reviews` | Все рецензии для отчёта |
| POST | `/api/reports/{id}/reviews` | Создать/обновить рецензию (upsert) |
| DELETE | `/api/reports/{id}/reviews/{det_idx}` | Отменить рецензию |
| GET | `/api/reports/{id}/reviews/summary` | Статистика: counts by status |

Request body (POST):
```json
{
  "detection_index": 3,
  "subclass": "ALCOHOL",
  "status": "rejected",
  "new_subclass": null
}
```

### D-3: Интеграция vpleer → board API (1-2 дня)

**Репо:** linza-vpleer
**Файлы:** `app/routes/player.py`

1. Добавить `?report_id=N` query param в player page
2. JS: при наличии report_id — загружать review из API вместо localStorage
3. JS: при setReview() — POST в API + fallback на localStorage при ошибке
4. JS: при загрузке — GET /api/reports/{id}/reviews → заполнить reviewData
5. Сохранить localStorage как offline-fallback

### D-4: Миграция существующих review (0.5 дня)

**Репо:** linza-vpleer
**Файлы:** `app/routes/player.py`

1. JS: кнопка "Синхронизировать" — отправить localStorage reviews в API
2. После успешной синхронизации — очистить localStorage
3. Индикатор "Сохранено в облаке" / "Только локально"

### D-5: nginx routing (0.5 дня)

**Репо:** linza-deploy
**Файлы:** `nginx/nginx.conf`

Добавить проксирование `/api/reports/*/reviews` → board:8000 (уже покрыто `/api/reports/*`).

## D4. Затрагиваемые файлы

| Репо | Файл | Изменения |
|------|------|-----------|
| linza-board | `app/models.py` | +ReviewRecord модель |
| linza-board | `app/database.py` | create_all включает review_records |
| linza-board | `app/routes/reports.py` | +4 эндпоинта рецензий |
| linza-board | `tests/` | Тесты на CRUD рецензий |
| linza-vpleer | `app/routes/player.py` | report_id param, API sync, fallback |
| linza-vpleer | `tests/test_player.py` | Тесты sync логики |
| linza-deploy | `nginx/nginx.conf` | Проверить routing |

## D5. Оценка: 4-6 дней

---

# Фаза E: Аналитика и метрики качества

## E1. Цель

Замкнуть цикл обратной связи: рецензии → метрики точности → экспорт для дообучения моделей.

## E2. Пошаговый план

### E-1: Accuracy dashboard в linza-board (2-3 дня)

**Репо:** linza-board
**Файлы:** `frontend/src/views/AnalyticsPage.vue` (расширение), `app/routes/reports.py`

Новый API:
```
GET /api/reports/accuracy?period=7d
```

Response:
```json
{
  "total_detections": 1234,
  "reviewed": 890,
  "confirmed": 720,
  "rejected": 150,
  "reclassified": 20,
  "accuracy_rate": 0.831,
  "by_subclass": {
    "NUDE": {"total": 100, "confirmed": 95, "rejected": 5, "accuracy": 0.95},
    "ALCOHOL": {"total": 200, "confirmed": 140, "rejected": 50, "accuracy": 0.74}
  },
  "by_category": {
    "prohibited": {"accuracy": 0.96},
    "18+": {"accuracy": 0.82},
    "16+": {"accuracy": 0.71}
  }
}
```

Vue компонент: таблица + bar chart (Chart.js или inline SVG), фильтр по периоду.

### E-2: Экспорт training data (1-2 дня)

**Репо:** linza-board
**Файлы:** `app/routes/reports.py`

```
GET /api/reports/export/training?format=jsonl&status=rejected
```

Формат JSONL (по строке на детекцию):
```json
{"filename": "video.mp4", "start": 15.5, "end": 25.8, "predicted": "ALCOHOL", "actual": "confirmed", "new_class": null, "reviewer": "admin", "timestamp": "2026-04-03T12:00:00Z"}
```

Фильтры: status, subclass, date_range, reviewer.

### E-3: Model version tracking (1 день)

**Репо:** linza-analytics
**Файлы:** `app/db.py`, `app/routes.py`

Новая таблица:
```sql
CREATE TABLE model_versions (
  id INTEGER PRIMARY KEY,
  version TEXT NOT NULL,
  description TEXT,
  deployed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  is_active BOOLEAN DEFAULT 1
);
```

API:
- `GET /api/classifier/versions` — список версий
- `POST /api/classifier/versions` — зарегистрировать новую версию
- `PUT /api/classifier/versions/{id}/activate` — активировать

AnalysisReport получает поле `model_version` для привязки результатов к версии модели.

### E-4: Confusion matrix API (1-2 дня)

**Репо:** linza-board
**Файлы:** `app/routes/reports.py`

```
GET /api/reports/confusion-matrix?model_version=v2.1
```

Response: матрица predicted × actual (21×21) для reclassified детекций.
Vue: heatmap-визуализация на AnalyticsPage.

## E3. Затрагиваемые файлы

| Репо | Файл | Изменения |
|------|------|-----------|
| linza-board | `app/routes/reports.py` | accuracy, export, confusion-matrix endpoints |
| linza-board | `frontend/src/views/AnalyticsPage.vue` | Dashboard, charts, confusion matrix |
| linza-analytics | `app/db.py` | model_versions таблица |
| linza-analytics | `app/routes.py` | versions CRUD |
| linza-board | `app/models.py` | AnalysisReport +model_version field |

## E4. Зависимости

- Фаза D (ReviewRecord) — обязательна для accuracy и export

## E5. Оценка: 5-8 дней

---

# Фаза F: Безопасность

## F1. Критические уязвимости

### F-1: Шифрование паролей AccessCredential (1 день)

**Репо:** linza-board
**Файлы:** `app/models.py`, `app/routes/settings.py`
**Приоритет:** CRITICAL

Сейчас `AccessCredential.password_encrypted` хранится **plaintext**.

Решение:
1. Добавить `cryptography` (Fernet) в зависимости
2. Генерировать FERNET_KEY из переменной окружения
3. Encrypt при записи, decrypt при чтении
4. Миграция: одноразовый скрипт шифрования существующих записей

### F-2: Rate limiting на /api/auth/login (0.5 дня)

**Репо:** linza-board
**Файлы:** `app/routes/auth.py`, `requirements.txt`

1. Добавить `slowapi` в зависимости
2. Лимит: 5 попыток / минута / IP
3. Ответ 429 Too Many Requests

### F-3: Межсервисный API key (1-2 дня)

**Репо:** все сервисы
**Файлы:** middleware в каждом сервисе

1. Общий `X-Service-Key` header для inter-service вызовов
2. Ключ из переменной окружения `LINZA_SERVICE_KEY`
3. Middleware: проверять ключ для внутренних эндпоинтов
4. Public-facing эндпоинты (board API) — через JWT как сейчас

### F-4: CORS hardening (0.5 дня)

**Репо:** все сервисы
**Файлы:** `app/main.py` в каждом сервисе

1. Убрать `allow_origins=["*"]` → явный список доменов
2. Из переменной окружения `CORS_ORIGINS`

### F-5: Input validation audit (1 день)

**Репо:** все сервисы

1. Pydantic models для всех request bodies
2. Path traversal проверки (уже есть в vpleer — распространить)
3. SQL injection — проверить raw queries (нет ORM)
4. XSS — проверить HTML-рендеринг в player.py

## F2. Оценка: 4-5 дней

---

# Фаза G: Наблюдаемость и отказоустойчивость

## G1. Пошаговый план

### G-1: Structured logging (1 день)

**Репо:** все сервисы
**Файлы:** `app/main.py`, новый `app/logging_config.py`

1. `python-json-logger` — JSON-формат логов
2. Поля: timestamp, service, level, request_id, user_id, endpoint, duration_ms
3. Correlation ID: `X-Request-ID` header, прокидывать между сервисами

### G-2: Health checks расширенные (0.5 дня)

**Репо:** все сервисы

Текущий `/health` → расширить:
```json
{
  "status": "ok",
  "service": "vpleer",
  "version": "1.0.0",
  "uptime_seconds": 3600,
  "dependencies": {
    "storage": "ok",
    "analytics": "ok"
  }
}
```

### G-3: Circuit breaker для межсервисных вызовов (1-2 дня)

**Репо:** linza-vpleer, linza-board
**Файлы:** новый `app/circuit_breaker.py`

1. Обёртка над httpx: 3 failures → open → 30s cooldown → half-open → probe
2. Graceful degradation: vpleer работает без analytics (default categories)
3. board работает без storage (cached file list)

### G-4: Prometheus метрики (1-2 дня)

**Репо:** все сервисы
**Файлы:** `app/main.py`, `requirements.txt`

1. `prometheus-fastapi-instrumentator`
2. Метрики: request_count, request_duration, active_connections
3. Custom: detections_reviewed_total, reports_created_total, ffmpeg_transcode_duration
4. Endpoint: `GET /metrics`

### G-5: Grafana dashboards (1 день)

**Репо:** linza-deploy
**Файлы:** `grafana/dashboards/`, `docker-compose.yml`

1. Добавить Prometheus + Grafana в docker-compose
2. Dashboards: Overview, Per-Service, Errors, Review Activity

## G2. Оценка: 5-7 дней

---

# Фаза H: CI/CD и продакшн-деплой

## H1. Пошаговый план

### H-1: GitHub Actions CI (1-2 дня)

**Репо:** все
**Файлы:** `.github/workflows/ci.yml`

```yaml
# Для каждого репо:
- lint (ruff / flake8)
- test (pytest -v)
- build (docker build)
- security scan (bandit / safety)
```

Trigger: push + PR на main.

### H-2: Docker оптимизация (1 день)

**Репо:** все
**Файлы:** `Dockerfile`

1. Multi-stage builds (builder → runtime)
2. Non-root user
3. Health check в Dockerfile
4. `.dockerignore` актуализация

### H-3: Docker Compose production profile (1 день)

**Репо:** linza-deploy
**Файлы:** `docker-compose.prod.yml`

1. Resource limits (CPU, memory)
2. Restart policies
3. Volume mounts для persistent data
4. Logging driver (json-file с rotation)
5. Secrets management (Docker secrets / .env.prod)

### H-4: Backup strategy (0.5 дня)

**Репо:** linza-deploy
**Файлы:** `scripts/backup.sh`

1. SQLite → daily backup (cp + gzip)
2. S3 bucket → versioning enabled
3. Retention: 30 дней

### H-5: Документация деплоя (0.5 дня)

**Репо:** linza-deploy
**Файлы:** `docs/deployment.md`

1. Требования к серверу (RAM, CPU, disk)
2. Пошаговая установка
3. Переменные окружения (все сервисы)
4. Troubleshooting

## H2. Оценка: 4-5 дней

---

# Бэклог задач (Backlog)

## Приоритет: CRITICAL (блокеры продакшна)

| ID | Задача | Фаза | Репо | Зависимости | Дней |
|----|--------|------|------|-------------|------|
| BL-001 | Шифрование паролей AccessCredential (Fernet) | F-1 | board | — | 1 |
| BL-002 | Rate limiting /api/auth/login (slowapi) | F-2 | board | — | 0.5 |
| BL-003 | Модель ReviewRecord + миграция | D-1 | board | — | 1 |
| BL-004 | CRUD API рецензий (/api/reports/{id}/reviews) | D-2 | board | BL-003 | 1-2 |

## Приоритет: HIGH (ключевой функционал)

| ID | Задача | Фаза | Репо | Зависимости | Дней |
|----|--------|------|------|-------------|------|
| BL-005 | Интеграция vpleer → board review API | D-3 | vpleer | BL-004 | 1-2 |
| BL-006 | Миграция localStorage → API | D-4 | vpleer | BL-005 | 0.5 |
| BL-007 | Accuracy dashboard API | E-1 | board | BL-004 | 1-2 |
| BL-008 | Accuracy dashboard Vue | E-1 | board | BL-007 | 1 |
| BL-009 | Межсервисный API key | F-3 | все | — | 1-2 |
| BL-010 | CORS hardening | F-4 | все | — | 0.5 |
| BL-011 | GitHub Actions CI (все репо) | H-1 | все | — | 1-2 |

## Приоритет: MEDIUM (улучшения)

| ID | Задача | Фаза | Репо | Зависимости | Дней |
|----|--------|------|------|-------------|------|
| BL-012 | Экспорт training data (JSONL) | E-2 | board | BL-004 | 1-2 |
| BL-013 | Model version tracking | E-3 | analytics | — | 1 |
| BL-014 | Confusion matrix API + heatmap | E-4 | board | BL-012, BL-013 | 1-2 |
| BL-015 | Input validation audit | F-5 | все | — | 1 |
| BL-016 | Structured logging (JSON) | G-1 | все | — | 1 |
| BL-017 | Расширенные health checks | G-2 | все | — | 0.5 |
| BL-018 | Circuit breaker (httpx) | G-3 | vpleer, board | — | 1-2 |
| BL-019 | Prometheus метрики | G-4 | все | — | 1-2 |
| BL-020 | Docker multi-stage builds | H-2 | все | — | 1 |

## Приоритет: LOW (nice-to-have)

| ID | Задача | Фаза | Репо | Зависимости | Дней |
|----|--------|------|------|-------------|------|
| BL-021 | Grafana dashboards | G-5 | deploy | BL-019 | 1 |
| BL-022 | Docker Compose production profile | H-3 | deploy | BL-020 | 1 |
| BL-023 | Backup strategy (SQLite + S3) | H-4 | deploy | — | 0.5 |
| BL-024 | Документация деплоя | H-5 | deploy | — | 0.5 |
| BL-025 | Светлая тема linza-board | — | board | — | 2 |
| BL-026 | API versioning (v1/ prefix) | — | все | — | 2 |

## Граф зависимостей

```
BL-001 (encrypt passwords) ─────────────────────────── standalone
BL-002 (rate limiting) ──────────────────────────────── standalone
BL-003 (ReviewRecord) ──→ BL-004 (review API) ──→ BL-005 (vpleer integration)
                                                  ──→ BL-006 (migration)
                                                  ──→ BL-007 (accuracy API) ──→ BL-008 (accuracy Vue)
                                                  ──→ BL-012 (training export) ──→ BL-014 (confusion matrix)
BL-013 (model versions) ────────────────────────────→ BL-014
BL-009 (service keys) ──────────────────────────────── standalone
BL-011 (CI) ─────────────────────────────────────────── standalone
BL-019 (Prometheus) ────────────────────────────────→ BL-021 (Grafana)
BL-020 (Docker builds) ─────────────────────────────→ BL-022 (prod compose)
```

## Рекомендованный порядок спринтов

### Спринт 1 (1-2 недели): Безопасность + Персистентность
- BL-001, BL-002, BL-003, BL-004
- Результат: пароли зашифрованы, review сохраняются в БД

### Спринт 2 (1-2 недели): Интеграция + CI
- BL-005, BL-006, BL-009, BL-010, BL-011
- Результат: vpleer синхронизирует review с board, CI работает

### Спринт 3 (1-2 недели): Аналитика
- BL-007, BL-008, BL-012, BL-013
- Результат: accuracy dashboard, training export, model versions

### Спринт 4 (1-2 недели): Observability + Production
- BL-016, BL-017, BL-018, BL-019, BL-020
- Результат: structured logs, metrics, circuit breakers

### Спринт 5 (1 неделя): Polish
- BL-014, BL-021, BL-022, BL-023, BL-024
- Результат: confusion matrix, Grafana, prod compose, docs

## Общая оценка: 18-31 день (Фазы D-H)

| Фаза | Описание | Дней |
|------|----------|------|
| D | Персистентность рецензий | 4-6 |
| E | Аналитика и метрики | 5-8 |
| F | Безопасность | 4-5 |
| G | Наблюдаемость | 5-7 |
| H | CI/CD и деплой | 4-5 |
| **Итого** | | **22-31** |
