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
    index_name = os.getenv("PINECONE_INDEX_NAME", "docuchat")
    
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

def delete_vectors_by_source(source: str) -> int:
    """Delete all vectors with a specific source
    
    Args:
        source: Source name (e.g., filename) to delete
        
    Returns:
        Number of vectors deleted
    """
    index = get_index()
    
    # Query to find all vectors with this source
    # Note: We need to query to find the IDs first, then delete
    # Pinecone doesn't support delete by metadata filter directly in all plans
    
    # Use query to find vectors (we'll query with a dummy vector and filter)
    # Since we can't easily query all, we'll use fetch to get all and filter
    # Actually, better approach: use delete by metadata filter if available
    
    # Query first to find all vectors with this source, then delete by IDs
    # This is more reliable than delete by filter (which may not be supported in all plans)
    embeddings_model = get_embeddings_model()
    dummy_vector = embeddings_model.encode("cricket").tolist()
    
    # Query with metadata filter to find matching vectors
    results = index.query(
        vector=dummy_vector,
        top_k=10000,  # Large number to get all matching vectors
        filter={"source": source},
        include_metadata=True
    )
    
    if results.matches:
        vector_ids = [match.id for match in results.matches]
        # Delete in batches (Pinecone recommends batches of 1000)
        batch_size = 1000
        deleted = 0
        for i in range(0, len(vector_ids), batch_size):
            batch_ids = vector_ids[i:i + batch_size]
            index.delete(ids=batch_ids)
            deleted += len(batch_ids)
        return deleted
    return 0

def list_all_sources() -> List[Dict]:
    """List all unique sources (files) in the vector store
    
    Returns:
        List of dictionaries with source info and count
    """
    index = get_index()
    
    # Use fetch to get all vectors (limited to first batch)
    # Actually, better: use stats to get total count, then query samples
    # For simplicity, we'll query with a dummy vector and get unique sources
    embeddings_model = get_embeddings_model()
    dummy_vector = embeddings_model.encode("cricket").tolist()
    
    # Query to get a sample of vectors
    results = index.query(
        vector=dummy_vector,
        top_k=1000,  # Get a large sample
        include_metadata=True
    )
    
    # Extract unique sources
    sources = {}
    if results.matches:
        for match in results.matches:
            source = match.metadata.get("source", "Unknown")
            file_type = match.metadata.get("file_type", "text")
            file_name = match.metadata.get("file_name", source)
            
            if source not in sources:
                sources[source] = {
                    "source": source,
                    "file_name": file_name,
                    "file_type": file_type,
                    "count": 0
                }
            sources[source]["count"] += 1
    
    return list(sources.values())

def list_vectors_by_source(source: str, limit: int = 100) -> List[Dict]:
    """List vectors from a specific source
    
    Args:
        source: Source name to filter by
        limit: Maximum number of vectors to return
        
    Returns:
        List of vector dictionaries with metadata
    """
    index = get_index()
    embeddings_model = get_embeddings_model()
    
    # Query with metadata filter
    dummy_vector = embeddings_model.encode("cricket").tolist()
    
    results = index.query(
        vector=dummy_vector,
        top_k=limit,
        filter={"source": source},
        include_metadata=True
    )
    
    vectors = []
    if results.matches:
        for match in results.matches:
            vectors.append({
                "id": match.id,
                "text": match.metadata.get("text", "")[:200],  # Preview
                "metadata": match.metadata,
                "score": match.score
            })
    
    return vectors
