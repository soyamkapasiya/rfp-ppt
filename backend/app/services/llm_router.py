from enum import Enum


class TaskType(str, Enum):
    FAST_EXTRACT = "fast_extract"
    REASONING = "reasoning"
    WRITING = "writing"


class RoutedModel:
    def __init__(self, provider: str, model: str):
        self.provider = provider
        self.model = model


def get_chat_model(task: TaskType) -> RoutedModel:
    if task == TaskType.FAST_EXTRACT:
        return RoutedModel(provider="ollama", model="llama3.1:8b")
    if task == TaskType.REASONING:
        return RoutedModel(provider="groq", model="llama-3.3-70b-versatile")
    return RoutedModel(provider="gemini", model="gemini-1.5-flash")
