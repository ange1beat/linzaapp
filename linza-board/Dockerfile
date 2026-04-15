# Stage 1: Build Vue frontend
FROM node:20-alpine AS frontend-build
WORKDIR /app

# Сборка в Docker часто падает на npm из‑за таймаутов/нестабильной сети — больше ретраев и ожидание.
# При необходимости: docker compose build --build-arg NPM_REGISTRY=https://registry.npmmirror.com
ARG NPM_REGISTRY=https://registry.npmjs.org/

COPY package.json package-lock.json ./
RUN npm config set registry "${NPM_REGISTRY}" \
  && npm config set fetch-retries 15 \
  && npm config set fetch-retry-mintimeout 30000 \
  && npm config set fetch-retry-maxtimeout 180000 \
  && npm config set fetch-timeout 600000 \
  && npm config set audit false \
  && npm config set fund false \
  && npm ci --no-audit --no-fund
COPY . .
RUN npm run build

# Stage 2: Production (Python + FastAPI)
FROM python:3.12-slim
WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY backend/ ./backend/
COPY scripts/ ./scripts/
COPY alembic.ini ./
COPY alembic/ ./alembic/
COPY --from=frontend-build /app/dist ./dist

ENV PORT=8000
EXPOSE 8000

CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
