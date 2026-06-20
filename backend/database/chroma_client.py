# backend/database/chroma_client.py

import chromadb
from chromadb.config import Settings
import os

# ── Persistent ChromaDB Client ────────────────────────────────────────────────
# Using PersistentClient means data survives server restarts.
# It stores everything in the chroma_store/ folder on disk.

_client = None  # Singleton pattern — one client instance for the whole app

def get_chroma_client():
    """
    Returns a singleton ChromaDB client.
    
    Why singleton? ChromaDB holds file locks on its storage.
    Creating multiple clients would cause conflicts.
    """
    global _client
    if _client is None:
        # Path where ChromaDB will store its data
        persist_dir = os.path.join(os.path.dirname(__file__), "..", "chroma_store")
        _client = chromadb.PersistentClient(path=persist_dir)
    return _client


def get_or_create_collection(collection_name: str = "placement_docs"):
    """
    Gets an existing ChromaDB collection or creates it if it doesn't exist.
    
    A 'collection' in ChromaDB = a table in SQL.
    All our embedded PDF chunks go into one collection: 'placement_docs'
    
    We use cosine similarity (best for text embeddings) instead of 
    the default L2 (Euclidean) distance.
    """
    client = get_chroma_client()
    collection = client.get_or_create_collection(
        name=collection_name,
        metadata={"hnsw:space": "cosine"}  # cosine similarity for text
    )
    return collection