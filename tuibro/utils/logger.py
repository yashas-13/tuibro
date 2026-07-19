"""Debug logging for Tuibro."""
import logging
from pathlib import Path

LOG_DIR = Path.home() / ".tuibro"
LOG_FILE = LOG_DIR / "debug.log"


def setup_logger(debug: bool = False) -> logging.Logger:
    logger = logging.getLogger("tuibro")
    logger.setLevel(logging.DEBUG if debug else logging.WARNING)
    if debug:
        LOG_DIR.mkdir(parents=True, exist_ok=True)
        handler = logging.FileHandler(LOG_FILE)
        handler.setLevel(logging.DEBUG)
        formatter = logging.Formatter(
            "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    return logger
