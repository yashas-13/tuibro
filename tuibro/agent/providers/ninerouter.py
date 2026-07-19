"""9router provider — combo model router at localhost:20128."""
import json
import httpx
from tuibro.agent.providers.base import BaseProvider, ProviderResponse, TokenUsage, ToolCall
from tuibro.agent.providers import register_provider


class NineRouterProvider(BaseProvider):
    name = "9router"
    models = ["oc", "oc/big-pickle", "oc/deepseek-v4-flash-free", "oc/mimo-v2.5-free",
              "oc/hy3-free", "oc/north-mini-code-free",
              "openai/gpt-5.4", "anthropic/claude-sonnet-4-20250514", "google/gemini-2.5-flash"]
    default_model = "oc"

    def __init__(self, api_key=None, model=None, base_url=None):
        super().__init__(api_key or "sk_9router", model, base_url or "http://localhost:20128/v1")

    def _headers(self) -> dict:
        return {"Content-Type": "application/json", "Authorization": f"Bearer {self.api_key}"}

    async def complete(self, messages, tools=None):
        payload = {"model": self.model, "messages": messages}
        if tools:
            payload["tools"] = tools
            payload["tool_choice"] = "auto"
        try:
            async with httpx.AsyncClient(timeout=120.0) as client:
                resp = await client.post(
                    f"{self.base_url}/chat/completions",
                    headers=self._headers(),
                    json=payload,
                )
                if resp.status_code != 200:
                    return ProviderResponse(error=f"HTTP {resp.status_code}: {resp.text[:300]}")
                return self._parse_response(resp.text)
        except httpx.ConnectError:
            return ProviderResponse(error="9router not running. Start with: 9router")
        except Exception as e:
            return ProviderResponse(error=str(e))

    def _parse_raw(self, body: str) -> dict:
        """Parse response body — JSON possibly followed by SSE trailer like 'data: [DONE]'."""
        if not body or not body.strip():
            raise ValueError("Empty response body from 9router")
        # Try direct JSON parse first
        try:
            return json.loads(body)
        except json.JSONDecodeError:
            pass
        # Find first complete JSON object by brace-matching
        depth = 0
        end = 0
        in_string = False
        escape = False
        for i, ch in enumerate(body):
            if escape:
                escape = False
                continue
            if ch == '\\':
                if in_string:
                    escape = True
                continue
            if ch == '"':
                in_string = not in_string
                continue
            if not in_string:
                if ch == '{':
                    depth += 1
                elif ch == '}':
                    depth -= 1
                    if depth == 0:
                        end = i + 1
                        break
        if end > 0:
            return json.loads(body[:end])
        # Try line-by-line (SSE format)
        for line in body.split("\n"):
            line = line.strip()
            if line.startswith("data: ") and line != "data: [DONE]":
                try:
                    return json.loads(line[6:])
                except json.JSONDecodeError:
                    pass
        raise ValueError(f"Could not parse response body ({len(body)} bytes)")

    def _parse_response(self, raw_body: str) -> ProviderResponse:
        data = self._parse_raw(raw_body)
        choices = data.get("choices") or []
        if not choices:
            return ProviderResponse(error=f"No choices. Keys: {list(data.keys())}")
        choice = choices[0]
        msg = choice.get("message") or {}
        if not msg:
            return ProviderResponse(error="No message in choice")

        content = msg.get("content") or ""
        # Some models put output in 'reasoning' when content is null
        if not content and msg.get("reasoning"):
            reasoning = msg["reasoning"]
            if isinstance(reasoning, str):
                content = reasoning
            elif isinstance(reasoning, dict):
                content = reasoning.get("text", "") or reasoning.get("summary", "")
        finish_reason = choice.get("finish_reason", "")

        usage_data = data.get("usage") or {}
        usage = TokenUsage(
            prompt_tokens=usage_data.get("prompt_tokens", 0),
            completion_tokens=usage_data.get("completion_tokens", 0),
        )
        usage.total_tokens = usage_data.get("total_tokens", usage.prompt_tokens + usage.completion_tokens)

        tool_calls = []
        raw_tc = msg.get("tool_calls") or []
        if isinstance(raw_tc, list):
            for tc in raw_tc:
                if not isinstance(tc, dict):
                    continue
                func = tc.get("function") or {}
                args_raw = func.get("arguments", "{}")
                try:
                    args = json.loads(args_raw) if isinstance(args_raw, str) else (args_raw or {})
                except (json.JSONDecodeError, TypeError):
                    args = {}
                tool_calls.append(ToolCall(id=tc.get("id", ""), name=func.get("name", ""), arguments=args))

        return ProviderResponse(content=content, tool_calls=tool_calls, usage=usage, finish_reason=finish_reason)


register_provider("9router", NineRouterProvider)
