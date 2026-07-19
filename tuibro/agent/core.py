"""Agent core loop — observe, think, act, render. Full DOM + tab control."""
import asyncio
import logging
from typing import Callable, Optional
from tuibro.agent.providers.base import BaseProvider, ProviderResponse
from tuibro.agent.providers import import_all
from tuibro.browser.actions import TOOL_DEFINITIONS, execute_tool
from tuibro.agent.prompts import get_system_prompt, get_task_prompt
from tuibro.browser.engine import BrowserEngine, PageInfo, BrowserEvent

logger = logging.getLogger("tuibro.agent")


class AgentCore:
    def __init__(self, provider: BaseProvider, browser: BrowserEngine, max_iterations: int = 20):
        self.provider = provider
        self.browser = browser
        self.max_iterations = max_iterations
        self._running = False
        self._messages: list[dict] = []
        self._iteration = 0

        # Callbacks for TUI updates
        self.on_agent_message: Optional[Callable[[str], None]] = None
        self.on_action: Optional[Callable[[str, str], None]] = None
        self.on_error: Optional[Callable[[str], None]] = None
        self.on_page_update: Optional[Callable[[PageInfo, str], None]] = None
        self.on_status_change: Optional[Callable[[str], None]] = None
        self.on_event: Optional[Callable[[BrowserEvent], None]] = None

    @property
    def is_running(self) -> bool:
        return self._running

    def stop(self):
        self._running = False

    def reset(self):
        self._messages = []
        self._iteration = 0

    async def run_task(self, task: str) -> str:
        """Execute a user task autonomously."""
        self._running = True
        self._iteration = 0
        self._notify_status("Running")

        # System prompt with tool info
        system_prompt = get_system_prompt(self.max_iterations)
        tool_descriptions = "\n".join([
            f"  - {t['function']['name']}: {t['function']['description']}"
            for t in TOOL_DEFINITIONS
        ])
        full_system = f"{system_prompt}\n\nAvailable tools:\n{tool_descriptions}"

        self._messages = [{"role": "system", "content": full_system}]

        # Get initial page state
        try:
            page_state = await self.browser.get_page_state()
            self._notify_page_update(page_state, "Task started")
        except Exception:
            page_state = PageInfo()

        # Format task with page state
        task_msg = get_task_prompt(task)
        self._messages.append({"role": "user", "content": task_msg})

        final_answer = ""

        while self._running and self._iteration < self.max_iterations:
            self._iteration += 1
            self._notify_status(f"Iter {self._iteration}/{self.max_iterations}")

            # Get current page state
            try:
                page_state = await self.browser.get_page_state()
                page_context = self._format_page_state(page_state)
                self._notify_page_update(page_state, f"Iter {self._iteration}")
            except Exception as e:
                page_context = f"Error getting page state: {e}"

            # Build user message with current state
            state_msg = (
                f"{task_msg}\n\n"
                f"=== CURRENT STATE (Iteration {self._iteration}) ===\n"
                f"{page_context}\n"
                f"=== END STATE ==="
            )

            # Update last user message or add new one
            if self._messages and self._messages[-1]["role"] == "user":
                self._messages[-1]["content"] = state_msg
            else:
                self._messages.append({"role": "user", "content": state_msg})

            # Call LLM
            response: ProviderResponse = await self.provider.complete(
                self._messages, TOOL_DEFINITIONS
            )

            if response.error:
                self._notify_error(f"Provider error: {response.error}")
                await asyncio.sleep(1)
                continue

            # Add assistant message
            assistant_msg = {"role": "assistant", "content": response.content}
            if response.tool_calls:
                assistant_msg["tool_calls"] = [
                    {
                        "id": tc.id,
                        "type": "function",
                        "function": {"name": tc.name, "arguments": str(tc.arguments)},
                    }
                    for tc in response.tool_calls
                ]
            self._messages.append(assistant_msg)

            if response.content:
                self._notify_agent_message(response.content)

            # Process tool calls
            if response.tool_calls:
                for tc in response.tool_calls:
                    if tc.name == "done":
                        final_answer = tc.arguments.get("answer", "Task complete.")
                        self._notify_agent_message(f"[DONE] {final_answer}")
                        self._running = False
                        break

                    self._notify_action(f"{tc.name}({self._format_args(tc.arguments)})")
                    result = await execute_tool(tc.name, tc.arguments, self.browser)

                    # Truncate long results
                    display_result = result[:150] + "..." if len(result) > 150 else result
                    self._notify_action(f"  → {display_result}")

                    self._messages.append({
                        "role": "tool",
                        "tool_call_id": tc.id,
                        "content": result,
                    })

                if not self._running:
                    break
            else:
                if response.content:
                    final_answer = response.content
                break

            await asyncio.sleep(0.05)

        self._running = False
        self._notify_status("Idle")

        if not final_answer:
            final_answer = f"Agent completed {self._iteration} iterations. Check the browser view for results."

        return final_answer

    async def send_message(self, message: str) -> str:
        """Direct message mode (non-autonomous)."""
        self._messages.append({"role": "user", "content": message})

        try:
            page_state = await self.browser.get_page_state()
            page_context = self._format_page_state(page_state)
            self._messages.append({
                "role": "user",
                "content": f"[Current page state]\n{page_context}",
            })
        except Exception:
            pass

        response = await self.provider.complete(self._messages, TOOL_DEFINITIONS)
        if response.error:
            return f"Error: {response.error}"

        content = response.content or ""
        self._messages.append({"role": "assistant", "content": content})

        for tc in response.tool_calls:
            result = await execute_tool(tc.name, tc.arguments, self.browser)
            self._messages.append({"role": "tool", "tool_call_id": tc.id, "content": result})

        return content

    def _format_page_state(self, page: PageInfo) -> str:
        if page.error:
            return f"Error: {page.error}"

        lines = []

        # Tab info
        if page.tab_count > 1:
            lines.append(f"Tab: [{page.tab_index}/{page.tab_count}] {page.tab_title}")
        lines.append(f"URL: {page.url}")
        lines.append(f"Title: {page.title}")

        if page.scroll_position:
            sp = page.scroll_position
            pct = (sp.get("y", 0) / max(sp.get("maxY", 1), 1)) * 100
            lines.append(f"Scroll: {pct:.0f}%")

        lines.append("")
        lines.append("Interactive elements:")

        for el in page.interactive_elements[:35]:
            focused = " [FOCUSED]" if el.focused else ""
            val = f" = {el.value}" if el.value else ""
            lines.append(f"  [{el.index}] {el.role}: {el.name}{val}{focused}")

        if len(page.interactive_elements) > 35:
            lines.append(f"  ... and {len(page.interactive_elements) - 35} more")

        if page.page_text:
            lines.append("")
            lines.append(f"Page text: {page.page_text[:400]}")

        return "\n".join(lines)

    def _format_args(self, args: dict) -> str:
        parts = []
        for k, v in args.items():
            sv = str(v)
            if len(sv) > 40:
                sv = sv[:37] + "..."
            parts.append(f"{k}={sv}")
        return ", ".join(parts)

    def _notify_agent_message(self, text: str):
        if self.on_agent_message:
            self.on_agent_message(text)

    def _notify_action(self, action: str):
        if self.on_action:
            self.on_action(action, "")

    def _notify_error(self, error: str):
        if self.on_error:
            self.on_error(error)

    def _notify_page_update(self, page: PageInfo, action: str = ""):
        if self.on_page_update:
            self.on_page_update(page, action)

    def _notify_status(self, status: str):
        if self.on_status_change:
            self.on_status_change(status)
