# HDB Agentic RAG Lab - Session Memory

## Project Overview
- **Path:** `C:\Users\yehtu\Documents\Gemini_CLI\Agentic-RAG-Lab\my-hdb-agent`
- **Core Stack:** Google Cloud ADK (v2.2.0), FastAPI, Pinecone, Gemini 1.5 Flash.

## Configuration Details
- **Model:** `gemini-1.5-flash-latest` (Switched from 2.0 to avoid 429 errors).
- **Auth:** Uses `GOOGLE_API_KEY` (standard environment variable).
- **Service Port:** `8000` (Localhost).
- **Frontend Compatibility:** Configured for Open WebUI (mimics OpenAI `/v1/chat/completions`).

## Key Implementation Notes
- **Streaming:** SSE streaming implemented in `main.py` using `StreamingResponse`.
- **Personas:** 5 personas (`citizen`, `frontline_staff`, `legal_officer`, `hdb_manager`, `vendor`) mapped to Pinecone Namespaces.
- **Resiliency:** `tenacity` retry logic added to `execute_agent_query` to handle Gemini rate limits.
- **Routing:** Model IDs in Open WebUI (e.g., `hdb-legal-officer`) are automatically parsed to set the correct persona.

## Pending Tasks
- [ ] Implement actual PDF ingestion/embedding pipeline.
- [ ] Connect `agent/tools.py` to live Pinecone index (currently mocked).
