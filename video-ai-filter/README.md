# Video AI Filter API

REST API: загрузка видео (в том числе очень больших файлов — потоковая запись на диск), выбор кадра каждые **0.5 с** через OpenCV, отправка кадров в **мультимодальную** модель через OpenAI-совместимый `chat.completions` API. Два режима:

1. **OpenRouter** — облако, ключ API, модели вроде [Qwen3 VL](https://openrouter.ai/qwen/qwen3-vl-8b-thinking).
2. **vLLM** — свой сервер [vLLM](https://docs.vllm.ai/en/stable/serving/openai_compatible_server.html) с OpenAI-compatible HTTP API (`/v1/chat/completions`), без OpenRouter; нужна **vision-модель**, поднятая через `vllm serve`.

### Аудио (Whisper)

После разбора **кадров** по тому же джобу: из видео извлекается дорожка (**нужен [ffmpeg](https://ffmpeg.org/) в `PATH`**), транскрипция **[faster-whisper](https://github.com/SYSTRAN/faster-whisper)** (по умолчанию модель **`tiny`** — лёгкая), затем **тот же** LLM (OpenRouter/vLLM) получает текст и те же **категории** из конструктора (или общий текстовый промпт). Результат в `GET /jobs/{id}/results` в поле **`audio`** и в экспорте JSON (`audio` внутри отчёта).

## Требования

- Python 3.11+
- Либо ключ **OpenRouter** (`OPENROUTER_API_KEY`), либо доступный **vLLM** и заданные `VLLM_BASE_URL` + `VLLM_MODEL`

## Установка

```bash
cd video-ai-filter
python3 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# Отредактируйте .env и вставьте OPENROUTER_API_KEY
```

## Запуск

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

Документация интерактивно: `http://127.0.0.1:8000/docs`.

**Веб-интерфейс (конструктор промпта):** откройте `http://127.0.0.1:8000/` — добавление категорий (имя + описание), предпросмотр промпта, загрузка видео и таблица вердиктов по кадрам.

## Docker

Образ: Python 3.12, **ffmpeg** уже внутри, данные (загрузки и SQLite) в volume **`/data`**.

```bash
cp .env.example .env
# укажите OPENROUTER_API_KEY или режим vLLM

docker compose up --build
```

- API и UI: **http://127.0.0.1:8000** (если порт занят — в `.env` добавьте `HOST_PORT=8080` и откройте **http://127.0.0.1:8080**)
- Первый запуск **Whisper** может скачать модель с Hugging Face (нужен выход в интернет).

Только образ без Compose:

```bash
docker build -t video-ai-filter .
docker run --rm -p 8000:8000 --env-file .env \
  -e UPLOAD_DIR=/data/uploads -e DB_PATH=/data/jobs.db \
  -v video-ai-data:/data \
  --add-host=host.docker.internal:host-gateway \
  video-ai-filter
```

Если **vLLM** крутится на машине-хосте, в `.env` задайте `VLLM_BASE_URL=http://host.docker.internal:8001/v1` (в `docker-compose.yml` уже добавлен `extra_hosts`).

## Переменные окружения

| Переменная | Описание |
|------------|----------|
| `INFERENCE_BACKEND` | `openrouter` (по умолчанию) или `vllm` |
| `OPENROUTER_API_KEY` | Нужен при `INFERENCE_BACKEND=openrouter` |
| `OPENROUTER_BASE_URL` | По умолчанию `https://openrouter.ai/api/v1` |
| `OPENROUTER_MODEL` | По умолчанию `qwen/qwen3-vl-8b-thinking` |
| `VLLM_BASE_URL` | База API до `/v1`, напр. `http://127.0.0.1:8001/v1` |
| `VLLM_API_KEY` | Часто `EMPTY`; если vLLM за прокси с ключом — подставьте |
| `VLLM_MODEL` | Имя модели как в `vllm serve` (должна поддерживать изображения в чате) |
| `AUDIO_TRANSCRIPTION_ENABLED` | `true` / `false` — Whisper + модерация речи после кадров |
| `FFMPEG_PATH` | Бинарник ffmpeg (по умолчанию `ffmpeg`) |
| `WHISPER_MODEL_SIZE` | `tiny` (легче всего), `base`, `small`, … |
| `WHISPER_DEVICE` | `auto`, `cpu`, `cuda` |
| `WHISPER_COMPUTE_TYPE` | `auto` (cpu→int8, cuda→float16), или явно `int8` / `float16` |
| `MAX_TRANSCRIPT_CHARS_FOR_LLM` | Обрезка текста перед запросом к LLM |
| `UPLOAD_DIR` | Каталог загрузок (по умолчанию `./data/uploads`) |
| `DB_PATH` | SQLite (по умолчанию `./data/jobs.db`) |
| `MAX_UPLOAD_BYTES` | Лимит размера файла, `0` = без лимита |
| `ALLOWED_IMPORT_DIR` | Если задан — включается `POST /jobs/from-path` только для путей внутри этого каталога |
| `DEFAULT_PROMPT` | Промпт по умолчанию, если не передан в запросе |

Опционально заголовки для OpenRouter: `HTTP_REFERER`, `HTTP_TITLE` в настройках (см. `app/config.py`).

### Пример: vLLM локально

Поднимите vLLM на другом порту, чем это приложение (например **8001**), с vision-моделью по [документации vLLM](https://docs.vllm.ai/en/stable/serving/openai_compatible_server.html). В `.env`:

```env
INFERENCE_BACKEND=vllm
VLLM_BASE_URL=http://127.0.0.1:8001/v1
VLLM_MODEL=Qwen/Qwen2-VL-7B-Instruct
```

Этот сервис шлёт те же сообщения (`text` + `image_url` base64), что и для OpenRouter.

## API

- **`GET /meta/inference`** — без секретов: активный `INFERENCE_BACKEND` и имя модели (для проверки конфига).
- **`GET /`** — статическая страница с конструктором категорий и загрузкой видео.
- **`POST /prompt/preview`** — JSON `{"categories": [{"name":"nude","description":"…"}], "extra_instructions": null}` → собранный текст промпта.
- **`POST /jobs`** — `multipart/form-data`: поле `file` (видео), опционально `prompt` (доп. инструкции), **`categories_json`** (JSON-массив тех же категорий — если задан, промпт собирается из конструктора), `max_frames`, `max_duration_sec`.
- **`POST /jobs/from-path`** — JSON `{"path": "/abs/path/video.mp4", "categories": [...], ...}`: файл уже на сервере (нужен `ALLOWED_IMPORT_DIR`). Сначала пробуется hard link, иначе копирование (большие копии не блокируют event loop).
- **`GET /jobs/{job_id}`** — статус и прогресс; при `completed` в ответе есть **`export_url`** (`/jobs/{id}/export`) для выгрузки JSON.
- **`GET /jobs/{job_id}/results`** — JSON с массивом `results` по кадрам (после `completed`).
- **`GET /jobs/{job_id}/export`** — удобная выгрузка файла/JSON:
  - **`format=time-based`** (по умолчанию) — отчёт `TIME_BASED_REPORT` (`source_info`, `detections`, интервалы по кадрам).
  - **`format=raw`** — объект `RAW_FRAME_RESULTS` с тем же массивом, что в БД (каждый сэмпл: `time_sec`, `frame_index`, `verdict_raw`, …).
  - **`attachment=true`** (по умолчанию) — заголовок `Content-Disposition` для скачивания файла; **`attachment=false`** — ответ без скачивания (удобно для `curl … | jq`).
- **`GET /jobs/{job_id}/report.json`** — то же, что `export?format=time-based&attachment=true` (совместимость).
- **`DELETE /jobs/{job_id}`** — отмена активной джобы (`cancelling`) или удаление записи для завершённых/упавших (`deleted`).

### Пример: загрузка и опрос

```bash
curl -s -X POST "http://127.0.0.1:8000/jobs" \
  -F "file=@./sample.mp4" \
  -F 'categories_json=[{"name":"smoking","description":"Видимое курение в кадре."}]' \
  -F "max_frames=10"

curl -s "http://127.0.0.1:8000/jobs/<job_id>"
curl -s "http://127.0.0.1:8000/jobs/<job_id>/results"
curl -sOJ "http://127.0.0.1:8000/jobs/<job_id>/export?format=time-based"
curl -s "http://127.0.0.1:8000/jobs/<job_id>/export?format=raw&attachment=false" | jq .
```

## Большие файлы (до ~14 ГБ) и прокси

- Сервер пишет тело запроса **чанками по 1 MiB**, не загружая файл в память целиком.
- Для nginx (и аналогов) увеличьте **`client_max_body_size`** и таймауты (`proxy_read_timeout`, `send_timeout`). Иначе длинная загрузка оборвётся.
- Чтобы не передавать десятки гигабайт по HTTP, положите файл на машину с API и вызовите **`POST /jobs/from-path`** с путём внутри `ALLOWED_IMPORT_DIR`.

## Стоимость и нагрузка

Примерно **2 запроса к модели на секунду** длительности ролика (шаг 0.5 с). Ограничивайте объём через `max_frames` и `max_duration_sec`. Цены на токены см. на [странице модели OpenRouter](https://openrouter.ai/qwen/qwen3-vl-8b-thinking).

## Безопасность

API без аутентификации подходит для локальной разработки. Для публичной сети добавьте reverse-proxy с авторизацией или API-key middleware.
