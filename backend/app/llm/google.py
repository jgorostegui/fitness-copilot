"""
Google Gemini LLM Provider.

Provides structured data extraction using Google's Generative AI API.
Includes vision capabilities for image analysis.
"""

from __future__ import annotations

import asyncio
import base64
import json
import logging
import re
from typing import Any

import google.generativeai as genai
from google.generativeai.types import HarmBlockThreshold, HarmCategory

from app.core.config import settings

logger = logging.getLogger(__name__)


class GoogleLLMProvider:
    """Google Gemini LLM provider for structured data extraction."""

    def __init__(self, model: str = "gemini-2.5-flash"):
        api_key = getattr(settings, "GOOGLE_API_KEY", None)
        if not api_key:
            raise ValueError("GOOGLE_API_KEY must be set for the Google LLM provider.")

        genai.configure(api_key=api_key)
        self.model_name = (model or "gemini-2.5-flash").strip()
        self.model = genai.GenerativeModel(self.model_name)

    async def is_healthy(self) -> bool:
        """Check if the LLM provider is healthy."""
        try:
            _ = genai.list_models()
            return True
        except Exception as e:
            logger.debug("Google LLM health check error: %s", e)
            return bool(self.model)

    async def generate(self, prompt: str, timeout_s: float = 30.0) -> str | None:
        """Generate text from a prompt."""
        try:
            response = await asyncio.wait_for(
                self.model.generate_content_async(
                    prompt,
                    generation_config=genai.types.GenerationConfig(
                        temperature=0.7,
                    ),
                    safety_settings=self._get_safety_settings(),
                ),
                timeout=timeout_s,
            )
            return self._extract_text(response)
        except TimeoutError:
            logger.warning("LLM generation timed out after %.1fs", timeout_s)
            return None
        except Exception as e:
            logger.error("LLM generation error: %s", e)
            return None

    async def extract_json(
        self, prompt: str, timeout_s: float = 30.0
    ) -> list[dict[str, Any]]:
        """Extract structured JSON data from a prompt."""
        max_retries = 3

        for attempt in range(max_retries):
            try:
                response = await asyncio.wait_for(
                    self.model.generate_content_async(
                        prompt,
                        generation_config=genai.types.GenerationConfig(
                            response_mime_type="application/json",
                            temperature=0.2,
                        ),
                        safety_settings=self._get_safety_settings(),
                    ),
                    timeout=timeout_s,
                )
                raw = self._extract_text(response)
                return self._parse_json(raw)

            except Exception as e:
                msg = str(e)
                is_rate_limit = "429" in msg or "rate" in msg.lower()

                if is_rate_limit and attempt < max_retries - 1:
                    wait_time = 2 ** (attempt + 1)
                    logger.warning(
                        "LLM rate limited (attempt %d/%d). Waiting %ds...",
                        attempt + 1,
                        max_retries,
                        wait_time,
                    )
                    await asyncio.sleep(wait_time)
                    continue

                logger.error("LLM JSON extraction failed: %s", msg)
                return []

        return []

    def _get_safety_settings(self) -> dict:
        """Get permissive safety settings."""
        return {
            HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
            HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
            HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
            HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
        }

    def _extract_text(self, response: Any) -> str | None:
        """Extract text from Gemini response."""
        try:
            candidates = getattr(response, "candidates", None) or []
            for candidate in candidates:
                content = getattr(candidate, "content", None)
                parts = getattr(content, "parts", None) or []
                for part in parts:
                    text = getattr(part, "text", None)
                    if isinstance(text, str) and text.strip():
                        return text
        except Exception:
            pass

        try:
            text = getattr(response, "text", None)
            if isinstance(text, str) and text.strip():
                return text
        except Exception:
            pass

        return None

    def _parse_json(self, raw: str | None) -> list[dict[str, Any]]:
        """Parse JSON from raw LLM output."""
        if not raw:
            return []

        raw = raw.strip()

        # Try direct parse
        try:
            obj = json.loads(raw)
            if isinstance(obj, dict):
                return [obj]
            if isinstance(obj, list):
                return [d for d in obj if isinstance(d, dict)]
        except json.JSONDecodeError:
            pass

        # Strip code fences
        if raw.startswith("```"):
            raw = raw.strip("`")
            if raw.lower().startswith("json"):
                raw = raw[4:].strip()

        # Try to find JSON array
        match = re.search(r"\[[\s\S]*\]", raw)
        if match:
            try:
                obj = json.loads(match.group(0))
                if isinstance(obj, list):
                    return [d for d in obj if isinstance(d, dict)]
            except json.JSONDecodeError:
                pass

        # Try to find JSON object
        match = re.search(r"\{[\s\S]*\}", raw)
        if match:
            try:
                obj = json.loads(match.group(0))
                if isinstance(obj, dict):
                    return [obj]
            except json.JSONDecodeError:
                pass

        return []

    def _build_image_parts(
        self,
        prompt: str,
        image_url: str | None = None,
        image_base64: str | None = None,
    ) -> list[Any]:
        """Build content parts for image analysis.

        Args:
            prompt: Text prompt for the analysis
            image_url: URL to fetch image from (for demo images)
            image_base64: Base64-encoded image data

        Returns:
            List of content parts for Gemini API
        """
        parts: list[Any] = []

        # Add image part first (Gemini prefers image before text)
        if image_base64:
            # Decode base64 to bytes for inline_data
            try:
                image_bytes = base64.b64decode(image_base64)
                parts.append(
                    {
                        "inline_data": {
                            "mime_type": "image/jpeg",
                            "data": base64.b64encode(image_bytes).decode("utf-8"),
                        }
                    }
                )
            except Exception as e:
                logger.warning("Failed to decode base64 image: %s", e)
        elif image_url:
            # For URLs, we need to fetch and include as inline_data
            # Gemini doesn't support direct URL fetching in all cases
            import urllib.request

            try:
                with urllib.request.urlopen(image_url, timeout=10) as response:
                    image_bytes = response.read()
                    parts.append(
                        {
                            "inline_data": {
                                "mime_type": "image/jpeg",
                                "data": base64.b64encode(image_bytes).decode("utf-8"),
                            }
                        }
                    )
            except Exception as e:
                logger.warning("Failed to fetch image from URL: %s", e)

        # Add text prompt
        parts.append(prompt)

        return parts

    async def analyze_image(
        self,
        prompt: str,
        image_url: str | None = None,
        image_base64: str | None = None,
        timeout_s: float = 30.0,
    ) -> str | None:
        """Analyze an image with a text prompt using Gemini Vision.

        Args:
            prompt: Text prompt describing what to analyze
            image_url: URL to the image (e.g., from demo-images/)
            image_base64: Base64-encoded image data
            timeout_s: Timeout in seconds (default 30s)

        Returns:
            Extracted text response or None on failure
        """
        if not image_url and not image_base64:
            logger.warning("analyze_image called without image data")
            return None

        try:
            parts = self._build_image_parts(prompt, image_url, image_base64)

            if len(parts) < 2:
                # No image was successfully added
                logger.warning("No valid image data provided for analysis")
                return None

            response = await asyncio.wait_for(
                self.model.generate_content_async(
                    parts,
                    generation_config=genai.types.GenerationConfig(temperature=0.3),
                    safety_settings=self._get_safety_settings(),
                ),
                timeout=timeout_s,
            )
            return self._extract_text(response)
        except TimeoutError:
            logger.warning("Vision analysis timed out after %.1fs", timeout_s)
            return None
        except Exception as e:
            logger.error("Vision analysis error: %s", e)
            return None

    async def extract_json_from_image(
        self,
        prompt: str,
        image_url: str | None = None,
        image_base64: str | None = None,
        timeout_s: float = 30.0,
    ) -> list[dict[str, Any]]:
        """Extract structured JSON from an image analysis.

        Args:
            prompt: Text prompt requesting JSON output
            image_url: URL to the image
            image_base64: Base64-encoded image data
            timeout_s: Timeout in seconds (default 30s)

        Returns:
            List of parsed JSON objects, empty list on failure
        """
        if not image_url and not image_base64:
            logger.warning("extract_json_from_image called without image data")
            return []

        max_retries = 3

        for attempt in range(max_retries):
            try:
                parts = self._build_image_parts(prompt, image_url, image_base64)

                if len(parts) < 2:
                    logger.warning("No valid image data provided for JSON extraction")
                    return []

                response = await asyncio.wait_for(
                    self.model.generate_content_async(
                        parts,
                        generation_config=genai.types.GenerationConfig(
                            response_mime_type="application/json",
                            temperature=0.2,
                        ),
                        safety_settings=self._get_safety_settings(),
                    ),
                    timeout=timeout_s,
                )
                raw = self._extract_text(response)
                return self._parse_json(raw)

            except Exception as e:
                msg = str(e)
                is_rate_limit = "429" in msg or "rate" in msg.lower()

                if is_rate_limit and attempt < max_retries - 1:
                    wait_time = 2 ** (attempt + 1)
                    logger.warning(
                        "Vision JSON extraction rate limited (attempt %d/%d). Waiting %ds...",
                        attempt + 1,
                        max_retries,
                        wait_time,
                    )
                    await asyncio.sleep(wait_time)
                    continue

                logger.error("Vision JSON extraction failed: %s", msg)
                return []

        return []
