"""Cohere provider."""
import json
import httpx
from tuibro.agent.providers.base import BaseProvider, ProviderResponse, TokenUsage, ToolCall
from tuibro.agent.providers import register_provider


class CohereProvider(BaseProvider):
    name = "cohere"
    models = ["command-r-plus", "command-r", "command"]
    default_model = "command-r-plus"

    def __init__(self, api_key, model=None, base_url=None):
        super().__init__(api_key, model, base_url or "https://api.cohere.com")

    def _headers(self) -> dict:
        return {"Content-Type": "application/json", "Authorization": f"Bearer {self.api_key}"}

    async def complete(self, messages, tools=None):
        system_msg = ""
        chat_history = []
        for msg in messages:
            role = msg.get("role", "user")
            if role == "system":
                system_msg = msg.get("content", "")
            elif role == "user":
                chat_history.append({"role": "USER", "message": msg.get("content", "")})
            elif role == "assistant":
                chat_history.append({"role": "CHATBOT", "message": msg.get("content", "")})

        payload = {"model": self.model, "message": chat_history[-1]["message"] if chat_history else "", "chat_history": chat_history[:-1]}
        if system_msg:
            payload["preamble"] = system_msg
        if tools:
            payload["tools"] = self._format_tools_for_cohere(tools)

        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                resp = await client.post(f"{self.base_url}/v2/chat", headers=self._headers(), json=payload)
                if resp.status_code != 200:
                    return ProviderResponse(error=f"HTTP {resp.status_code}: {resp.text[:200]}")
                return self._parse_response(resp.json())
        except Exception as e:
            return ProviderResponse(error=str(e))

    def _format_tools_for_cohere(self, tools: list) -> list:
        result = []
        for tool in tools:
            func = tool.get("function", tool)
            result.append({
                "name": func.get("name", ""),
                "description": func.get("description", ""),
                "parameter_definitions": func.get("parameters", {}).get("properties", {}),
            })
        return result

    def _parse_response(self, data: dict) -> ProviderResponse:
        text = data.get("message", {}).get("content", [])
        text_parts = []
        if isinstance(text, list):
            for part in text:
                if isinstance(part, dict) and part.get("type") == "text":
                    text_parts.append(part.get("text", ""))
                elif isinstance(part, str):
                    text_parts.append(part)
        elif isinstance(text, str):
            text_parts = [text]

        tool_calls = []
        for tc in data.get("tool_calls", []):
            tool_calls.append(ToolCall(
                id=tc.get("id", ""),
                name=tc.get("function", {}).get("name", ""),
                arguments=tc.get("function", {}).get("arguments", {}),
            ))

        usage_data = data.get("meta", {}).get("tokens", {})
        usage = TokenUsage(
            prompt_tokens=usage_data.get("input_tokens", 0),
            completion_tokens=usage_data.get("output_tokens", 0),
        )
        usage.total_tokens = usage.prompt_tokens + usage.completion_tokens
        return ProviderResponse(
            content="\n".join(text_parts),
            tool_calls=tool_calls,
            usage=usage,
            finish_reason=data.get("finish_reason", ""),
        )


register_provider("cohere", CohereProvider)
