"""
LLM module for Fitness Copilot.

Provides integration with Google Gemini API for AI-powered features.
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from app.core.config import settings

if TYPE_CHECKING:
    from app.llm.google import GoogleLLMProvider

logger = logging.getLogger(__name__)

_provider_instance: GoogleLLMProvider | None = None


def get_llm_provider() -> GoogleLLMProvider | None:
    """Return a singleton LLM provider if enabled; else None."""
    global _provider_instance

    if not getattr(settings, "LLM_ENABLED", False):
        return None

    if _provider_instance is not None:
        return _provider_instance

    try:
        from app.llm.google import GoogleLLMProvider

        _provider_instance = GoogleLLMProvider(
            model=getattr(settings, "LLM_MODEL", "gemini-2.5-flash"),
        )
    except Exception as e:
        logger.error("Failed to initialize LLM provider: %s", e)
        _provider_instance = None

    return _provider_instance
