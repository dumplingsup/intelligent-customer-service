"""Shared pytest fixtures and configuration."""

import pytest
from unittest.mock import MagicMock, patch
from fastapi.testclient import TestClient


@pytest.fixture
def mock_vectorstore():
    """Create a mock vectorstore for testing."""
    mock = MagicMock()
    mock.add = MagicMock()
    mock.similarity_search = MagicMock(return_value=[])
    return mock


@pytest.fixture
def mock_agent():
    """Create a mock agent for testing."""
    mock = MagicMock()
    mock.query = MagicMock(return_value={
        "answer": "Mock response",
        "session_id": "test-session"
    })
    mock.get_session_history = MagicMock(return_value=[])
    mock.clear_session = MagicMock()
    return mock


@pytest.fixture
def client(mock_vectorstore, mock_agent):
    """Create a test client with mocked dependencies."""
    with patch('src.api.routes.get_vectorstore', return_value=mock_vectorstore):
        with patch('src.api.routes.get_agent', return_value=mock_agent):
            from src.api.routes import app
            with TestClient(app) as test_client:
                yield test_client


@pytest.fixture
def real_client():
    """Create a test client with real dependencies (for integration tests)."""
    from src.api.routes import app
    with TestClient(app) as test_client:
        yield test_client
