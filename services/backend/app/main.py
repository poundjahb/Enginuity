from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.db import Base, engine
from app.routes.requests import router as requests_router
from app.services.health import check_ollama_health

app = FastAPI(title=settings.app_name)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def on_startup():
    Base.metadata.create_all(bind=engine)
    if settings.startup_fail_fast:
        healthy, error = await check_ollama_health()
        if not healthy:
            raise RuntimeError(f"Ollama dependency unavailable at startup: {error}")


@app.get("/health")
async def health():
    return {
        "status": "ok",
        "profile": {
            "name": settings.profile_name,
            "max_workers": settings.max_workers,
            "heavy_workers": settings.heavy_workers,
        },
    }


@app.get("/health/dependencies")
async def dependency_health():
    healthy, error = await check_ollama_health()
    return {
        "ollama": {
            "healthy": healthy,
            "base_url": settings.ollama_base_url,
            "error": error,
        }
    }


app.include_router(requests_router)
