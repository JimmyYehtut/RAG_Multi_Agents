# HDB Agentic RAG Platform

A platform-agnostic, multi-tenant Agentic Retrieval-Augmented Generation (RAG) backend system tailored for Singapore HDB (Housing & Development Board) document handling. 

This project utilizes **FastAPI** to mimic the OpenAI Chat Completions API (`/v1/chat/completions`), allowing seamless integration with frontends like Open WebUI or LibreChat. Under the hood, it leverages the **Google Cloud Agent Development Kit (ADK)** for agentic workflow orchestration and **Pinecone** for strict, persona-isolated vector document retrieval.

## Key Features

- **OpenAI API Compatibility:** Exposes a `/v1/chat/completions` endpoint making it plug-and-play for OpenAI-compatible client libraries and frontends.
- **Strict Multi-Tenancy (Access Control):** Enforces data security by ensuring users only access documents they have permissions for. Supports 5 distinct personas:
  - `citizen`
  - `frontline_staff`
  - `legal_officer`
  - `hdb_manager`
  - `vendor`
- **Data Isolation:** Uses Pinecone Namespaces to physically separate embeddings by persona (e.g., `hdb-citizen`, `hdb-legal`).
- **Agentic Workflow:** Utilizes Google ADK to dynamically invoke vector database retrieval as a tool (`search_hdb_knowledge`) when answering queries.
- **Resiliency:** Built-in retry mechanisms for API limits (e.g., Gemini `RESOURCE_EXHAUSTED` limits).

## Prerequisites

- Python 3.9+
- Pinecone Account & API Key
- Google Gemini API Key (or appropriately configured LLM credentials for Google ADK)

## Installation

1. Clone the repository and navigate to the project directory:
```bash
cd my-hdb-agent
```

2. Install the required dependencies:
```bash
pip install -r requirements.txt
```
*(Note: Ensure you have `fastapi`, `uvicorn`, `google-adk`, `pinecone-client`, `python-dotenv`, `tenacity`, and `pydantic` installed)*

## Configuration

Create a `.env` file in the root directory and add the following configuration variables:

```env
PINECONE_API_KEY=your-pinecone-api-key
PINECONE_INDEX_NAME=hdb-docs
LLM_MODEL_NAME=gemini-2.0-flash
GEMINI_API_KEY=your-gemini-api-key # Or appropriate Google ADK auth setup
```

## Running the Server

Start the FastAPI server using Uvicorn:

```bash
python main.py
# Alternatively: uvicorn main:app --host 0.0.0.0 --port 8000
```

The server will be available at `http://localhost:8000`. You can check the health of the service at `http://localhost:8000/health`.

## API Usage

The main endpoint is `POST /v1/chat/completions`. You can specify the user's persona via the `X-Persona` HTTP header, or the `user` field in the JSON body. If neither is provided, it defaults to `citizen`.

### Example Request (cURL)

```bash
curl -X POST "http://localhost:8000/v1/chat/completions" \
     -H "Content-Type: application/json" \
     -H "X-Persona: frontline_staff" \
     -d '{
           "model": "gemini-2.0-flash",
           "messages": [
             {
               "role": "user",
               "content": "What is the standard operating procedure for escalating a delayed BTO handover?"
             }
           ],
           "temperature": 0.7
         }'
```

### Architecture
- **`main.py`**: The FastAPI application layer, handling HTTP requests, standardizing inputs/outputs to the OpenAI schema, and persona resolution.
- **`agent/brain.py`**: The core LLM execution layer powered by Google ADK. Responsible for the agent's behavior, instructions, and tool orchestration.
- **`agent/tools.py`**: Defines the tools the agent can use, primarily the Pinecone vector database integration (`search_hdb_knowledge`) for RAG.