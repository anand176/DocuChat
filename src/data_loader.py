"""Utility functions for loading and processing cricket data"""
from typing import List

def split_text_into_chunks(text: str, chunk_size: int = 1000, chunk_overlap: int = 200) -> List[str]:
    """Split text into chunks with overlap"""
    chunks = []
    start = 0
    text_length = len(text)
    
    while start < text_length:
        end = start + chunk_size
        chunk = text[start:end]
        chunks.append(chunk.strip())
        start = end - chunk_overlap  # Overlap with next chunk
    
    return chunks

def load_cricket_data_from_text(text: str, metadata: dict = None) -> List[dict]:
    """Load cricket data from plain text and split into chunks
    
    Returns:
        List of dictionaries with 'text' and 'metadata' keys
    """
    chunks = split_text_into_chunks(text, chunk_size=1000, chunk_overlap=200)
    
    documents = []
    for chunk in chunks:
        if chunk:  # Only add non-empty chunks
            documents.append({
                "text": chunk,
                "metadata": metadata.copy() if metadata else {}
            })
    
    return documents

def load_cricket_data_from_file(file_path: str) -> List[dict]:
    """Load cricket data from a text file"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    metadata = {"source": file_path}
    return load_cricket_data_from_text(content, metadata)

def get_sample_cricket_data() -> str:
    """Return sample cricket knowledge for testing"""
    return """
    Cricket is a bat-and-ball game played between two teams of eleven players on a field at the centre of which is a 22-yard (20-metre) pitch with a wicket at each end.
    
    The game of cricket has its origins in England and is now played worldwide, particularly in countries that were part of the British Empire.
    
    There are three main formats of cricket:
    1. Test cricket - played over 5 days with unlimited overs
    2. One Day International (ODI) - played over 50 overs per side
    3. Twenty20 (T20) - played over 20 overs per side
    
    Key cricket terms:
    - Batting: The act of hitting the ball with the bat
    - Bowling: Delivering the ball to the batsman
    - Wicket: The stumps and bails, or when a batsman is dismissed
    - Run: The basic unit of scoring, achieved by running between the wickets
    - Over: A set of 6 deliveries by a bowler
    
    Famous cricket tournaments:
    - ICC Cricket World Cup (ODI format)
    - ICC T20 World Cup
    - The Ashes (Test series between England and Australia)
    - Indian Premier League (IPL) - T20 franchise tournament
    
    Cricket has been an Olympic sport once, in 1900, but is being considered for reintroduction.
    
    The highest individual score in Test cricket is 400 not out by Brian Lara of West Indies.
    The highest team score in Test cricket is 952/6 declared by Sri Lanka against India.
    
    Cricket is governed internationally by the International Cricket Council (ICC).
    """
