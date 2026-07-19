"""Base LLM provider abstraction."""
import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any

logger = logging.getLogger("tuibro.providers")


@dataclass
class TokenUsage:
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0


@dataclass
class ToolCall:
    id: str = ""
    name: str = ""
    arguments: dict = field(default_factory=dict)


@dataclass
class ProviderResponse:
    content: str = ""
    tool_calls: list = field(default_factory=list)
    usage: TokenUsage = field(default_factory=TokenUsage)
    finish_reason: str = ""
    error: str = ""

    @property
    def has_tool_calls(self) -> bool:
        return len(self.tool_calls) > 0

    @property
    def is_done(self) -> bool:
        return self.finish_reason == "stop" or self.finish_reason == "end_turn"


class BaseProvider(ABC):
    name: str = "base"
    models: list[str] = []
    default_model: str = ""

    def __init__(self, api_key: str, model: str = None, base_url: str = None):
        self.api_key = api_key
        self.model = model or self.default_model
        self.base_url = base_url

    @abstractmethod
    async def complete(self, messages: list[dict], tools: list[dict] = None) -> ProviderResponse:
        """Send a completion request and return a response."""
        ...

    def _headers(self) -> dict:
        return {"Content-Type": "application/json"}

    def _format_messages(self, messages: list[dict]) -> list[dict]:
        """Override for providers with non-standard message formats."""
        return messages

    def _format_tools(self, tools: list[dict]) -> list[dict]:
        """Override for providers with non-standard tool formats."""
        return tools
