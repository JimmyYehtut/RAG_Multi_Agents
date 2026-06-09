from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import time
import uuid

from agent.brain import execute_agent_query

app = FastAPI(
    title="HDB Agentic RAG Platform",
    description="Multi-tenant HDB backend mimicking OpenAI Chat Completions API"
)

import json
from fastapi.responses import StreamingResponse

# OpenAI-compatible Data Models
class Message(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    model: str
    messages: List[Message]
    temperature: Optional[float] = 0.7
    user: Optional[str] = None  # Can be used to pass persona
    stream: Optional[bool] = False

@app.get("/")
def read_root():
    return {"message": "HDB Agentic RAG API is running. Use /v1 for chat completions."}

@app.get("/v1/models")
async def list_models():
    """
    OpenAI-compatible models endpoint.
    Exposes all 5 HDB personas as selectable models.
    """
    personas = ["citizen", "frontline_staff", "legal_officer", "hdb_manager", "vendor"]
    models = []
    for p in personas:
        models.append({
            "id": f"hdb-{p.replace('_', '-')}",
            "object": "model",
            "created": int(time.time()),
            "owned_by": "hdb"
        })
    
    return {
        "object": "list",
        "data": models
    }

@app.post("/v1/chat/completions")
async def chat_completions(request: ChatRequest, x_persona: Optional[str] = Header(None)):
    """
    OpenAI-compatible endpoint.
    Determines persona via model ID, 'X-Persona' header, or 'user' field in body.
    Supports both streaming and non-streaming modes.
    """
    # 1. Persona Resolution (Multi-tenancy logic)
    # Priority: Header > Model ID > Request Body 'user' field > Default
    persona = x_persona
    
    if not persona:
        # Check model ID (e.g., hdb-legal-officer -> legal_officer)
        model_id = request.model.lower()
        if model_id.startswith("hdb-"):
            potential_persona = model_id.replace("hdb-", "").replace("-", "_")
            # Special case for staff/frontline
            if potential_persona == "staff": potential_persona = "frontline_staff"
            
            allowed_personas = ["citizen", "frontline_staff", "legal_officer", "hdb_manager", "vendor"]
            if potential_persona in allowed_personas:
                persona = potential_persona
    
    persona = persona or request.user or "citizen"
    
    allowed_personas = ["citizen", "frontline_staff", "legal_officer", "hdb_manager", "vendor"]
    if persona not in allowed_personas:
        raise HTTPException(
            status_code=403, 
            detail=f"Invalid persona '{persona}'. Access denied."
        )

    # 2. Extract Last User Message
    user_messages = [m.content for m in request.messages if m.role == "user"]
    if not user_messages:
        raise HTTPException(status_code=400, detail="No user messages provided.")
    
    latest_input = user_messages[-1]

    # 3. Handle Streaming Response
    if request.stream:
        async def stream_generator():
            chat_id = f"chatcmpl-{uuid.uuid4()}"
            created_time = int(time.time())
            
            async for chunk in execute_agent_query(latest_input, persona):
                data = {
                    "id": chat_id,
                    "object": "chat.completion.chunk",
                    "created": created_time,
                    "model": request.model,
                    "choices": [
                        {
                            "index": 0,
                            "delta": {"content": chunk},
                            "finish_reason": None
                        }
                    ]
                }
                yield f"data: {json.dumps(data)}\n\n"
            
            # End of stream
            yield "data: [DONE]\n\n"

        return StreamingResponse(stream_generator(), media_type="text/event-stream")

    # 4. Handle Non-Streaming Response
    try:
        full_content = ""
        async for chunk in execute_agent_query(latest_input, persona):
            full_content += chunk
            
        return {
            "id": f"chatcmpl-{uuid.uuid4()}",
            "object": "chat.completion",
            "created": int(time.time()),
            "model": request.model,
            "choices": [
                {
                    "index": 0,
                    "message": {
                        "role": "assistant",
                        "content": full_content
                    },
                    "finish_reason": "stop"
                }
            ],
            "usage": {
                "prompt_tokens": len(latest_input) // 4,
                "completion_tokens": len(full_content) // 4,
                "total_tokens": (len(latest_input) + len(full_content)) // 4
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Agent execution failed: {str(e)}")

@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "hdb-agentic-rag"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
