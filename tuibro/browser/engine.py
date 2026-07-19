"""Playwright browser engine for Tuibro — tabs, DOM control, events."""
import asyncio
import logging
import time
from dataclasses import dataclass, field
from typing import Any, Optional, Callable
from enum import Enum

logger = logging.getLogger("tuibro.browser")


class EventType(str, Enum):
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
    event_type: EventType
    timestamp: float
    detail: str
    url: str = ""
    element: str = ""
    data: Any = None

    def __str__(self):
        icons = {
            EventType.NAVIGATE: "→",
            EventType.CLICK: "👆",
            EventType.TYPE: "⌨",
            EventType.SCROLL: "↕",
            EventType.TAB_OPEN: "＋",
            EventType.TAB_CLOSE: "✕",
            EventType.TAB_SWITCH: "⇄",
            EventType.EXTRACT: "📋",
            EventType.JS_EVAL: "⚙",
            EventType.FORM_SUBMIT: "📝",
            EventType.NETWORK: "🌐",
            EventType.ERROR: "✗",
            EventType.INFO: "·",
        }
        icon = icons.get(self.event_type, "·")
        ts = time.strftime("%H:%M:%S", time.localtime(self.timestamp))
        return f"{ts} {icon} {self.detail}"


@dataclass
class Tab:
    index: int
    page: Any = None  # Playwright Page
    title: str = ""
    url: str = ""
    is_active: bool = False


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


