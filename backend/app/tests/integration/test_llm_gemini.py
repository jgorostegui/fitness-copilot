"""
Integration tests for Google Gemini LLM provider.

These tests hit the live Gemini API and are skipped by default.
Run with: RUN_INTEGRATION_TESTS=1 uv run pytest -m integration
"""

from __future__ import annotations

import os

import pytest

# Skip all tests in this module unless RUN_INTEGRATION_TESTS is set
pytestmark = [
    pytest.mark.integration,
    pytest.mark.skipif(
        not os.getenv("RUN_INTEGRATION_TESTS"),
        reason="Integration tests skipped by default. Set RUN_INTEGRATION_TESTS=1 to run.",
    ),
]


@pytest.fixture
def llm_provider():
    """Get a configured LLM provider for testing."""
    from app.llm.google import GoogleLLMProvider

    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        pytest.skip("GOOGLE_API_KEY not set")

    return GoogleLLMProvider(model="gemini-2.5-flash")


@pytest.mark.asyncio
async def test_gemini_health_check(llm_provider):
    """Test that the Gemini API is reachable."""
    is_healthy = await llm_provider.is_healthy()
    assert is_healthy is True


@pytest.mark.asyncio
async def test_gemini_generate_text(llm_provider):
    """Test basic text generation."""
    prompt = "Say 'hello world' and nothing else."
    result = await llm_provider.generate(prompt, timeout_s=30.0)

    assert result is not None
    assert "hello" in result.lower()


@pytest.mark.asyncio
async def test_gemini_extract_json(llm_provider):
    """Test JSON extraction from structured prompt."""
    prompt = """
    Return a JSON object with the following structure:
    {"name": "test", "value": 42}

    Return ONLY the JSON, no other text.
    """
    result = await llm_provider.extract_json(prompt, timeout_s=30.0)

    assert isinstance(result, list)
    assert len(result) > 0
    assert "name" in result[0]
    assert "value" in result[0]
