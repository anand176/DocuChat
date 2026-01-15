"""Helper utility functions for the cricket chatbot"""
from typing import List, Dict, Any

def format_chat_history(history: List[List[str]]) -> List[tuple]:
    formatted = []
    for human_msg, ai_msg in history:
        formatted.append(("human", human_msg))
        formatted.append(("ai", ai_msg))
    return formatted

def extract_sources(documents: List[Any]) -> List[str]:
    """Extract source metadata from documents"""
    sources = []
    for doc in documents:
        if hasattr(doc, 'metadata') and 'source' in doc.metadata:
            sources.append(doc.metadata['source'])
    return list(set(sources))

def validate_environment():
    """Validate that required environment variables are set"""
    import os
    required_vars = ["PINECONE_API_KEY", "GOOGLE_API_KEY"]
    missing = [var for var in required_vars if not os.getenv(var)]
    if missing:
        raise ValueError(f"Missing required environment variables: {', '.join(missing)}")
    return True
