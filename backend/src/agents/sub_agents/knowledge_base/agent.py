"""Placeholder for Knowledge Base agent"""
import google.genai.types as genai_types
from core.config import config
from google.adk.agents import Agent

def search_knowledge_base(query: str) -> str:
    """Searches the document knowledge base for relevant information."""
    return f"Knowledge Base placeholder: No relevant documentation found for '{query}' at this time."

knowledge_base_agent = Agent(
    name="knowledge_base_agent",
    model="gemini/gemini-2.5-flash",
    description="Searches for documentation and guides in the knowledge base.",
    instruction="Search for relevant technical documentation based on the user query.",
    tools=[search_knowledge_base],
)
