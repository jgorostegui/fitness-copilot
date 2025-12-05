"""
API acceptance tests for vision endpoints.

These are Medium (Acceptance) tests - require DB.
Tests run with LLM_ENABLED=false for deterministic results.

Feature: vision
"""

import base64

import pytest
from fastapi.testclient import TestClient

from app.core.config import settings


def get_demo_token(client: TestClient, persona: str = "cut") -> str:
    """Helper to get a demo user token."""
    r = client.post(f"{settings.API_V1_STR}/demo/login/{persona}")
    return r.json()["access_token"]


def create_test_image_base64() -> str:
    """Create a minimal valid JPEG for testing."""
    # Minimal 1x1 red JPEG
    jpeg_bytes = bytes(
        [
            0xFF,
            0xD8,
            0xFF,
            0xE0,
            0x00,
            0x10,
            0x4A,
            0x46,
            0x49,
            0x46,
            0x00,
            0x01,
            0x01,
            0x00,
            0x00,
            0x01,
            0x00,
            0x01,
            0x00,
            0x00,
            0xFF,
            0xDB,
            0x00,
            0x43,
            0x00,
            0x08,
            0x06,
            0x06,
            0x07,
            0x06,
            0x05,
            0x08,
            0x07,
            0x07,
            0x07,
            0x09,
            0x09,
            0x08,
            0x0A,
            0x0C,
            0x14,
            0x0D,
            0x0C,
            0x0B,
            0x0B,
            0x0C,
            0x19,
            0x12,
            0x13,
            0x0F,
            0x14,
            0x1D,
            0x1A,
            0x1F,
            0x1E,
            0x1D,
            0x1A,
            0x1C,
            0x1C,
            0x20,
            0x24,
            0x2E,
            0x27,
            0x20,
            0x22,
            0x2C,
            0x23,
            0x1C,
            0x1C,
            0x28,
            0x37,
            0x29,
            0x2C,
            0x30,
            0x31,
            0x34,
            0x34,
            0x34,
            0x1F,
            0x27,
            0x39,
            0x3D,
            0x38,
            0x32,
            0x3C,
            0x2E,
            0x33,
            0x34,
            0x32,
            0xFF,
            0xC0,
            0x00,
            0x0B,
            0x08,
            0x00,
            0x01,
            0x00,
            0x01,
            0x01,
            0x01,
            0x11,
            0x00,
            0xFF,
            0xC4,
            0x00,
            0x1F,
            0x00,
            0x00,
            0x01,
            0x05,
            0x01,
            0x01,
            0x01,
            0x01,
            0x01,
            0x01,
            0x00,
            0x00,
            0x00,
            0x00,
            0x00,
            0x00,
            0x00,
            0x00,
            0x01,
            0x02,
            0x03,
            0x04,
            0x05,
            0x06,
            0x07,
            0x08,
            0x09,
            0x0A,
            0x0B,
            0xFF,
            0xC4,
            0x00,
            0xB5,
            0x10,
            0x00,
            0x02,
            0x01,
            0x03,
            0x03,
            0x02,
            0x04,
            0x03,
            0x05,
            0x05,
            0x04,
            0x04,
            0x00,
            0x00,
            0x01,
            0x7D,
            0x01,
            0x02,
            0x03,
            0x00,
            0x04,
            0x11,
            0x05,
            0x12,
            0x21,
            0x31,
            0x41,
            0x06,
            0x13,
            0x51,
            0x61,
            0x07,
            0x22,
            0x71,
            0x14,
            0x32,
            0x81,
            0x91,
            0xA1,
            0x08,
            0x23,
            0x42,
            0xB1,
            0xC1,
            0x15,
            0x52,
            0xD1,
            0xF0,
            0x24,
            0x33,
            0x62,
            0x72,
            0x82,
            0x09,
            0x0A,
            0x16,
            0x17,
            0x18,
            0x19,
            0x1A,
            0x25,
            0x26,
            0x27,
            0x28,
            0x29,
            0x2A,
            0x34,
            0x35,
            0x36,
            0x37,
            0x38,
            0x39,
            0x3A,
            0x43,
            0x44,
            0x45,
            0x46,
            0x47,
            0x48,
            0x49,
            0x4A,
            0x53,
            0x54,
            0x55,
            0x56,
            0x57,
            0x58,
            0x59,
            0x5A,
            0x63,
            0x64,
            0x65,
            0x66,
            0x67,
            0x68,
            0x69,
            0x6A,
            0x73,
            0x74,
            0x75,
            0x76,
            0x77,
            0x78,
            0x79,
            0x7A,
            0x83,
            0x84,
            0x85,
            0x86,
            0x87,
            0x88,
            0x89,
            0x8A,
            0x92,
            0x93,
            0x94,
            0x95,
            0x96,
            0x97,
            0x98,
            0x99,
            0x9A,
            0xA2,
            0xA3,
            0xA4,
            0xA5,
            0xA6,
            0xA7,
            0xA8,
            0xA9,
            0xAA,
            0xB2,
            0xB3,
            0xB4,
            0xB5,
            0xB6,
            0xB7,
            0xB8,
            0xB9,
            0xBA,
            0xC2,
            0xC3,
            0xC4,
            0xC5,
            0xC6,
            0xC7,
            0xC8,
            0xC9,
            0xCA,
            0xD2,
            0xD3,
            0xD4,
            0xD5,
            0xD6,
            0xD7,
            0xD8,
            0xD9,
            0xDA,
            0xE1,
            0xE2,
            0xE3,
            0xE4,
            0xE5,
            0xE6,
            0xE7,
            0xE8,
            0xE9,
            0xEA,
            0xF1,
            0xF2,
            0xF3,
            0xF4,
            0xF5,
            0xF6,
            0xF7,
            0xF8,
            0xF9,
            0xFA,
            0xFF,
            0xDA,
            0x00,
            0x08,
            0x01,
            0x01,
            0x00,
            0x00,
            0x3F,
            0x00,
            0xFB,
            0xD5,
            0xDB,
            0x20,
            0xA8,
            0xF1,
            0x7E,
            0xA9,
            0x00,
            0x0C,
            0x3E,
            0xF5,
            0xFF,
            0xD9,
        ]
    )
    return base64.b64encode(jpeg_bytes).decode("utf-8")


