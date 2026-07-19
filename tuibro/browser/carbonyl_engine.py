"""Carbonyl browser engine — text-native, agent-optimized, lightweight."""
import asyncio
import logging
import time
import base64
from dataclasses import dataclass, field
from typing import Any, Optional, Callable

logger = logging.getLogger("tuibro.carbonyl")


@dataclass
class InteractiveElement:
    index: int
    role: str
    name: str
    value: str = ""
    description: str = ""
    focused: bool = False
    rect: dict = field(default_factory=dict)
    tag: str = ""
    attributes: dict = field(default_factory=dict)


@dataclass
class PageInfo:
    url: str = ""
    title: str = ""
    a11y_tree: dict = field(default_factory=dict)
    interactive_elements: list = field(default_factory=list)
    page_text: str = ""
    scroll_position: dict = field(default_factory=dict)
    viewport_size: dict = field(default_factory=dict)
    loading: bool = False
    error: str = ""
    tab_index: int = 0
    tab_count: int = 1
    tab_title: str = ""
    cookies: list = field(default_factory=list)
    local_storage: dict = field(default_factory=dict)
    headers: dict = field(default_factory=dict)


class EventType:
    NAVIGATE = "navigate"
    CLICK = "click"
    TYPE = "type"
    SCROLL = "scroll"
    TAB_OPEN = "tab_open"
    TAB_CLOSE = "tab_close"
    TAB_SWITCH = "tab_switch"
    EXTRACT = "extract"
    JS_EVAL = "js_eval"
    FORM_SUBMIT = "form_submit"
    NETWORK = "network"
    ERROR = "error"
    INFO = "info"


@dataclass
class BrowserEvent:
    event_type: str
    timestamp: float
    detail: str
    url: str = ""
    element: str = ""
    data: Any = None

    def __str__(self):
        icons = {
            EventType.NAVIGATE: "→", EventType.CLICK: "👆", EventType.TYPE: "⌨",
            EventType.SCROLL: "↕", EventType.TAB_OPEN: "＋", EventType.TAB_CLOSE: "✕",
            EventType.TAB_SWITCH: "⇄", EventType.EXTRACT: "📋", EventType.JS_EVAL: "⚙",
            EventType.FORM_SUBMIT: "📝", EventType.NETWORK: "🌐", EventType.ERROR: "✗",
            EventType.INFO: "·",
        }
        icon = icons.get(self.event_type, "·")
        ts = time.strftime("%H:%M:%S", time.localtime(self.timestamp))
        return f"{ts} {icon} {self.detail}"


