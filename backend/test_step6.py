# backend/test_step6.py
# Run: python test_step6.py

import asyncio, sys, os
sys.path.insert(0, os.path.dirname(__file__))
from dotenv import load_dotenv
load_dotenv()

from services.generator_service import (
    create_revision_notes,
    create_interview_questions,
    get_search_query
)

def test_topic_expansion():
    print("\n" + "="*60)
    print("TEST 1: Topic Query Expansion")
    print("="*60)

    cases = [
        ("DBMS",              "dbms"),
        ("Operating Systems", "os"),
        ("Deadlock",          None),       # Specific — no expansion
        ("Computer Networks", "cn"),
    ]

    for topic, doc_type in cases:
        query = get_search_query(topic, doc_type)
        expanded = len(query) > len(topic)
        print(f"  Topic='{topic}' | doc_type={doc_type}")
        print(f"  Query='{query[:70]}...' {'(expanded ✅)' if expanded else '(direct)'}")
        print()

    print("  ✅ Topic expansion test passed")


async def test_revision_notes():
    print("\n" + "="*60)
    print("TEST 2: Revision Notes Generation")
    print("="*60)

    from database.chroma_client import get_or_create_collection
    if get_or_create_collection().count() == 0:
        print("  ⚠️  No documents. Upload PDFs first.")
        return

    result = await create_revision_notes(
        topic="Deadlock",
        doc_type="os",
    )

    print(f"  Topic        : {result['topic']}")
    print(f"  Chunks used  : {result['chunks_used']}")
    print(f"  Theory chunks: {result['theory_chunks']}")
    print(f"  Interview    : {result['interview_chunks']}")
    print(f"  Content len  : {len(result['content'])} chars")
    print(f"\n  Preview:\n  {result['content'][:400]}...")
    print("\n  ✅ Revision notes test passed")


async def test_interview_questions():
    print("\n" + "="*60)
    print("TEST 3: Interview Question Generation")
    print("="*60)

    from database.chroma_client import get_or_create_collection
    if get_or_create_collection().count() == 0:
        print("  ⚠️  No documents. Upload PDFs first.")
        return

    result = await create_interview_questions(
        topic="DBMS",
        doc_type="dbms",
        num_questions=5,
    )

    print(f"  Topic         : {result['topic']}")
    print(f"  Num questions : {result['num_questions']}")
    print(f"  Chunks used   : {result['chunks_used']}")
    print(f"  Content len   : {len(result['content'])} chars")
    print(f"\n  Preview:\n  {result['content'][:500]}...")
    print("\n  ✅ Interview questions test passed")


async def main():
    print("\n🔬 PlacementGPT — Step 6 Tests")

    test_topic_expansion()   # No API needed

    if not os.getenv("GOOGLE_API_KEY") or \
       os.getenv("GOOGLE_API_KEY") == "your_gemini_api_key_here":
        print("\n⚠️  Skipping LLM tests — add GOOGLE_API_KEY to .env")
        return

    await test_revision_notes()
    await test_interview_questions()

    print("\n" + "="*60)
    print("✅ All Step 6 tests passed!")
    print("="*60)


if __name__ == "__main__":
    asyncio.run(main())