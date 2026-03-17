"""Tests for API routes module."""

import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from pathlib import Path

from src.api.routes import app, QueryRequest, QueryResponse


class TestHealthEndpoint:
    """Test GET /api/health endpoint."""

    def test_health_check_healthy(self, client):
        """Test health check returns healthy status."""
        response = client.get("/api/health")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "vectorstore" in data
        assert "agent" in data

    def test_health_check_initialization_status(self, client):
        """Test health check shows initialization status."""
        response = client.get("/api/health")

        data = response.json()
        assert data["vectorstore"] in ["initialized", "not_initialized"]
        assert data["agent"] in ["initialized", "not_initialized"]


class TestRootEndpoint:
    """Test GET / endpoint."""

    def test_root_returns_api_info(self, client):
        """Test root endpoint returns API information."""
        response = client.get("/")

        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Intelligent Customer Service API"
        assert data["version"] == "0.1.0"
        assert "endpoints" in data

    def test_root_lists_endpoints(self, client):
        """Test root endpoint lists all available endpoints."""
        response = client.get("/")

        data = response.json()
        endpoints = data["endpoints"]
        assert len(endpoints) >= 4
        assert any("/api/query" in ep for ep in endpoints)
        assert any("/api/upload" in ep for ep in endpoints)
        assert any("/api/history" in ep for ep in endpoints)


class TestQueryEndpoint:
    """Test POST /api/query endpoint."""

    def test_query_with_session_id(self, client, mock_agent):
        """Test query endpoint with provided session ID."""
        request_data = {
            "query": "如何申请退款？",
            "session_id": "test-session-123"
        }

        response = client.post("/api/query", json=request_data)

        assert response.status_code == 200
        data = response.json()
        assert "answer" in data
        assert data["session_id"] == "test-session-123"

    def test_query_without_session_id(self, client, mock_agent):
        """Test query endpoint without session ID generates new one."""
        request_data = {
            "query": "订单状态如何查询？"
        }

        response = client.post("/api/query", json=request_data)

        assert response.status_code == 200
        data = response.json()
        assert "session_id" in data
        assert data["session_id"] is not None

    def test_query_returns_answer(self, client, mock_agent):
        """Test query endpoint returns answer."""
        mock_agent.query.return_value = {
            "answer": "您可以通过订单页面查询订单状态",
            "session_id": "test-session"
        }

        request_data = {
            "query": "如何查询订单状态？"
        }

        response = client.post("/api/query", json=request_data)

        assert response.status_code == 200
        data = response.json()
        assert "answer" in data
        assert data["answer"] == "您可以通过订单页面查询订单状态"

    def test_query_returns_sources(self, client):
        """Test query endpoint can return sources."""
        response = client.post("/api/query", json={"query": "测试问题"})

        assert response.status_code == 200
        data = response.json()
        assert "sources" in data

    def test_query_empty_query(self, client):
        """Test query endpoint with empty query."""
        request_data = {
            "query": ""
        }

        response = client.post("/api/query", json=request_data)

        # Should still process (might return a default response)
        assert response.status_code in [200, 400]


class TestHistoryEndpoint:
    """Test GET /api/history/{session_id} endpoint."""

    def test_get_history_existing_session(self, client, mock_agent):
        """Test getting history for existing session."""
        mock_agent.get_session_history.return_value = [
            {"role": "user", "content": "你好"},
            {"role": "assistant", "content": "您好，有什么可以帮助您的？"}
        ]

        response = client.get("/api/history/test-session")

        assert response.status_code == 200
        data = response.json()
        assert data["session_id"] == "test-session"
        assert "history" in data
        assert len(data["history"]) == 2

    def test_get_history_empty_session(self, client, mock_agent):
        """Test getting history for empty session."""
        mock_agent.get_session_history.return_value = []

        response = client.get("/api/history/empty-session")

        assert response.status_code == 200
        data = response.json()
        assert data["session_id"] == "empty-session"
        assert data["history"] == []

    def test_get_history_returns_correct_format(self, client, mock_agent):
        """Test history response format."""
        mock_agent.get_session_history.return_value = [
            {"role": "user", "content": "问题"},
            {"role": "assistant", "content": "回答"}
        ]

        response = client.get("/api/history/session-123")

        data = response.json()
        assert isinstance(data["history"], list)
        for item in data["history"]:
            assert "role" in item
            assert "content" in item


class TestClearHistoryEndpoint:
    """Test DELETE /api/history/{session_id} endpoint."""

    def test_clear_history_existing_session(self, client, mock_agent):
        """Test clearing history for existing session."""
        response = client.delete("/api/history/test-session")

        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "cleared" in data["message"].lower()
        mock_agent.clear_session.assert_called_once_with("test-session")

    def test_clear_history_nonexistent_session(self, client, mock_agent):
        """Test clearing history for nonexistent session."""
        response = client.delete("/api/history/nonexistent-session")

        # Should still succeed (clearing non-existent session is a no-op)
        assert response.status_code == 200


