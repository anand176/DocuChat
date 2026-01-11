"""LLM setup using Google Generative AI SDK directly (without LangChain)"""
import os
import google.generativeai as genai
from dotenv import load_dotenv
from src.vector_store import query_vectors

load_dotenv()

def get_gemini_model():
    """Initialize and return Gemini model"""
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError("GOOGLE_API_KEY environment variable is not set")
    
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-2.5-flash')
    return model

def format_chat_history(history: list) -> str:
    """Format chat history as a string for the prompt"""
    if not history:
        return "None"
    
    formatted = []
    for human_msg, ai_msg in history:
        formatted.append(f"Human: {human_msg}")
        formatted.append(f"Assistant: {ai_msg}")
    
    return "\n".join(formatted)

def generate_response(question: str, chat_history: list = None) -> dict:
    """Generate response using Gemini with RAG
    
    Args:
        question: User's question
        chat_history: List of tuples [(human_msg, ai_msg), ...]
        
    Returns:
        Dictionary with 'answer' and 'sources' keys
    """
    # Get relevant context from Pinecone
    context_docs = query_vectors(question, top_k=3)
    
    # Combine context
    context_text = "\n\n".join([doc["text"] for doc in context_docs])
    sources = [doc["metadata"].get("source", "Unknown") for doc in context_docs]
    
    # Format chat history
    history_text = format_chat_history(chat_history) if chat_history else "None"
    
    # Create prompt
    prompt = f"""You are a helpful cricket knowledge assistant. Use the following pieces of context to answer the user's question about cricket.
If you don't know the answer based on the provided context, just say that you don't know, don't try to make up an answer.
Be concise and informative in your responses.

Context:
{context_text}

Chat History:
{history_text}

Human: {question}
Assistant:"""
    
    # Get Gemini model
    model = get_gemini_model()
    
    # Generate response
    response = model.generate_content(prompt)
    
    # Extract answer
    answer = response.text if response.text else "I'm sorry, I couldn't generate a response."
    
    return {
        "answer": answer,
        "sources": list(set(sources))
    }

def get_conversational_chain(chat_history=None):
    """Compatibility function - returns a callable object
    
    Args:
        chat_history: List of tuples [(human_msg, ai_msg), ...]
        
    Returns:
        Callable object with invoke method
    """
    class ChainWrapper:
        def __init__(self, history):
            self.history = history or []
        
        def invoke(self, inputs: dict):
            question = inputs.get("question", "")
            result = generate_response(question, self.history)
            return {
                "answer": result["answer"],
                "sources": result["sources"],
                "source_documents": [
                    type('obj', (object,), {'metadata': {"source": src}}) 
                    for src in result["sources"]
                ]
            }
    
    return ChainWrapper(chat_history)
