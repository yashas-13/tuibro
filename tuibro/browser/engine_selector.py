"""Browser engine selector — Carbonyl (text/agent-optimized) vs Playwright (DOM/full-featured)."""
import logging
from enum import Enum

logger = logging.getLogger("tuibro.engine")


class EngineType(str, Enum):
    CARBONYL = "carbonyl"
    PLAYWRIGHT = "playwright"


# Module-level state: which engine we're using
_active_engine: EngineType = EngineType.PLAYWRIGHT
_carbonyl_available: bool | None = None  # None = not checked yet


def set_engine(engine: str):
    global _active_engine
    if engine == "carbonyl":
        _active_engine = EngineType.CARBONYL
    elif engine == "playwright":
        _active_engine = EngineType.PLAYWRIGHT
    else:
        raise ValueError(f"Unknown engine: {engine}. Use 'carbonyl' or 'playwright'")


def get_engine() -> EngineType:
    return _active_engine


def check_carbonyl_available() -> bool:
    """Check if the Carbonyl binary is available and working."""
    global _carbonyl_available
    if _carbonyl_available is not None:
        return _carbonyl_available
    try:
        from carbonyl_agent import CarbonylBrowser
        # Quick smoke test: try instantiating and opening blank page
        b = CarbonylBrowser()
        b.open("about:blank")
        b.drain(1.0)
        b.close()
        _carbonyl_available = True
        return True
    except (ImportError, FileNotFoundError, Exception):
        _carbonyl_available = False
        return False


def get_best_engine(preferred: str = None) -> EngineType:
    """Get the best available engine. Falls Carbonyl → Playwright."""
    if preferred:
        set_engine(preferred)

    if _active_engine == EngineType.CARBONYL and not check_carbonyl_available():
        logger.warning("Carbonyl not available, falling back to Playwright")
        return EngineType.PLAYWRIGHT

    return _active_engine


def create_engine(headless: bool = True, slow_mo: int = 0,
                   viewport_width: int = 1280, viewport_height: int = 720,
                   preferred: str = None):
    """Factory: creates the best available browser engine."""
    engine_type = get_best_engine(preferred)

    if engine_type == EngineType.CARBONYL:
        from tuibro.browser.carbonyl_engine import CarbonylBrowserEngine
        logger.info("Using Carbonyl browser engine")
        return CarbonylBrowserEngine(
            headless=headless,
            slow_mo=slow_mo,
            viewport_width=viewport_width,
            viewport_height=viewport_height,
        )

    if engine_type == EngineType.PLAYWRIGHT:
        from tuibro.browser.engine import BrowserEngine
        logger.info("Using Playwright browser engine")
        return BrowserEngine(
            headless=headless,
            slow_mo=slow_mo,
            viewport_width=viewport_width,
            viewport_height=viewport_height,
        )

    raise RuntimeError("No browser engine available")
