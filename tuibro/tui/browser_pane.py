"""Browser pane — DOM view, tab indicators, activity visualization."""
import time
from tuibro.browser.dom import render_a11y_page
from tuibro.browser.engine import PageInfo, BrowserEvent, EventType


class BrowserPane:
    def __init__(self):
        self.page_info = PageInfo()
        self.last_action: str = ""
        self.view_offset: int = 0
        self.loading: bool = False
        self._event_log: list[BrowserEvent] = []
        self._max_viz_lines = 200

    def update(self, page_info: PageInfo, last_action: str = ""):
        self.page_info = page_info
        if last_action:
            self.last_action = last_action

    def set_loading(self, loading: bool):
        self.loading = loading

    def add_event(self, event: BrowserEvent):
        self._event_log.append(event)
        if len(self._event_log) > self._max_viz_lines:
            self._event_log = self._event_log[-self._max_viz_lines:]

    def render(self, width: int, height: int) -> list[str]:
        if self.loading and not self.page_info.url:
            frames = ["⣾", "⣽", "⣻", "⢿", "⡿", "⣟", "⣯", "⣷"]
            frame = frames[int(time.time() * 8) % len(frames)]
            return [""] + [f"  {frame} Browser starting..."] + [""] * (height - 3)

        if self.page_info.error and not self.page_info.url:
            return self._render_error_view(width, height)

        lines = self._render_dom_view(width, height)
        return lines

    def render_activity(self, width: int, height: int) -> list[str]:
        """Render the real-time activity/viz pane."""
        lines = []

        # Current page info header
        if self.page_info.url:
            url = self.page_info.url
            if len(url) > width - 4:
                url = url[:width - 7] + "..."
            lines.append(f"URL: {url}")

            if self.page_info.scroll_position:
                sp = self.page_info.scroll_position
                pct = (sp.get("y", 0) / max(sp.get("maxY", 1), 1)) * 100
                elem_count = len(self.page_info.interactive_elements)
                lines.append(f"Scroll: {pct:.0f}% | Elements: {elem_count}")
            lines.append("─" * min(width, 40))

        # Recent events (most recent at bottom)
        lines.append("Activity Log:")
        lines.append("")

        if not self._event_log:
            lines.append("  (no activity yet)")
        else:
            recent = self._event_log[-(height - 6):]
            for event in recent:
                entry = str(event)
                if len(entry) > width - 3:
                    entry = entry[:width - 6] + "..."
                lines.append(f"  {entry}")

        # Pad to height
        while len(lines) < height:
            lines.append("")

        return lines[:height]

    def _render_dom_view(self, width: int, height: int) -> list[str]:
        """Render the DOM/a11y tree with tab info."""
        lines = []

        # Tab indicator
        if self.page_info.tab_count > 1:
            tab_str = self._render_tab_indicator(width)
            lines.append(tab_str)
            lines.append("─" * min(width, 40))

        # A11y tree
        tree_lines = render_a11y_page(self.page_info, width, height - 4)
        lines.extend(tree_lines)

        # Last action
        if self.last_action:
            lines.append("")
            lines.append(f"Last: {self.last_action}")

        # Pad to height
        while len(lines) < height:
            lines.append("")

        return lines[:height]

    def _render_tab_indicator(self, width: int) -> str:
        """Render tab indicator bar."""
        parts = []
        for i in range(self.page_info.tab_count):
            title = self.page_info.tab_title[:12] if self.page_info.tab_title and i == self.page_info.tab_index else ""
            if i == self.page_info.tab_index:
                parts.append(f"[{i}:{title}]" if title else f"[{i}]")
            else:
                parts.append(f" {i} ")
        return " ".join(parts)

    def _render_error_view(self, width: int, height: int) -> list[str]:
        lines = [
            "",
            f"  ✗ {self.page_info.error[:width - 6]}",
            "",
            "  Navigate to a URL or let the agent browse.",
            "",
            "  Commands:",
            "    /url <URL>       — Navigate directly",
            "    /google <query>  — Quick Google search",
            "    /bing <query>    — Quick Bing search",
            "    <task>           — Let agent handle it",
            "",
            "  Keyboard:",
            "    Tab              — Switch panes",
            "    F2               — Cycle providers",
            "    F5               — Toggle activity pane",
            "    Ctrl+C           — Stop/Quit",
        ]
        while len(lines) < height:
            lines.append("")
        return lines[:height]

    def scroll_view(self, direction: str, amount: int = 3):
        if direction == "up":
            self.view_offset = max(0, self.view_offset - amount)
        else:
            self.view_offset += amount
