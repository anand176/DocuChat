"""Script to populate Pinecone vector store with cricket data"""
import os
import uuid
from dotenv import load_dotenv
from src.vector_store import init_pinecone, add_texts
from src.data_loader import get_sample_cricket_data, load_cricket_data_from_text

load_dotenv()

def populate_vector_store():
    """Populate the vector store with cricket knowledge"""
    print("Initializing Pinecone...")
    init_pinecone()
    
    print("Loading cricket data...")
    cricket_data = get_sample_cricket_data()
    
    print("Splitting and embedding documents...")
    # Split the data into chunks and create documents
    documents = load_cricket_data_from_text(cricket_data, metadata={"source": "cricket_knowledge_base"})
    
    # Extract texts and metadatas
    texts = [doc["text"] for doc in documents]
    metadatas = [doc["metadata"] for doc in documents]
    
    print(f"Adding {len(texts)} document chunks to vector store...")
    
    # Add documents to vector store
    add_texts(texts, metadatas)
    
    print("✅ Successfully populated vector store with cricket data!")
    print(f"   Total chunks added: {len(texts)}")

if __name__ == "__main__":
    try:
        populate_vector_store()
    except Exception as e:
        print(f" Error: {str(e)}")
        import traceback
        traceback.print_exc()
