"""Tests for document processor module."""

import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock

from src.document_processor.processor import (
    load_documents,
    split_documents,
    create_embeddings,
    process_documents
)


class TestLoadDocuments:
    """Test document loading functionality."""

    def test_load_txt_document(self, tmp_path):
        """Test loading a TXT document."""
        # Create a test file
        test_file = tmp_path / "test.txt"
        test_file.write_text("Hello, this is a test document.")

        documents = load_documents([str(test_file)])

        assert len(documents) == 1
        assert "Hello, this is a test document." in documents[0].page_content

    def test_load_nonexistent_file(self):
        """Test loading a nonexistent file."""
        documents = load_documents(["/nonexistent/file.txt"])
        assert len(documents) == 0

    def test_load_unsupported_format(self, tmp_path):
        """Test loading an unsupported file format."""
        test_file = tmp_path / "test.exe"
        test_file.write_text("binary content")

        documents = load_documents([str(test_file)])
        assert len(documents) == 0


class TestSplitDocuments:
    """Test document splitting functionality."""

    def test_split_short_document(self):
        """Test splitting a short document (no split needed)."""
        from langchain_core.documents import Document

        doc = Document(page_content="Short content.")
        result = split_documents([doc], chunk_size=100, chunk_overlap=10)

        assert len(result) == 1
        assert result[0].page_content == "Short content."

    def test_split_long_document(self):
        """Test splitting a long document."""
        from langchain_core.documents import Document

        # Create a long document (500+ characters)
        content = "This is a sentence. " * 50
        doc = Document(page_content=content)
        result = split_documents([doc], chunk_size=100, chunk_overlap=20)

        assert len(result) > 1
        # Check overlap exists
        assert len(result) >= 2

    def test_split_preserves_metadata(self):
        """Test that splitting preserves document metadata."""
        from langchain_core.documents import Document

        doc = Document(
            page_content="Test content " * 20,
            metadata={"source": "test.pdf", "page": 1}
        )
        result = split_documents([doc], chunk_size=50, chunk_overlap=10)

        for split_doc in result:
            assert split_doc.metadata.get("source") == "test.pdf"


class TestCreateEmbeddings:
    """Test embeddings creation."""

    def test_create_embeddings_default(self):
        """Test creating embeddings with default model."""
        embeddings = create_embeddings()

        assert embeddings is not None
        assert embeddings.model == "text-embedding-3-small"
        assert embeddings.dimensions == 1536

    def test_create_embeddings_custom(self):
        """Test creating embeddings with custom parameters."""
        embeddings = create_embeddings(
            model="text-embedding-3-large",
            dimensions=3072
        )

        assert embeddings.model == "text-embedding-3-large"


class TestProcessDocuments:
    """Test full document processing pipeline."""

    def test_process_documents_empty_list(self):
        """Test processing an empty file list."""
        result = process_documents([])
        assert result == []

    def test_process_documents_single_file(self, tmp_path):
        """Test processing a single file."""
        test_file = tmp_path / "test.txt"
        test_file.write_text("Test content for processing.")

        result = process_documents([str(test_file)])

        assert len(result) >= 1


class TestLoadDocumentsFromDirectory:
    """Test directory loading functionality."""

    def test_load_from_empty_directory(self):
        """Test loading from an empty directory."""
        from src.document_processor.processor import load_documents_from_directory

        result = load_documents_from_directory("/nonexistent/directory")
        assert result == []

    def test_load_from_directory(self, tmp_path):
        """Test loading documents from a directory."""
        from src.document_processor.processor import load_documents_from_directory

        # Create test files
        (tmp_path / "doc1.txt").write_text("Content 1")
        (tmp_path / "doc2.txt").write_text("Content 2")

        result = load_documents_from_directory(str(tmp_path))

        assert len(result) == 2
