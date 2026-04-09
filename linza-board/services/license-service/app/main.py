from fastapi import FastAPI

app = FastAPI(
    title="License Service",
    description="Сервис управления лицензиями платформы Linza",
    version="0.1.0",
)


@app.get("/health")
async def health():
    return {"status": "ok", "service": "license-service"}
