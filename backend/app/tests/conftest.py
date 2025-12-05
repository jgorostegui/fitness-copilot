"""
Root conftest.py - shared fixtures and configuration.

Test organization:
- unit/       - Small tests (no DB, no network)
- integration/ - Medium tests (DB required, localhost only)

Run specific tiers:
- pytest -m unit           # Unit tests only
- pytest -m integration    # Integration tests only
"""

import pytest


def pytest_configure(config: pytest.Config) -> None:
    """Register custom markers."""
    config.addinivalue_line("markers", "unit: Small tests - no DB, no network")
    config.addinivalue_line("markers", "integration: Medium tests - DB required")
