"""Browser action definitions — tabs, DOM control, extraction, navigation."""
TOOL_DEFINITIONS = [
    # ── Navigation ──────────────────────────────────────────────────
    {
        "type": "function",
        "function": {
            "name": "navigate",
            "description": "Navigate to a URL in the current tab",
            "parameters": {
                "type": "object",
                "properties": {
                    "url": {"type": "string", "description": "URL to navigate to (include https://)"}
                },
                "required": ["url"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "go_back",
            "description": "Go back in browser history",
            "parameters": {"type": "object", "properties": {}},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "go_forward",
            "description": "Go forward in browser history",
            "parameters": {"type": "object", "properties": {}},
        },
    },
    # ── Tab Management ──────────────────────────────────────────────
    {
        "type": "function",
        "function": {
            "name": "new_tab",
            "description": "Open a new browser tab, optionally navigating to a URL",
            "parameters": {
                "type": "object",
                "properties": {
                    "url": {"type": "string", "description": "URL to open in the new tab (default: about:blank)"}
                },
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "close_tab",
            "description": "Close a browser tab by index (default: current tab)",
            "parameters": {
                "type": "object",
                "properties": {
                    "index": {"type": "integer", "description": "Tab index to close (default: current tab)"}
                },
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "switch_tab",
            "description": "Switch to a different tab by index. Check the tab list in the page state first.",
            "parameters": {
                "type": "object",
                "properties": {
                    "index": {"type": "integer", "description": "Tab index to switch to (0-based)"}
                },
                "required": ["index"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "list_tabs",
            "description": "List all open tabs with their index, title, URL, and active status",
            "parameters": {"type": "object", "properties": {}},
        },
    },
    # ── Interaction ─────────────────────────────────────────────────
    {
        "type": "function",
        "function": {
            "name": "click",
            "description": "Click an element by its index from the interactive elements list",
            "parameters": {
                "type": "object",
                "properties": {
                    "element_index": {"type": "integer", "description": "Index of the element to click"}
                },
                "required": ["element_index"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "type_text",
            "description": "Type text into an input element",
            "parameters": {
                "type": "object",
                "properties": {
                    "element_index": {"type": "integer", "description": "Index of the input element"},
                    "text": {"type": "string", "description": "Text to type"},
                },
                "required": ["element_index", "text"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "select_option",
            "description": "Select an option from a dropdown/select element",
            "parameters": {
                "type": "object",
                "properties": {
                    "element_index": {"type": "integer", "description": "Index of the select element"},
                    "value": {"type": "string", "description": "Value to select"},
                },
                "required": ["element_index", "value"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "scroll",
            "description": "Scroll the page up or down",
            "parameters": {
                "type": "object",
                "properties": {
                    "direction": {"type": "string", "enum": ["up", "down"], "description": "Direction to scroll"},
                    "amount": {"type": "integer", "description": "Number of scroll units (default 3)"},
                },
                "required": ["direction"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "wait",
            "description": "Wait for a number of seconds",
            "parameters": {
                "type": "object",
                "properties": {
                    "seconds": {"type": "number", "description": "Seconds to wait (max 10)"}
                },
                "required": ["seconds"],
            },
        },
    },
    # ── DOM Control ─────────────────────────────────────────────────
    {
        "type": "function",
        "function": {
            "name": "get_element_text",
            "description": "Get the full text content of an element by its index",
            "parameters": {
                "type": "object",
                "properties": {
                    "element_index": {"type": "integer", "description": "Index of the element"}
                },
                "required": ["element_index"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_element_attribute",
            "description": "Get an attribute value from an element by its index",
            "parameters": {
                "type": "object",
                "properties": {
                    "element_index": {"type": "integer", "description": "Index of the element"},
                    "attribute": {"type": "string", "description": "Attribute name (href, src, class, id, etc.)"},
                },
                "required": ["element_index", "attribute"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "evaluate_js",
            "description": "Execute arbitrary JavaScript in the page context and return the result. Use for data extraction, DOM manipulation, or reading page state.",
            "parameters": {
                "type": "object",
                "properties": {
                    "expression": {"type": "string", "description": "JavaScript expression to evaluate. Return value will be serialized."}
                },
                "required": ["expression"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_page_html",
            "description": "Get the full or partial HTML of the page. Use CSS selector to get specific elements.",
            "parameters": {
                "type": "object",
                "properties": {
                    "selector": {"type": "string", "description": "CSS selector (default: entire body). e.g. '.content', '#main', 'table.results'"}
                },
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_all_links",
            "description": "Extract all links from the current page with their text and URLs",
            "parameters": {"type": "object", "properties": {}},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_all_forms",
            "description": "Extract all forms on the page with their fields, names, types, and current values",
            "parameters": {"type": "object", "properties": {}},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_cookies",
            "description": "Get all cookies for the current page",
            "parameters": {"type": "object", "properties": {}},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "set_local_storage",
            "description": "Set a value in the page's localStorage",
            "parameters": {
                "type": "object",
                "properties": {
                    "key": {"type": "string", "description": "localStorage key"},
                    "value": {"type": "string", "description": "Value to set"},
                },
                "required": ["key", "value"],
            },
        },
    },
    # ── Completion ──────────────────────────────────────────────────
    {
        "type": "function",
        "function": {
            "name": "done",
            "description": "Signal task completion and provide the final answer",
            "parameters": {
                "type": "object",
                "properties": {
                    "answer": {"type": "string", "description": "Final answer or summary"}
                },
                "required": ["answer"],
            },
        },
    },
]


async def execute_tool(tool_name: str, arguments: dict, engine) -> str:
    """Execute a browser tool call and return a result string."""
    # Coerce missing required parameters from available args
    if tool_name == "navigate" and "url" not in arguments:
        for v in arguments.values():
            if isinstance(v, str) and ("http" in v or "www" in v):
                arguments["url"] = v
                break
    elif tool_name == "evaluate_js" and "expression" not in arguments:
        for v in arguments.values():
            if isinstance(v, str) and len(v) > 2:
                arguments["expression"] = v
                break
    elif tool_name == "scroll" and "direction" not in arguments:
        arguments["direction"] = "down"
    elif tool_name in ("click", "type_text", "get_element_text", "get_element_attribute") and "element_index" not in arguments:
        for v in arguments.values():
            if isinstance(v, int):
                arguments["element_index"] = v
                break
    elif tool_name == "switch_tab" and "index" not in arguments:
        for v in arguments.values():
            if isinstance(v, int):
                arguments["index"] = v
                break
    elif tool_name == "done" and "answer" not in arguments:
        for v in arguments.values():
            if isinstance(v, str) and len(v) > 2:
                arguments["answer"] = v
                break
        if "answer" not in arguments:
            arguments["answer"] = "Task complete."

    try:
        # ── Navigation ──
        if tool_name == "navigate":
            result = await engine.navigate(arguments["url"])
            return _format_page_result(result, "Navigate")

        if tool_name == "go_back":
            result = await engine.go_back()
            return _format_page_result(result, "Go back")

        if tool_name == "go_forward":
            result = await engine.go_forward()
            return _format_page_result(result, "Go forward")

        # ── Tabs ──
        if tool_name == "new_tab":
            url = arguments.get("url", "about:blank")
            result = await engine.new_tab(url)
            return _format_page_result(result, f"New tab: {url}")

        if tool_name == "close_tab":
            index = arguments.get("index")
            result = await engine.close_tab(index)
            return _format_page_result(result, f"Closed tab {index or 'current'}")

        if tool_name == "switch_tab":
            result = await engine.switch_tab(arguments["index"])
            return _format_page_result(result, f"Switched to tab {arguments['index']}")

        if tool_name == "list_tabs":
            return _format_tab_list(engine)

        # ── Interaction ──
        if tool_name == "click":
            result = await engine.click(arguments["element_index"])
            return _format_page_result(result, f"Click [{arguments['element_index']}]")

        if tool_name == "type_text":
            result = await engine.type_text(arguments["element_index"], arguments["text"])
            return _format_page_result(result, f"Type '{arguments['text'][:30]}'")

        if tool_name == "select_option":
            result = await engine.select_option(arguments["element_index"], arguments["value"])
            return _format_page_result(result, f"Select '{arguments['value']}'")

        if tool_name == "scroll":
            amount = arguments.get("amount", 3)
            result = await engine.scroll(arguments["direction"], amount)
            return _format_page_result(result, f"Scroll {arguments['direction']} {amount}")

        if tool_name == "wait":
            await engine.wait(arguments.get("seconds", 1.0))
            return f"Waited {arguments.get('seconds', 1.0)}s"

        # ── DOM Control ──
        if tool_name == "get_element_text":
            return await _get_element_text(arguments["element_index"], engine)

        if tool_name == "get_element_attribute":
            return await _get_element_attribute(arguments["element_index"], arguments["attribute"], engine)

        if tool_name == "evaluate_js":
            return await _evaluate_js(arguments["expression"], engine)

        if tool_name == "get_page_html":
            selector = arguments.get("selector", "")
            return await _get_page_html(selector, engine)

        if tool_name == "get_all_links":
            return await _get_all_links(engine)

        if tool_name == "get_all_forms":
            return await _get_all_forms(engine)

        if tool_name == "get_cookies":
            return await _get_cookies(engine)

        if tool_name == "set_local_storage":
            return await _set_local_storage(arguments["key"], arguments["value"], engine)

        # ── Completion ──
        if tool_name == "done":
            return f"DONE: {arguments['answer']}"

        return f"Unknown tool: {tool_name}"

    except Exception as e:
        return f"Error executing {tool_name}: {e}"


# ── Formatting helpers ─────────────────────────────────────────────

def _format_page_result(page, action: str) -> str:
    if page.error:
        return f"Error: {page.error}"

    lines = [f"=== {action} ==="]
    lines.append(f"Tab: [{page.tab_index}/{page.tab_count}] {page.tab_title}")
    lines.append(f"URL: {page.url}")
    lines.append(f"Title: {page.title}")

    if page.scroll_position:
        sp = page.scroll_position
        pct = (sp.get("y", 0) / max(sp.get("maxY", 1), 1)) * 100
        lines.append(f"Scroll: {pct:.0f}%")

    lines.append("")
    lines.append(f"Interactive elements ({len(page.interactive_elements)}):")
    for el in page.interactive_elements[:35]:
        focused = " [FOCUSED]" if el.focused else ""
        lines.append(f"  [{el.index}] {el.role}: {el.name}{focused}")

    if len(page.interactive_elements) > 35:
        lines.append(f"  ... and {len(page.interactive_elements) - 35} more")

    if page.page_text:
        lines.append("")
        lines.append(f"Text: {page.page_text[:400]}")

    return "\n".join(lines)


def _format_tab_list(engine) -> str:
    lines = ["Open tabs:"]
    for tab in engine.tabs:
        active = " ◄ active" if tab.is_active else ""
        title = tab.title[:40] if tab.title else "Untitled"
        url = tab.page.url if tab.page else "about:blank"
        url = url[:60]
        lines.append(f"  [{tab.index}] {title}{active}")
        lines.append(f"       {url}")
    return "\n".join(lines)


# ── DOM control helpers ────────────────────────────────────────────

async def _get_element_text(element_index: int, engine) -> str:
    cache = getattr(engine, "_interactive_cache", [])
    element = None
    for el in cache:
        if el.index == element_index:
            element = el
            break
    if not element:
        return f"Element {element_index} not found"

    selector = engine._build_selector(element)
    try:
        text = await engine._page.eval_on_selector(selector, "el => el.textContent")
        return f"[{element_index}] text: {(text or '').strip()[:500]}"
    except Exception as e:
        return f"Error reading text: {e}"


async def _get_element_attribute(element_index: int, attribute: str, engine) -> str:
    cache = getattr(engine, "_interactive_cache", [])
    element = None
    for el in cache:
        if el.index == element_index:
            element = el
            break
    if not element:
        return f"Element {element_index} not found"

    selector = engine._build_selector(element)
    try:
        value = await engine._page.eval_on_selector(
            selector, f"el => el.getAttribute('{attribute}')"
        )
        return f"[{element_index}] {attribute}={value}"
    except Exception as e:
        return f"Error reading attribute: {e}"


async def _evaluate_js(expression: str, engine) -> str:
    try:
        result = await engine._page.evaluate(expression)
        if isinstance(result, str):
            return result[:2000]
        import json
        return json.dumps(result, indent=2, default=str)[:2000]
    except Exception as e:
        return f"JS error: {e}"


async def _get_page_html(selector: str, engine) -> str:
    try:
        if selector:
            html = await engine._page.eval_on_selector(
                selector, "el => el.outerHTML"
            )
        else:
            html = await engine._page.evaluate("document.body.innerHTML")
        return (html or "")[:3000]
    except Exception as e:
        return f"HTML error: {e}"


async def _get_all_links(engine) -> str:
    try:
        links = await engine._page.evaluate("""
            () => Array.from(document.querySelectorAll('a[href]')).map(a => ({
                text: a.textContent.trim().substring(0, 60),
                href: a.href,
            })).slice(0, 50)
        """)
        lines = [f"Links ({len(links)}):"]
        for i, link in enumerate(links):
            lines.append(f"  [{i}] {link['text']}")
            lines.append(f"      {link['href']}")
        return "\n".join(lines)
    except Exception as e:
        return f"Error: {e}"


async def _get_all_forms(engine) -> str:
    try:
        forms = await engine._page.evaluate("""
            () => Array.from(document.querySelectorAll('form')).map(f => ({
                action: f.action,
                method: f.method,
                fields: Array.from(f.querySelectorAll('input,select,textarea')).map(el => ({
                    name: el.name || el.id,
                    type: el.type || el.tagName.toLowerCase(),
                    value: el.value || '',
                    placeholder: el.placeholder || '',
                    required: el.required,
                })),
            })).slice(0, 10)
        """)
        lines = [f"Forms ({len(forms)}):"]
        for i, form in enumerate(forms):
            lines.append(f"\n  Form {i}: {form['method'].upper()} {form['action']}")
            for field in form['fields']:
                req = " *" if field.get('required') else ""
                ph = f" (placeholder: {field['placeholder']})" if field.get('placeholder') else ""
                lines.append(f"    {field['name']}: {field['type']} = {field['value']}{req}{ph}")
        return "\n".join(lines)
    except Exception as e:
        return f"Error: {e}"


async def _get_cookies(engine) -> str:
    try:
        cookies = await engine._context.cookies()
        lines = [f"Cookies ({len(cookies)}):"]
        for c in cookies[:20]:
            lines.append(f"  {c['name']}={c['value'][:40]} domain={c.get('domain','')}")
        return "\n".join(lines)
    except Exception as e:
        return f"Error: {e}"


async def _set_local_storage(key: str, value: str, engine) -> str:
    try:
        await engine._page.evaluate(
            f"localStorage.setItem('{key}', '{value}')"
        )
        return f"Set localStorage[{key}] = {value[:50]}"
    except Exception as e:
        return f"Error: {e}"
