from fastapi import FastAPI

from app.config import settings
from app.api.routes import router


app = FastAPI(
    title=settings.app_name,
    description="Adaptive and Context-Aware LLM Question Answering System",
    version="0.1.0"
)

app.include_router(router)


@app.get("/")
async def root():
    return {
        "application": "SYNTRA",
        "status": "online"
    }


@app.get("/health")
async def health():
    return {
        "status": "healthy"
    }