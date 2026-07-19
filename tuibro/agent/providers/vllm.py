"""vLLM provider - OpenAI-compatible local inference server."""
import json
import httpx
from tuibro.agent.providers.base import BaseProvider, ProviderResponse, TokenUsage, ToolCall
from tuibro.agent.providers import register_provider


class VLLMProvider(BaseProvider):
    name = "vllm"
    models = ["local-model"]
    default_model = "local-model"

    def __init__(self, api_key=None, model=None, base_url=None):
        super().__init__(api_key or "", model, base_url or "http://localhost:8000/v1")

    def _headers(self) -> dict:
        return {"Content-Type": "application/json", "Authorization": f"Bearer {self.api_key or 'token-abc123'}"}

    async def complete(self, messages, tools=None):
        payload = {"model": self.model, "messages": messages}
        if tools:
            payload["tools"] = tools
        try:
            async with httpx.AsyncClient(timeout=120.0) as client:
                resp = await client.post(f"{self.base_url}/chat/completions", headers=self._headers(), json=payload)
                if resp.status_code != 200:
                    return ProviderResponse(error=f"HTTP {resp.status_code}: {resp.text[:200]}")
                return self._parse_response(resp.json())
        except httpx.ConnectError:
            return ProviderResponse(error="vLLM not running. Start with: vllm serve <model>")
        except Exception as e:
            return ProviderResponse(error=str(e))

    def _parse_response(self, data: dict) -> ProviderResponse:
        choice = data.get("choices", [{}])[0]
        msg = choice.get("message", {})
        usage_data = data.get("usage", {})
        usage = TokenUsage(prompt_tokens=usage_data.get("prompt_tokens", 0), completion_tokens=usage_data.get("completion_tokens", 0))
        usage.total_tokens = usage.prompt_tokens + usage.completion_tokens
        tool_calls = []
        for tc in msg.get("tool_calls", []):
            func = tc.get("function", {})
            args = func.get("arguments", "{}")
            try: args = json.loads(args) if isinstance(args, str) else args
            except json.JSONDecodeError: args = {}
            tool_calls.append(ToolCall(id=tc.get("id", ""), name=func.get("name", ""), arguments=args))
        return ProviderResponse(content=msg.get("content", "") or "", tool_calls=tool_calls, usage=usage, finish_reason=choice.get("finish_reason", ""))


register_provider("vllm", VLLMProvider)
