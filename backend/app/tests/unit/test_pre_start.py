"""
Unit tests for pre-start scripts.

These are Small (Unit) tests - fully mocked, no DB, no network.
"""

from unittest.mock import MagicMock, patch

import pytest


@pytest.mark.unit
def test_backend_init_successful_connection() -> None:
    """Test that backend init() successfully connects to the database."""
    engine_mock = MagicMock()
    session_mock = MagicMock()
    session_mock.exec.return_value = MagicMock(return_value=True)

    with (
        patch("app.backend_pre_start.Session") as mock_session_class,
        patch("app.backend_pre_start.logger"),
    ):
        mock_session_class.return_value.__enter__.return_value = session_mock
        mock_session_class.return_value.__exit__.return_value = None

        from app.backend_pre_start import init

        init(engine_mock)

        mock_session_class.assert_called_once_with(engine_mock)
        session_mock.exec.assert_called_once()


@pytest.mark.unit
def test_tests_init_successful_connection() -> None:
    """Test that tests init() successfully connects to the database."""
    engine_mock = MagicMock()
    session_mock = MagicMock()
    session_mock.exec.return_value = MagicMock(return_value=True)

    with (
        patch("app.tests_pre_start.Session") as mock_session_class,
        patch("app.tests_pre_start.logger"),
    ):
        mock_session_class.return_value.__enter__.return_value = session_mock
        mock_session_class.return_value.__exit__.return_value = None

        from app.tests_pre_start import init

        init(engine_mock)

        mock_session_class.assert_called_once_with(engine_mock)
        session_mock.exec.assert_called_once()
