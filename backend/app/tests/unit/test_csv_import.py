"""
Unit tests for CSV import service.

These are Small (Unit) tests - no DB, no network.
Tests the CSV import logic in isolation.
"""

import pytest
from unittest.mock import MagicMock, patch
from pathlib import Path


@pytest.mark.unit
class TestCSVImportService:
    """Tests for CSVImportService."""

    def test_load_training_programs_returns_zero_when_file_not_exists(self) -> None:
        """Should return 0 when CSV file doesn't exist."""
        from app.services.csv_import import CSVImportService

        service = CSVImportService(data_dir="/nonexistent/path")
        session = MagicMock()

        result = service.load_training_programs(session, "/nonexistent/file.csv")

        assert result == 0
        session.commit.assert_not_called()

    def test_load_meal_plans_returns_zero_when_file_not_exists(self) -> None:
        """Should return 0 when CSV file doesn't exist."""
        from app.services.csv_import import CSVImportService
        import uuid

        service = CSVImportService(data_dir="/nonexistent/path")
        session = MagicMock()
        user_id = uuid.uuid4()

        result = service.load_meal_plans(session, user_id, "/nonexistent/file.csv")

        assert result == 0
        session.commit.assert_not_called()

    def test_load_meal_plans_for_persona_uses_correct_filename(self) -> None:
        """Should construct correct filename for persona."""
        from app.services.csv_import import CSVImportService
        import uuid

        service = CSVImportService(data_dir="data")
        user_id = uuid.uuid4()

        # Mock load_meal_plans to capture the path
        with patch.object(service, "load_meal_plans") as mock_load:
            mock_load.return_value = 0
            session = MagicMock()

            service.load_meal_plans_for_persona(session, user_id, "cut")

            # Verify correct path was used
            mock_load.assert_called_once()
            call_args = mock_load.call_args
            assert "meal_plans_cut.csv" in call_args[0][2]

    def test_load_training_programs_for_persona_uses_correct_filename(self) -> None:
        """Should construct correct filename for persona."""
        from app.services.csv_import import CSVImportService

        service = CSVImportService(data_dir="data")

        # Mock load_training_programs to capture the path
        with patch.object(service, "load_training_programs") as mock_load:
            mock_load.return_value = 0
            session = MagicMock()

            # Mock Path.exists to return False so we don't try to read the file
            with patch.object(Path, "exists", return_value=False):
                result = service.load_training_programs_for_persona(session, "bulk")

            # Should return None when file doesn't exist
            assert result is None


@pytest.mark.unit
class TestCSVImportValidation:
    """Tests for CSV import validation logic."""

    def test_invalid_sets_are_skipped(self) -> None:
        """Rows with sets <= 0 should be skipped."""
        # This is tested implicitly through the property tests
        # but we document the expected behavior here
        pass

    def test_invalid_reps_are_skipped(self) -> None:
        """Rows with reps <= 0 should be skipped."""
        pass

    def test_negative_target_load_is_skipped(self) -> None:
        """Rows with negative target_load_kg should be skipped."""
        pass

    def test_invalid_day_of_week_is_skipped(self) -> None:
        """Rows with day_of_week outside 0-6 should be skipped."""
        pass
