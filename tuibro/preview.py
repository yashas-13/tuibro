"""Text-based TUI preview — renders the layout as ASCII art."""
from tuibro.browser.engine import PageInfo, BrowserEvent, EventType
import time


def build_preview(width: int = 96, height: int = 34) -> str:
    W = width
    # 3 panes: chat 34%, browser 46%, activity 20%
    C = 32  # chat width
    A = 20  # activity width
    B = W - C - A - 3  # browser width (minus 3 borders)

    def pad(s, n):
        s = str(s)
        if len(s) > n:
            return s[:n-2] + ".."
        return s + " " * max(0, n - len(s))

    # ── Mock data ───────────────────────────────────────────────────
    mock_elements = [
        (0, "searchbox", "Search", True),
        (1, "button", "Google Search", False),
        (2, "button", "I'm Feeling Lucky", False),
        (3, "link", "Python.org", False),
        (4, "link", "Real Python - Tutorials", False),
        (5, "link", "W3Schools Python", False),
        (6, "link", "GeeksforGeeks Python", False),
        (7, "link", "MDN Web Docs", False),
        (8, "link", "freeCodeCamp Python", False),
        (9, "button", "Settings", False),
    ]

    mock_events = [
        ("06:33:06", "·", "Browser started"),
        ("06:33:08", "+", "Tab 0 opened: about:blank"),
        ("06:33:11", "->", "-> https://google.com"),
        ("06:33:16", "o", "Click [0] Search"),
        ("06:33:18", "t", "Type: python tutorials"),
        ("06:33:21", "o", "Click [1] Google Search"),
        ("06:33:24", "+", "Tab 1 opened: httpbin.org"),
        ("06:33:26", "<>", "Switched to tab 0"),
        ("06:33:28", "[]", "Extracted 12 links"),
        ("06:33:31", "v", "Scroll down 3"),
    ]

    chat_lines = [
        "You: Search Google for Python",
        "     tutorials and find the",
        "     best free resources",
        "",
        "Agent: I'll navigate to Google,",
        "  search for Python tutorials,",
        "  and analyze the results.",
        "",
        "  > navigate(https://google.com)",
        "  Page: Google | URL: google.com",
        "",
        "  > click(0)  Search box",
        "  > type_text(0, python tutorials)",
        "  > click(1)  Google Search",
        "",
        "Agent: Found great results:",
        "  1. Python.org - Official docs",
        "  2. Real Python - Tutorials",
        "  3. W3Schools - Interactive",
        "  4. freeCodeCamp - Full course",
        "",
        "  Waiting for next instruction...",
    ]

    br_lines = [
        "Tab: [1/3] python tutorials",
        "URL: https://www.google.com/search?q=python+tutorials",
        "Title: python tutorials - Google Search",
        "Scroll: 0% | Elements: 12",
        "",
        "Interactive elements:",
        "  [0] searchbox: Search [FOCUSED]",
        "  [1] button: Google Search",
        "  [2] button: I'm Feeling Lucky",
        "  [3] link: Python.org",
        "  [4] link: Real Python - Tutorials",
        "  [5] link: W3Schools Python",
        "  [6] link: GeeksforGeeks Python",
        "  [7] link: MDN Web Docs",
        "  [8] link: freeCodeCamp Python",
        "  [9] button: Settings",
        "",
        "Last: Click [1] Google Search",
    ]

    act_lines = [
        "URL: google.com/search?q=py..",
        "Scroll: 0% | Elements: 12",
        "--------------------------------",
        "Activity Log:",
        "",
    ]

    lines = []

    # ── Top border ──────────────────────────────────────────────────
    lines.append("+--" + "-"*(C-1) + "+--" + "-"*(B-1) + "+--" + "-"*(A-1) + "+")

    # ── Tab bar ─────────────────────────────────────────────────────
    tabs = " 0:NewTab  1:Google◄  2:Bing  (chat)"
    lines.append("|" + pad(tabs, C+B+A+2) + "|")

    # ── Separator ───────────────────────────────────────────────────
    lines.append("+" + "-"*C + "+" + "-"*B + "+" + "-"*A + "+")

    # ── Title bars ──────────────────────────────────────────────────
    ct = " Chat "
    bt = " python tutorials - Google Search "
    at = " Activity "
    lines.append("|" + pad(ct, C) + "|" + pad(bt, B) + "|" + pad(at, A) + "|")

    # ── Content ─────────────────────────────────────────────────────
    for i in range(height - 6):
        cl = pad(chat_lines[i] if i < len(chat_lines) else "", C)
        bl = pad(br_lines[i] if i < len(br_lines) else "", B)

        if i < len(act_lines):
            al = pad(act_lines[i], A)
        elif i - len(act_lines) < len(mock_events):
            ev = mock_events[i - len(act_lines)]
            entry = f"{ev[0]} {ev[1]} {ev[2]}"
            al = pad(entry, A)
        else:
            al = pad("", A)

        lines.append(f"|{cl}|{bl}|{al}|")

    # ── Separator ───────────────────────────────────────────────────
    lines.append("+" + "-"*C + "+" + "-"*B + "+" + "-"*A + "+")

    # ── Status bar ──────────────────────────────────────────────────
    status = " Provider: openai | Model: gpt-4o | Agent: Running iter 3/20 | [F1]Help [F2]Prov [F5]Viz"
    lines.append("|" + pad(status, C+B+A+2) + "|")

    # ── Bottom border ───────────────────────────────────────────────
    lines.append("+--" + "-"*(C-1) + "+--" + "-"*(B-1) + "+--" + "-"*(A-1) + "+")

    return "\n".join(lines)


if __name__ == "__main__":
    print(build_preview())
