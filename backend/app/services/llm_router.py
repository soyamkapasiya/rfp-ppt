from __future__ import annotations

from enum import Enum

import httpx

from app.core.config import settings


class TaskType(str, Enum):
    FAST_EXTRACT = "fast_extract"
    REASONING = "reasoning"
    WRITING = "writing"
    VISION = "vision"
    THOUGHTS = "thoughts"
    RAG_EVAL = "rag_eval"
    SUGGEST_ANSWER = "suggest_answer"  # New task type for answering mined questions
    COMPETITOR_ANALYSIS = "competitor_analysis"


def _call_ollama(prompt: str, model: str) -> str:
    try:
        response = httpx.post(
            f"{settings.ollama_base_url}/api/generate",
            json={"model": model, "prompt": prompt, "stream": False},
            timeout=30,
        )
        response.raise_for_status()
        return response.json().get("response", "")
    except Exception as e:
        logger.warning("Ollama call failed: %s", e)
        raise


def _call_openrouter(prompt: str, model: str, images: list[str] | None = None) -> str:
    if not settings.openrouter_api_key:
        raise RuntimeError("OPENROUTER_API_KEY not configured")

    content: list[dict[str, Any]] = [{"type": "text", "text": prompt}]
    if images:
        for img in images:
            content.append({
                "type": "image_url",
                "image_url": {"url": img}
            })

    response = httpx.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {settings.openrouter_api_key}",
            "HTTP-Referer": "https://rfp-ai-platform.com", 
            "X-Title": "RFP AI Platform"
        },
        json={
            "model": model,
            "messages": [{"role": "user", "content": content}]
        },
        timeout=60,
    )
    response.raise_for_status()
    return response.json()["choices"][0]["message"]["content"]


def generate_text(task: TaskType, prompt: str, images: list[str] | None = None) -> str:
    # Optimized Task-Model Mapping for Token Efficiency & Quality
    model_chain = {
        TaskType.THOUGHTS: [("ollama", "qwen2.5:7b"), ("openrouter", "google/gemini-flash-1.5-8b")],
        TaskType.FAST_EXTRACT: [("ollama", "llama3.2:3b"), ("openrouter", "google/gemini-flash-1.5-8b")],
        TaskType.REASONING: [("openrouter", "meta-llama/llama-3.3-70b-instruct"), ("openrouter", "google/gemini-flash-1.5")],
        TaskType.WRITING: [("openrouter", "anthropic/claude-3.5-sonnet"), ("openrouter", "google/gemini-flash-1.5")],
        TaskType.VISION: [("openrouter", "openai/gpt-4o"), ("openrouter", "google/gemini-flash-1.5-vision")],
        TaskType.RAG_EVAL: [("openrouter", "meta-llama/llama-3.1-8b-instruct"), ("ollama", "llama3:8b")],
        TaskType.SUGGEST_ANSWER: [("openrouter", "google/gemini-flash-1.5"), ("ollama", "llama3.1:8b")],
        TaskType.COMPETITOR_ANALYSIS: [("openrouter", "meta-llama/llama-3.1-405b-instruct"), ("openrouter", "anthropic/claude-3.5-sonnet")],
    }[task]

    errors = []
    for provider, model in model_chain:
        try:
            if provider == "ollama":
                return _call_ollama(prompt, model)
            if provider == "openrouter":
                return _call_openrouter(prompt, model, images=images)
        except Exception as exc:
            errors.append(f"{provider}:{exc}")

    raise RuntimeError(f"No LLM provider available: {' | '.join(errors)}")
