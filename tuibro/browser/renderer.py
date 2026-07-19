"""Terminal-friendly rendering of browser page data for TUI display."""

from tuibro.browser.dom import render_a11y_page


def render_browser_view(pageinfo, width: int = 80, height: int = 40) -> list:
    """Render complete browser view for a TUI pane."""
    if pageinfo.loading:
        return __loading_lines(width)

    lines = render_a11y_page(pageinfo, width, height - 1)

    if not lines:
        lines = ["No content available"]

    return lines


def render_status_title(pageinfo) -> str:
    if pageinfo.loading:
        return "Loading..."
    if pageinfo.error:
        return f"Error: {pageinfo.error[:50]}"
    if not pageinfo.url:
        return "No page loaded"
    title = pageinfo.title[:50] if pageinfo.title else "Untitled"
    return title


def __loading_lines(width: int) -> list:
    frames = ["⣾", "⣽", "⣻", "⢿", "⡿", "⣟", "⣯", "⣷"]
    import itertools
    spinner = itertools.cycle(frames)
    return [f"{next(spinner)} Loading..."]
