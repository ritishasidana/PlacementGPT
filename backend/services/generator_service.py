# backend/services/generator_service.py

"""
Generator Service — orchestrates the full generation pipeline.

WHY A SEPARATE SERVICE?
The generate router could call retrieval + LLM directly.
But generation has more complex orchestration than Q&A:
  - Multi-source retrieval (theory + interviews)
  - Topic expansion (e.g., "DBMS" → search multiple sub-topics)
  - Result post-processing (word count, section validation)

Keeping this in a service makes the router thin and
the logic independently testable.
"""

import logging
from services.retrieval_service import search_multi_source, search_chunks
from services.llm_service       import (
    generate_revision_notes,
    generate_interview_questions
)

logger = logging.getLogger(__name__)


# ── Topic expansion map ────────────────────────────────────────────────────────
# When a user asks for "DBMS" revision notes, we want to retrieve
# chunks about specific DBMS concepts, not just the word "DBMS".
# This map expands broad topics into targeted search queries.

TOPIC_QUERY_MAP = {
    "dbms": (
        "database transactions ACID normalization indexing SQL joins "
        "deadlock concurrency ER diagram relational model"
    ),
    "os": (
        "process thread scheduling deadlock memory management "
        "paging segmentation virtual memory file system synchronization"
    ),
    "cn": (
        "TCP IP OSI model HTTP DNS routing switching protocols "
        "network layers congestion control socket programming"
    ),
    "oop": (
        "classes objects inheritance polymorphism encapsulation "
        "abstraction design patterns SOLID principles"
    ),
}


def get_search_query(topic: str, doc_type: str | None) -> str:
    """
    Returns the best search query for a given topic.

    If the topic matches a known subject and a doc_type is provided,
    returns an expanded query. Otherwise uses the topic directly.

    Example:
        topic="DBMS", doc_type="dbms" → expanded query about ACID, SQL...
        topic="Deadlock",  doc_type=None → "Deadlock" (specific enough)
    """
    # Check if topic name maps to a known subject
    topic_lower = topic.lower().strip()

    # Exact match on doc_type key
    if doc_type and doc_type in TOPIC_QUERY_MAP:
        return TOPIC_QUERY_MAP[doc_type]

    # Topic name matches a subject label
    subject_names = {
        "dbms": "dbms", "database": "dbms", "databases": "dbms",
        "os": "os", "operating system": "os", "operating systems": "os",
        "cn": "cn", "computer networks": "cn", "networking": "cn",
        "oop": "oop", "object oriented": "oop",
    }
    matched = subject_names.get(topic_lower)
    if matched and matched in TOPIC_QUERY_MAP:
        return TOPIC_QUERY_MAP[matched]

    # Specific topic — use as-is
    return topic


async def create_revision_notes(
    topic:    str,
    doc_type: str | None = None,
    company:  str | None = None,
) -> dict:
    """
    Full pipeline for revision note generation.

    Returns:
        {
            "content":       str,   # Generated markdown notes
            "topic":         str,
            "chunks_used":   int,   # How many chunks contributed
            "theory_chunks": int,
            "interview_chunks": int,
        }
    """
    logger.info(f"Creating revision notes | topic='{topic}' | doc_type={doc_type}")

    # ── Step 1: Expand topic into effective search query ───────────────────────
    search_query = get_search_query(topic, doc_type)
    logger.info(f"Search query: '{search_query[:80]}...'")

    # ── Step 2: Multi-source retrieval ─────────────────────────────────────────
    chunks = search_multi_source(
        query=search_query,
        topic_doc_type=doc_type,
        company=company,
        theory_k=8,       # More theory for revision notes
        interview_k=3,    # Some interview context is useful
    )

    # Count by type
    theory_count    = sum(1 for c in chunks if c.get("search_source") == "theory")
    interview_count = sum(1 for c in chunks if c.get("search_source") == "interview")

    logger.info(
        f"Retrieved {len(chunks)} chunks "
        f"({theory_count} theory, {interview_count} interview)"
    )

    # ── Step 3: Generate revision notes ───────────────────────────────────────
    content = await generate_revision_notes(
        topic=topic,
        context_chunks=chunks
    )

    return {
        "content":          content,
        "topic":            topic,
        "chunks_used":      len(chunks),
        "theory_chunks":    theory_count,
        "interview_chunks": interview_count,
    }


async def create_interview_questions(
    topic:         str,
    doc_type:      str | None = None,
    company:       str | None = None,
    num_questions: int = 20,
) -> dict:
    """
    Full pipeline for interview question generation.

    For interview questions, we weight interview experiences
    more heavily than for revision notes.

    Returns:
        {
            "content":          str,
            "topic":            str,
            "company":          str | None,
            "num_questions":    int,
            "chunks_used":      int,
            "theory_chunks":    int,
            "interview_chunks": int,
        }
    """
    logger.info(
        f"Creating interview questions | topic='{topic}' | "
        f"company={company} | num={num_questions}"
    )

    # ── Step 1: Build search query ─────────────────────────────────────────────
    search_query = get_search_query(topic, doc_type)

    # ── Step 2: Multi-source retrieval ─────────────────────────────────────────
    # For questions: equal weight theory and interview experiences
    chunks = search_multi_source(
        query=search_query,
        topic_doc_type=doc_type,
        company=company,
        theory_k=5,       # Theory for accurate answers
        interview_k=6,    # More interview experiences for real questions
    )

    theory_count    = sum(1 for c in chunks if c.get("search_source") == "theory")
    interview_count = sum(1 for c in chunks if c.get("search_source") == "interview")

    logger.info(
        f"Retrieved {len(chunks)} chunks "
        f"({theory_count} theory, {interview_count} interview)"
    )

    # ── Step 3: Generate interview questions ───────────────────────────────────
    content = await generate_interview_questions(
        topic=topic,
        context_chunks=chunks,
        num_questions=num_questions,
        company=company
    )

    return {
        "content":          content,
        "topic":            topic,
        "company":          company,
        "num_questions":    num_questions,
        "chunks_used":      len(chunks),
        "theory_chunks":    theory_count,
        "interview_chunks": interview_count,
    }