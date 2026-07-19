"""Google Gemini provider."""
import json
import httpx
from tuibro.agent.providers.base import BaseProvider, ProviderResponse, TokenUsage, ToolCall
from tuibro.agent.providers import register_provider


class GoogleProvider(BaseProvider):
    name = "google"
    models = ["gemini-2.0-flash", "gemini-1.5-pro", "gemini-1.5-flash"]
    default_model = "gemini-2.0-flash"

    def __init__(self, api_key, model=None, base_url=None):
        super().__init__(api_key, model, base_url or "https://generativelanguage.googleapis.com")

    async def complete(self, messages, tools=None):
        system_instruction = ""
        contents = []
        for msg in messages:
            role = msg.get("role", "user")
            if role == "system":
                system_instruction = msg.get("content", "")
            else:
                role_map = {"assistant": "model", "user": "user"}
                contents.append({
                    "role": role_map.get(role, role),
                    "parts": [{"text": msg.get("content", "")}],
                })

        payload = {"contents": contents, "generationConfig": {"maxOutputTokens": 4096}}
        if system_instruction:
            payload["systemInstruction"] = {"parts": [{"text": system_instruction}]}
        if tools:
            payload["tools"] = self._format_tools_for_google(tools)

        model_name = self.model
        if not model_name.startswith("models/"):
            model_name = f"models/{model_name}"

        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                resp = await client.post(
                    f"{self.base_url}/v1beta/{model_name}:generateContent?key={self.api_key}",
                    headers={"Content-Type": "application/json"},
                    json=payload,
                )
                if resp.status_code != 200:
                    return ProviderResponse(error=f"HTTP {resp.status_code}: {resp.text[:200]}")
                data = resp.json()
                return self._parse_response(data)
        except Exception as e:
            return ProviderResponse(error=str(e))

    def _format_tools_for_google(self, tools: list) -> list:
        funcs = []
        for tool in tools:
            func = tool.get("function", tool)
            funcs.append({
                "name": func.get("name", ""),
                "description": func.get("description", ""),
                "parameters": func.get("parameters", {}),
            })
        return [{"functionDeclarations": funcs}]

    def _parse_response(self, data: dict) -> ProviderResponse:
        candidates = data.get("candidates", [])
        if not candidates:
            return ProviderResponse(error="No candidates in response")
        candidate = candidates[0]
        parts = candidate.get("content", {}).get("parts", [])
        text_parts = []
        tool_calls = []
        for part in parts:
            if "text" in part:
                text_parts.append(part["text"])
            if "functionCall" in part:
                fc = part["functionCall"]
                tool_calls.append(ToolCall(
                    id=f"google_{fc.get('name', '')}",
                    name=fc.get("name", ""),
                    arguments=fc.get("args", {}),
                ))
        usage_data = data.get("usageMetadata", {})
        usage = TokenUsage(
            prompt_tokens=usage_data.get("promptTokenCount", 0),
            completion_tokens=usage_data.get("candidatesTokenCount", 0),
        )
        usage.total_tokens = usage_data.get("totalTokenCount", 0)
        finish = candidate.get("finishReason", "")
        finish_map = {"STOP": "stop", "MAX_TOKENS": "max_tokens"}
        return ProviderResponse(
            content="\n".join(text_parts),
            tool_calls=tool_calls,
            usage=usage,
            finish_reason=finish_map.get(finish, finish.lower()),
        )


register_provider("google", GoogleProvider)
