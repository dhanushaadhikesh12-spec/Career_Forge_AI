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

        # If previous message is tool result, synthesize an intelligent response with student names
        if role == "tool":
            import json
            try:
                data = json.loads(last_msg.get("content") or "{}")
            except Exception:
                data = {}

            if "error" in data:
                return LLMResponse(content=f"Error: {data['error']}", tool_calls=[], model=self.model)

            if data.get("ambiguous"):
                return LLMResponse(content=data.get("message", "Multiple matching students found. Please specify the batch or full name."), tool_calls=[], model=self.model)

            # 1. Placement ready students
            if "placement_ready_students" in data:
                ready = data.get("placement_ready_students", [])
                total = data.get("placement_ready_count", len(ready))
                if ready:
                    lines = [f"{idx+1}. **{s['student_name']}** — Readiness: {s.get('readiness_score')}% | Aptitude: {s.get('aptitude_score')}% | Coding: {s.get('coding_score')}%" for idx, s in enumerate(ready)]
                    text = f"**Placement-ready students:**\n\n" + "\n".join(lines) + f"\n\nTotal: {total} students currently meet the placement-readiness threshold."
                else:
                    text = f"No students currently meet the full placement readiness threshold ({total} ready)."
                return LLMResponse(content=text, tool_calls=[], model=self.model)

            # 2. Weak students
            if "weak_students" in data:
                weak = data.get("weak_students", [])
                topic = data.get("topic", "DSA")
                if weak:
                    lines = [f"{idx+1}. **{s['student_name']}** — {topic} accuracy: {s.get('topic_accuracy')}% — Weak: {', '.join(s.get('weak_topics', [])) or 'Fundamental topics'}" for idx, s in enumerate(weak)]
                    text = f"**Students weak in {topic}:**\n\n" + "\n".join(lines)
                else:
                    text = f"No students currently below benchmark in {topic}."
                return LLMResponse(content=text, tool_calls=[], model=self.model)

            # 3. At-risk students
            if "at_risk_students" in data:
                risk = data.get("at_risk_students", [])
                if risk:
                    lines = [f"{idx+1}. **{s['student_name']}** — {s.get('risk_level')} — Readiness: {s.get('readiness_score')}% — {s.get('main_reason')}" for idx, s in enumerate(risk)]
                    text = f"**At-risk students:**\n\n" + "\n".join(lines)
                else:
                    text = "No students are currently flagged as at-risk."
                return LLMResponse(content=text, tool_calls=[], model=self.model)

            # 4. Top students
            if "top_students" in data:
                top = data.get("top_students", [])
                metric = data.get("ranking_metric", "Placement Readiness Score")
                lines = [f"{s.get('rank', idx+1)}. **{s['student_name']}** — {metric}: {s.get('ranking_score', s.get('readiness_score'))}% | Status: {s.get('status')}" for idx, s in enumerate(top)]
                text = f"**Top performers (Ranked by {metric}):**\n\n" + "\n".join(lines)
                return LLMResponse(content=text, tool_calls=[], model=self.model)

            # 5. Single student performance
            if "student_name" in data and "readiness_score" in data and "batch_names" not in data:
                name = data["student_name"]
                text = (
                    f"### {name}\n\n"
                    f"- **Readiness Score:** {data.get('readiness_score')}%\n"
                    f"- **Aptitude Performance:** {data.get('aptitude_score')}%\n"
                    f"- **Coding Performance:** {data.get('coding_score')}%\n"
                    f"- **Strong Areas:** {', '.join(data.get('strong_areas', [])) or 'None recorded'}\n"
                    f"- **Weak Areas:** {', '.join(data.get('weak_areas', [])) or 'None recorded'}\n"
                    f"- **Recent Trend:** {data.get('recent_trend')}\n"
                    f"- **Recommended Action:** {data.get('recommended_action')}"
                )
                return LLMResponse(content=text, tool_calls=[], model=self.model)

            # 6. Batch performance
            if "total_students" in data and "students" in data:
                text = (
                    f"### Batch Overview\n"
                    f"- **Total Students:** {data.get('total_students')}\n"
                    f"- **Average Readiness:** {data.get('avg_readiness')}%\n"
                    f"- **Average Aptitude:** {data.get('avg_aptitude_score')}%\n"
                    f"- **Average Coding:** {data.get('avg_coding_score')}%\n"
                    f"- **Placement Ready:** {data.get('placement_ready_count')}\n"
                    f"- **At Risk:** {data.get('at_risk_count')}\n\n"
                    f"### Student Performance\n\n"
                    f"| Student | Readiness | Aptitude | Coding | Status |\n"
                    f"| :--- | :---: | :---: | :---: | :---: |\n"
                )
                for s in data.get("students", []):
                    text += f"| {s['student_name']} | {s['readiness']}% | {s['aptitude']}% | {s['coding']}% | {s['status']} |\n"
                return LLMResponse(content=text, tool_calls=[], model=self.model)

            # 7. Malpractice
            if "students_requiring_review" in data:
                rev = data.get("students_requiring_review", [])
                lines = [f"{idx+1}. **{s['student_name']}** — {s.get('risk_level')} anomaly risk — {s.get('reason')}" for idx, s in enumerate(rev)]
                text = f"**Students requiring review ({data.get('test_title')}):**\n\n" + "\n".join(lines)
                return LLMResponse(content=text, tool_calls=[], model=self.model)

            return LLMResponse(
                content="Based on the database records, here is the analyzed breakdown of your cohort's performance.",
                tool_calls=[],
                model=self.model,
            )

        # Detect tool call from user query

        # Student-specific questions (e.g., "How is Rahul performing?", "How is Rahul Kumar doing?")
        import re
        name_match = re.search(r"\b(how is|how's|about)\s+([a-zA-Z\s]+?)(?:\s+(?:performing|doing|in coding|scores?))?\??$", content)
        named_students = ["rahul kumar", "rahul sharma", "rahul", "priya", "priya s", "arun", "arun k", "meena", "karthik", "alice", "bob"]
        queried_name = None
        for n in named_students:
            if re.search(r"\b" + re.escape(n) + r"\b", content):
                queried_name = n.title()
                break

        if queried_name and ("how is" in content or "performing" in content or "doing" in content or "performance" in content):
            return LLMResponse(
                content="",
                tool_calls=[
                    ToolCall(
                        id="call_mock_student_perf",
                        name="get_student_performance",
                        arguments={"student_name": queried_name},
                    )
                ],
                model=self.model,
            )

        if "top" in content or "highest" in content or "better in coding" in content or "best" in content:
            metric = "coding" if ("coding" in content or "code" in content) else ("aptitude" if "aptitude" in content else "readiness")
            return LLMResponse(
                content="",
                tool_calls=[
                    ToolCall(
                        id="call_mock_top",
                        name="get_top_students",
                        arguments={"metric": metric, "limit": 5},
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

        if "risk" in content or "at-risk" in content or "need help" in content or "improvement" in content or "attention" in content or "struggling" in content:
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

        if "reasoning" in content or "weak" in content or "arrays" in content or "dsa" in content or "trees" in content or "graphs" in content or "poorly" in content:
            topic = "Logical Reasoning" if "reasoning" in content else ("Arrays" if "arrays" in content else ("DSA" if "dsa" in content else None))
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

        if "malpractice" in content or "suspicious" in content or "cheat" in content or "violation" in content:
            return LLMResponse(
                content="",
                tool_calls=[
                    ToolCall(
                        id="call_mock_malpractice",
                        name="get_malpractice_summary",
                        arguments={},
                    )
                ],
                model=self.model,
            )

        if "summary" in content or "overview" in content or "batch" in content or "cohort" in content:
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
