import os


STORAGE_SERVICE_URL = os.getenv("STORAGE_SERVICE_URL", "http://localhost:8001")
ANALYTICS_SERVICE_URL = os.getenv("ANALYTICS_SERVICE_URL", "http://localhost:8002")
SERVICE_API_KEY = os.getenv("SERVICE_API_KEY", "").strip()
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "http://localhost:5173").split(",")

TEMP_DIR = os.getenv("TEMP_DIR", "/tmp/vpleer")
CHUNK_SIZE = 1024 * 1024  # 1 MB for streaming

# Таймауты для HTTP-клиента (B6)
HTTP_CONNECT_TIMEOUT = 30
HTTP_READ_TIMEOUT = 3600  # 1 час — для 20ГБ+ файлов на медленных сетях

# Таймауты для ffmpeg/ffprobe операций
FFPROBE_TIMEOUT = 60              # 60 секунд для ffprobe
FFMPEG_THUMBNAIL_TIMEOUT = 90     # 90 секунд для генерации превью
FFMPEG_FRAGMENT_TIMEOUT = 240     # 4 минуты для извлечения фрагмента
FFMPEG_HLS_TIMEOUT = 900          # 15 минут для полного HLS-транскодирования

# Фоновая очистка кэша (B7)
CACHE_CLEANUP_INTERVAL = 600  # 10 минут
CACHE_FILE_TTL = 3600  # 1 час
MAX_CACHE_SIZE = 50 * 1024 * 1024 * 1024  # 50 ГБ
