"""API Service Module - FastAPI REST endpoints."""

from .routes import app, QueryRequest, QueryResponse

__all__ = [
    "app",
    "QueryRequest",
    "QueryResponse"
]
