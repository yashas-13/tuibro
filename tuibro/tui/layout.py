"""Split-pane layout manager — chat | browser | activity log + tab bar."""
import curses
from tuibro.tui.theme import (
    PAIR_BORDER, PAIR_TITLE, PAIR_STATUS, PAIR_DIM,
    PAIR_FOCUSED, PAIR_INTERACTIVE,
    BORDER_H, BORDER_V, BORDER_TL, BORDER_TR, BORDER_BL, BORDER_BR,
    BORDER_L, BORDER_T, BORDER_B, BORDER_R,
)


class Layout:
    """
    Layout:
    ┌───────────────────────────────────────────────────────┐
    │ [Tab: 0 Chat | 1 Google | 2 Bing]          status    │  ← Tab bar (row 0)
    ├───────────────────┬───────────────────────┬───────────┤
    │                   │                       │           │
    │    Chat Pane      │    Browser Pane       │  Activity │  ← Content
    │    (40%)          │    (40%)              │  (20%)    │
    │                   │                       │           │
    ├───────────────────┴───────────────────────┴───────────┤
    │ Provider: openai | Model: gpt-4o                      │  ← Status bar
    └───────────────────────────────────────────────────────┘
    """

    def __init__(self, stdscr, chat_ratio: float = 0.35, activity_ratio: float = 0.20):
        self.stdscr = stdscr
        self.chat_ratio = chat_ratio
        self.activity_ratio = activity_ratio
        self.show_activity = True
        self._resize()

    def _resize(self):
        self.height, self.width = self.stdscr.getmaxyx()
        tab_bar_height = 1
        status_height = 1
        self.content_height = self.height - tab_bar_height - status_height
        self.content_top = tab_bar_height

        usable = self.width - 2  # borders
        if self.show_activity:
            self.chat_width = max(20, int(usable * self.chat_ratio))
            self.activity_width = max(15, int(usable * self.activity_ratio))
            self.browser_width = usable - self.chat_width - self.activity_width
        else:
            self.chat_width = max(20, int(usable * self.chat_ratio))
            self.activity_width = 0
            self.browser_width = usable - self.chat_width

        try:
            self._tab_bar_win = curses.newwin(1, self.width, 0, 0)
            self._chat_win = curses.newwin(self.content_height, self.chat_width, self.content_top, 1)
            self._browser_win = curses.newwin(self.content_height, self.browser_width, self.content_top, 1 + self.chat_width)
            if self.show_activity:
                self._activity_win = curses.newwin(self.content_height, self.activity_width, self.content_top, 1 + self.chat_width + self.browser_width)
            self._status_win = curses.newwin(status_height, self.width, self.height - status_height, 0)
        except curses.error:
            pass

    def handle_resize(self):
        self._resize()

    def toggle_activity(self):
        self.show_activity = not self.show_activity
        self._resize()

    # ── Borders ─────────────────────────────────────────────────────
    def draw_borders(self):
        h, w = self.height, self.width
        split1 = 1 + self.chat_width
        split2 = split1 + self.browser_width

        try:
            # Tab bar top border (row 0 is tab bar content, no border needed there)
            # Content area borders
            row = self.content_top
            self.stdscr.addch(row, 0, ord(BORDER_L), curses.color_pair(PAIR_BORDER))
            self.stdscr.addch(row, w - 1, ord(BORDER_R), curses.color_pair(PAIR_BORDER))
            # Vertical dividers in content area
            for y in range(self.content_top, h - 1):
                self.stdscr.addch(y, split1, ord(BORDER_V), curses.color_pair(PAIR_BORDER))
                if self.show_activity:
                    self.stdscr.addch(y, split2, ord(BORDER_V), curses.color_pair(PAIR_BORDER))
            # Top border
            self.stdscr.addstr(0, 0, BORDER_TL, curses.color_pair(PAIR_BORDER))
            self.stdscr.addstr(0, 1, BORDER_H * (split1 - 1), curses.color_pair(PAIR_BORDER))
            self.stdscr.addstr(0, split1, BORDER_T, curses.color_pair(PAIR_BORDER))
            self.stdscr.addstr(0, split1 + 1, BORDER_H * (split2 - split1 - 1), curses.color_pair(PAIR_BORDER))
            if self.show_activity:
                self.stdscr.addstr(0, split2, BORDER_T, curses.color_pair(PAIR_BORDER))
                self.stdscr.addstr(0, split2 + 1, BORDER_H * (w - split2 - 2), curses.color_pair(PAIR_BORDER))
            self.stdscr.addstr(0, w - 1, BORDER_TR, curses.color_pair(PAIR_BORDER))
            # Bottom border
            self.stdscr.addstr(h - 1, 0, BORDER_BL, curses.color_pair(PAIR_BORDER))
            self.stdscr.addstr(h - 1, 1, BORDER_H * (split1 - 1), curses.color_pair(PAIR_BORDER))
            self.stdscr.addstr(h - 1, split1, BORDER_B, curses.color_pair(PAIR_BORDER))
            self.stdscr.addstr(h - 1, split1 + 1, BORDER_H * (split2 - split1 - 1), curses.color_pair(PAIR_BORDER))
            if self.show_activity:
                self.stdscr.addstr(h - 1, split2, BORDER_B, curses.color_pair(PAIR_BORDER))
                self.stdscr.addstr(h - 1, split2 + 1, BORDER_H * (w - split2 - 2), curses.color_pair(PAIR_BORDER))
            self.stdscr.addstr(h - 1, w - 1, BORDER_BR, curses.color_pair(PAIR_BORDER))
        except curses.error:
            pass

    # ── Tab Bar ─────────────────────────────────────────────────────
    def render_tab_bar(self, tabs: list, active_idx: int, focus: str = "chat"):
        self._tab_bar_win.erase()
        try:
            w = self._tab_bar_win.getmaxyx()[1]
            x = 1
            for tab in tabs:
                title = tab.title[:15] if tab.title else "Untitled"
                if tab.index == active_idx:
                    label = f"[{tab.index}:{title}]"
                    style = curses.color_pair(PAIR_FOCUSED) | curses.A_BOLD
                else:
                    label = f" {tab.index}:{title} "
                    style = curses.color_pair(PAIR_DIM)
                if x + len(label) + 1 > w - 10:
                    self._tab_bar_win.addnstr(0, x, "...", 3, style)
                    break
                self._tab_bar_win.addnstr(0, x, label, w - x, style)
                x += len(label) + 1
            # Focus indicator
            focus_label = f" ({focus})" if focus else ""
            self._tab_bar_win.addnstr(0, w - len(focus_label) - 1, focus_label, len(focus_label), curses.color_pair(PAIR_INTERACTIVE))
            self._tab_bar_win.refresh()
        except curses.error:
            pass

    # ── Title Bars ──────────────────────────────────────────────────
    def draw_title_bars(self, chat_title: str, browser_title: str, activity_title: str = ""):
        try:
            cw = self.chat_width - 2
            bw = self.browser_width - 2

            self._chat_win.erase()
            self._browser_win.erase()

            self._chat_win.addstr(0, 1, f" {chat_title[:cw]} ", curses.color_pair(PAIR_TITLE) | curses.A_BOLD)
            self._browser_win.addstr(0, 1, f" {browser_title[:bw]} ", curses.color_pair(PAIR_TITLE) | curses.A_BOLD)

            self._chat_win.refresh()
            self._browser_win.refresh()

            if self.show_activity and self.activity_width > 0:
                aw = self.activity_width - 2
                self._activity_win.erase()
                self._activity_win.addstr(0, 1, f" {activity_title[:aw]} ", curses.color_pair(PAIR_TITLE) | curses.A_BOLD)
                self._activity_win.refresh()
        except curses.error:
            pass

    # ── Content Rendering ───────────────────────────────────────────
    def render_chat_lines(self, lines: list):
        self._chat_win.erase()
        h, w = self._chat_win.getmaxyx()
        for i, line in enumerate(lines):
            if i >= h - 1:
                break
            self._chat_win.addnstr(i + 1, 1, line[:w - 2], w - 2)
        self._chat_win.refresh()

    def render_browser_lines(self, lines: list):
        self._browser_win.erase()
        h, w = self._browser_win.getmaxyx()
        for i, line in enumerate(lines):
            if i >= h - 1:
                break
            self._browser_win.addnstr(i + 1, 1, line[:w - 2], w - 2)
        self._browser_win.refresh()

    def render_activity_lines(self, lines: list):
        if not self.show_activity:
            return
        self._activity_win.erase()
        h, w = self._activity_win.getmaxyx()
        for i, line in enumerate(lines):
            if i >= h - 1:
                break
            self._activity_win.addnstr(i + 1, 1, line[:w - 2], w - 2)
        self._activity_win.refresh()

    def render_status(self, text: str):
        self._status_win.erase()
        try:
            w = self._status_win.getmaxyx()[1]
            self._status_win.addnstr(0, 0, text[:w], w, curses.color_pair(PAIR_STATUS))
            self._status_win.refresh()
        except curses.error:
            pass

    @property
    def chat_win(self):
        return self._chat_win

    @property
    def browser_win(self):
        return self._browser_win
