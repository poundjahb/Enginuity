import httpx

from app.config import settings
from app.agents.receptionist import normalize_model_name


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


async def fetch_ollama_models() -> tuple[list[str], str | None]:
    url = f"{settings.ollama_base_url.rstrip('/')}/api/tags"
    try:
        async with httpx.AsyncClient(timeout=3.0) as client:
            response = await client.get(url)
        if response.status_code != 200:
            return [], f"Unexpected Ollama status code: {response.status_code}"

        payload = response.json()
        models = payload.get("models", [])
        names = [model.get("name", "") for model in models if model.get("name")]
        return names, None
    except Exception as exc:
        return [], str(exc)


async def check_receptionist_model_available() -> tuple[bool, str | None]:
    models, error = await fetch_ollama_models()
    if error:
        return False, error

    configured_model = normalize_model_name(settings.receptionist_model)
    if configured_model in models:
        return True, None

    return (
        False,
        f"Configured RECEPTIONIST_MODEL '{configured_model}' is not available in Ollama. "
        f"Installed models: {', '.join(models) if models else 'none'}.",
    )


async def check_analyst_model_available() -> tuple[bool, str | None]:
    models, error = await fetch_ollama_models()
    if error:
        return False, error

    configured_model = normalize_model_name(settings.analyst_model)
    if configured_model in models:
        return True, None

    return (
        False,
        f"Configured ANALYST_MODEL '{configured_model}' is not available in Ollama. "
        f"Installed models: {', '.join(models) if models else 'none'}.",
    )
