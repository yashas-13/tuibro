"""Ollama provider - local model server."""
import json
import httpx
from tuibro.agent.providers.base import BaseProvider, ProviderResponse, TokenUsage, ToolCall
from tuibro.agent.providers import register_provider


class OllamaProvider(BaseProvider):
    name = "ollama"
    models = ["llama3.1", "mistral", "codellama", "gemma2", "phi3"]
    default_model = "llama3.1"

    def __init__(self, api_key=None, model=None, base_url=None):
        super().__init__(api_key or "", model, base_url or "http://localhost:11434")

    async def complete(self, messages, tools=None):
        payload = {"model": self.model, "messages": messages, "stream": False}
        if tools:
            payload["tools"] = tools
        try:
            async with httpx.AsyncClient(timeout=120.0) as client:
                resp = await client.post(f"{self.base_url}/api/chat", json=payload)
                if resp.status_code != 200:
                    return ProviderResponse(error=f"HTTP {resp.status_code}: {resp.text[:200]}")
                return self._parse_response(resp.json())
        except httpx.ConnectError:
            return ProviderResponse(error="Ollama not running. Start with: ollama serve")
        except Exception as e:
            return ProviderResponse(error=str(e))

    def _parse_response(self, data: dict) -> ProviderResponse:
        msg = data.get("message", {})
        tool_calls = []
        for tc in msg.get("tool_calls", []):
            func = tc.get("function", {})
            tool_calls.append(ToolCall(name=func.get("name", ""), arguments=func.get("arguments", {})))
        usage_data = data.get("prompt_eval_count", 0)
        usage = TokenUsage(prompt_tokens=usage_data, completion_tokens=data.get("eval_count", 0))
        usage.total_tokens = usage.prompt_tokens + usage.completion_tokens
        return ProviderResponse(
            content=msg.get("content", ""),
            tool_calls=tool_calls,
            usage=usage,
            finish_reason="stop",
        )


register_provider("ollama", OllamaProvider)