class BrowserEngine:
    def __init__(self, headless: bool = True, slow_mo: int = 0,
                 viewport_width: int = 1280, viewport_height: int = 720):
        self.headless = headless
        self.slow_mo = slow_mo
        self.viewport_width = viewport_width
        self.viewport_height = viewport_height
        self._playwright = None
        self._browser = None
        self._context = None
        self._tabs: list[Tab] = []
        self._active_tab_idx: int = 0
        self._element_counter = 0
        self._interactive_cache: list[InteractiveElement] = []
        self._event_log: list[BrowserEvent] = []
        self._max_events = 500
        self._event_listeners: list[Callable] = []

    # ── Events ──────────────────────────────────────────────────────
    def on_event(self, callback: Callable[[BrowserEvent], None]):
        self._event_listeners.append(callback)

    def _emit(self, event_type: EventType, detail: str, **kwargs):
        event = BrowserEvent(
            event_type=event_type,
            timestamp=time.time(),
            detail=detail,
            **kwargs,
        )
        self._event_log.append(event)
        if len(self._event_log) > self._max_events:
            self._event_log = self._event_log[-self._max_events:]
        for cb in self._event_listeners:
            try:
                cb(event)
            except Exception:
                pass

    def get_event_log(self, limit: int = 50) -> list[BrowserEvent]:
        return self._event_log[-limit:]

    # ── Lifecycle ───────────────────────────────────────────────────
    async def start(self):
        from playwright.async_api import async_playwright
        self._playwright = await async_playwright().start()
        self._browser = await self._playwright.chromium.launch(
            headless=self.headless,
            slow_mo=self.slow_mo,
            args=[
                "--no-sandbox", "--disable-gpu", "--disable-dev-shm-usage",
                "--disable-setuid-sandbox", "--single-process",
                "--disable-extensions", "--disable-background-networking",
                "--disable-default-apps", "--no-first-run",
            ],
        )
        self._context = await self._browser.new_context(
            viewport={"width": self.viewport_width, "height": self.viewport_height},
            user_agent=(
                "Mozilla/5.0 (Linux; Android 14; Pixel 8) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Mobile Safari/537.36"
            ),
        )
        first_page = await self._context.new_page()
        self._tabs = [Tab(index=0, page=first_page, is_active=True, title="New Tab")]
        self._active_tab_idx = 0
        self._emit(EventType.INFO, "Browser started")
        logger.info("Browser started (headless=%s)", self.headless)

    async def stop(self):
        for tab in self._tabs:
            try:
                await tab.page.close()
            except Exception:
                pass
        if self._context:
            await self._context.close()
        if self._browser:
            await self._browser.close()
        if self._playwright:
            await self._playwright.stop()
        self._emit(EventType.INFO, "Browser stopped")

    @property
    def _page(self):
        if self._tabs and 0 <= self._active_tab_idx < len(self._tabs):
            return self._tabs[self._active_tab_idx].page
        return None

    @property
    def active_tab(self) -> Tab | None:
        if 0 <= self._active_tab_idx < len(self._tabs):
            return self._tabs[self._active_tab_idx]
        return None

    @property
    def tabs(self) -> list[Tab]:
        return self._tabs

    # ── Tab Management ──────────────────────────────────────────────
    async def new_tab(self, url: str = "about:blank") -> PageInfo:
        page = await self._context.new_page()
        idx = len(self._tabs)
        tab = Tab(index=idx, page=page, is_active=False)
        self._tabs.append(tab)
        await self.switch_tab(idx)
        if url and url != "about:blank":
            await self.navigate(url)
        self._emit(EventType.TAB_OPEN, f"Tab {idx} opened: {url}")
        return await self.get_page_state()

    async def close_tab(self, index: int = None) -> PageInfo:
        if index is None:
            index = self._active_tab_idx
        if index < 0 or index >= len(self._tabs):
            return PageInfo(error=f"Tab {index} does not exist")
        if len(self._tabs) == 1:
            return PageInfo(error="Cannot close the last tab")

        tab = self._tabs[index]
        tab_url = tab.page.url if tab.page else "unknown"
        try:
            await tab.page.close()
        except Exception:
            pass
        self._tabs.pop(index)
        # Re-index tabs
        for i, t in enumerate(self._tabs):
            t.index = i
        # Switch to nearest tab
        if self._active_tab_idx >= len(self._tabs):
            self._active_tab_idx = len(self._tabs) - 1
        self._tabs[self._active_tab_idx].is_active = True
        self._emit(EventType.TAB_CLOSE, f"Tab {index} closed: {tab_url}")
        return await self.get_page_state()

    async def switch_tab(self, index: int) -> PageInfo:
        if index < 0 or index >= len(self._tabs):
            return PageInfo(error=f"Tab {index} does not exist (0-{len(self._tabs)-1})")
        for t in self._tabs:
            t.is_active = False
        self._active_tab_idx = index
        self._tabs[index].is_active = True
        self._emit(EventType.TAB_SWITCH, f"Switched to tab {index}")
        return await self.get_page_state()

    # ── Navigation ──────────────────────────────────────────────────
    async def navigate(self, url: str) -> PageInfo:
        if not url.startswith(("http://", "https://", "about:", "data:")):
            url = "https://" + url
        try:
            await self._page.goto(url, wait_until="domcontentloaded", timeout=30000)
            try:
                await self._page.wait_for_load_state("networkidle", timeout=10000)
            except Exception:
                pass
            self._emit(EventType.NAVIGATE, f"→ {url}", url=url)
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
            selector = self._build_selector(element)
            await self._page.click(selector, timeout=10000)
            self._emit(EventType.CLICK, f"Click [{element.role}] {element.name}", element=f"[{element_index}] {element.name}")
            await self._page.wait_for_load_state("domcontentloaded", timeout=5000)
            try:
                await self._page.wait_for_load_state("networkidle", timeout=5000)
            except Exception:
                pass
        except Exception as e:
            self._emit(EventType.ERROR, f"Click failed: {e}")
            return PageInfo(error=f"Click failed: {e}")
        return await self.get_page_state()

    async def type_text(self, element_index: int, text: str) -> PageInfo:
        element = self._find_element(element_index)
        if not element:
            return PageInfo(error=f"Element {element_index} not found")
        try:
            selector = self._build_selector(element)
            await self._page.click(selector, timeout=5000)
            await self._page.fill(selector, "", timeout=5000)
            await self._page.type(selector, text, delay=30)
            self._emit(EventType.TYPE, f"Type into [{element.role}] {element.name}: {text[:40]}", element=f"[{element_index}] {element.name}")
        except Exception as e:
            self._emit(EventType.ERROR, f"Type failed: {e}")
            return PageInfo(error=f"Type failed: {e}")
        return await self.get_page_state()

    async def select_option(self, element_index: int, value: str) -> PageInfo:
        element = self._find_element(element_index)
        if not element:
            return PageInfo(error=f"Element {element_index} not found")
        try:
            selector = self._build_selector(element)
            await self._page.select_option(selector, value, timeout=5000)
            self._emit(EventType.FORM_SUBMIT, f"Select [{element.role}] {element.name} = {value}", element=f"[{element_index}] {element.name}")
        except Exception as e:
            return PageInfo(error=f"Select failed: {e}")
        return await self.get_page_state()

    async def check(self, element_index: int) -> PageInfo:
        element = self._find_element(element_index)
        if not element:
            return PageInfo(error=f"Element {element_index} not found")
        try:
            selector = self._build_selector(element)
            await self._page.check(selector, timeout=5000)
            self._emit(EventType.CLICK, f"Check [{element.role}] {element.name}", element=f"[{element_index}] {element.name}")
        except Exception as e:
            return PageInfo(error=f"Check failed: {e}")
        return await self.get_page_state()

    async def uncheck(self, element_index: int) -> PageInfo:
        element = self._find_element(element_index)
        if not element:
            return PageInfo(error=f"Element {element_index} not found")
        try:
            selector = self._build_selector(element)
            await self._page.uncheck(selector, timeout=5000)
            self._emit(EventType.CLICK, f"Uncheck [{element.role}] {element.name}", element=f"[{element_index}] {element.name}")
        except Exception as e:
            return PageInfo(error=f"Uncheck failed: {e}")
        return await self.get_page_state()

    async def scroll(self, direction: str = "down", amount: int = 3) -> PageInfo:
        pixels = amount * 300
        delta = pixels if direction == "down" else -pixels
        try:
            await self._page.mouse.wheel(0, delta)
            await asyncio.sleep(0.3)
            self._emit(EventType.SCROLL, f"Scroll {direction} {amount}")
        except Exception as e:
            logger.warning("Scroll failed: %s", e)
        return await self.get_page_state()

    async def go_back(self) -> PageInfo:
        try:
            await self._page.go_back(wait_until="domcontentloaded", timeout=10000)
            self._emit(EventType.NAVIGATE, "← Back")
        except Exception as e:
            logger.warning("Go back failed: %s", e)
        return await self.get_page_state()

    async def go_forward(self) -> PageInfo:
        try:
            await self._page.go_forward(wait_until="domcontentloaded", timeout=10000)
            self._emit(EventType.NAVIGATE, "→ Forward")
        except Exception as e:
            logger.warning("Go forward failed: %s", e)
        return await self.get_page_state()

    async def wait(self, seconds: float = 1.0) -> PageInfo:
        await asyncio.sleep(min(seconds, 10.0))
        self._emit(EventType.INFO, f"Wait {seconds}s")
        return await self.get_page_state()

    # ── Full DOM Control ────────────────────────────────────────────
    async def evaluate_js(self, expression: str) -> PageInfo:
        try:
            result = await self._page.evaluate(expression)
            result_str = str(result)[:500] if result else "(null)"
            self._emit(EventType.JS_EVAL, f"JS: {expression[:60]} → {result_str[:40]}")
            page = await self.get_page_state()
            page.local_storage = {"_js_result": result_str}
            return page
        except Exception as e:
            self._emit(EventType.ERROR, f"JS eval failed: {e}")
            return PageInfo(error=f"JS eval failed: {e}")

    async def get_element_text(self, element_index: int) -> PageInfo:
        element = self._find_element(element_index)
        if not element:
            return PageInfo(error=f"Element {element_index} not found")
        try:
            selector = self._build_selector(element)
            text = await self._page.inner_text(selector, timeout=5000)
            self._emit(EventType.EXTRACT, f"Extract text from [{element.role}] {element.name}")
            page = await self.get_page_state()
            page.page_text = text[:3000]
            return page
        except Exception as e:
            return PageInfo(error=f"Extract text failed: {e}")

    async def get_element_html(self, element_index: int) -> PageInfo:
        element = self._find_element(element_index)
        if not element:
            return PageInfo(error=f"Element {element_index} not found")
        try:
            selector = self._build_selector(element)
            html = await self._page.inner_html(selector, timeout=5000)
            self._emit(EventType.EXTRACT, f"Extract HTML from [{element.role}] {element.name}")
            page = await self.get_page_state()
            page.page_text = html[:5000]
            return page
        except Exception as e:
            return PageInfo(error=f"Extract HTML failed: {e}")

    async def get_element_attribute(self, element_index: int, attribute: str) -> PageInfo:
        element = self._find_element(element_index)
        if not element:
            return PageInfo(error=f"Element {element_index} not found")
        try:
            selector = self._build_selector(element)
            value = await self._page.get_attribute(selector, attribute, timeout=5000)
            self._emit(EventType.EXTRACT, f"Get attribute '{attribute}' from [{element.role}] {element.name}")
            page = await self.get_page_state()
            page.page_text = f"{attribute}={value}"
            return page
        except Exception as e:
            return PageInfo(error=f"Get attribute failed: {e}")

    async def get_all_links(self) -> PageInfo:
        try:
            links = await self._page.evaluate("""
                () => Array.from(document.querySelectorAll('a[href]')).map((a, i) => ({
                    index: i,
                    text: a.innerText.trim().substring(0, 80),
                    href: a.href,
                    title: a.title || '',
                })).filter(l => l.text || l.href).slice(0, 100)
            """)
            self._emit(EventType.EXTRACT, f"Extracted {len(links)} links")
            page = await self.get_page_state()
            lines = []
            for link in links:
                lines.append(f"[{link['index']}] {link['text']} → {link['href']}")
            page.page_text = "\n".join(lines)
            return page
        except Exception as e:
            return PageInfo(error=f"Get links failed: {e}")

    async def get_page_metadata(self) -> PageInfo:
        try:
            meta = await self._page.evaluate("""
                () => ({
                    title: document.title,
                    description: document.querySelector('meta[name="description"]')?.content || '',
                    og_title: document.querySelector('meta[property="og:title"]')?.content || '',
                    og_image: document.querySelector('meta[property="og:image"]')?.content || '',
                    canonical: document.querySelector('link[rel="canonical"]')?.href || '',
                    lang: document.documentElement.lang || '',
                    charset: document.characterSet,
                    links_count: document.querySelectorAll('a[href]').length,
                    images_count: document.querySelectorAll('img').length,
                    forms_count: document.querySelectorAll('form').length,
                    inputs_count: document.querySelectorAll('input,textarea,select').length,
                })
            """)
            self._emit(EventType.EXTRACT, "Extracted page metadata")
            page = await self.get_page_state()
            lines = [
                f"Title: {meta['title']}",
                f"Description: {meta['description'][:200]}",
                f"Language: {meta['lang']}",
                f"Charset: {meta['charset']}",
                f"Canonical: {meta['canonical']}",
                f"Links: {meta['links_count']} | Images: {meta['images_count']} | Forms: {meta['forms_count']} | Inputs: {meta['inputs_count']}",
            ]
            if meta['og_title']:
                lines.append(f"OG Title: {meta['og_title']}")
            if meta['og_image']:
                lines.append(f"OG Image: {meta['og_image']}")
            page.page_text = "\n".join(lines)
            return page
        except Exception as e:
            return PageInfo(error=f"Get metadata failed: {e}")

    async def get_cookies(self) -> PageInfo:
        try:
            cookies = await self._context.cookies()
            self._emit(EventType.EXTRACT, f"Extracted {len(cookies)} cookies")
            page = await self.get_page_state()
            lines = [f"{c['name']}={c['value'][:40]} (domain={c.get('domain','')})" for c in cookies[:50]]
            page.page_text = "\n".join(lines) if lines else "No cookies"
            return page
        except Exception as e:
            return PageInfo(error=f"Get cookies failed: {e}")

    async def get_local_storage(self) -> PageInfo:
        try:
            storage = await self._page.evaluate("() => { const s = {}; for(let i=0; i<localStorage.length; i++){ const k = localStorage.key(i); s[k] = localStorage.getItem(k)?.substring(0,200); } return s; }")
            self._emit(EventType.EXTRACT, f"Extracted {len(storage)} localStorage keys")
            page = await self.get_page_state()
            lines = [f"{k}: {v}" for k, v in list(storage.items())[:50]]
            page.page_text = "\n".join(lines) if lines else "Empty localStorage"
            return page
        except Exception as e:
            return PageInfo(error=f"Get localStorage failed: {e}")

    async def get_network_requests(self) -> PageInfo:
        try:
            # Use performance entries as network proxy
            entries = await self._page.evaluate("""
                () => performance.getEntriesByType('resource').slice(-30).map(e => ({
                    name: e.name.substring(0, 120),
                    type: e.initiatorType,
                    duration: Math.round(e.duration),
                    size: e.transferSize,
                }))
            """)
            self._emit(EventType.NETWORK, f"Got {len(entries)} network entries")
            page = await self.get_page_state()
            lines = []
            for e in entries:
                size_kb = f"{e['size']//1024}KB" if e['size'] > 0 else "?"
                lines.append(f"[{e['type']}] {e['name'][:80]} ({e['duration']}ms, {size_kb})")
            page.page_text = "\n".join(lines) if lines else "No network entries"
            return page
        except Exception as e:
            return PageInfo(error=f"Get network failed: {e}")

    # ── Page State ──────────────────────────────────────────────────
    async def get_page_state(self) -> PageInfo:
        if not self._page:
            return PageInfo(error="Browser not started")
        try:
            url = self._page.url
            title = await self._page.title()
            scroll = await self._page.evaluate(
                "() => ({x: window.scrollX, y: window.scrollY, "
                "maxY: document.documentElement.scrollHeight - window.innerHeight})"
            )
            viewport = {"width": self.viewport_width, "height": self.viewport_height}

            a11y_tree = {}
            try:
                a11y_tree = await self._page.accessibility.snapshot(interesting_only=True) or {}
            except Exception:
                pass

            elements = self._parse_interactive_elements(a11y_tree)

            page_text = ""
            try:
                page_text = await self._page.evaluate(
                    "() => document.body?.innerText?.substring(0, 3000) || ''"
                )
            except Exception:
                pass

            self._interactive_cache = elements

            # Update tab info
            tab = self.active_tab
            if tab:
                tab.url = url
                tab.title = title

            return PageInfo(
                url=url,
                title=title,
                a11y_tree=a11y_tree,
                interactive_elements=elements,
                page_text=page_text,
                scroll_position=scroll,
                viewport_size=viewport,
                tab_index=self._active_tab_idx,
                tab_count=len(self._tabs),
                tab_title=title,
            )
        except Exception as e:
            logger.error("get_page_state failed: %s", e)
            return PageInfo(error=str(e))

    # ── DOM Parsing ─────────────────────────────────────────────────
    def _parse_interactive_elements(self, tree: dict) -> list:
        elements = []
        counter = [0]
        INTERACTIVE_ROLES = {
            "link", "button", "textbox", "searchbox", "combobox",
            "checkbox", "radio", "slider", "spinbutton", "menuitem",
            "tab", "option", "switch", "scrollbar", "treeitem",
            "menuitemcheckbox", "menuitemradio",
        }

        def walk(node: dict, depth: int = 0):
            if not node or depth > 8:
                return
            role = node.get("role", "")
            name = node.get("name", "")
            if role in INTERACTIVE_ROLES or (role not in ("", "generic", "StaticText", "None") and name and depth < 6):
                idx = counter[0]
                counter[0] += 1
                elements.append(InteractiveElement(
                    index=idx,
                    role=role or "element",
                    name=name[:80] if name else "",
                    value=node.get("value", ""),
                    description=node.get("description", ""),
                    focused=node.get("focused", False),
                    rect=node.get("rect", {}),
                    tag=node.get("tagName", ""),
                ))
            for child in node.get("children", []):
                walk(child, depth + 1)

        walk(tree)
        return elements

    def _find_element(self, index: int) -> InteractiveElement | None:
        for el in self._interactive_cache:
            if el.index == index:
                return el
        return None

    def _build_selector(self, element: InteractiveElement) -> str:
        role = element.role
        name = element.name
        if role == "link":
            return f'a:has-text("{name}")' if name else "a"
        if role == "button":
            return f'button:has-text("{name}")' if name else "button"
        if role in ("textbox", "searchbox"):
            if name:
                return f'[placeholder="{name}"]'
            return 'input[type="text"], input:not([type]), textarea'
        if role == "checkbox":
            return 'input[type="checkbox"]'
        if role == "combobox":
            return 'select'
        if role == "radio":
            return 'input[type="radio"]'
        if name:
            return f'[aria-label="{name}"]'
        return f'[role="{role}"]'

    # ── Context Manager ─────────────────────────────────────────────
    async def __aenter__(self):
        await self.start()
        return self

    async def __aexit__(self, *args):
        await self.stop()
