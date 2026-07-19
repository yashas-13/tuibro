"""A11y tree parsing for Tuibro."""
from dataclasses import dataclass, field
from typing import Any


@dataclass
class A11yNode:
    index: int
    role: str
    name: str
    value: str = ""
    description: str = ""
    focused: bool = False
    depth: int = 0
    is_interactive: bool = False
    rect: dict = field(default_factory=dict)
    tag: str = ""
    attributes: dict = field(default_factory=dict)
    children: list = field(default_factory=list)


INTERACTIVE_ROLES = {
    "link", "button", "textbox", "searchbox", "combobox",
    "checkbox", "radio", "slider", "spinbutton", "menuitem",
    "tab", "option", "switch", "scrollbar", "treeitem",
    "menuitemcheckbox", "menuitemradio", "listbox", "colorwell",
    "date", "time", "datetime", "number",
}

BORING_ROLES = {
    "paragraph", "StaticText", "listitem", "list",
    "region", "main", "contentinfo", "banner", "navigation",
}

INCLUDE_EVEN_BORING_THRESHOLD = 10  # include boring if there are fewer interactive elements


def is_interactive_role(role: str) -> bool:
    return role in INTERACTIVE_ROLES or role.endswith("box") or role.startswith("menu")


def parse_a11y_tree(tree: dict) -> list[A11yNode]:
    """Convert a Playwright a11y snapshot to a list of A11yNode objects."""
    nodes = []
    index_counter = [0]
    interactive_count = [0]

    def walk(subtree: dict, depth: int) -> A11yNode:
        if not subtree or depth > 10:
            return None
        role = subtree.get("role", "")
        name = subtree.get("name", "")
        value = subtree.get("value", "")
        focused = subtree.get("focused", False)

        is_interactive = is_interactive_role(role)

        if is_interactive or (name and role not in BORING_ROLES) or (focused) or depth < 3:
            idx = index_counter[0]
            index_counter[0] += 1
            if is_interactive:
                interactive_count[0] += 1
            node = A11yNode(
                index=idx,
                role=role or "element",
                name=name[:100] if name else "",
                value=value[:100] if value else "",
                description=subtree.get("description", ""),
                focused=focused,
                depth=depth,
                is_interactive=is_interactive,
                rect=subtree.get("rect", {}),
                tag=subtree.get("tagName", ""),
            )
            nodes.append(node)
        else:
            node = None

        children = subtree.get("children", [])
        for child in children:
            walk(child, depth + 1)

        return node

    walk(tree, 0)
    return nodes


def render_a11y_page(pageinfo, width: int, max_lines: int) -> list:
    """Render a page's a11y tree as terminal lines."""
    if pageinfo.error:
        return [f"Error: {pageinfo.error}"]

    if not pageinfo.a11y_tree and not pageinfo.url:
        return ["No page loaded. Type a URL or an agent task (uses /example)!", "", "Examples:", "  /google - Navigate to Google", "   help me find ... - Agent mode"]

    nodes = parse_a11y_tree(pageinfo.a11y_tree)
    if not nodes:
        return [
            f"URL: {pageinfo.title}",
            f"[No interactive elements found on page]",
            f"Page text: {pageinfo.page_text[:200]}" if pageinfo.page_text else "",
        ]

    lines = []
    # Header
    title = pageinfo.title or "Untitled"
    url = pageinfo.url or ""
    lines.append(f"URL: {url}")
    lines.append(f"Title: {title}")

    # Scroll position info
    sp = pageinfo.scroll_position
    if sp and sp.get("maxY", 0) > 0:
        pct = (sp.get("y", 0) / sp.get("maxY", 1)) * 100 if sp.get("maxY") > 0 else 0
        lines.append(f"Scrolled: {pct:.0f}% | Elements: {len(nodes)}")
    else:
        lines.append(f"Elements: {len(nodes)}")

    lines.append("")

    for node in nodes:
        if len(lines) >= max_lines:
            remaining = len(nodes) - nodes.index(node)
            lines.append(f"... and {remaining} more elements")
            break

        indent = "  " * min(node.depth, 6)
        suffix = ""
        if node.focused:
            suffix = "  [FOCUSED]"
        elif node.is_interactive:
            suffix = f"  [→{node.index}]"

        # Build element string
        content = node.name if node.name else node.value if node.value else node.role
        if node.value and node.role not in ("textbox", "searchbox"):
            content = f"{node.name}: {node.value}" if node.name else node.value

        # Truncate
        max_len = width - len(indent) - len(suffix) - 4
        if max_len > 0 and len(content) > max_len:
            content = content[:max_len - 3] + "..."

        if node.is_interactive:
            line = f"{indent}[{node.role}"
            if node.name:
                extra = 30 - len(node.role)
                truncated_name = node.name[:extra + 10]
                line += f"] {truncated_name}"
            else:
                line += "]"
            line += suffix
        else:
            line = f"{indent}{content}"

        lines.append(line)

    return lines
