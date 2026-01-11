from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import os
from dotenv import load_dotenv
from typing import List, Optional
import uvicorn
from pydantic import BaseModel

from src.vector_store import get_vector_store, init_pinecone
from src.llm_chain import get_conversational_chain

# Load environment variables
load_dotenv()

app = FastAPI(title="Cricket Chatbot", version="1.0.0")

# Mount static files and templates
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Lazy initialization flag
_pinecone_initialized = False

@app.on_event("startup")
async def startup_event():
    """Initialize Pinecone on application startup"""
    global _pinecone_initialized
    try:
        init_pinecone()
        _pinecone_initialized = True
        print("✅ Pinecone initialized successfully")
    except Exception as e:
        print(f"⚠️  Warning: Pinecone initialization failed: {e}")
        print("   The app will still start, but vector search may not work.")
        print("   Make sure to set PINECONE_API_KEY in your .env file")

# Request/Response models
class ChatMessage(BaseModel):
    message: str
    history: Optional[List[List[str]]] = []

class ChatResponse(BaseModel):
    response: str
    sources: Optional[List[str]] = []

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Serve the main chat interface"""
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(message: ChatMessage):
    """Handle chat messages and return AI responses"""
    global _pinecone_initialized
    
    if not _pinecone_initialized:
        try:
            init_pinecone()
            _pinecone_initialized = True
        except Exception as e:
            return ChatResponse(
                response=f"Vector store not initialized. Please check your Pinecone configuration: {str(e)}",
                sources=[]
            )
    
    try:
        # Get the conversational chain with chat history
        # Convert history format: [[human, ai], ...] to [(human, ai), ...]
        history_tuples = [(h, a) for h, a in message.history] if message.history else []
        chain = get_conversational_chain(chat_history=history_tuples)
        
        # Invoke the chain with the user's question
        # The chain will handle retrieval, context, and chat history automatically
        result = chain.invoke({"question": message.message})
        
        # Extract sources if available
        sources = result.get("sources", [])
        if "source_documents" in result and result["source_documents"]:
            # Extract sources from source_documents (compatibility format)
            sources = [
                doc.metadata.get("source", "Unknown") 
                for doc in result["source_documents"]
                if hasattr(doc, 'metadata') and doc.metadata
            ]
        
        return ChatResponse(
            response=result.get("answer", "I'm sorry, I couldn't generate a response."),
            sources=list(set(sources))
        )
    except Exception as e:
        import traceback
        traceback.print_exc()
        return ChatResponse(
            response=f"An error occurred: {str(e)}. Please check your API keys and configuration.",
            sources=[]
        )

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "cricket-chatbot"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
