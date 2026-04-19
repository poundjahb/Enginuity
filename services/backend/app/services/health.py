import httpx

from app.config import settings


async def check_ollama_health() -> tuple[bool, str | None]:
    url = f"{settings.ollama_base_url.rstrip('/')}/api/tags"
    try:
        async with httpx.AsyncClient(timeout=3.0) as client:
            response = await client.get(url)
        if response.status_code == 200:
            return True, None
        return False, f"Unexpected Ollama status code: {response.status_code}"
    except Exception as exc:
        return False, str(exc)
