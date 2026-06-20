# backend/routers/query.py
# FULL IMPLEMENTATION

import logging
from fastapi import APIRouter, HTTPException

from models.schemas import QueryRequest, QueryResponse, Citation
from services.retrieval_service import (
    search_chunks,
    get_available_companies,
    get_available_doc_types
)
from services.llm_service import generate_answer

logger = logging.getLogger(__name__)
router = APIRouter()

print("QUERY ROUTER FILE LOADED")
# ── POST /query ────────────────────────────────────────────────────────────────
@router.post("/query", response_model=QueryResponse)
async def query_documents(request: QueryRequest):

    print("\n========== QUERY REQUEST ==========")
    print("Question:", request.question)
    print("Doc Types:", request.doc_types)
    print("Company:", request.company)
    print("===================================\n")

    try:
        print("STEP 1: Calling search_chunks()")

        chunks = search_chunks(
            query=request.question,
            top_k=request.top_k,
            doc_types=request.doc_types,
            company=request.company
        )

        print("STEP 2: search_chunks SUCCESS")
        print("Chunks retrieved:", len(chunks))

    except Exception:
        print("\nSEARCH_CHUNKS FAILED\n")
        import traceback
        traceback.print_exc()
        raise

    try:
        print("STEP 3: Calling generate_answer()")

        answer = await generate_answer(
            question=request.question,
            context_chunks=chunks
        )

        print("STEP 4: generate_answer SUCCESS")
        print("Answer length:", len(answer))

    except Exception:
        print("\nGENERATE_ANSWER FAILED\n")
        import traceback
        traceback.print_exc()
        raise

    try:
        print("STEP 5: Building citations")

        citations = []

        for chunk in chunks:
            meta = chunk.get("metadata", {})

            citations.append(
                Citation(
                    source=meta.get("source", "Unknown"),
                    doc_type=meta.get("doc_type", "unknown"),
                    similarity=round(
                        chunk.get("similarity_score", 0.0),
                        4
                    ),
                    chunk_text=chunk.get("text", "")
                )
            )

        print("STEP 6: Citations SUCCESS")
        print("Citations:", len(citations))

    except Exception:
        print("\nCITATION BUILD FAILED\n")
        import traceback
        traceback.print_exc()
        raise

    print("\n========== SUCCESS ==========\n")

    return QueryResponse(
        answer=answer,
        citations=citations,
        chunks_retrieved=len(chunks)
    )

# ── GET /filters ───────────────────────────────────────────────────────────────
@router.get("/filters")
async def get_filters():
    """
    Returns available filter options based on what's been uploaded.

    React frontend calls this to populate the filter dropdowns.
    Instead of hardcoding filter options, we derive them from
    what's actually in ChromaDB — dynamic and always accurate.
    """
    try:
        companies = get_available_companies()
        doc_types = get_available_doc_types()

        return {
            "companies": companies,
            "doc_types": doc_types
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
