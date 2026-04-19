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
    receptionist_model: str = os.getenv("RECEPTIONIST_MODEL", "llama3.2:3b")
    agent_timeout_seconds: int = int(os.getenv("AGENT_TIMEOUT_SECONDS", "45"))
    receptionist_timeout_seconds: int = int(
        os.getenv("RECEPTIONIST_TIMEOUT_SECONDS", os.getenv("AGENT_TIMEOUT_SECONDS", "120"))
    )
    disable_openai: bool = os.getenv("DISABLE_OPENAI", "true").lower() == "true"
    agent_definition_db_enabled: bool = os.getenv("AGENT_DEFINITION_DB_ENABLED", "true").lower() == "true"
    agent_definition_fallback_enabled: bool = os.getenv("AGENT_DEFINITION_FALLBACK_ENABLED", "true").lower() == "true"


settings = Settings()
