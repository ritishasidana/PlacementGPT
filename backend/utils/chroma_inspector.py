# backend/utils/chroma_inspector.py
# Run this directly: python utils/chroma_inspector.py
# Useful for debugging what's actually stored in ChromaDB

import sys
import os

# Add backend/ to path so imports work
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from database.chroma_client import get_or_create_collection
from dotenv import load_dotenv

load_dotenv()


def inspect_collection():
    """Prints a summary of everything stored in ChromaDB."""
    collection = get_or_create_collection()

    # Get total count
    total = collection.count()
    print(f"\n{'='*60}")
    print(f"ChromaDB Collection: 'placement_docs'")
    print(f"Total chunks stored: {total}")
    print(f"{'='*60}")

    if total == 0:
        print("Collection is empty. Upload a PDF first.")
        return

    # Fetch all metadata (no embeddings — they're huge)
    results = collection.get(include=["metadatas", "documents"])

    # Group by filename
    doc_groups = {}
    for meta in results["metadatas"]:
        fname = meta.get("filename", "unknown")
        if fname not in doc_groups:
            doc_groups[fname] = {
                "doc_type": meta.get("doc_type"),
                "company":  meta.get("company"),
                "chunks":   0,
                "pages":    set()
            }
        doc_groups[fname]["chunks"] += 1
        doc_groups[fname]["pages"].add(meta.get("page_number", 0))

    # Print per-document summary
    print(f"\n{'Documents':}")
    print(f"{'-'*60}")
    for fname, info in doc_groups.items():
        print(f"  📄 {fname}")
        print(f"     Type    : {info['doc_type']}")
        print(f"     Company : {info['company'] or 'N/A'}")
        print(f"     Pages   : {len(info['pages'])}")
        print(f"     Chunks  : {info['chunks']}")
        print()

    # Print sample chunk
    print(f"{'Sample Chunk (first stored)':}")
    print(f"{'-'*60}")
    if results["documents"]:
        sample_text = results["documents"][0][:300]
        sample_meta = results["metadatas"][0]
        print(f"  Text    : {sample_text}...")
        print(f"  Source  : {sample_meta.get('source')}")
        print(f"  DocType : {sample_meta.get('doc_type')}")
    print(f"{'='*60}\n")


def test_similarity_search(query: str):
    """
    Tests similarity search directly on ChromaDB (without LLM).
    Useful to verify embeddings are working correctly.
    """
    from services.embedding_service import embed_query

    print(f"\nTesting similarity search for: '{query}'")
    print(f"{'-'*60}")

    query_vector = embed_query(query)
    collection   = get_or_create_collection()

    results = collection.query(
        query_embeddings=[query_vector],
        n_results=3,
        include=["documents", "metadatas", "distances"]
    )

    for i, (doc, meta, dist) in enumerate(zip(
        results["documents"][0],
        results["metadatas"][0],
        results["distances"][0]
    )):
        # Convert distance to similarity score
        # ChromaDB cosine distance: 0 = identical, 2 = opposite
        # Similarity = 1 - (distance / 2) → range [0, 1]
        similarity = round(1 - (dist / 2), 4)

        print(f"\n  Result #{i+1}")
        print(f"  Similarity : {similarity:.2%}")
        print(f"  Source     : {meta.get('source')}")
        print(f"  Preview    : {doc[:150]}...")


if __name__ == "__main__":
    inspect_collection()

    # Uncomment to test search (requires at least one PDF uploaded):
    # test_similarity_search("What is a deadlock?")
    # test_similarity_search("Amazon interview DBMS questions")