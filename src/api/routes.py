"""FastAPI routes for customer service API."""

import os
import uuid
from typing import List, Optional, Dict, Any
from pathlib import Path

from fastapi import FastAPI, UploadFile, File, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from src.vector_database import (
    get_or_create_vectorstore,
    init_vectorstore,
    add_documents,
    retrieve_context
)
from src.document_processor import process_documents, create_embeddings
from src.agent_core import CustomerServiceAgent, create_tools

# Pydantic models
class QueryRequest(BaseModel):
    """Query request model."""
    query: str
    session_id: Optional[str] = None


class QueryResponse(BaseModel):
    """Query response model."""
    answer: str
    sources: Optional[List[str]] = None
    session_id: Optional[str] = None


class UploadResponse(BaseModel):
    """File upload response model."""
    message: str
    documents_processed: int
    chunks_created: int


class HistoryResponse(BaseModel):
    """Conversation history response model."""
    session_id: str
    history: List[Dict[str, str]]


# Global instances
_vectorstore = None
_agent = None
_conversation_histories: Dict[str, List[Dict[str, str]]] = {}


def get_vectorstore():
    """Get or create vector store instance."""
    global _vectorstore
    if _vectorstore is None:
        persist_dir = os.getenv("CHROMA_PERSIST_DIR", "./chroma_db")
        _vectorstore = get_or_create_vectorstore(persist_dir=persist_dir)
    return _vectorstore


def get_agent():
    """Get or create agent instance."""
    global _agent
    if _agent is None:
        _agent = CustomerServiceAgent(
            model=os.getenv("LLM_MODEL", "gpt-4"),
            temperature=float(os.getenv("LLM_TEMPERATURE", "0.7"))
        )
    return _agent


# Create FastAPI app
app = FastAPI(
    title="Intelligent Customer Service API",
    description="Enterprise-level intelligent customer service system based on LangChain + RAG",
    version="0.1.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event():
    """Initialize services on startup."""
    get_vectorstore()
    get_agent()
    print("Customer Service API started successfully!")


@app.post("/api/query", response_model=QueryResponse)
async def query_endpoint(request: QueryRequest):
    """
    Process user query and return answer with sources.

    Args:
        request: Query request with question and optional session ID

    Returns:
        Query response with answer and sources
    """
    try:
        # Generate session ID if not provided
        session_id = request.session_id or str(uuid.uuid4())

        # Get vector store and retrieve context
        vectorstore = get_vectorstore()
        retriever = vectorstore.as_retriever(
            search_type="similarity_score_threshold",
            search_kwargs={"score_threshold": 0.7, "k": 3}
        )

        # Retrieve context
        context_docs = retriever.invoke(request.query)
        context = [doc.page_content for doc in context_docs]

        # Get agent and process query
        agent = get_agent()
        result = agent.query(
            question=request.query,
            session_id=session_id,
            context=context if context else None
        )

        return QueryResponse(
            answer=result["answer"],
            sources=context if context else None,
            session_id=session_id
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Query processing error: {str(e)}")


@app.post("/api/upload", response_model=UploadResponse)
async def upload_documents(
    files: List[UploadFile] = File(...),
    chunk_size: int = 500,
    chunk_overlap: int = 50
):
    """
    Upload and process knowledge base documents.

    Args:
        files: List of files to upload
        chunk_size: Text chunk size
        chunk_overlap: Chunk overlap size

    Returns:
        Upload response with processing stats
    """
    try:
        # Create temp directory for uploads
        temp_dir = Path("./temp_uploads")
        temp_dir.mkdir(exist_ok=True)

        # Save uploaded files
        file_paths = []
        for file in files:
            file_path = temp_dir / file.filename
            with open(file_path, "wb") as f:
                content = await file.read()
                f.write(content)
            file_paths.append(str(file_path))

        # Process documents
        documents = process_documents(
            file_paths,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap
        )

        if not documents:
            raise HTTPException(status_code=400, detail="No documents were processed")

        # Add to vector store
        vectorstore = get_vectorstore()
        add_documents(vectorstore, documents)

        # Clean up temp files
        for file_path in file_paths:
            try:
                os.remove(file_path)
            except Exception:
                pass

        return UploadResponse(
            message=f"Successfully processed {len(file_paths)} files",
            documents_processed=len(file_paths),
            chunks_created=len(documents)
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload error: {str(e)}")


@app.get("/api/history/{session_id}", response_model=HistoryResponse)
async def get_conversation_history(session_id: str):
    """
    Get conversation history for a session.

    Args:
        session_id: Session identifier

    Returns:
        Conversation history
    """
    agent = get_agent()
    history = agent.get_session_history(session_id)
    return HistoryResponse(session_id=session_id, history=history)


@app.delete("/api/history/{session_id}")
async def clear_conversation_history(session_id: str):
    """
    Clear conversation history for a session.

    Args:
        session_id: Session identifier
    """
    agent = get_agent()
    agent.clear_session(session_id)
    return {"message": f"Conversation history for session {session_id} cleared"}


@app.get("/api/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "vectorstore": "initialized" if _vectorstore else "not_initialized",
        "agent": "initialized" if _agent else "not_initialized"
    }


@app.get("/")
async def root():
    """Root endpoint with API info."""
    return {
        "name": "Intelligent Customer Service API",
        "version": "0.1.0",
        "endpoints": [
            "POST /api/query - Process user query",
            "POST /api/upload - Upload knowledge documents",
            "GET /api/history/{session_id} - Get conversation history",
            "DELETE /api/history/{session_id} - Clear conversation history",
            "GET /api/health - Health check"
        ]
    }


def main():
    """Run the API server."""
    import uvicorn

    host = os.getenv("APP_HOST", "0.0.0.0")
    port = int(os.getenv("APP_PORT", 8000))

    uvicorn.run(
        "src.api.routes:app",
        host=host,
        port=port,
        reload=True
    )


if __name__ == "__main__":
    main()