# ============================================================================
# Task 13.1: Test image upload endpoint
# Validates: Requirements 5.2
# ============================================================================


@pytest.mark.acceptance
class TestImageUpload:
    """Tests for POST /upload/image endpoint."""

    def test_upload_image_returns_attachment_id(self, client: TestClient) -> None:
        """
        Test POST /upload/image with base64 image data returns attachment_id.

        Validates: Requirements 5.2
        """
        token = get_demo_token(client, "maintain")
        headers = {"Authorization": f"Bearer {token}"}

        image_base64 = create_test_image_base64()

        r = client.post(
            f"{settings.API_V1_STR}/upload/image",
            headers=headers,
            json={
                "image_base64": image_base64,
                "content_type": "image/jpeg",
            },
        )

        assert r.status_code == 200
        data = r.json()
        assert "attachmentId" in data
        assert len(data["attachmentId"]) > 0

    def test_upload_image_invalid_base64_returns_400(self, client: TestClient) -> None:
        """Test POST /upload/image with invalid base64 returns 400."""
        token = get_demo_token(client, "maintain")
        headers = {"Authorization": f"Bearer {token}"}

        r = client.post(
            f"{settings.API_V1_STR}/upload/image",
            headers=headers,
            json={
                "image_base64": "not-valid-base64!!!",
                "content_type": "image/jpeg",
            },
        )

        assert r.status_code == 400

    def test_upload_image_invalid_content_type_returns_400(
        self, client: TestClient
    ) -> None:
        """Test POST /upload/image with invalid content type returns 400."""
        token = get_demo_token(client, "maintain")
        headers = {"Authorization": f"Bearer {token}"}

        image_base64 = create_test_image_base64()

        r = client.post(
            f"{settings.API_V1_STR}/upload/image",
            headers=headers,
            json={
                "image_base64": image_base64,
                "content_type": "application/pdf",  # Not allowed
            },
        )

        assert r.status_code == 400

    def test_upload_image_unauthenticated_returns_401(self, client: TestClient) -> None:
        """Test POST /upload/image without auth returns 401."""
        image_base64 = create_test_image_base64()

        r = client.post(
            f"{settings.API_V1_STR}/upload/image",
            json={
                "image_base64": image_base64,
                "content_type": "image/jpeg",
            },
        )

        assert r.status_code in [401, 403]


# ============================================================================
# Task 13.4: Test LLM disabled fallback
# Validates: Requirements 7.1, 7.3
# ============================================================================


