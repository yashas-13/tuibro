"""Configuration management for Tuibro."""
import json
import os
from dataclasses import dataclass, field, asdict
from pathlib import Path


CONFIG_DIR = Path.home() / ".tuibro"
CONFIG_FILE = CONFIG_DIR / "config.json"
KEYS_FILE = CONFIG_DIR / "keys.json"


@dataclass
class Config:
    provider: str = "openai"
    model: str = "gpt-4o"
    headless: bool = True
    browser_engine: str = "playwright"
    slow_mo: int = 0
    max_iterations: int = 20
    chat_ratio: float = 0.4
    viewport_width: int = 1280
    viewport_height: int = 720
    debug: bool = False
    _api_keys: dict = field(default_factory=dict, repr=False)

    def load(self) -> "Config":
        if CONFIG_FILE.exists():
            try:
                data = json.loads(CONFIG_FILE.read_text())
                for k, v in data.items():
                    if k != "_api_keys" and hasattr(self, k):
                        setattr(self, k, v)
            except (json.JSONDecodeError, KeyError):
                pass
        self._load_keys()
        return self

    def save(self):
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        data = asdict(self)
        data.pop("_api_keys", None)
        CONFIG_FILE.write_text(json.dumps(data, indent=2))

    def _load_keys(self):
        if KEYS_FILE.exists():
            try:
                self._api_keys = json.loads(KEYS_FILE.read_text())
            except (json.JSONDecodeError, KeyError):
                self._api_keys = {}

    def get_api_key(self, provider: str = None) -> str | None:
        provider = provider or self.provider
        env_key = os.environ.get(f"TUIBRO_{provider.upper()}_API_KEY")
        if env_key:
            return env_key
        return self._api_keys.get(provider)

    def set_api_key(self, provider: str, key: str):
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        self._api_keys[provider] = key
        KEYS_FILE.write_text(json.dumps(self._api_keys, indent=2))
        os.chmod(KEYS_FILE, 0o600)

    def has_api_key(self, provider: str = None) -> bool:
        return self.get_api_key(provider) is not None
