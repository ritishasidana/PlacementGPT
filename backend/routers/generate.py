# backend/routers/generate.py  (complete replacement)

import logging
from fastapi import APIRouter, HTTPException
from models.schemas import GenerateRequest, GenerateResponse
from services.generator_service import (
    create_revision_notes,
    create_interview_questions
)

logger = logging.getLogger(__name__)
router = APIRouter()


# ── POST /generate ─────────────────────────────────────────────────────────────
@router.post("/generate", response_model=GenerateResponse)
async def generate_content(request: GenerateRequest):
    """
    Generates revision notes or interview questions.

    Uses multi-source RAG — retrieves from both subject notes
    and interview experiences simultaneously.
    """
    logger.info(
        f"Generate | type='{request.generate_type}' | "
        f"topic='{request.topic}' | company={request.company}"
    )

    try:
        if request.generate_type == "revision_notes":
            result = await create_revision_notes(
                topic=    request.topic,
                doc_type= request.doc_type,
                company=  request.company,
            )

        elif request.generate_type == "interview_questions":
            result = await create_interview_questions(
                topic=         request.topic,
                doc_type=      request.doc_type,
                company=       request.company,
                num_questions= request.num_questions,
            )

        else:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid generate_type: '{request.generate_type}'. "
                       f"Must be 'revision_notes' or 'interview_questions'."
            )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Generation failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Content generation failed: {str(e)}"
        )

    logger.info(
        f"Generation complete | "
        f"chunks_used={result['chunks_used']} | "
        f"content_length={len(result['content'])}"
    )

    return GenerateResponse(
        content=       result["content"],
        topic=         result["topic"],
        generate_type= request.generate_type,
    )


# ── GET /generate/topics ───────────────────────────────────────────────────────
@router.get("/generate/topics")
async def get_suggested_topics():
    """
    Returns suggested topics for generation based on uploaded documents.
    Frontend uses this to populate the topic selector dynamically.
    """
    from services.retrieval_service import get_available_doc_types
    from utils.prompt_templates import TOPIC_QUERY_MAP

    doc_types = get_available_doc_types()

    # Map doc_types to suggested topics
    TOPIC_SUGGESTIONS = {
        "dbms": [
            "DBMS", "SQL", "Normalization", "Indexing",
            "Transactions & ACID", "Deadlock in DBMS",
            "ER Diagrams", "Joins"
        ],
        "os": [
            "Operating Systems", "Process Scheduling",
            "Deadlock", "Memory Management",
            "Virtual Memory", "File Systems",
            "Synchronization", "Threads vs Processes"
        ],
        "cn": [
            "Computer Networks", "OSI Model",
            "TCP vs UDP", "HTTP & HTTPS",
            "DNS", "Routing Algorithms",
            "Congestion Control", "Socket Programming"
        ],
        "oop": [
            "OOP Concepts", "Inheritance & Polymorphism",
            "Design Patterns", "SOLID Principles",
            "Abstract Classes vs Interfaces",
            "Encapsulation & Abstraction"
        ],
        "interview_experience": [],  # Interview experiences fuel questions, not topics
    }

    # Only return topics for doc_types that are actually uploaded
    topics = []
    for dt in doc_types:
        topics.extend(TOPIC_SUGGESTIONS.get(dt, []))

    # Deduplicate while preserving order
    seen    = set()
    unique  = []
    for t in topics:
        if t not in seen:
            seen.add(t)
            unique.append(t)

    return {
        "topics":     unique,
        "doc_types":  doc_types
    }