@pytest.mark.acceptance
class TestVisionLLMDisabled:
    """Tests for vision with LLM_ENABLED=false (default in tests)."""

    def test_image_message_returns_fallback_when_llm_disabled(
        self, client: TestClient
    ) -> None:
        """
        Test POST /chat/messages with image returns fallback when LLM disabled.

        Validates: Requirements 7.1, 7.3
        """
        token = get_demo_token(client, "maintain")
        headers = {"Authorization": f"Bearer {token}"}

        # First upload an image
        image_base64 = create_test_image_base64()
        upload_r = client.post(
            f"{settings.API_V1_STR}/upload/image",
            headers=headers,
            json={
                "image_base64": image_base64,
                "content_type": "image/jpeg",
            },
        )
        attachment_id = upload_r.json()["attachmentId"]

        # Send message with image attachment
        r = client.post(
            f"{settings.API_V1_STR}/chat/messages",
            headers=headers,
            json={
                "content": "What is this?",
                "attachment_type": "image",
                "attachment_url": attachment_id,
            },
        )

        assert r.status_code == 200
        data = r.json()
        assert data["role"] == "assistant"
        # With LLM disabled, should return fallback message
        assert data["actionType"] == "none"
        assert "describe" in data["content"].lower()

    def test_image_message_without_attachment_id_returns_fallback(
        self, client: TestClient
    ) -> None:
        """
        Test POST /chat/messages with image type but no attachment returns fallback.

        Validates: Requirements 7.1, 7.3
        """
        token = get_demo_token(client, "maintain")
        headers = {"Authorization": f"Bearer {token}"}

        r = client.post(
            f"{settings.API_V1_STR}/chat/messages",
            headers=headers,
            json={
                "content": "What is this?",
                "attachment_type": "image",
                "attachment_url": None,
            },
        )

        assert r.status_code == 200
        data = r.json()
        assert data["actionType"] == "none"


# ============================================================================
# Task 13.2 & 13.3: Test gym/food image flows (with mocked LLM)
# These tests verify the flow works, but use LLM disabled fallback
# Validates: Requirements 2.4, 2.5, 3.4, 3.5
# ============================================================================


@pytest.mark.acceptance
class TestVisionImageFlow:
    """Tests for the complete image upload -> chat flow."""

    def test_upload_then_chat_flow_works(self, client: TestClient) -> None:
        """
        Test the complete flow: upload image -> send chat with attachment_id.

        This verifies the integration between upload and chat endpoints.
        """
        token = get_demo_token(client, "maintain")
        headers = {"Authorization": f"Bearer {token}"}

        # Step 1: Upload image
        image_base64 = create_test_image_base64()
        upload_r = client.post(
            f"{settings.API_V1_STR}/upload/image",
            headers=headers,
            json={
                "image_base64": image_base64,
                "content_type": "image/jpeg",
            },
        )
        assert upload_r.status_code == 200
        attachment_id = upload_r.json()["attachmentId"]

        # Step 2: Send chat message with attachment
        chat_r = client.post(
            f"{settings.API_V1_STR}/chat/messages",
            headers=headers,
            json={
                "content": "Analyze this",
                "attachment_type": "image",
                "attachment_url": attachment_id,
            },
        )
        assert chat_r.status_code == 200

        # Step 3: Verify response is valid
        data = chat_r.json()
        assert data["role"] == "assistant"
        assert data["content"] is not None
        assert len(data["content"]) > 0

    def test_chat_messages_include_image_attachments(self, client: TestClient) -> None:
        """
        Test GET /chat/messages includes messages with image attachments.
        """
        token = get_demo_token(client, "maintain")
        headers = {"Authorization": f"Bearer {token}"}

        # Upload and send image message
        image_base64 = create_test_image_base64()
        upload_r = client.post(
            f"{settings.API_V1_STR}/upload/image",
            headers=headers,
            json={
                "image_base64": image_base64,
                "content_type": "image/jpeg",
            },
        )
        attachment_id = upload_r.json()["attachmentId"]

        client.post(
            f"{settings.API_V1_STR}/chat/messages",
            headers=headers,
            json={
                "content": "Check this image",
                "attachment_type": "image",
                "attachment_url": attachment_id,
            },
        )

        # Get messages
        r = client.get(f"{settings.API_V1_STR}/chat/messages", headers=headers)
        assert r.status_code == 200

        data = r.json()
        # Find the user message with image attachment
        user_messages = [m for m in data["data"] if m["role"] == "user"]
        image_messages = [m for m in user_messages if m["attachmentType"] == "image"]
        assert len(image_messages) >= 1
