# HDB Agentic RAG Lab - Project Status

## 🚀 Overview
This project is a platform-agnostic, multi-tenant Agentic RAG system designed for HDB document handling. It leverages **Google Cloud ADK** for orchestration, **FastAPI** for an OpenAI-compatible API layer, and **Pinecone** for persona-based data isolation.

## 🛠 Current Implementation State
- **API Layer:** FastAPI server running on `localhost:8000` mimicking `/v1/chat/completions`.
- **Orchestration:** Google ADK `Runner` (v2.2.0) with `gemini-1.5-flash-latest`.
- **Streaming:** Full support for SSE streaming chunks.
- **Mock RAG:** The system currently uses a mock retrieval tool in `agent/tools.py`. It simulates namespace-based search results to demonstrate routing without requiring pre-indexed vectors.

## 👥 Persona & Multi-Tenancy Mapping
The system automatically routes requests based on the selected Model ID or `X-Persona` header:

| Model ID | Persona | Pinecone Namespace |
| :--- | :--- | :--- |
| `hdb-citizen` | `citizen` | `hdb-citizen` |
| `hdb-frontline-staff` | `frontline_staff` | `hdb-frontline` |
| `hdb-legal-officer` | `legal_officer` | `hdb-legal` |
| `hdb-manager` | `hdb_manager` | `hdb-management` |
| `hdb-vendor` | `vendor` | `hdb-vendor` |

## ⚙️ Configuration (.env)
- `GOOGLE_API_KEY`: Authentication for Gemini.
- `LLM_MODEL_NAME`: Currently `gemini-1.5-flash-latest`.
- `PINECONE_API_KEY`: Required for future vector search integration.

## 📝 Roadmap / Next Steps
1. **Document Ingestion:** Create a pipeline to chunk and embed PDFs.
2. **Vector Upload:** Script to populate namespaces in Pinecone.
3. **Real Retrieval:** Enable the `index.query()` logic in `agent/tools.py`.
