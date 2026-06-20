# backend/utils/chunker.py

import logging
from langchain_text_splitters import RecursiveCharacterTextSplitter
from typing import List

logger = logging.getLogger(__name__)

# ── Chunking Configuration ─────────────────────────────────────────────────────
#
# CHUNK_SIZE: Maximum characters per chunk.
# Why 800? Gemini Flash handles ~30k tokens. We want chunks small enough
# to be precise but large enough to carry a complete idea.
# 800 chars ≈ 120-150 words ≈ one concept explained fully.
#
# CHUNK_OVERLAP: Characters shared between consecutive chunks.
# Why 150? ~19% overlap. Prevents losing context at boundaries.
# A sentence that starts at char 780 will appear in both chunk N and N+1.
#
# These numbers are tunable — in interviews, say:
# "I chose these values empirically. Smaller chunks = more precise retrieval
#  but less context per chunk. Larger chunks = more context but less precise.
#  800/150 is a common starting point for technical documents."

CHUNK_SIZE    = 800
CHUNK_OVERLAP = 150

# ── Separators (order matters!) ────────────────────────────────────────────────
# RecursiveCharacterTextSplitter tries each separator in order.
# It prefers to split on paragraph breaks, then sentences, then words.
# Only splits mid-word as absolute last resort.
SEPARATORS = [
    "\n\n",   # Paragraph break (best split point)
    "\n",     # Line break
    ". ",     # End of sentence
    "! ",     # End of exclamation
    "? ",     # End of question
    "; ",     # Semicolon
    ", ",     # Comma
    " ",      # Word boundary
    "",       # Character boundary (last resort)
]


def create_text_splitter() -> RecursiveCharacterTextSplitter:
    """
    Creates a LangChain RecursiveCharacterTextSplitter.

    Why RecursiveCharacterTextSplitter over simple split()?
    Simple split() on '\n' would break mid-sentence.
    Recursive splitter tries increasingly smaller separators
    until chunks are within the size limit — preserving sentence integrity.
    """
    return RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        separators=SEPARATORS,
        length_function=len,          # Count characters (not tokens)
        is_separator_regex=False,     # Treat separators as plain strings
    )


def chunk_page(page_text: str, metadata: dict) -> List[dict]:
    """
    Splits a single page's text into overlapping chunks.

    Args:
        page_text: Raw text from one PDF page
        metadata:  Metadata dict (filename, doc_type, company, page_number)

    Returns:
        List of chunk dicts:
        [
            {
                "text": "ACID properties stand for...",
                "metadata": {
                    "filename": "DBMS_Notes_a3f8b2c1.pdf",
                    "doc_type": "dbms",
                    "page_number": 3,
                    "chunk_index": 0,       ← position within the page
                    "source": "DBMS_Notes_a3f8b2c1.pdf (Page 3, Chunk 1)"
                }
            },
            ...
        ]
    """
    splitter = create_text_splitter()

    # Split the page text into chunks
    raw_chunks = splitter.split_text(page_text)

    # Filter out chunks that are too short to be meaningful
    # (e.g., a chunk that's just a page number or header)
    meaningful_chunks = [c for c in raw_chunks if len(c.strip()) >= 50]

    # Attach enriched metadata to each chunk
    chunks = []
    for idx, chunk_text in enumerate(meaningful_chunks):
        chunk_metadata = {
            **metadata,                     # Copy all page-level metadata
            "chunk_index": idx,             # Position within this page
            "chunk_size": len(chunk_text),  # Actual size for debugging
            "source": (
                f"{metadata['filename']} "
                f"(Page {metadata['page_number']}, Chunk {idx + 1})"
            )
        }
        chunks.append({
            "text": chunk_text.strip(),
            "metadata": chunk_metadata
        })

    return chunks


def chunk_all_pages(pages: List[dict]) -> List[dict]:
    """
    Chunks all pages from a processed PDF.

    Args:
        pages: List of page dicts from pdf_service.process_pdf()
                Each has: {"page_number": int, "text": str, "metadata": dict}

    Returns:
        Flat list of all chunks across all pages.
    """
    all_chunks = []

    for page in pages:
        page_chunks = chunk_page(
            page_text=page["text"],
            metadata=page["metadata"]
        )
        all_chunks.extend(page_chunks)

        logger.debug(
            f"Page {page['page_number']}: "
            f"{len(page['text'])} chars → {len(page_chunks)} chunks"
        )

    logger.info(
        f"Chunking complete: {len(pages)} pages → {len(all_chunks)} total chunks"
    )

    return all_chunks