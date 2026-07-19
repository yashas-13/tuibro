"""Main Tuibro app — tabs, full DOM control, real-time activity viz."""
import asyncio
import curses
import threading
import time
import logging
from typing import Optional
from tuibro.config import Config
from tuibro.tui.layout import Layout
from tuibro.tui.chat_pane import ChatPane
from tuibro.tui.browser_pane import BrowserPane
from tuibro.tui.status_bar import render_status_line
from tuibro.tui.theme import setup_colors, PAIR_SYSTEM
from tuibro.browser.engine import BrowserEngine, PageInfo, BrowserEvent
from tuibro.agent.core import AgentCore
from tuibro.agent.providers import import_all, get_provider, list_providers
from tuibro.agent.prompts import get_search_prompt

logger = logging.getLogger("tuibro")


class TuibroApp:
    def __init__(self, config: Config):
        self.config = config
        self.chat = ChatPane()
        self.browser_view = BrowserPane()
        self.engine = BrowserEngine(
            headless=config.headless,
            slow_mo=config.slow_mo,
            viewport_width=config.viewport_width,
            viewport_height=config.viewport_height,
        )
        import_all()
        self.provider = None
        self.agent: Optional[AgentCore] = None
        self._loop: Optional[asyncio.AbstractEventLoop] = None
        self._layout: Optional[Layout] = None
        self._running = True
        self._agent_status = "Idle"
        self._provider_names = list_providers()
        self._provider_idx = 0
        self._focus = "chat"  # chat | browser | activity
        self._initial_task = None

        # Wire browser events to activity pane
        self.engine.on_event(self._on_browser_event)

    def _on_browser_event(self, event: BrowserEvent):
        self.browser_view.add_event(event)

    async def run(self, task: str = None):
        self._loop = asyncio.get_event_loop()
        self._init_provider()

        try:
            await self.engine.start()
            self.chat.add_system_message("Browser started. Ready to browse!")
        except Exception as e:
            self.chat.add_error(f"Browser failed: {e}")
            self.chat.add_system_message("Chat works, but browsing needs the browser.")

        try:
            curses.wrapper(self._tui_main)
        except KeyboardInterrupt:
            pass
        finally:
            await self.engine.stop()

    def _init_provider(self):
        api_key = self.config.get_api_key()
        if not api_key:
            self.chat.add_system_message(
                f"No API key for {self.config.provider}. "
                f"Set TUIBRO_{self.config.provider.upper()}_API_KEY or "
                f"edit ~/.tuibro/keys.json"
            )
        try:
            self.provider = get_provider(
                self.config.provider, api_key or "", self.config.model
            )
            self.chat.add_system_message(
                f"Provider: {self.config.provider} | Model: {self.config.model}"
            )
        except ValueError as e:
            self.chat.add_error(str(e))

    # ── TUI Main Loop ───────────────────────────────────────────────
    def _tui_main(self, stdscr):
        curses.curs_set(1)
        stdscr.nodelay(False)
        stdscr.timeout(50)
        setup_colors()

        self._layout = Layout(stdscr, self.config.chat_ratio)
        self._full_redraw()

        if self._initial_task:
            self.chat.add_user_message(self._initial_task)
            self._start_agent_task(self._initial_task)
            self._initial_task = None

        while self._running:
            try:
                key = stdscr.getch()
                if key == -1:
                    continue
                self._handle_key(key)
                self._full_redraw()
            except curses.error:
                pass

    def _full_redraw(self):
        if not self._layout:
            return
        self._layout.draw_borders()

        # Tab bar
        self._layout.render_tab_bar(
            self.engine.tabs,
            self.engine._active_tab_idx,
            self._focus,
        )

        # Titles
        chat_title = "💬 Chat"
        br_title = f"🌐 {self.browser_view.page_info.title[:25] if self.browser_view.page_info.title else self.browser_view.page_info.url[:25] if self.browser_view.page_info.url else 'Browser'}"
        act_title = "📊 Activity"
        self._layout.draw_title_bars(chat_title, br_title, act_title)

        # Content
        chat_lines = self.chat.render(self._layout.chat_width, self._layout.content_height)
        br_lines = self.browser_view.render(self._layout.browser_width, self._layout.content_height)
        self._layout.render_chat_lines(chat_lines)
        self._layout.render_browser_lines(br_lines)

        if self._layout.show_activity:
            act_lines = self.browser_view.render_activity(self._layout.activity_width, self._layout.content_height)
            self._layout.render_activity_lines(act_lines)

        # Status bar
        status = render_status_line(self.config.provider, self.config.model, self._agent_status)
        self._layout.render_status(status)

    # ── Key Handling ────────────────────────────────────────────────
    def _handle_key(self, key: int):
        # Ctrl+C — stop agent or quit
        if key == 3:
            if self.agent and self.agent.is_running:
                self.agent.stop()
                self.chat.add_system_message("Agent stopped.")
            else:
                self._running = False
            return

        # Tab — cycle focus
        if key == 9:
            if self._layout and self._layout.show_activity:
                cycle = ["chat", "browser", "activity"]
            else:
                cycle = ["chat", "browser"]
            idx = cycle.index(self._focus) if self._focus in cycle else 0
            self._focus = cycle[(idx + 1) % len(cycle)]
            return

        # Function keys
        if key == curses.KEY_F1:
            self._show_help()
            return
        if key == curses.KEY_F2:
            self._cycle_provider()
            return
        if key == curses.KEY_F3:
            self._cycle_model()
            return
        if key == curses.KEY_F4:
            self.chat = ChatPane()
            self.chat.add_system_message("Chat cleared.")
            return
        if key == curses.KEY_F5:
            if self._layout:
                self._layout.toggle_activity()
            return
        if key == curses.KEY_F6:
            # Open new tab
            asyncio.run_coroutine_threadsafe(self._new_tab(), self._loop)
            return
        if key == curses.KEY_F7:
            # Close current tab
            asyncio.run_coroutine_threadsafe(self._close_tab(), self._loop)
            return

        # Focus-specific input
        if self._focus == "chat":
            result = self.chat.handle_input(key)
            if result is not None:
                self._handle_user_input(result)
        elif self._focus == "browser":
            if key == curses.KEY_UP:
                self.browser_view.scroll_view("up")
            elif key == curses.KEY_DOWN:
                self.browser_view.scroll_view("down")

    def _show_help(self):
        self.chat.add_system_message(
            "Tuibro Keyboard Shortcuts:\n"
            "  Tab       — Cycle focus (Chat/Browser/Activity)\n"
            "  Enter     — Send message (in chat)\n"
            "  F1        — This help\n"
            "  F2        — Cycle LLM provider\n"
            "  F3        — Cycle model\n"
            "  F4        — Clear chat\n"
            "  F5        — Toggle activity pane\n"
            "  F6        — Open new tab\n"
            "  F7        — Close current tab\n"
            "  Ctrl+C    — Stop agent / Quit\n\n"
            "Chat Commands:\n"
            "  /url <URL>        Navigate to URL\n"
            "  /google <query>   Quick Google search\n"
            "  /bing <query>     Quick Bing search\n"
            "  /tab N            Switch to tab N\n"
            "  /newtab [URL]     Open new tab\n"
            "  /closetab         Close current tab\n"
            "  /help, /clear, /providers, /model"
        )

    # ── User Input ──────────────────────────────────────────────────
    def _handle_user_input(self, text: str):
        if not text:
            return
        tl = text.strip().lower()

        # Built-in commands
        if tl == "help":
            self._show_help()
            return
        if tl == "clear":
            self.chat = ChatPane()
            return
        if tl == "providers":
            self.chat.add_system_message(f"Providers: {', '.join(self._provider_names)}")
            return
        if tl.startswith("model"):
            self.chat.add_system_message(f"Current model: {self.config.model}")
            return
        if tl == "status":
            s = "Running" if self.agent and self.agent.is_running else "Idle"
            self.chat.add_system_message(f"Agent: {s} | Tab: {self.engine._active_tab_idx} | Tabs: {len(self.engine.tabs)}")
            return
        if tl == "tabs":
            tab_info = [f"[{t.index}] {'◄ ' if t.is_active else ''}{t.title[:20]}" for t in self.engine.tabs]
            self.chat.add_system_message("Tabs:\n" + "\n".join(tab_info))
            return

        # Navigation commands
        if text.startswith("/url "):
            url = text[5:].strip()
            asyncio.run_coroutine_threadsafe(self._navigate(url), self._loop)
            return
        if text.startswith("/google ") or text.startswith("/g "):
            query = text.split(" ", 1)[1]
            self._start_agent_task(get_search_prompt(query, "https://google.com"))
            return
        if text.startswith("/bing ") or text.startswith("/b "):
            query = text.split(" ", 1)[1]
            self._start_agent_task(get_search_prompt(query, "https://bing.com"))
            return

        # Tab commands
        if text.startswith("/tab ") or text.startswith("/switch "):
            try:
                idx = int(text.split(" ", 1)[1])
                asyncio.run_coroutine_threadsafe(self._switch_tab(idx), self._loop)
            except ValueError:
                self.chat.add_error("Usage: /tab <number>")
            return
        if text.startswith("/newtab") or text.startswith("/nt"):
            parts = text.split(" ", 1)
            url = parts[1].strip() if len(parts) > 1 else ""
            asyncio.run_coroutine_threadsafe(self._new_tab(url), self._loop)
            return
        if tl in ("/closetab", "/ct"):
            asyncio.run_coroutine_threadsafe(self._close_tab(), self._loop)
            return

        # Agent task
        if self.provider:
            self._start_agent_task(text)
        else:
            self.chat.add_error("No provider configured. Set an API key first.")

    # ── Browser Actions (async) ─────────────────────────────────────
    async def _navigate(self, url: str):
        page = await self.engine.navigate(url)
        self.browser_view.update(page, f"Navigate: {url}")
        if self._layout:
            self._full_redraw()

    async def _new_tab(self, url: str = ""):
        page = await self.engine.new_tab(url or "about:blank")
        self.browser_view.update(page, f"New tab: {url or 'blank'}")
        self.chat.add_system_message(f"Opened tab {page.tab_index}: {url or 'about:blank'}")
        if self._layout:
            self._full_redraw()

    async def _close_tab(self, index: int = None):
        page = await self.engine.close_tab(index)
        if page.error:
            self.chat.add_error(page.error)
        else:
            self.chat.add_system_message(f"Closed tab. Now on tab {page.tab_index}")
        self.browser_view.update(page)
        if self._layout:
            self._full_redraw()

    async def _switch_tab(self, index: int):
        page = await self.engine.switch_tab(index)
        if page.error:
            self.chat.add_error(page.error)
        else:
            self.browser_view.update(page, f"Switched to tab {index}")
        if self._layout:
            self._full_redraw()

    # ── Agent ───────────────────────────────────────────────────────
    def _start_agent_task(self, task: str):
        if not self.provider:
            self.chat.add_error("No provider configured.")
            return
        if self.agent and self.agent.is_running:
            self.chat.add_system_message("Agent busy. Ctrl+C to stop.")
            return

        self.agent = AgentCore(self.provider, self.engine, self.config.max_iterations)

        def on_message(text):
            self.chat.add_agent_message(text)
            if self._layout:
                self._full_redraw()

        def on_action(action, result):
            self.chat.add_action_log(action, result)
            if self._layout:
                self._full_redraw()

        def on_error(error):
            self.chat.add_error(error)
            if self._layout:
                self._full_redraw()

        def on_page_update(page, action):
            self.browser_view.update(page, action)
            if self._layout:
                self._full_redraw()

        def on_status(status):
            self._agent_status = status
            if self._layout:
                status_text = render_status_line(self.config.provider, self.config.model, status)
                self._layout.render_status(status_text)

        def on_event(event):
            self.browser_view.add_event(event)

        self.agent.on_agent_message = on_message
        self.agent.on_action = on_action
        self.agent.on_error = on_error
        self.agent.on_page_update = on_page_update
        self.agent.on_status_change = on_status
        self.browser.on_event = lambda e: None  # events already wired

        def run_in_thread():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                loop.run_until_complete(self.agent.run_task(task))
            except Exception as e:
                self.chat.add_error(f"Agent error: {e}")
            finally:
                loop.close()

        self._agent_thread = threading.Thread(target=run_in_thread, daemon=True)
        self._agent_thread.start()

    # ── Provider Cycling ────────────────────────────────────────────
    def _cycle_provider(self):
        self._provider_idx = (self._provider_idx + 1) % len(self._provider_names)
        name = self._provider_names[self._provider_idx]
        key = self.config.get_api_key(name)
        if key:
            self.config.provider = name
            try:
                self.provider = get_provider(name, key, self.config.model)
                self.chat.add_system_message(f"Switched to {name}")
            except Exception as e:
                self.chat.add_error(f"Failed: {e}")
        else:
            self.chat.add_system_message(f"No API key for {name}")

    def _cycle_model(self):
        if not self.provider:
            return
        models = self.provider.models
        if not models:
            return
        try:
            idx = models.index(self.config.model) if self.config.model in models else -1
        except ValueError:
            idx = -1
        self.config.model = models[(idx + 1) % len(models)]
        try:
            self.provider = get_provider(
                self.config.provider,
                self.config.get_api_key() or "",
                self.config.model,
            )
            self.chat.add_system_message(f"Model: {self.config.model}")
        except Exception as e:
            self.chat.add_error(f"Failed: {e}")
