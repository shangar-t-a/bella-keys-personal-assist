# ruff: noqa: PLR2004, E501
"""Test configuration and fixtures for EMS MCP Server tests."""

import pytest


@pytest.fixture(scope="session")
def anyio_backend() -> str:
    """Set anyio backend to asyncio."""
    return "asyncio"
