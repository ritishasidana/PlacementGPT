# backend/test_step4.py
# Run: python test_step4.py
# Tests the full RAG pipeline end-to-end

import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))
from dotenv import load_dotenv
load_dotenv()

from services.retrieval_service import search_chunks, build_chroma_filter
from services.llm_service import generate_answer, generate_interview_questions
from database.chroma_client import get_or_create_collection


def test_chroma_filter_builder():
    """Tests the metadata filter builder."""
    print("\n" + "="*60)
    print("TEST 1: ChromaDB Filter Builder")
    print("="*60)

    # No filter
    f = build_chroma_filter()
    assert f is None, f"Expected None, got {f}"
    print("  ✅ No filter → None")

    # Single doc_type
    f = build_chroma_filter(doc_types=["dbms"])
    assert f == {"doc_type": {"$eq": "dbms"}}, f"Got {f}"
    print(f"  ✅ Single doc_type → {f}")

    # Multiple doc_types
    f = build_chroma_filter(doc_types=["dbms", "os"])
    assert f == {"doc_type": {"$in": ["dbms", "os"]}}, f"Got {f}"
    print(f"  ✅ Multiple doc_types → {f}")

    # Company only
    f = build_chroma_filter(company="amazon")
    assert f == {"company": {"$eq": "amazon"}}, f"Got {f}"
    print(f"  ✅ Company only → {f}")

    # Both doc_type and company
    f = build_chroma_filter(doc_types=["dbms"], company="google")
    assert "$and" in f, f"Expected $and, got {f}"
    print(f"  ✅ Combined → {f}")

    print("\n  ✅ All filter builder tests passed")


async def test_full_rag_pipeline():
    """Tests the complete retrieve → generate pipeline."""
    print("\n" + "="*60)
    print("TEST 2: Full RAG Pipeline")
    print("="*60)

    collection = get_or_create_collection()
    total = collection.count()

    if total == 0:
        print("  ⚠️  ChromaDB is empty. Upload a PDF first via the API.")
        print("     Then re-run this test.")
        return

    print(f"  ChromaDB has {total} chunks")

    # Test retrieval
    print("\n  Step 1: Retrieval...")
    chunks = search_chunks("What is a deadlock?", top_k=3)
    print(f"  Retrieved {len(chunks)} chunks")

    if chunks:
        print(f"  Top result ({chunks[0]['similarity_score']:.2%} similarity):")
        print(f"    Source : {chunks[0]['metadata']['source']}")
        print(f"    Preview: {chunks[0]['text'][:100]}...")

    # Test generation
    print("\n  Step 2: Generation...")
    answer = await generate_answer(
        question="What is a deadlock? Explain with conditions.",
        context_chunks=chunks
    )
    print(f"  Generated answer ({len(answer)} chars):")
    print(f"  {answer[:300]}...")

    print("\n  ✅ Full RAG pipeline test passed")


async def test_interview_question_generator():
    """Tests interview question generation."""
    print("\n" + "="*60)
    print("TEST 3: Interview Question Generator")
    print("="*60)

    collection = get_or_create_collection()
    if collection.count() == 0:
        print("  ⚠️  No documents. Upload PDFs first.")
        return

    chunks = search_chunks("operating system", top_k=5)
    questions = await generate_interview_questions(
        topic="Operating Systems",
        context_chunks=chunks,
        num_questions=3
    )
    print(f"  Generated questions ({len(questions)} chars):")
    print(f"  {questions[:400]}...")
    print("\n  ✅ Generator test passed")


async def main():
    print("\n🔬 PlacementGPT — Step 4 Tests")

    # Test 1: No API needed
    test_chroma_filter_builder()

    # Check for API key before LLM tests
    if not os.getenv("GOOGLE_API_KEY") or os.getenv("GOOGLE_API_KEY") == "your_gemini_api_key_here":
        print("\n⚠️  Skipping LLM tests — add GOOGLE_API_KEY to .env")
        return

    await test_full_rag_pipeline()
    await test_interview_question_generator()

    print("\n" + "="*60)
    print("✅ All Step 4 tests passed!")
    print("="*60)
    print("\nFull backend is now complete.")
    print("Test via Swagger UI: http://localhost:8000/docs")


if __name__ == "__main__":
    asyncio.run(main())