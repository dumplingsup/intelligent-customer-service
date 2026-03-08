"""Tests for vector database module."""

import pytest
import os
import shutil
from pathlib import Path
from unittest.mock import patch, MagicMock

from src.vector_database.store import (
    init_vectorstore,
    load_vectorstore,
    retrieve_context,
    get_or_create_vectorstore,
    add_documents,
    clear_vectorstore
)


@pytest.fixture
def test_db_dir(tmp_path):
    """Fixture for test database directory."""
    db_dir = tmp_path / "test_chroma_db"
    yield str(db_dir)
    # Cleanup
    if db_dir.exists():
        shutil.rmtree(db_dir)


@pytest.fixture
def sample_documents():
    """Fixture with sample documents."""
    from langchain_core.documents import Document

    return [
        Document(page_content="Product A costs $99 and includes free shipping.", metadata={"source": "products.pdf"}),
        Document(page_content="Product B costs $149 with premium features.", metadata={"source": "products.pdf"}),
        Document(page_content="Return policy allows returns within 30 days.", metadata={"source": "policy.txt"}),
    ]


class TestVectorStoreInit:
    """Test vector store initialization."""

    @pytest.mark.skip(reason="Requires OpenAI API key")
    def test_init_vectorstore(self, test_db_dir, sample_documents):
        """Test initializing vector store with documents."""
        vectorstore = init_vectorstore(
            documents=sample_documents,
            persist_dir=test_db_dir
        )

        assert vectorstore is not None
        assert os.path.exists(test_db_dir)

    @pytest.mark.skip(reason="Requires OpenAI API key")
    def test_load_vectorstore_empty(self, test_db_dir):
        """Test loading an empty vector store."""
        # Create empty vector store first
        init_vectorstore([], persist_dir=test_db_dir)

        # Load it
        vectorstore = load_vectorstore(persist_dir=test_db_dir)
        assert vectorstore is not None


class TestRetrieveContext:
    """Test context retrieval."""

    @pytest.mark.skip(reason="Requires OpenAI API key")
    def test_retrieve_context(self, test_db_dir, sample_documents):
        """Test retrieving relevant context."""
        # Initialize with documents
        vectorstore = init_vectorstore(
            documents=sample_documents,
            persist_dir=test_db_dir
        )

        # Query
        results, filtered = retrieve_context(
            vectorstore,
            "What is the price of Product A?",
            k=3,
            score_threshold=0.5
        )

        assert len(results) > 0
        assert "Product A" in results[0] or any("Product A" in str(f) for f in filtered)

    @pytest.mark.skip(reason="Requires OpenAI API key")
    def test_retrieve_context_no_matches(self, test_db_dir, sample_documents):
        """Test retrieval with no matching content."""
        vectorstore = init_vectorstore(
            documents=sample_documents,
            persist_dir=test_db_dir
        )

        # Query unrelated content
        results, filtered = retrieve_context(
            vectorstore,
            "Quantum physics explained",
            k=3,
            score_threshold=0.9  # High threshold
        )

        # May return empty due to high threshold
        assert isinstance(results, list)


class TestAddDocuments:
    """Test adding documents to existing store."""

    @pytest.mark.skip(reason="Requires OpenAI API key")
    def test_add_documents(self, test_db_dir, sample_documents):
        """Test adding documents to vector store."""
        from langchain_core.documents import Document

        # Initialize with some documents
        vectorstore = init_vectorstore(
            documents=sample_documents[:1],
            persist_dir=test_db_dir
        )

        # Add more documents
        new_docs = [
            Document(page_content="New product information.", metadata={"source": "new.pdf"})
        ]
        add_documents(vectorstore, new_docs)

        # Verify store still works
        assert os.path.exists(test_db_dir)


class TestClearVectorStore:
    """Test clearing vector store."""

    def test_clear_vectorstore(self, test_db_dir):
        """Test clearing vector store directory."""
        # Create directory
        os.makedirs(test_db_dir, exist_ok=True)
        test_file = Path(test_db_dir) / "test.txt"
        test_file.write_text("test")

        assert os.path.exists(test_db_dir)

        # Clear
        clear_vectorstore(persist_dir=test_db_dir)

        assert not os.path.exists(test_db_dir)


class TestGetOrCreateVectorStore:
    """Test get or create functionality."""

    @pytest.mark.skip(reason="Requires OpenAI API key")
    def test_get_or_create_new(self, test_db_dir):
        """Test getting or creating a new vector store."""
        vectorstore = get_or_create_vectorstore(persist_dir=test_db_dir)
        assert vectorstore is not None

    @pytest.mark.skip(reason="Requires OpenAI API key")
    def test_get_or_create_existing(self, test_db_dir):
        """Test getting an existing vector store."""
        # Create first
        get_or_create_vectorstore(persist_dir=test_db_dir)

        # Get again
        vectorstore = get_or_create_vectorstore(persist_dir=test_db_dir)
        assert vectorstore is not None
