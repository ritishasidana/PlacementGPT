# backend/services/embedding_service.py
# FULL IMPLEMENTATION — replaces the stub from Step 2
import os
import uuid
import logging
import time
from typing import List

from google import genai
from dotenv import load_dotenv

from database.chroma_client import get_or_create_collection
from utils.chunker import chunk_all_pages

load_dotenv()

logger = logging.getLogger(__name__)

print("NEW EMBEDDING SERVICE LOADED")
# ── Embedding Model Configuration ──────────────────────────────────────────────
#
# We use Gemini's text-embedding-004 model.
#
# Why this model?
# - Free tier: 1500 requests/minute
# - Produces 768-dimensional vectors
# - Optimized for retrieval tasks (as opposed to classification)
# - Same Google ecosystem as our Gemini Flash LLM
#
# task_type="retrieval_document" tells the model we're embedding
# documents for storage (vs "retrieval_query" for search queries).
# Using the right task type improves retrieval accuracy.

EMBEDDING_MODEL = "gemini-embedding-001"
EMBEDDING_DIMENSIONS = 3072

# ── Batching Configuration ─────────────────────────────────────────────────────
#
# Why batch embeddings?
# Sending 200 chunks one-by-one = 200 API calls = slow + rate limit risk.
# Sending in batches of 20 = 10 API calls = fast.
# Gemini allows up to 100 texts per embedding batch call.

BATCH_SIZE = 20          # Chunks per API call
BATCH_DELAY_SECONDS = 0.5  # Small delay between batches (rate limit safety)


def embed_texts_in_batches(texts: List[str]) -> List[List[float]]:
    all_embeddings = []

    client = genai.Client(
        api_key=os.getenv("GOOGLE_API_KEY")
    )

    total_batches = (len(texts) + BATCH_SIZE - 1) // BATCH_SIZE

    for batch_num in range(total_batches):
        start = batch_num * BATCH_SIZE
        end = start + BATCH_SIZE
        batch = texts[start:end]

        logger.info(
            f"Embedding batch {batch_num + 1}/{total_batches} "
            f"({len(batch)} chunks)..."
        )

        try:
            batch_embeddings = []

            for text in batch:
                response = client.models.embed_content(
                    model=EMBEDDING_MODEL,
                    contents=text
                )

                batch_embeddings.append(
                    response.embeddings[0].values
                )

            all_embeddings.extend(batch_embeddings)

            if batch_num < total_batches - 1:
                time.sleep(BATCH_DELAY_SECONDS)

        except Exception as e:
            logger.exception("Embedding failed")
            raise RuntimeError(
                f"Embedding API call failed: {str(e)}"
            )

    logger.info(
        f"Generated {len(all_embeddings)} embeddings successfully"
    )

    return all_embeddings

def generate_chunk_ids(chunks: List[dict]) -> List[str]:
    """
    Generates unique IDs for each chunk.

    ChromaDB requires a unique string ID for every stored item.

    Format: "{filename}_{page}_{chunk_index}_{random}"
    Example: "DBMS_Notes_a3f8b2c1_p3_c0_7f2a"

    Why include filename + page + chunk_index?
    Makes IDs human-readable during debugging.
    The random suffix handles edge cases where same file is
    uploaded twice.
    """
    ids = []
    for chunk in chunks:
        meta = chunk["metadata"]
        base = (
            f"{meta['filename'][:20]}_"      # First 20 chars of filename
            f"p{meta['page_number']}_"
            f"c{meta['chunk_index']}_"
            f"{uuid.uuid4().hex[:6]}"         # 6-char random suffix
        )
        # ChromaDB IDs must not contain spaces or slashes
        safe_id = base.replace(" ", "_").replace("/", "_")
        ids.append(safe_id)

    return ids


async def embed_and_store(pages: List[dict]) -> int:
    """
    Main pipeline: chunk → embed → store in ChromaDB.

    This is called by the upload router after PDF text extraction.

    Args:
        pages: List of page dicts from pdf_service.process_pdf()

    Returns:
        Number of chunks stored in ChromaDB

    Full pipeline:
    1. Chunk all pages into smaller pieces
    2. Extract just the text strings for batch embedding
    3. Call Gemini to embed all texts
    4. Store (text + embeddings + metadata) in ChromaDB
    """

    # ── Step 1: Chunk all pages ────────────────────────────────────────────────
    logger.info(f"Starting embedding pipeline for {len(pages)} pages...")
    chunks = chunk_all_pages(pages)

    if not chunks:
        logger.warning("No chunks generated — possibly empty pages")
        return 0

    logger.info(f"Generated {len(chunks)} chunks from {len(pages)} pages")

    # ── Step 2: Extract texts for embedding ────────────────────────────────────
    texts     = [chunk["text"]     for chunk in chunks]
    metadatas = [chunk["metadata"] for chunk in chunks]

    # ── Step 3: Generate embeddings ────────────────────────────────────────────
    logger.info("Calling Gemini embedding API...")
    embeddings = embed_texts_in_batches(texts)

    # Sanity check: embeddings count must match chunks count
    assert len(embeddings) == len(chunks), (
        f"Embedding count mismatch: {len(embeddings)} embeddings "
        f"for {len(chunks)} chunks"
    )

    # ── Step 4: Generate unique IDs ────────────────────────────────────────────
    ids = generate_chunk_ids(chunks)

    # ── Step 5: Store in ChromaDB ──────────────────────────────────────────────
    logger.info("Storing chunks in ChromaDB...")
    collection = get_or_create_collection()

    # ChromaDB's add() stores everything together:
    # - ids:        unique identifier per chunk
    # - embeddings: the vector representation
    # - documents:  the original text (for retrieval display)
    # - metadatas:  filterable metadata dict
    collection.add(
        ids=ids,
        embeddings=embeddings,
        documents=texts,
        metadatas=metadatas
    )

    logger.info(
        f"✅ Successfully stored {len(chunks)} chunks in ChromaDB "
        f"(collection: 'placement_docs')"
    )

    return len(chunks)


def embed_query(query_text: str):
    print("NEW EMBED_QUERY EXECUTED")

    client = genai.Client(
        api_key=os.getenv("GOOGLE_API_KEY")
    )

    response = client.models.embed_content(
        model=EMBEDDING_MODEL,
        contents=query_text
    )

    return response.embeddings[0].values