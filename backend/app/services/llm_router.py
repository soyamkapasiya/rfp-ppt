from __future__ import annotations

from enum import Enum

import httpx

from app.core.config import settings


class TaskType(str, Enum):
    FAST_EXTRACT = "fast_extract"
    REASONING = "reasoning"
    WRITING = "writing"


def _call_ollama(prompt: str, model: str) -> str:
    response = httpx.post(
        f"{settings.ollama_base_url}/api/generate",
        json={"model": model, "prompt": prompt, "stream": False},
        timeout=30,
    )
    response.raise_for_status()
    return response.json().get("response", "")


def _call_openrouter(prompt: str, model: str) -> str:
    if not settings.openrouter_api_key:
        raise RuntimeError("OPENROUTER_API_KEY not configured")

    response = httpx.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers={"Authorization": f"Bearer {settings.openrouter_api_key}"},
        json={"model": model, "messages": [{"role": "user", "content": prompt}]},
        timeout=45,
    )
    response.raise_for_status()
    return response.json()["choices"][0]["message"]["content"]


def generate_text(task: TaskType, prompt: str) -> str:
    model_chain = {
        TaskType.FAST_EXTRACT: [("ollama", "llama3.1:8b"), ("openrouter", "meta-llama/llama-3.1-8b-instruct")],
        TaskType.REASONING: [("ollama", "llama3.1:8b"), ("openrouter", "meta-llama/llama-3.3-70b-instruct")],
        TaskType.WRITING: [("ollama", "llama3.1:8b"), ("openrouter", "google/gemini-flash-1.5")],
    }[task]

    errors = []
    for provider, model in model_chain:
        try:
            if provider == "ollama":
                return _call_ollama(prompt, model)
            if provider == "openrouter":
                return _call_openrouter(prompt, model)
        except Exception as exc:
            errors.append(f"{provider}:{exc}")

    raise RuntimeError(f"No LLM provider available: {' | '.join(errors)}")
