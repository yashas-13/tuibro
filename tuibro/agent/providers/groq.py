"""Groq provider - OpenAI-compatible."""
import json
import httpx
from tuibro.agent.providers.base import BaseProvider, ProviderResponse, TokenUsage, ToolCall
from tuibro.agent.providers import register_provider


class GroqProvider(BaseProvider):
    name = "groq"
    models = ["llama-3.3-70b-versatile", "llama-3.1-8b-instant", "mixtral-8x7b-32768", "gemma2-9b-it"]
    default_model = "llama-3.3-70b-versatile"

    def __init__(self, api_key, model=None, base_url=None):
        super().__init__(api_key, model, base_url or "https://api.groq.com/openai/v1")

    def _headers(self) -> dict:
        return {"Content-Type": "application/json", "Authorization": f"Bearer {self.api_key}"}

    async def complete(self, messages, tools=None):
        payload = {"model": self.model, "messages": messages}
        if tools:
            payload["tools"] = tools
        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                resp = await client.post(f"{self.base_url}/chat/completions", headers=self._headers(), json=payload)
                if resp.status_code != 200:
                    return ProviderResponse(error=f"HTTP {resp.status_code}: {resp.text[:200]}")
                data = resp.json()
                return self._parse_response(data)
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


register_provider("groq", GroqProvider)