class CarbonylBrowserEngine:
    """Carbonyl-based browser engine — text-native, agent-optimized."""

    def __init__(self, headless: bool = True, slow_mo: int = 0,
                 viewport_width: int = 1280, viewport_height: int = 720,
                 session: str = "tuibro"):
        self.headless = headless
        self.slow_mo = slow_mo
        self.viewport_width = viewport_width
        self.viewport_height = viewport_height
        self.session = session
        self._browser = None
        self._tabs: list = []
        self._active_tab_idx: int = 0
        self._element_counter = 0
        self._interactive_cache: list = []
        self._event_log: list = []
        self._max_events = 500
        self._event_listeners: list = []

    # ── Events ──────────────────────────────────────────────────────
    def on_event(self, callback):
        self._event_listeners.append(callback)

    def _emit(self, event_type: str, detail: str, **kwargs):
        event = BrowserEvent(event_type=event_type, timestamp=time.time(), detail=detail, **kwargs)
        self._event_log.append(event)
        if len(self._event_log) > self._max_events:
            self._event_log = self._event_log[-self._max_events:]
        for cb in self._event_listeners:
            try:
                cb(event)
            except Exception:
                pass

    def get_event_log(self, limit: int = 50) -> list:
        return self._event_log[-limit:]

    # ── Lifecycle ───────────────────────────────────────────────────
    async def start(self):
        try:
            from carbonyl_agent import CarbonylBrowser
            self._browser = CarbonylBrowser(session=self.session)
            self._browser.open("about:blank")
            self._browser.drain(2.0)
            self._tabs = [{"index": 0, "title": "New Tab", "url": "about:blank", "active": True}]
            self._active_tab_idx = 0
            self._emit(EventType.INFO, "Carbonyl browser started")
            logger.info("Carbonyl browser started (session=%s)", self.session)
        except FileNotFoundError:
            raise RuntimeError("Carbonyl binary not found. Run: carbonyl-agent install")
        except Exception as e:
            raise RuntimeError(f"Carbonyl start failed: {e}")

    async def stop(self):
        if self._browser:
            try:
                self._browser.close()
            except Exception:
                pass
        self._emit(EventType.INFO, "Carbonyl browser stopped")

    # ── Navigation ──────────────────────────────────────────────────
    async def navigate(self, url: str) -> PageInfo:
        if not url.startswith(("http://", "https://", "about:", "data:")):
            url = "https://" + url
        try:
            self._browser.navigate(url)
            self._browser.drain(3.0)
            self._emit(EventType.NAVIGATE, f"→ {url}", url=url)
            # Update tab info
            if 0 <= self._active_tab_idx < len(self._tabs):
                self._tabs[self._active_tab_idx]["url"] = url
        except Exception as e:
            self._emit(EventType.ERROR, f"Navigate failed: {e}", url=url)
            logger.warning("Navigation issue: %s", e)
        return await self.get_page_state()

    # ── Actions ─────────────────────────────────────────────────────
    async def click(self, element_index: int) -> PageInfo:
        element = self._find_element(element_index)
        if not element:
            return PageInfo(error=f"Element {element_index} not found")
        try:
            # Use text-based click if element has a name
            if element.name:
                self._browser.click_text(element.name)
            else:
                # Fall back to coordinate click
                x = element.rect.get("x", 0) + element.rect.get("width", 0) // 2
                y = element.rect.get("y", 0) + element.rect.get("height", 0) // 2
                self._browser.click(x, y)
            self._browser.drain(2.0)
            self._emit(EventType.CLICK, f"Click [{element.role}] {element.name}",
                       element=f"[{element_index}] {element.name}")
        except Exception as e:
            self._emit(EventType.ERROR, f"Click failed: {e}")
            return PageInfo(error=f"Click failed: {e}")
        return await self.get_page_state()

    async def type_text(self, element_index: int, text: str) -> PageInfo:
        element = self._find_element(element_index)
        if not element:
            return PageInfo(error=f"Element {element_index} not found")
        try:
            # Click to focus, then type
            if element.name:
                self._browser.click_text(element.name)
            self._browser.send_keys(text)
            self._browser.drain(1.0)
            self._emit(EventType.TYPE, f"Type into [{element.role}] {element.name}: {text[:40]}",
                       element=f"[{element_index}] {element.name}")
        except Exception as e:
            self._emit(EventType.ERROR, f"Type failed: {e}")
            return PageInfo(error=f"Type failed: {e}")
        return await self.get_page_state()

    async def scroll(self, direction: str = "down", amount: int = 3) -> PageInfo:
        try:
            key = "ArrowDown" if direction == "down" else "ArrowUp"
            for _ in range(amount):
                self._browser.send_key(key)
            self._browser.drain(0.5)
            self._emit(EventType.SCROLL, f"Scroll {direction} {amount}")
        except Exception as e:
            logger.warning("Scroll failed: %s", e)
        return await self.get_page_state()

    async def go_back(self) -> PageInfo:
        try:
            self._browser.send_key("Alt+ArrowLeft")
            self._browser.drain(2.0)
            self._emit(EventType.NAVIGATE, "← Back")
        except Exception as e:
            logger.warning("Go back failed: %s", e)
        return await self.get_page_state()

    async def go_forward(self) -> PageInfo:
        try:
            self._browser.send_key("Alt+ArrowRight")
            self._browser.drain(2.0)
            self._emit(EventType.NAVIGATE, "→ Forward")
        except Exception as e:
            logger.warning("Go forward failed: %s", e)
        return await self.get_page_state()

    async def wait(self, seconds: float = 1.0) -> PageInfo:
        await asyncio.sleep(min(seconds, 10.0))
        self._emit(EventType.INFO, f"Wait {seconds}s")
        return await self.get_page_state()

    # ── Tab Management ──────────────────────────────────────────────
    async def new_tab(self, url: str = "about:blank") -> PageInfo:
        # Carbonyl uses sessions for tab-like isolation
        # For now, navigate in current tab (true multi-tab requires multiple instances)
        self._emit(EventType.TAB_OPEN, f"New tab (navigating): {url}")
        return await self.navigate(url)

    async def close_tab(self, index: int = None) -> PageInfo:
        self._emit(EventType.TAB_CLOSE, f"Close tab {index or 'current'}")
        return PageInfo(tab_index=self._active_tab_idx, tab_count=len(self._tabs))

    async def switch_tab(self, index: int) -> PageInfo:
        if index < 0 or index >= len(self._tabs):
            return PageInfo(error=f"Tab {index} does not exist")
        self._active_tab_idx = index
        self._emit(EventType.TAB_SWITCH, f"Switched to tab {index}")
        return await self.get_page_state()

    # ── DOM Control (text-based) ────────────────────────────────────
    async def evaluate_js(self, expression: str) -> PageInfo:
        try:
            # Carbonyl doesn't expose JS execution directly
            # Use page_text as a proxy
            text = self._browser.page_text()
            self._emit(EventType.JS_EVAL, f"JS eval (text proxy): {expression[:60]}")
            page = await self.get_page_state()
            page.page_text = text[:3000]
            return page
        except Exception as e:
            return PageInfo(error=f"JS eval failed: {e}")

    async def get_element_text(self, element_index: int) -> PageInfo:
        element = self._find_element(element_index)
        if not element:
            return PageInfo(error=f"Element {element_index} not found")
        try:
            # Use find_text to locate and extract
            matches = self._browser.find_text(element.name)
            text = matches[0]["text"] if matches else element.name
            self._emit(EventType.EXTRACT, f"Extract text from [{element.role}] {element.name}")
            page = await self.get_page_state()
            page.page_text = text[:3000]
            return page
        except Exception as e:
            return PageInfo(error=f"Extract text failed: {e}")

    async def get_page_html(self, selector: str = "") -> PageInfo:
        # Carbonyl doesn't expose HTML directly — return text representation
        try:
            text = self._browser.page_text()
            self._emit(EventType.EXTRACT, "Extract page text (Carbonyl text mode)")
            page = await self.get_page_state()
            page.page_text = text[:5000]
            return page
        except Exception as e:
            return PageInfo(error=f"Extract failed: {e}")

    async def get_all_links(self) -> PageInfo:
        try:
            text = self._browser.page_text()
            # Parse links from text output
            lines = text.split("\n")
            link_lines = [l.strip() for l in lines if "http" in l.lower() or "www." in l.lower()]
            self._emit(EventType.EXTRACT, f"Extracted {len(link_lines)} link-like lines")
            page = await self.get_page_state()
            page.page_text = "\n".join(link_lines[:50])
            return page
        except Exception as e:
            return PageInfo(error=f"Get links failed: {e}")

    async def screenshot_page(self, path: str = None) -> PageInfo:
        try:
            # Carbonyl renders to terminal — capture screen as text
            text = self._browser.page_text()
            if path:
                with open(path, "w") as f:
                    f.write(text)
            self._emit(EventType.EXTRACT, "Captured page as text (Carbonyl text mode)")
            page = await self.get_page_state()
            page.page_text = text[:5000]
            return page
        except Exception as e:
            return PageInfo(error=f"Screenshot failed: {e}")

    # ── Page State ──────────────────────────────────────────────────
    async def get_page_state(self) -> PageInfo:
        if not self._browser:
            return PageInfo(error="Browser not started")
        try:
            # Get page text (Carbonyl's native output)
            page_text = self._browser.page_text() or ""

            # Parse text to extract basic info
            lines = page_text.split("\n")
            title = lines[0][:80] if lines else "Untitled"
            url = self._tabs[self._active_tab_idx]["url"] if self._active_tab_idx < len(self._tabs) else ""

            # Extract interactive elements from text
            elements = self._parse_elements_from_text(page_text)
            self._interactive_cache = elements

            return PageInfo(
                url=url,
                title=title,
                page_text=page_text[:3000],
                interactive_elements=elements,
                scroll_position={"x": 0, "y": 0, "maxY": 0},
                viewport_size={"width": self.viewport_width, "height": self.viewport_height},
                tab_index=self._active_tab_idx,
                tab_count=len(self._tabs),
                tab_title=title,
            )
        except Exception as e:
            logger.error("get_page_state failed: %s", e)
            return PageInfo(error=str(e))

    def _parse_elements_from_text(self, text: str) -> list:
        """Parse interactive elements from Carbonyl text output."""
        elements = []
        lines = text.split("\n")
        idx = 0

        for line in lines:
            line = line.strip()
            if not line:
                continue

            # Detect common interactive patterns
            role = "element"
            if any(kw in line.lower() for kw in ["button", "submit", "sign in", "log in", "search"]):
                role = "button"
            elif any(kw in line.lower() for kw in ["link", "http", "www."]):
                role = "link"
            elif any(kw in line.lower() for kw in ["input", "search", "type", "enter"]):
                role = "textbox"
            elif any(kw in line.lower() for kw in ["select", "dropdown", "choose"]):
                role = "combobox"

            if role != "element" or (len(line) > 3 and len(line) < 100):
                elements.append(InteractiveElement(
                    index=idx,
                    role=role,
                    name=line[:80],
                ))
                idx += 1

            if idx >= 30:
                break

        return elements

    def _find_element(self, index: int) -> InteractiveElement | None:
        for el in self._interactive_cache:
            if el.index == index:
                return el
        return None

    # ── Context Manager ─────────────────────────────────────────────
    async def __aenter__(self):
        await self.start()
        return self

    async def __aexit__(self, *args):
        await self.stop()
