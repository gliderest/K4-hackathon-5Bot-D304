from __future__ import annotations

from .openrouter_provider import OpenRouterProvider


def make_provider(provider_name: str) -> OpenRouterProvider:
    """Factory function to create provider instances."""
    if provider_name == "openrouter":
        return OpenRouterProvider()
    else:
        raise ValueError(f"Unknown provider: {provider_name}")