# backend/services/pdf_service.py

import os
import uuid
import logging
from pypdf import PdfReader
from fastapi import UploadFile, HTTPException
from typing import Optional

# ── Logging Setup ──────────────────────────────────────────────────────────────
# Always use logging, not print(), in production code.
# It gives you timestamps, severity levels, and can be redirected to files.
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ── Constants ──────────────────────────────────────────────────────────────────
UPLOAD_DIR = os.path.join(os.path.dirname(__file__), "..", "uploads")
MAX_FILE_SIZE_MB = 50
ALLOWED_EXTENSIONS = {".pdf"}


# ── Directory Setup ────────────────────────────────────────────────────────────
def ensure_upload_dir():
    """Create the uploads directory if it doesn't exist."""
    os.makedirs(UPLOAD_DIR, exist_ok=True)


# ── File Validation ────────────────────────────────────────────────────────────
def validate_pdf_file(filename: str, file_size_bytes: int):
    """
    Validates that the uploaded file is a PDF within size limits.
    
    Why validate here and not in the router?
    Validation of file-specific rules belongs in the service layer.
    The router only validates HTTP-level concerns.
    """
    # Check extension
    _, ext = os.path.splitext(filename.lower())
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Only PDF files are allowed. Got: {ext}"
        )

    # Check size (convert bytes to MB)
    size_mb = file_size_bytes / (1024 * 1024)
    if size_mb > MAX_FILE_SIZE_MB:
        raise HTTPException(
            status_code=400,
            detail=f"File too large: {size_mb:.1f}MB. Maximum allowed: {MAX_FILE_SIZE_MB}MB"
        )


# ── Save File to Disk ──────────────────────────────────────────────────────────
async def save_upload_file(upload_file: UploadFile) -> tuple[str, bytes]:
    """
    Reads the uploaded file bytes and saves to disk.
    
    Returns:
        tuple: (saved_file_path, file_bytes)
    
    Why save to disk?
    PyPDF reads from a file path or file object.
    We also save originals so users could re-process them later.
    """
    ensure_upload_dir()

    # Read all bytes from the uploaded file
    file_bytes = await upload_file.read()

    # Validate before saving
    validate_pdf_file(upload_file.filename, len(file_bytes))

    # Generate a unique filename to avoid collisions
    # e.g., "DBMS_Notes.pdf" → "DBMS_Notes_a3f8b2c1.pdf"
    base_name, ext = os.path.splitext(upload_file.filename)
    unique_id = uuid.uuid4().hex[:8]  # Short 8-char unique suffix
    safe_filename = f"{base_name}_{unique_id}{ext}"

    # Build the full file path
    file_path = os.path.join(UPLOAD_DIR, safe_filename)

    # Write bytes to disk
    with open(file_path, "wb") as f:
        f.write(file_bytes)

    logger.info(f"Saved uploaded file: {safe_filename} ({len(file_bytes)/1024:.1f} KB)")
    return file_path, file_bytes, safe_filename


# ── Extract Text from PDF ──────────────────────────────────────────────────────
def extract_text_from_pdf(file_path: str) -> list[dict]:
    """
    Extracts text from each page of a PDF.

    Returns a list of dicts, one per page:
    [
        {"page_number": 1, "text": "Introduction to DBMS..."},
        {"page_number": 2, "text": "Relational Model..."},
        ...
    ]

    Why page-by-page?
    Preserving page numbers lets us include them in citations.
    "This answer is from Page 7 of your DBMS Notes" is much more useful
    than just a raw chunk of text.
    """
    pages = []

    try:
        reader = PdfReader(file_path)
        total_pages = len(reader.pages)
        logger.info(f"PDF has {total_pages} pages: {file_path}")

        for page_num, page in enumerate(reader.pages, start=1):
            # Extract text from this page
            text = page.extract_text()

            # Skip pages with no readable text
            # (e.g., scanned image PDFs, decorative pages)
            if not text or len(text.strip()) < 50:
                logger.warning(f"Page {page_num}: skipped (insufficient text)")
                continue

            # Clean up the extracted text
            cleaned_text = clean_text(text)

            pages.append({
                "page_number": page_num,
                "text": cleaned_text
            })

        if not pages:
            raise HTTPException(
                status_code=422,
                detail=(
                    "No readable text found in this PDF. "
                    "This may be a scanned image PDF. "
                    "Please upload a text-based PDF."
                )
            )

        logger.info(f"Successfully extracted text from {len(pages)} pages")
        return pages

    except HTTPException:
        raise  # Re-raise our own exceptions as-is

    except Exception as e:
        logger.error(f"Failed to extract text from PDF: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to read PDF file: {str(e)}"
        )


# ── Text Cleaning ──────────────────────────────────────────────────────────────
def clean_text(text: str) -> str:
    """
    Cleans raw PDF-extracted text.

    PDF text extraction is messy — it picks up:
    - Extra whitespace from column layouts
    - Hyphenated line breaks ("rela-\ntionship" → "relationship")
    - Multiple blank lines
    - Leading/trailing whitespace on each line

    Why clean? Cleaner text → better embeddings → more accurate retrieval.
    """
    import re

    # Fix hyphenated line breaks (word split across lines)
    text = re.sub(r'(\w+)-\n(\w+)', r'\1\2', text)

    # Replace multiple whitespace/newlines with a single space
    text = re.sub(r'\s+', ' ', text)

    # Remove non-printable characters
    text = re.sub(r'[^\x20-\x7E\n]', '', text)

    return text.strip()


# ── Build Metadata Dictionary ──────────────────────────────────────────────────
def build_metadata(
    filename: str,
    doc_type: str,
    company: Optional[str],
    page_number: int
) -> dict:
    """
    Builds the metadata dict attached to every chunk in ChromaDB.

    CRITICAL CONCEPT:
    This metadata is how we filter later.
    When a user asks "Show only Amazon interview questions",
    ChromaDB filters on metadata["company"] == "amazon".

    Every field here becomes a filterable attribute in ChromaDB.
    """
    metadata = {
        "filename": filename,
        "doc_type": doc_type,       # "dbms", "os", "cn", "oop", "interview_experience"
        "page_number": page_number,
        "source": f"{filename} (Page {page_number})"
    }

    # Only add company if it's an interview experience
    if company:
        metadata["company"] = company.lower()

    return metadata


# ── Main Processing Pipeline ───────────────────────────────────────────────────
async def process_pdf(
    upload_file: UploadFile,
    doc_type: str,
    company: Optional[str] = None
) -> dict:
    """
    Full PDF processing pipeline:
    1. Save file to disk
    2. Extract text page by page
    3. Return pages with metadata

    Returns:
        {
            "filename": "DBMS_Notes_a3f8b2c1.pdf",
            "pages": [{"page_number": 1, "text": "...", "metadata": {...}}, ...]
        }
    """
    # Step 1: Save uploaded file
    file_path, file_bytes, safe_filename = await save_upload_file(upload_file)

    # Step 2: Extract text from PDF
    pages = extract_text_from_pdf(file_path)

    # Step 3: Attach metadata to each page
    pages_with_metadata = []
    for page in pages:
        metadata = build_metadata(
            filename=safe_filename,
            doc_type=doc_type,
            company=company,
            page_number=page["page_number"]
        )
        pages_with_metadata.append({
            "page_number": page["page_number"],
            "text": page["text"],
            "metadata": metadata
        })

    logger.info(
        f"Processed '{safe_filename}': "
        f"{len(pages_with_metadata)} pages, "
        f"doc_type='{doc_type}', "
        f"company='{company}'"
    )

    return {
        "filename": safe_filename,
        "pages": pages_with_metadata
    }