from pydantic import BaseModel
import os


class Settings(BaseModel):
    app_name: str = "EOH Backend"
    database_url: str = os.getenv("DATABASE_URL", "sqlite:///./eoh.db")
    ollama_base_url: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    profile_name: str = os.getenv("PROFILE_NAME", "S")
    max_workers: int = int(os.getenv("MAX_WORKERS", "2"))
    heavy_workers: int = int(os.getenv("HEAVY_WORKERS", "1"))
    startup_fail_fast: bool = os.getenv("STARTUP_FAIL_FAST", "false").lower() == "true"


settings = Settings()
