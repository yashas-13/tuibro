"""Anthropic Claude provider."""
import json
import httpx
from tuibro.agent.providers.base import BaseProvider, ProviderResponse, TokenUsage, ToolCall
from tuibro.agent.providers import register_provider


class AnthropicProvider(BaseProvider):
    name = "anthropic"
    models = ["claude-sonnet-4-20250514", "claude-3-5-sonnet-20241022", "claude-3-haiku-20240307"]
    default_model = "claude-sonnet-4-20250514"

    def __init__(self, api_key, model=None, base_url=None):
        super().__init__(api_key, model, base_url or "https://api.anthropic.com")

    def _headers(self) -> dict:
        return {
            "Content-Type": "application/json",
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01",
        }

    async def complete(self, messages, tools=None):
        system_msg = ""
        api_messages = []
        for msg in messages:
            if msg.get("role") == "system":
                system_msg = msg.get("content", "")
            else:
                api_messages.append(msg)

        payload = {"model": self.model, "messages": api_messages, "max_tokens": 4096}
        if system_msg:
            payload["system"] = system_msg
        if tools:
            payload["tools"] = self._format_tools_for_anthropic(tools)

        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                resp = await client.post(
                    f"{self.base_url}/v1/messages",
                    headers=self._headers(),
                    json=payload,
                )
                if resp.status_code != 200:
                    return ProviderResponse(error=f"HTTP {resp.status_code}: {resp.text[:200]}")
                data = resp.json()
                return self._parse_response(data)
        except Exception as e:
            return ProviderResponse(error=str(e))

    def _format_tools_for_anthropic(self, tools: list) -> list:
        result = []
        for tool in tools:
            func = tool.get("function", tool)
            result.append({
                "name": func.get("name", ""),
                "description": func.get("description", ""),
                "input_schema": func.get("parameters", {}),
            })
        return result

    def _parse_response(self, data: dict) -> ProviderResponse:
        content_blocks = data.get("content", [])
        text_parts = []
        tool_calls = []
        for block in content_blocks:
            if block.get("type") == "text":
                text_parts.append(block.get("text", ""))
            elif block.get("type") == "tool_use":
                tool_calls.append(ToolCall(
                    id=block.get("id", ""),
                    name=block.get("name", ""),
                    arguments=block.get("input", {}),
                ))
        usage_data = data.get("usage", {})
        usage = TokenUsage(
            prompt_tokens=usage_data.get("input_tokens", 0),
            completion_tokens=usage_data.get("output_tokens", 0),
        )
        usage.total_tokens = usage.prompt_tokens + usage.completion_tokens
        return ProviderResponse(
            content="\n".join(text_parts),
            tool_calls=tool_calls,
            usage=usage,
            finish_reason=data.get("stop_reason", ""),
        )


register_provider("anthropic", AnthropicProvider)
