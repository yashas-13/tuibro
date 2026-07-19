"""Chat pane - conversation display and input for Tuibro TUI."""
import curses
from dataclasses import dataclass
from tuibro.tui.theme import (
    PAIR_USER_MSG, PAIR_AGENT_MSG, PAIR_ACTION_LOG, PAIR_ERROR,
    PAIR_SYSTEM, PAIR_INPUT, PAIR_DIM,
)


@dataclass
class Message:
    role: str  # "user", "agent", "action", "error", "system"
    content: str
    timestamp: float = 0.0


class ChatPane:
    def __init__(self):
        self.messages: list[Message] = []
        self.input_buffer: str = ""
        self.input_cursor: int = 0
        self.scroll_offset: int = 0
        self.max_messages: int = 500

    def add_message(self, role: str, content: str):
        import time
        msg = Message(role=role, content=content, timestamp=time.time())
        self.messages.append(msg)
        if len(self.messages) > self.max_messages:
            self.messages = self.messages[-self.max_messages:]
        self.scroll_offset = 0  # auto-scroll to bottom

    def add_user_message(self, text: str):
        self.add_message("user", text)

    def add_agent_message(self, text: str):
        self.add_message("agent", text)

    def add_action_log(self, action: str, result: str = ""):
        truncated_result = result[:100] if result else ""
        self.add_message("action", f"{action}  {truncated_result}")

    def add_system_message(self, text: str):
        self.add_message("system", text)

    def add_error(self, text: str):
        self.add_message("error", text)

    def render(self, width: int, height: int) -> list[str]:
        lines = []
        input_area = 3  # bottom 3 lines for input
        display_height = height - input_area

        for msg in self.messages:
            formatted = self._format_message(msg, width)
            lines.extend(formatted)

        # Apply scroll offset
        if self.scroll_offset > 0:
            visible = lines[-self.scroll_offset:] if self.scroll_offset < len(lines) else lines
        else:
            visible = lines

        # Trim to display area
        visible = visible[-display_height:]

        # Pad to fill display area
        while len(visible) < display_height:
            visible.insert(0, "")

        # Add input area
        visible.append("─" * width)
        prompt = f"> {self.input_buffer}"
        if len(prompt) > width - 2:
            prompt = prompt[:width - 2]
        visible.append(prompt)
        visible.append("")

        return visible

    def _format_message(self, msg: Message, width: int) -> list[str]:
        content = msg.content
        lines = []

        if msg.role == "user":
            prefix = "You: "
            prefix_len = len(prefix)
            wrapped = self._wrap_text(content, width - prefix_len)
            lines.append(f"{prefix}{wrapped[0]}")
            for wline in wrapped[1:]:
                lines.append(" " * prefix_len + wline)
        elif msg.role == "agent":
            prefix = "Agent: "
            prefix_len = len(prefix)
            wrapped = self._wrap_text(content, width - prefix_len)
            lines.append(f"{prefix}{wrapped[0]}")
            for wline in wrapped[1:]:
                lines.append(" " * prefix_len + wline)
        elif msg.role == "action":
            lines.append(f"  → {content}")
        elif msg.role == "error":
            lines.append(f"  ✗ {content}")
        elif msg.role == "system":
            lines.append(f"  · {content}")

        lines.append("")
        return lines

    def _wrap_text(self, text: str, max_width: int) -> list[str]:
        if not text:
            return [""]
        if max_width <= 0:
            return [text]

        words = text.split()
        result = []
        current = []
        current_len = 0

        for word in words:
            if current_len + len(word) + (1 if current else 0) <= max_width:
                if current:
                    current.append(" ")
                    current_len += 1
                current.append(word)
                current_len += len(word)
            else:
                if current:
                    result.append("".join(current))
                current = [word]
                current_len = len(word)

        if current:
            result.append("".join(current))

        return result if result else [""]

    def handle_input(self, key: int) -> str | None:
        if key == 10:  # Enter
            text = self.input_buffer.strip()
            self.input_buffer = ""
            self.input_cursor = 0
            if text:
                self.add_user_message(text)
                return text
            return None
        elif key == 127 or key == curses.KEY_BACKSPACE or key == 8:  # Backspace
            if self.input_cursor > 0:
                self.input_buffer = (
                    self.input_buffer[: self.input_cursor - 1]
                    + self.input_buffer[self.input_cursor:]
                )
                self.input_cursor -= 1
        elif key == curses.KEY_DC:  # Delete
            if self.input_cursor < len(self.input_buffer):
                self.input_buffer = (
                    self.input_buffer[: self.input_cursor]
                    + self.input_buffer[self.input_cursor + 1 :]
                )
        elif key == curses.KEY_LEFT:
            if self.input_cursor > 0:
                self.input_cursor -= 1
        elif key == curses.KEY_RIGHT:
            if self.input_cursor < len(self.input_buffer):
                self.input_cursor += 1
        elif key == curses.KEY_HOME:
            self.input_cursor = 0
        elif key == curses.KEY_END:
            self.input_cursor = len(self.input_buffer)
        elif 32 <= key < 256:
            ch = chr(key)
            self.input_buffer = (
                self.input_buffer[: self.input_cursor]
                + ch
                + self.input_buffer[self.input_cursor :]
            )
            self.input_cursor += 1
        elif key == curses.KEY_PPAGE:
            self.scroll_offset += 5
        elif key == curses.KEY_NPAGE:
            self.scroll_offset = max(0, self.scroll_offset - 5)

        return None
