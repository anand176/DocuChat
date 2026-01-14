from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import os
from dotenv import load_dotenv
from typing import List, Optional
import uvicorn
from pydantic import BaseModel

from src.vector_store import get_vector_store, init_pinecone, add_texts, delete_vectors_by_source, list_all_sources
from src.llm_chain import get_conversational_chain
from src.data_loader import process_uploaded_file

# Load environment variables
load_dotenv()

app = FastAPI(title="DocuChat API", version="1.0.0")

# CORS middleware for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],  # React dev servers
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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

@app.post("/add_document")
async def add_document(file: UploadFile = File(...)):
    """Upload and add a document to the knowledge base
    
    Supports: PDF, DOCX, TXT files
    """
    global _pinecone_initialized
    
    if not _pinecone_initialized:
        try:
            init_pinecone()
            _pinecone_initialized = True
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Vector store not initialized: {str(e)}")
    
    # Check file type
    filename = file.filename
    file_ext = filename.lower().split('.')[-1] if '.' in filename else ''
    
    if file_ext not in ['pdf', 'docx', 'doc', 'txt', 'text']:
        raise HTTPException(
            status_code=400, 
            detail=f"Unsupported file type: {file_ext}. Supported: pdf, docx, txt"
        )
    
    try:
        # Read file content
        file_content = await file.read()
        
        # Process file and extract text
        documents = process_uploaded_file(file_content, filename, file_ext)
        
        # Extract texts and metadatas
        texts = [doc["text"] for doc in documents]
        metadatas = [doc["metadata"] for doc in documents]
        
        # Add to vector store
        add_texts(texts, metadatas)
        
        return JSONResponse({
            "status": "success",
            "message": f"Successfully added {len(texts)} chunks from {filename}",
            "filename": filename,
            "chunks_added": len(texts)
        })
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")

@app.delete("/delete_document/{source}")
async def delete_document(source: str):
    """Delete all vectors from a specific source (file)
    
    Args:
        source: Source name (filename) to delete
    """
    global _pinecone_initialized
    
    if not _pinecone_initialized:
        try:
            init_pinecone()
            _pinecone_initialized = True
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Vector store not initialized: {str(e)}")
    
    try:
        deleted_count = delete_vectors_by_source(source)
        
        return JSONResponse({
            "status": "success",
            "message": f"Deleted {deleted_count} vectors from {source}",
            "source": source,
            "deleted_count": deleted_count
        })
    
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error deleting document: {str(e)}")

@app.get("/list_documents")
async def list_documents():
    """List all documents (sources) in the knowledge base"""
    global _pinecone_initialized
    
    if not _pinecone_initialized:
        try:
            init_pinecone()
            _pinecone_initialized = True
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Vector store not initialized: {str(e)}")
    
    try:
        sources = list_all_sources()
        
        return JSONResponse({
            "status": "success",
            "documents": sources,
            "total": len(sources)
        })
    
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error listing documents: {str(e)}")

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "docuchat-api"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