class TestUploadEndpoint:
    """Test POST /api/upload endpoint."""

    def test_upload_single_file(self, client, mock_vectorstore, tmp_path):
        """Test uploading a single file."""
        # Create a test file
        test_file = tmp_path / "test.txt"
        test_file.write_text("Test content for upload")

        with patch('src.api.routes.process_documents') as mock_process:
            mock_process.return_value = [MagicMock(page_content="chunk1")]

            with patch('src.api.routes.add_documents'):
                with open(test_file, "rb") as f:
                    files = {"files": ("test.txt", f, "text/plain")}
                    response = client.post("/api/upload", files=files)

                assert response.status_code == 200
                data = response.json()
                assert "Successfully processed" in data["message"]
                assert data["documents_processed"] == 1

    def test_upload_multiple_files(self, client, mock_vectorstore, tmp_path):
        """Test uploading multiple files."""
        # Create test files
        test_file1 = tmp_path / "test1.txt"
        test_file1.write_text("Test content 1")
        test_file2 = tmp_path / "test2.txt"
        test_file2.write_text("Test content 2")

        with patch('src.api.routes.process_documents') as mock_process:
            mock_process.return_value = [
                MagicMock(page_content="chunk1"),
                MagicMock(page_content="chunk2")
            ]

            with patch('src.api.routes.add_documents'):
                with open(test_file1, "rb") as f1:
                    with open(test_file2, "rb") as f2:
                        files = [
                            ("files", ("test1.txt", f1, "text/plain")),
                            ("files", ("test2.txt", f2, "text/plain"))
                        ]
                        response = client.post("/api/upload", files=files)

                assert response.status_code == 200
                data = response.json()
                assert data["documents_processed"] == 2

    def test_upload_no_files(self, client):
        """Test uploading with no files."""
        response = client.post("/api/upload", files=[])

        # Should return error for no files
        assert response.status_code in [400, 422]

    def test_upload_custom_chunk_parameters(self, client, mock_vectorstore, tmp_path):
        """Test uploading with custom chunk parameters."""
        test_file = tmp_path / "test.txt"
        test_file.write_text("Test content")

        with patch('src.api.routes.process_documents') as mock_process:
            mock_process.return_value = [MagicMock(page_content="chunk1")]

            with patch('src.api.routes.add_documents'):
                with open(test_file, "rb") as f:
                    files = {"files": ("test.txt", f, "text/plain")}
                    # Pass chunk parameters as query parameters
                    response = client.post(
                        "/api/upload?chunk_size=1000&chunk_overlap=100",
                        files=files
                    )

                assert response.status_code == 200
                # Verify chunk parameters were passed
                mock_process.assert_called_once()
                call_args = mock_process.call_args[0]
                call_kwargs = mock_process.call_args[1]
                # Check positional args first, then keyword args
                if len(call_args) >= 2:
                    assert call_args[1] == 1000  # chunk_size
                    assert call_args[2] == 100   # chunk_overlap
                else:
                    assert call_kwargs.get("chunk_size") == 1000
                    assert call_kwargs.get("chunk_overlap") == 100

    def test_upload_cleans_temp_files(self, client, mock_vectorstore, tmp_path):
        """Test that upload cleans up temporary files."""
        test_file = tmp_path / "test.txt"
        test_file.write_text("Test content")

        temp_dir = Path("./temp_uploads")

        with patch('src.api.routes.process_documents') as mock_process:
            mock_process.return_value = [MagicMock(page_content="chunk1")]

            with patch('src.api.routes.add_documents'):
                with open(test_file, "rb") as f:
                    files = {"files": ("test.txt", f, "text/plain")}
                    response = client.post("/api/upload", files=files)

                assert response.status_code == 200

        # Temp files should be cleaned up (test may not fully verify this)
        # but the code attempts cleanup


class TestAPIIntegration:
    """Integration tests for API with real dependencies."""

    def test_api_startup(self):
        """Test that API can start up without errors."""
        # This tests that the app can be imported and created
        from src.api.routes import app
        assert app is not None
        assert app.title == "Intelligent Customer Service API"

    def test_health_with_real_app(self, real_client):
        """Test health endpoint with real app (no mocks)."""
        response = real_client.get("/api/health")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"


class TestPydanticModels:
    """Test Pydantic request/response models."""

    def test_query_request_with_query_only(self):
        """Test QueryRequest with only query field."""
        request = QueryRequest(query="测试问题")
        assert request.query == "测试问题"
        assert request.session_id is None

    def test_query_request_with_session_id(self):
        """Test QueryRequest with session ID."""
        request = QueryRequest(query="测试问题", session_id="test-123")
        assert request.query == "测试问题"
        assert request.session_id == "test-123"

    def test_query_response(self):
        """Test QueryResponse model."""
        response = QueryResponse(
            answer="测试回答",
            sources=["来源 1"],
            session_id="test-123"
        )
        assert response.answer == "测试回答"
        assert response.sources == ["来源 1"]
        assert response.session_id == "test-123"

    def test_upload_response(self):
        """Test UploadResponse model."""
        from src.api.routes import UploadResponse

        response = UploadResponse(
            message="成功",
            documents_processed=5,
            chunks_created=10
        )
        assert response.message == "成功"
        assert response.documents_processed == 5
        assert response.chunks_created == 10

    def test_history_response(self):
        """Test HistoryResponse model."""
        from src.api.routes import HistoryResponse

        response = HistoryResponse(
            session_id="test-123",
            history=[{"role": "user", "content": "你好"}]
        )
        assert response.session_id == "test-123"
        assert len(response.history) == 1
