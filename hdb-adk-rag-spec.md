# Architecture Prompt: Building a Platform-Agnostic, Multi-Tenant Agentic RAG System via Google ADK, FastAPI, and Pinecone

You are an expert software engineer specializing in Google Cloud Agent Development Kit (ADK), FastAPI, and distributed Vector Databases (Pinecone). Your task is to implement a platform-agnostic, model-agnostic, multi-tenant Agentic RAG backend system based on the specifications detailed below.

---

## 1. System Requirements & Context
* **Domain:** Singapore HDB (Housing & Development Board) document handling (PDF Emails, SOPs, User Manuals, and Case Files).
* **Multi-Tenancy / Access Control:** The system serves **5 distinct personas**: `citizen`, `frontline_staff`, `legal_officer`, `hdb_manager`, and `vendor`.
* **Security Policy:** Strict data isolation using **Pinecone Namespaces** to ensure a persona can never access documents belonging to another persona.
* **Architecture Pattern:** Platform-agnostic core logic wrapped in a **FastAPI** web framework mimicking the **OpenAI Chat Completions specification** (`/v1/chat/completions`). This allows frontends like **Open WebUI** or **LibreChat** to consume the system seamlessly.
* **Model Agnosticism:** Core execution layer written to handle environment configurations (such as standard proxy interfaces or environment toggles) to cleanly switch LLM backends (e.g., Gemini, Claude, OpenAI).

---

## 2. File and Project Layout
Generate and implement the complete codebase matching this clean file structure:

```text
my-agnostic-agent/
├── agent/
│   ├── __init__.py
│   ├── brain.py       # Core Google ADK agent configuration & runner layer
│   └── tools.py       # Vector DB retrieval orchestration (Pinecone integration)
├── main.py            # FastAPI service layer matching OpenAI chat completions specification
├── requirements.txt   # Pin all critical dependencies
└── Dockerfile         # Containerized production runtime definition