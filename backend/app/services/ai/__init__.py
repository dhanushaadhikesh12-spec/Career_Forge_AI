"""
CareerForge AI Assistant & LLM Provider Package.
"""
from app.services.ai.provider import LLMProvider, OllamaProvider, MockLLMProvider, get_llm_provider
from app.services.ai.assistant import process_trainer_query, AssistantResponse, ChatMessage

__all__ = [
    "LLMProvider",
    "OllamaProvider",
    "MockLLMProvider",
    "get_llm_provider",
    "process_trainer_query",
    "AssistantResponse",
    "ChatMessage",
]
