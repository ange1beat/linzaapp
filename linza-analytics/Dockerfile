FROM python:3.12-slim
WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir --upgrade pip \
 && pip install --no-cache-dir -r requirements.txt \
 && python -c "import httpx; import fastapi; print('analytics-service deps OK')"

COPY app/ ./app/
RUN mkdir -p /app/data

RUN adduser --disabled-password --no-create-home appuser && \
    chown -R appuser:appuser /app/data
USER appuser

EXPOSE 8002

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8002"]
