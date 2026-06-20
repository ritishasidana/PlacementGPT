# backend/services/retrieval_service.py

import logging
from typing import Optional
from database.chroma_client import get_or_create_collection
from services.embedding_service import embed_query

logger = logging.getLogger(__name__)

# ── Similarity Threshold ───────────────────────────────────────────────────────
# Chunks below this similarity score are excluded from results.
# Why 0.3? Cosine similarity of 0.3 means the texts share some semantic
# overlap. Below this, retrieved chunks are likely irrelevant noise.
# In interviews: "I use a threshold to avoid hallucination from
# low-relevance context — better to say 'not found' than answer
# from vaguely related content."
MIN_SIMILARITY_THRESHOLD = 0.3


def build_chroma_filter(
    doc_types: Optional[list[str]] = None,
    company: Optional[str] = None
) -> Optional[dict]:
    """
    Builds a ChromaDB metadata filter (the `where` clause).

    ChromaDB supports these operators:
    - $eq   : equals
    - $in   : value in list
    - $and  : logical AND of conditions
    - $or   : logical OR of conditions

    Examples:
    - Filter by single doc_type:  {"doc_type": {"$eq": "dbms"}}
    - Filter by multiple types:   {"doc_type": {"$in": ["dbms", "os"]}}
    - Filter by company:          {"company":  {"$eq": "amazon"}}
    - Filter by both:             {"$and": [{...}, {...}]}

    Why a dedicated function?
    ChromaDB filter syntax is verbose. This function converts simple
    Python values into the correct filter structure, keeping the
    retrieval logic clean.
    """
    conditions = []

    # ── doc_type filter ────────────────────────────────────────────────────────
    if doc_types and len(doc_types) > 0:
        # Clean and validate doc_types
        clean_types = [dt.lower().strip() for dt in doc_types]

        if len(clean_types) == 1:
            # Single type — use $eq (simpler)
            conditions.append({"doc_type": {"$eq": clean_types[0]}})
        else:
            # Multiple types — use $in
            conditions.append({"doc_type": {"$in": clean_types}})

    # ── company filter ─────────────────────────────────────────────────────────
    if company:
        conditions.append({"company": {"$eq": company.lower().strip()}})

    # ── Combine conditions ─────────────────────────────────────────────────────
    if not conditions:
        return None          # No filter — search everything
    elif len(conditions) == 1:
        return conditions[0] # Single condition — no need for $and
    else:
        return {"$and": conditions}  # Multiple — combine with AND


def search_chunks(
    query: str,
    top_k: int = 5,
    doc_types: Optional[list[str]] = None,
    company: Optional[str] = None
) -> list[dict]:
    """
    Core retrieval function.

    Steps:
    1. Embed the user's query using Gemini (retrieval_query task type)
    2. Build optional metadata filter
    3. Query ChromaDB for top-k most similar chunks
    4. Filter out low-similarity results
    5. Return chunks with text, metadata, and similarity scores

    Args:
        query:     The user's question
        top_k:     Maximum number of chunks to return
        doc_types: Optional list to filter by document type
        company:   Optional company name to filter interview experiences

    Returns:
        List of chunk dicts with keys: text, metadata, similarity_score
    """
    logger.info(
        f"Searching: query='{query[:60]}...', "
        f"top_k={top_k}, doc_types={doc_types}, company={company}"
    )

    # ── Step 1: Embed the query ────────────────────────────────────────────────
    print("Reached retrieval service")
    query_vector = embed_query(query)

    # ── Step 2: Build metadata filter ─────────────────────────────────────────
    chroma_filter = build_chroma_filter(doc_types, company)
    logger.debug(f"ChromaDB filter: {chroma_filter}")

    # ── Step 3: Query ChromaDB ─────────────────────────────────────────────────
    collection = get_or_create_collection()

    # Check if collection has enough documents to query
    total_chunks = collection.count()
    if total_chunks == 0:
        logger.warning("ChromaDB collection is empty — no documents uploaded yet")
        return []

    # Ensure top_k doesn't exceed total available chunks
    effective_top_k = min(top_k, total_chunks)

    try:
        results = collection.query(
            query_embeddings=[query_vector],
            n_results=effective_top_k,
            where=chroma_filter,             # None = no filter = search all
            include=["documents", "metadatas", "distances"]
        )
    except Exception as e:
        logger.error(f"ChromaDB query failed: {e}")
        raise RuntimeError(f"Vector search failed: {str(e)}")

    # ── Step 4: Parse and filter results ──────────────────────────────────────
    # ChromaDB returns nested lists (one list per query, since you can
    # send multiple queries at once). We sent one query, so index [0].
    raw_docs      = results["documents"][0]
    raw_metadatas = results["metadatas"][0]
    raw_distances = results["distances"][0]

    chunks = []
    for doc, meta, dist in zip(raw_docs, raw_metadatas, raw_distances):
        # Convert cosine distance → similarity score [0, 1]
        # Distance 0 = identical (similarity 1.0)
        # Distance 2 = opposite  (similarity 0.0)
        similarity = round(1 - (dist / 2), 4)

        # Filter out low-relevance chunks
        if similarity < MIN_SIMILARITY_THRESHOLD:
            logger.debug(
                f"Filtered out low-similarity chunk: "
                f"{similarity:.2%} < {MIN_SIMILARITY_THRESHOLD:.2%}"
            )
            continue

        chunks.append({
            "text":             doc,
            "metadata":         meta,
            "similarity_score": similarity
        })

    # Sort by similarity (highest first — ChromaDB already does this,
    # but explicit sort ensures consistency after filtering)
    chunks.sort(key=lambda x: x["similarity_score"], reverse=True)

    logger.info(
        f"Retrieved {len(chunks)} relevant chunks "
        f"(filtered from {len(raw_docs)} raw results)"
    )

    return chunks


