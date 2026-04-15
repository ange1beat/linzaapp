# CPU image: ffmpeg + Python API (OpenCV, faster-whisper)
FROM python:3.12-slim-bookworm

RUN apt-get update \
    && apt-get install -y --no-install-recommends ffmpeg libglib2.0-0 fonts-dejavu-core \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app ./app
COPY static ./static
COPY linza-detector-logo.svg ./
COPY pyproject.toml ./

# PNG для PDF (reportlab); rsvg только на этапе сборки
RUN apt-get update \
    && apt-get install -y --no-install-recommends librsvg2-bin \
    && rsvg-convert -w 260 /app/linza-detector-logo.svg -o /app/linza-logo.png \
    && apt-get purge -y librsvg2-bin \
    && rm -rf /var/lib/apt/lists/*

RUN mkdir -p /data/uploads

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    UPLOAD_DIR=/data/uploads \
    DB_PATH=/data/jobs.db

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
