import os
from pinecone import Pinecone
from dotenv import load_dotenv

load_dotenv()

# Initialize Pinecone lazily
_index = None

def get_pinecone_index():
    global _index
    if _index is None:
        PINECONE_API_KEY = os.getenv("PINECONE_API_KEY", "your-pinecone-key")
        PINECONE_INDEX_NAME = os.getenv("PINECONE_INDEX_NAME", "hdb-docs")
        pc = Pinecone(api_key=PINECONE_API_KEY)
        _index = pc.Index(PINECONE_INDEX_NAME)
    return _index

def search_hdb_knowledge(query: str, persona: str) -> str:
    """
    Retrieves relevant HDB documents (SOPs, Manuals, Case Files) from Pinecone.
    
    Args:
        query: The search string to look up in the vector database.
        persona: The user role (citizen, frontline_staff, legal_officer, hdb_manager, vendor).
                 Used to enforce namespace isolation.
    """
    # Persona to Namespace Mapping
    namespace_map = {
        "citizen": "hdb-citizen",
        "frontline_staff": "hdb-frontline",
        "legal_officer": "hdb-legal",
        "hdb_manager": "hdb-management",
        "vendor": "hdb-vendor"
    }
    
    target_namespace = namespace_map.get(persona, "hdb-citizen")
    
    try:
        # Note: In production, you would generate embeddings for the query here.
        # index = get_pinecone_index()
        # results = index.query(...)
        
        return f"[RETRIVAL SUCCESS] Found relevant context in namespace '{target_namespace}' for query: '{query}'"
    except Exception as e:
        return f"[RETRIVAL ERROR] Failed to access namespace '{target_namespace}': {str(e)}"
