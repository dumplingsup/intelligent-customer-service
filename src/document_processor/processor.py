"""Document processing - Load, parse, chunk and embed documents."""

import os
from typing import List, Optional
from pathlib import Path

from langchain_community.document_loaders import (
    PyPDFLoader,
    Docx2txtLoader,
    TextLoader
)
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_core.documents import Document


def load_documents(file_paths: List[str]) -> List[Document]:
    """
    Load and parse multiple format documents.

    Args:
        file_paths: List of file paths to load

    Returns:
        List of Document objects
    """
    documents = []
    for path in file_paths:
        if not os.path.exists(path):
            print(f"Warning: File not found: {path}")
            continue

        if path.endswith('.pdf'):
            loader = PyPDFLoader(path)
        elif path.endswith('.docx'):
            loader = Docx2txtLoader(path)
        elif path.endswith('.txt'):
            loader = TextLoader(path, encoding='utf-8')
        else:
            print(f"Warning: Unsupported file format: {path}")
            continue

        try:
            docs = loader.load()
            documents.extend(docs)
            print(f"Loaded {len(docs)} documents from {path}")
        except Exception as e:
            print(f"Error loading {path}: {e}")

    return documents


def split_documents(
    documents: List[Document],
    chunk_size: int = 500,
    chunk_overlap: int = 50
) -> List[Document]:
    """
    Split documents into chunks using recursive character splitting.

    Args:
        documents: List of documents to split
        chunk_size: Maximum characters per chunk
        chunk_overlap: Number of overlapping characters between chunks

    Returns:
        List of split Document objects
    """
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n\n", "\n", "。", "!", "?", " ", ""]
    )
    return text_splitter.split_documents(documents)


def create_embeddings(
    model: str = "text-embedding-3-small",
    dimensions: int = 1536
) -> OpenAIEmbeddings:
    """
    Create OpenAI embeddings instance.

    Args:
        model: Embedding model name
        dimensions: Number of dimensions for embeddings

    Returns:
        OpenAIEmbeddings instance
    """
    return OpenAIEmbeddings(
        model=model,
        dimensions=dimensions
    )


def process_documents(
    file_paths: List[str],
    chunk_size: int = 500,
    chunk_overlap: int = 50
) -> List[Document]:
    """
    Complete document processing pipeline: load -> split.

    Args:
        file_paths: List of file paths to process
        chunk_size: Maximum characters per chunk
        chunk_overlap: Number of overlapping characters between chunks

    Returns:
        List of processed Document objects
    """
    print(f"Loading documents from {len(file_paths)} files...")
    documents = load_documents(file_paths)

    if not documents:
        print("No documents loaded!")
        return []

    print(f"Splitting {len(documents)} documents into chunks...")
    split_docs = split_documents(documents, chunk_size, chunk_overlap)

    print(f"Created {len(split_docs)} document chunks")
    return split_docs


def load_documents_from_directory(
    directory: str,
    extensions: Optional[List[str]] = None
) -> List[Document]:
    """
    Load all supported documents from a directory.

    Args:
        directory: Path to directory containing documents
        extensions: List of file extensions to load (default: ['.pdf', '.docx', '.txt'])

    Returns:
        List of Document objects
    """
    if extensions is None:
        extensions = ['.pdf', '.docx', '.txt']

    file_paths = []
    for ext in extensions:
        file_paths.extend(Path(directory).glob(f"*{ext}"))
        file_paths.extend(Path(directory).glob(f"*{ext.upper()}"))

    return load_documents([str(f) for f in file_paths])
