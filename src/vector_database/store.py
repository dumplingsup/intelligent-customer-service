"""Chroma DB vector store - Initialize, store, and retrieve vectors."""

import os
from typing import List, Optional, Tuple

from langchain_chroma import Chroma
from chromadb.config import Settings
from langchain_core.documents import Document
from langchain_core.embeddings import Embeddings

from src.document_processor import create_embeddings


def init_vectorstore(
    documents: List[Document],
    persist_dir: str = "./chroma_db",
    collection_name: str = "customer_service_kb",
    embeddings: Optional[Embeddings] = None
) -> Chroma:
    """
    Initialize vector database with documents.

    Args:
        documents: List of documents to embed and store
        persist_dir: Directory for persistent storage
        collection_name: Name of the collection
        embeddings: Embeddings instance (creates default if None)

    Returns:
        Chroma vector store instance
    """
    if embeddings is None:
        embeddings = create_embeddings()

    # Create vector store from documents
    vectorstore = Chroma.from_documents(
        documents=documents,
        embedding=embeddings,
        persist_directory=persist_dir,
        collection_name=collection_name,
        collection_metadata={"hnsw:space": "cosine"}
    )

    print(f"Created vector store with {len(documents)} documents")
    return vectorstore


def load_vectorstore(
    persist_dir: str = "./chroma_db",
    collection_name: str = "customer_service_kb",
    embeddings: Optional[Embeddings] = None
) -> Chroma:
    """
    Load existing vector database.

    Args:
        persist_dir: Directory for persistent storage
        collection_name: Name of the collection
        embeddings: Embeddings instance (creates default if None)

    Returns:
        Chroma vector store instance
    """
    if embeddings is None:
        embeddings = create_embeddings()

    vectorstore = Chroma(
        persist_directory=persist_dir,
        collection_name=collection_name,
        embedding_function=embeddings
    )

    print(f"Loaded vector store from {persist_dir}")
    return vectorstore


def get_or_create_vectorstore(
    persist_dir: str = "./chroma_db",
    collection_name: str = "customer_service_kb",
    embeddings: Optional[Embeddings] = None
) -> Chroma:
    """
    Get existing vector store or create new one.

    Args:
        persist_dir: Directory for persistent storage
        collection_name: Name of the collection
        embeddings: Embeddings instance (creates default if None)

    Returns:
        Chroma vector store instance
    """
    if embeddings is None:
        embeddings = create_embeddings()

    # Check if vector store exists
    if os.path.exists(persist_dir):
        try:
            return load_vectorstore(persist_dir, collection_name, embeddings)
        except Exception:
            print("Could not load existing vector store, creating new one...")

    # Create empty vector store
    vectorstore = Chroma(
        persist_directory=persist_dir,
        collection_name=collection_name,
        embedding_function=embeddings,
        collection_metadata={"hnsw:space": "cosine"}
    )

    print(f"Created new empty vector store at {persist_dir}")
    return vectorstore


def retrieve_context(
    vectorstore: Chroma,
    query: str,
    k: int = 3,
    score_threshold: float = 0.7
) -> Tuple[List[str], List[Tuple[Document, float]]]:
    """
    Retrieve k most relevant document chunks with score filtering.

    Args:
        vectorstore: Chroma vector store
        query: Search query
        k: Number of results to retrieve
        score_threshold: Minimum similarity score threshold

    Returns:
        Tuple of (list of page contents, list of (document, score) tuples)
    """
    results = vectorstore.similarity_search_with_score(query, k=k)

    # Filter by score threshold
    filtered_results = [
        (doc, score) for doc, score in results
        if score >= score_threshold
    ]

    page_contents = [doc.page_content for doc, _ in filtered_results]

    return page_contents, filtered_results


def add_documents(
    vectorstore: Chroma,
    documents: List[Document]
) -> None:
    """
    Add new documents to existing vector store.

    Args:
        vectorstore: Chroma vector store
        documents: List of documents to add
    """
    vectorstore.add_documents(documents)
    print(f"Added {len(documents)} documents to vector store")


def clear_vectorstore(
    persist_dir: str = "./chroma_db",
    collection_name: str = "customer_service_kb"
) -> None:
    """
    Clear all documents from vector store.

    Args:
        persist_dir: Directory for persistent storage
        collection_name: Name of the collection
    """
    import shutil

    if os.path.exists(persist_dir):
        shutil.rmtree(persist_dir)
        print(f"Cleared vector store at {persist_dir}")
