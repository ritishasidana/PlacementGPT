# backend/test_step3.py
# Run with: python test_step3.py
# Tests the full chunking + embedding + storage pipeline

import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from dotenv import load_dotenv
load_dotenv()

from utils.chunker import chunk_all_pages
from services.embedding_service import embed_and_store, embed_query


def test_chunker():
    """Tests chunking logic with a sample page."""
    print("\n" + "="*60)
    print("TEST 1: Chunker")
    print("="*60)

    # Simulate two pages from a PDF
    sample_pages = [
        {
            "page_number": 1,
            "text": """
            A database management system (DBMS) is software that interacts with
            end users, applications, and the database itself to capture and analyze
            data. A DBMS allows a user to interact with the database.

            ACID Properties are a set of properties that guarantee database
            transactions are processed reliably. ACID stands for Atomicity,
            Consistency, Isolation, and Durability.

            Atomicity means that each transaction is treated as a single unit,
            which either succeeds completely or fails completely. If any of the
            statements constituting a transaction fails to complete, the entire
            transaction fails and the database is left unchanged.

            Consistency ensures that a transaction can only bring the database
            from one valid state to another, maintaining database invariants.
            Any data written to the database must be valid according to all
            defined rules, including constraints, cascades, and triggers.

            Isolation ensures that concurrent execution of transactions leaves
            the database in the same state that would have been obtained if the
            transactions were executed sequentially.

            Durability guarantees that once a transaction has been committed,
            it will remain committed even in the case of a system failure.
            This is usually achieved through transaction logs.
            """ * 2,    # Repeat to generate multiple chunks
            "metadata": {
                "filename": "test_dbms.pdf",
                "doc_type": "dbms",
                "page_number": 1,
                "source": "test_dbms.pdf (Page 1)"
            }
        }
    ]

    chunks = chunk_all_pages(sample_pages)

    print(f"  Pages input  : {len(sample_pages)}")
    print(f"  Chunks output: {len(chunks)}")
    print(f"\n  Sample chunk:")
    print(f"  {'─'*50}")
    print(f"  Text    : {chunks[0]['text'][:200]}...")
    print(f"  Metadata: {chunks[0]['metadata']}")

    assert len(chunks) > 0, "Chunker produced no chunks!"
    print(f"\n  ✅ Chunker test passed")
    return chunks


async def test_embed_and_store():
    """Tests full embedding + storage pipeline."""
    print("\n" + "="*60)
    print("TEST 2: Embed and Store")
    print("="*60)

    sample_pages = [
        {
            "page_number": 1,
            "text": (
                "Deadlock in operating systems occurs when two or more processes "
                "are waiting for each other to release resources, and none of them "
                "ever does. The four necessary conditions for deadlock are: "
                "Mutual Exclusion, Hold and Wait, No Preemption, and Circular Wait. "
                "Deadlock detection algorithms include the Resource Allocation Graph "
                "and the Banker's Algorithm for deadlock avoidance."
            ),
            "metadata": {
                "filename": "test_os_notes.pdf",
                "doc_type": "os",
                "page_number": 1,
                "source": "test_os_notes.pdf (Page 1)"
            }
        }
    ]

    print("  Embedding and storing sample chunks...")
    chunks_stored = await embed_and_store(sample_pages)

    print(f"  Chunks stored: {chunks_stored}")
    assert chunks_stored > 0, "No chunks were stored!"
    print(f"  ✅ Storage test passed")


async def test_similarity_search():
    """Tests that stored embeddings can be retrieved by semantic search."""
    print("\n" + "="*60)
    print("TEST 3: Similarity Search")
    print("="*60)

    from database.chroma_client import get_or_create_collection

    query = "What are the conditions for deadlock?"
    print(f"  Query: '{query}'")

    query_vector = embed_query(query)
    collection   = get_or_create_collection()
    total        = collection.count()

    print(f"  Total chunks in ChromaDB: {total}")

    if total == 0:
        print("  ⚠️  No chunks stored yet. Run test 2 first.")
        return

    results = collection.query(
        query_embeddings=[query_vector],
        n_results=min(2, total),
        include=["documents", "metadatas", "distances"]
    )

    print(f"\n  Top results:")
    for i, (doc, meta, dist) in enumerate(zip(
        results["documents"][0],
        results["metadatas"][0],
        results["distances"][0]
    )):
        similarity = round(1 - (dist / 2), 4)
        print(f"\n  #{i+1} Similarity: {similarity:.2%}")
        print(f"      Source   : {meta.get('source')}")
        print(f"      Preview  : {doc[:120]}...")

    print(f"\n  ✅ Similarity search test passed")


async def main():
    print("\n🔬 PlacementGPT — Step 3 Tests")

    # Test 1: Chunker (no API needed)
    test_chunker()

    # Tests 2 & 3: Need Gemini API key
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key or api_key == "your_gemini_api_key_here":
        print("\n⚠️  Skipping embedding tests — add GOOGLE_API_KEY to .env")
        return

    await test_embed_and_store()
    await test_similarity_search()

    print("\n" + "="*60)
    print("✅ All Step 3 tests passed!")
    print("="*60)
    print("\nNext: Run the inspector to see what's in ChromaDB:")
    print("  python utils/chroma_inspector.py")


if __name__ == "__main__":
    asyncio.run(main())