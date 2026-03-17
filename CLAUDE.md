# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Build & Development Commands

```bash
# Install dependencies
poetry install

# Run tests
poetry run pytest tests/ -v

# Run single test file
poetry run pytest tests/test_document_processor.py -v

# Run single test class
poetry run pytest tests/test_document_processor.py::TestLoadDocuments -v

# Start API server
poetry run python -m uvicorn src.api.routes:app --host 0.0.0.0 --port 8000 --reload

# Start frontend
poetry run streamlit run src/frontend/app.py

# Docker deployment
docker-compose up -d
docker-compose logs -f
docker-compose down
```

## Architecture Overview

**4-layer architecture:**

```
User Interface (Streamlit/FastAPI)
         ▼
LangChain Agent (LangGraph ReAct)
         ▼
RAG Retrieval (Chroma DB + OpenAI Embeddings)
         ▼
Data Storage (Chroma vectors, conversation history)
```

**Core modules (`src/`):**
- `document_processor/` - Load/split documents (PDF, Word, TXT) using LangChain splitters
- `vector_database/` - Chroma DB wrapper for storing and retrieving embeddings
- `rag_chain/` - RAG retrieval chain using LCEL pattern
- `agent_core/` - LangGraph ReAct agent with tools (order query, refund, customer info)
- `api/` - FastAPI REST endpoints
- `frontend/` - Streamlit UI

**Key patterns:**
- Uses **DeepSeek API** as LLM provider (configured via `DEEPSEEK_API_KEY`, `DEEPSEEK_BASE_URL`)
- **LangGraph ReAct agent** for tool calling and conversation management
- **Session-based memory** - conversation history stored per `session_id` in memory
- **HNSW index** with cosine similarity in Chroma DB

## Environment Configuration

Required variables in `.env`:
```bash
OPENAI_API_KEY=       # Also used for DeepSeek
DEEPSEEK_API_KEY=     # DeepSeek API key
DEEPSEEK_BASE_URL=https://api.deepseek.com
DEEPSEEK_MODEL=deepseek-chat
CHROMA_PERSIST_DIR=./chroma_db
```

## Testing Notes

- Tests use `tmp_path` fixture for temporary files
- Mock external API calls using `unittest.mock`
- Run `poetry run pytest` after code changes
