import os
import uuid
import asyncio
from google.adk import Agent, Runner
from google.adk.sessions.in_memory_session_service import InMemorySessionService
from google.adk.utils.content_utils import extract_text_from_content
from google.genai import types
from .tools import search_hdb_knowledge
from dotenv import load_dotenv
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_message

load_dotenv()

# Configuration
MODEL_NAME = os.getenv("LLM_MODEL_NAME", "gemini-3.1-flash-lite")
# Global session service to persist state if needed
session_service = InMemorySessionService()

def create_hdb_agent(persona: str) -> Agent:
    """
    Configures a Google ADK Agent tailored to a specific HDB persona.
    """
    base_instruction = (
        "You are an expert HDB Assistant. Your goal is to provide accurate information "
        "based ONLY on the documents retrieved from the knowledge base. "
        f"You are currently assisting a user with the persona: {persona}. "
        "Strictly adhere to the following:\n"
        "1. Always use 'search_hdb_knowledge' to find answers.\n"
        f"2. You MUST pass the persona '{persona}' as the second argument to the search tool.\n"
        "3. If the retrieved content does not contain the answer, politely inform the user.\n"
        "4. Maintain a professional tone consistent with Singapore Government service standards."
    )

    return Agent(
        name=f"HDB_Agent_{persona}",
        model=MODEL_NAME,
        instruction=base_instruction,
        tools=[search_hdb_knowledge]
    )

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=4, max=10),
    retry=retry_if_exception_message(match=".*RESOURCE_EXHAUSTED.*"),
    reraise=True
)
async def execute_agent_query(user_input: str, persona: str):
    """
    Entry point to run the agentic workflow using the Runner class (ADK 2.2.0 style).
    Includes retry logic for Gemini Rate Limits.
    Yields chunks of text as they are received.
    """
    agent = create_hdb_agent(persona)
    
    # Initialize Runner
    runner = Runner(
        agent=agent, 
        app_name=f"HDB_App_{persona}",
        session_service=session_service,
        auto_create_session=True
    )
    
    # Prepare input content
    new_message = types.Content(role='user', parts=[types.Part(text=user_input)])
    
    try:
        # Run the agent and collect events
        async for event in runner.run_async(
            user_id="default_user",
            session_id=str(uuid.uuid4()),
            new_message=new_message
        ):
            print(f"DEBUG: Received event: {type(event)}")
            # Extract text from the event if available
            text_chunk = extract_text_from_content(event.content)
            if text_chunk:
                print(f"DEBUG: Yielding text chunk: {text_chunk[:50]}...")
                yield text_chunk
            
            # Check for function calls to log activity
            if event.content and event.content.parts:
                for part in event.content.parts:
                    if part.function_call:
                        print(f"DEBUG: Agent calling tool: {part.function_call.name}")
                
    except Exception as e:
        # If we still fail after retries, or for other errors, raise/return
        if "RESOURCE_EXHAUSTED" in str(e):
             raise e 
        yield f"Error during agent execution: {str(e)}"
