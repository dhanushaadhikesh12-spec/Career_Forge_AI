"""
AI / LLM Provider Abstraction.
Provides modular interface for LLM execution supporting Ollama (Gemma 12B)
and mock provider for testing/fallback.
"""
from __future__ import annotations
import logging
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
import httpx
from pydantic import BaseModel
from app.core.config import settings

logger = logging.getLogger(__name__)


class ToolCall(BaseModel):
    id: str
    name: str
    arguments: Dict[str, Any]


class LLMResponse(BaseModel):
    content: str = ""
    tool_calls: List[ToolCall] = []
    model: str = ""
    finish_reason: Optional[str] = None


class AIProviderError(Exception):
    """Raised when the AI provider is unavailable or fails."""
    pass


class LLMProvider(ABC):
    """Abstract Base Class for LLM inference providers."""

    @abstractmethod
    async def chat(
        self,
        messages: List[Dict[str, Any]],
        tools: Optional[List[Dict[str, Any]]] = None,
        temperature: float = 0.2,
    ) -> LLMResponse:
        pass

    @abstractmethod
    async def is_available(self) -> bool:
        pass


class OllamaProvider(LLMProvider):
    """Ollama API integration specifically optimized for Gemma 12B (gemma4:12b-mlx)."""

    def __init__(
        self,
        base_url: Optional[str] = None,
        model: Optional[str] = None,
        timeout: float = 90.0,
    ):
        self.base_url = (base_url or settings.OLLAMA_BASE_URL).rstrip("/")
        self.model = model or settings.OLLAMA_MODEL or "gemma4:12b-mlx"
        self.timeout = timeout

    async def is_available(self) -> bool:
        """Pings Ollama and verifies model presence."""
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                res = await client.get(f"{self.base_url}/api/tags")
                if res.status_code == 200:
                    data = res.json()
                    models = [m.get("name") for m in data.get("models", [])]
                    return any(self.model in m for m in models)
        except Exception as e:
            logger.debug("Ollama availability check failed: %s", e)
        return False

    async def chat(
        self,
        messages: List[Dict[str, Any]],
        tools: Optional[List[Dict[str, Any]]] = None,
        temperature: float = 0.2,
    ) -> LLMResponse:
        url = f"{self.base_url}/api/chat"

        # Format tools if provided
        formatted_tools = None
        if tools:
            formatted_tools = [
                {
                    "type": "function",
                    "function": t
                }
                for t in tools
            ]

        payload: Dict[str, Any] = {
            "model": self.model,
            "messages": messages,
            "stream": False,
            "options": {
                "temperature": temperature,
            }
        }
        if formatted_tools:
            payload["tools"] = formatted_tools

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                resp = await client.post(url, json=payload)
                if resp.status_code != 200:
                    raise AIProviderError(f"Ollama returned HTTP {resp.status_code}: {resp.text}")

                data = resp.json()
                msg = data.get("message", {})
                content = msg.get("content", "") or ""

                parsed_tool_calls: List[ToolCall] = []
                for tc in msg.get("tool_calls", []):
                    fn = tc.get("function", {})
                    name = fn.get("name", "")
                    raw_args = fn.get("arguments", {})
                    args = raw_args if isinstance(raw_args, dict) else {}
                    call_id = tc.get("id", f"call_{name}")
                    parsed_tool_calls.append(ToolCall(id=call_id, name=name, arguments=args))

                return LLMResponse(
                    content=content,
                    tool_calls=parsed_tool_calls,
                    model=data.get("model", self.model),
                    finish_reason=data.get("done_reason"),
                )

        except httpx.ConnectError:
            raise AIProviderError(
                f"Cannot connect to Ollama at {self.base_url}. Ensure Ollama is running (`ollama serve`)."
            )
        except httpx.TimeoutException:
            raise AIProviderError(
                f"Ollama inference timed out after {self.timeout}s for model {self.model}."
            )
        except Exception as e:
            if isinstance(e, AIProviderError):
                raise
            raise AIProviderError(f"Unexpected error communicating with Ollama: {str(e)}")


class MockLLMProvider(LLMProvider):
    """Deterministic mock provider for automated unit tests & offline scenarios."""

    def __init__(self, model: str = "mock-gemma4:12b-mlx"):
        self.model = model

    async def is_available(self) -> bool:
        return True

    async def chat(
        self,
        messages: List[Dict[str, Any]],
        tools: Optional[List[Dict[str, Any]]] = None,
        temperature: float = 0.2,
    ) -> LLMResponse:
        # Check last message
        last_msg = messages[-1]
        role = last_msg.get("role")
        content = (last_msg.get("content") or "").lower()

        # If previous message is tool result, summarize
        if role == "tool":
            return LLMResponse(
                content="Based on the database records, here is the analyzed breakdown of your cohort's performance.",
                tool_calls=[],
                model=self.model,
            )

        # Detect tool call from user query
        if "reasoning" in content or "weak" in content or "arrays" in content:
            topic = "Logical Reasoning" if "reasoning" in content else ("Arrays" if "arrays" in content else None)
            return LLMResponse(
                content="",
                tool_calls=[
                    ToolCall(
                        id="call_mock_weak",
                        name="get_weak_students",
                        arguments={"topic": topic} if topic else {},
                    )
                ],
                model=self.model,
            )

        if "ready" in content or "placement" in content:
            return LLMResponse(
                content="",
                tool_calls=[
                    ToolCall(
                        id="call_mock_readiness",
                        name="get_placement_readiness",
                        arguments={},
                    )
                ],
                model=self.model,
            )

        if "summary" in content or "overview" in content or "batch" in content:
            return LLMResponse(
                content="",
                tool_calls=[
                    ToolCall(
                        id="call_mock_summary",
                        name="get_batch_summary",
                        arguments={},
                    )
                ],
                model=self.model,
            )

        if "risk" in content or "at-risk" in content:
            return LLMResponse(
                content="",
                tool_calls=[
                    ToolCall(
                        id="call_mock_risk",
                        name="get_at_risk_students",
                        arguments={},
                    )
                ],
                model=self.model,
            )

        if "coding" in content:
            return LLMResponse(
                content="",
                tool_calls=[
                    ToolCall(
                        id="call_mock_coding",
                        name="get_coding_performance",
                        arguments={},
                    )
                ],
                model=self.model,
            )

        if "malpractice" in content or "suspicious" in content:
            return LLMResponse(
                content="",
                tool_calls=[
                    ToolCall(
                        id="call_mock_malpractice",
                        name="get_malpractice_summary",
                        arguments={"test_id": 1},
                    )
                ],
                model=self.model,
            )

        return LLMResponse(
            content="I am your CareerForge AI Assistant powered by Gemma 12B. I can help analyze batch progress, weak areas, placement readiness, and malpractice trends.",
            tool_calls=[],
            model=self.model,
        )


def get_llm_provider(force_mock: bool = False) -> LLMProvider:
    """Returns active LLM provider (Ollama by default, Mock in test mode)."""
    if force_mock or settings.APP_ENV == "test":
        return MockLLMProvider()
    return OllamaProvider()