def get_available_companies() -> list[str]:
    """
    Returns a list of all companies present in ChromaDB metadata.
    Used by the frontend to populate the company filter dropdown.
    """
    collection = get_or_create_collection()

    if collection.count() == 0:
        return []

    results = collection.get(include=["metadatas"])

    companies = set()
    for meta in results["metadatas"]:
        company = meta.get("company")
        if company:
            companies.add(company)

    return sorted(list(companies))


def get_available_doc_types() -> list[str]:
    """
    Returns all doc_types currently stored in ChromaDB.
    Used by the frontend to show active filter options.
    """
    collection = get_or_create_collection()

    if collection.count() == 0:
        return []

    results = collection.get(include=["metadatas"])

    doc_types = set()
    for meta in results["metadatas"]:
        dt = meta.get("doc_type")
        if dt:
            doc_types.add(dt)

    return sorted(list(doc_types))

# backend/services/retrieval_service.py  (add to existing file)
# Add this function below the existing search_chunks function

def search_multi_source(
    query:         str,
    topic_doc_type: str | None = None,
    company:       str | None = None,
    theory_k:      int = 6,
    interview_k:   int = 4,
) -> list[dict]:
    """
    Performs two parallel searches and merges results:
      1. Theory search  — finds subject-note chunks relevant to the topic
      2. Interview search — finds interview experience chunks for the company

    Why two separate searches?
    If we search everything at once with a company filter,
    we miss theory content (which has no company tag).
    If we search without a company filter, interview experiences
    from all companies dilute the results.

    Two targeted searches + merge gives the best of both.

    Args:
        query:          The topic or question to search for
        topic_doc_type: Specific subject to search in (e.g., "os", "dbms")
                        If None, searches all non-interview doc types
        company:        Company to focus interview experiences on
        theory_k:       Max theory chunks to retrieve
        interview_k:    Max interview experience chunks to retrieve

    Returns:
        Merged, deduplicated list of chunks sorted by similarity
    """
    logger.info(
        f"Multi-source search | query='{query[:50]}' | "
        f"doc_type={topic_doc_type} | company={company}"
    )

    all_chunks = []
    seen_texts = set()  # For deduplication

    # ── Search 1: Theory/Notes ─────────────────────────────────────────────────
    theory_doc_types = [topic_doc_type] if topic_doc_type else [
        "dbms", "os", "cn", "oop"   # All theory types, excluding interviews
    ]

    theory_chunks = search_chunks(
        query=query,
        top_k=theory_k,
        doc_types=theory_doc_types,
        company=None    # Theory notes don't have company tags
    )

    for chunk in theory_chunks:
        # Deduplicate by first 100 chars of text
        key = chunk["text"][:100]
        if key not in seen_texts:
            seen_texts.add(key)
            chunk["search_source"] = "theory"
            all_chunks.append(chunk)

    logger.info(f"Theory search returned {len(theory_chunks)} chunks")

    # ── Search 2: Interview Experiences ───────────────────────────────────────
    interview_chunks = search_chunks(
        query=query,
        top_k=interview_k,
        doc_types=["interview_experience"],
        company=company    # Filter by company if specified
    )

    for chunk in interview_chunks:
        key = chunk["text"][:100]
        if key not in seen_texts:
            seen_texts.add(key)
            chunk["search_source"] = "interview"
            all_chunks.append(chunk)

    logger.info(f"Interview search returned {len(interview_chunks)} chunks")

    # ── Merge and sort by similarity ──────────────────────────────────────────
    # Sort combined results by similarity score (highest first)
    all_chunks.sort(key=lambda x: x["similarity_score"], reverse=True)

    logger.info(
        f"Multi-source search complete: "
        f"{len(all_chunks)} total chunks "
        f"({len(theory_chunks)} theory + {len(interview_chunks)} interview)"
    )

    return all_chunks
