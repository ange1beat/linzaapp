from fastapi import FastAPI

app = FastAPI(
    title="License Check",
    description="Сервис проверки валидности лицензий платформы Linza",
    version="0.1.0",
)


@app.get("/health")
async def health():
    return {"status": "ok", "service": "license-check"}
