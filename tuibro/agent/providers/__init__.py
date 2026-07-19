"""Provider registry and factory for Tuibro."""
from tuibro.agent.providers.base import BaseProvider


PROVIDER_REGISTRY: dict[str, type[BaseProvider]] = {}


def register_provider(name: str, cls: type[BaseProvider]):
    PROVIDER_REGISTRY[name] = cls


def get_provider(name: str, api_key: str, model: str = None, base_url: str = None) -> BaseProvider:
    if name not in PROVIDER_REGISTRY:
        available = ", ".join(PROVIDER_REGISTRY.keys())
        raise ValueError(f"Unknown provider '{name}'. Available: {available}")
    cls = PROVIDER_REGISTRY[name]
    return cls(api_key=api_key, model=model, base_url=base_url)


def list_providers() -> list[str]:
    return list(PROVIDER_REGISTRY.keys())


def import_all():
    from tuibro.agent.providers import openai
    from tuibro.agent.providers import anthropic
    from tuibro.agent.providers import google
    from tuibro.agent.providers import groq
    from tuibro.agent.providers import mistral
    from tuibro.agent.providers import cohere
    from tuibro.agent.providers import together
    from tuibro.agent.providers import ollama
    from tuibro.agent.providers import lmstudio
    from tuibro.agent.providers import vllm
    from tuibro.agent.providers import openrouter
from tuibro.agent.providers import ninerouter
