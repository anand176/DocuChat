"""Vector store management using Pinecone directly (without LangChain)"""
import os
from typing import Optional, List, Dict
from pinecone import Pinecone, ServerlessSpec
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv

load_dotenv()

# Initialize Pinecone client
pc: Optional[Pinecone] = None
index = None
embeddings_model: Optional[SentenceTransformer] = None

def get_embeddings_model():
    """Get or create the embeddings model"""
    global embeddings_model
    if embeddings_model is None:
        embeddings_model = SentenceTransformer('all-MiniLM-L6-v2')
    return embeddings_model

def init_pinecone():
    """Initialize Pinecone connection and create index if it doesn't exist"""
    global pc, index
    
    api_key = os.getenv("PINECONE_API_KEY")
    environment = os.getenv("PINECONE_ENVIRONMENT", "gcp-starter")
    index_name = os.getenv("PINECONE_INDEX_NAME", "cricket-chatbot")
    
    if not api_key:
        raise ValueError("PINECONE_API_KEY environment variable is not set")
    
    # Initialize Pinecone client
    pc = Pinecone(api_key=api_key)
    
    # Check if index exists, create if it doesn't
    existing_indexes = [idx.name for idx in pc.list_indexes()]
    
    if index_name not in existing_indexes:
        print(f"Creating new Pinecone index: {index_name}")
        try:
            # Try to determine cloud and region from environment
            if environment.startswith("gcp"):
                cloud = "gcp"
                region = "us-east1"  # Default region for GCP starter
            elif environment.startswith("aws"):
                cloud = "aws"
                region = "us-east-1"
            else:
                cloud = "gcp"
                region = "us-east1"
            
            pc.create_index(
                name=index_name,
                dimension=384,  # Dimension for all-MiniLM-L6-v2 model
                metric="cosine",
                spec=ServerlessSpec(
                    cloud=cloud,
                    region=region
                )
            )
            print(f"Index {index_name} created successfully")
        except Exception as e:
            print(f"Error creating index: {e}")
            print(f"Index {index_name} might already exist or there was an issue with the configuration")
    else:
        print(f"Using existing Pinecone index: {index_name}")
        # Check if dimension matches
        index_info = pc.describe_index(index_name)
        if index_info.dimension != 384:
            raise ValueError(
                f"Index dimension mismatch! The existing index '{index_name}' has dimension {index_info.dimension}, "
                f"but the embedding model produces 384-dimensional vectors. "
                f"Please delete the index and recreate it, or use a different embedding model. "
                f"You can run 'python fix_index_dimension.py' to fix this."
            )
    
    # Get the index
    index = pc.Index(index_name)
    return index

def get_index():
    """Get the initialized Pinecone index"""
    global index
    if index is None:
        raise RuntimeError("Pinecone index not initialized. Call init_pinecone() first.")
    return index

def get_vector_store():
    """Get vector store components (for compatibility)"""
    return {
        "index": get_index(),
        "embeddings": get_embeddings_model()
    }

def query_vectors(query_text: str, top_k: int = 3) -> List[Dict]:
    """Query Pinecone for similar vectors
    
    Args:
        query_text: The text to search for
        top_k: Number of results to return
        
    Returns:
        List of dictionaries with 'text' and 'metadata' keys
    """
    index = get_index()
    embeddings_model = get_embeddings_model()
    
    # Generate embedding for query
    query_embedding = embeddings_model.encode(query_text).tolist()
    
    # Query Pinecone
    results = index.query(
        vector=query_embedding,
        top_k=top_k,
        include_metadata=True
    )
    
    # Format results
    documents = []
    if results.matches:
        for match in results.matches:
            documents.append({
                "text": match.metadata.get("text", ""),
                "metadata": match.metadata,
                "score": match.score
            })
    
    return documents

def add_texts(texts: List[str], metadatas: Optional[List[Dict]] = None):
    """Add texts to Pinecone vector store
    
    Args:
        texts: List of text strings to add
        metadatas: Optional list of metadata dictionaries
    """
    import uuid
    index = get_index()
    embeddings_model = get_embeddings_model()
    
    if metadatas is None:
        metadatas = [{}] * len(texts)
    
    # Generate embeddings
    embeddings = embeddings_model.encode(texts).tolist()
    
    # Prepare vectors for Pinecone
    vectors = []
    for text, embedding, metadata in zip(texts, embeddings, metadatas):
        vector_id = str(uuid.uuid4())  # Generate unique ID
        vectors.append({
            "id": vector_id,
            "values": embedding,
            "metadata": {**metadata, "text": text}
        })
    
    # Upsert to Pinecone in batches (Pinecone recommends batches of 100)
    batch_size = 100
    for i in range(0, len(vectors), batch_size):
        batch = vectors[i:i + batch_size]
        index.upsert(vectors=batch)
    
    print(f"Added {len(texts)} documents to vector store")

def add_documents_to_vector_store(texts: List[str], metadatas: Optional[List[Dict]] = None):
    """Alias for add_texts (for compatibility)"""
    add_texts(texts, metadatas)
