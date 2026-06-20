# backend/routers/upload.py

import logging
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from typing import Optional

from services.pdf_service import process_pdf
from services.embedding_service import embed_and_store  # We build this in Step 3
from models.schemas import UploadResponse, ListDocumentsResponse, DocumentInfo, ALLOWED_DOC_TYPES
from database.chroma_client import get_or_create_collection

logger = logging.getLogger(__name__)

router = APIRouter()


# ── POST /upload ───────────────────────────────────────────────────────────────
@router.post("/upload", response_model=UploadResponse)
async def upload_pdf(
    file: UploadFile = File(...),           # The PDF file
    doc_type: str = Form(...),             # "dbms", "os", "cn", "oop", "interview_experience"
    company: Optional[str] = Form(None),   # "amazon", "google", etc. (only for interview_experience)
):
    """
    Upload a PDF and process it into the vector database.

    Accepts multipart/form-data with:
    - file: the PDF binary
    - doc_type: category of document
    - company: (optional) company name for interview experiences
    """
    # ── Validate doc_type ────────────────────────────────────────────────────
    if doc_type not in ALLOWED_DOC_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid doc_type '{doc_type}'. Must be one of: {ALLOWED_DOC_TYPES}"
        )

    # ── Validate company requirement ─────────────────────────────────────────
    # Company is required only for interview_experience documents
    if doc_type == "interview_experience" and not company:
        raise HTTPException(
            status_code=400,
            detail="Company name is required for interview_experience documents"
        )

    # ── Company is irrelevant for subject notes ───────────────────────────────
    if doc_type != "interview_experience":
        company = None  # Force null — don't store company for subject notes

    # ── Normalize company name ────────────────────────────────────────────────
    if company:
        company = company.lower().strip()

    logger.info(f"Upload request: file='{file.filename}', doc_type='{doc_type}', company='{company}'")

    # ── Step 1: Process PDF (extract text + metadata) ─────────────────────────
    try:
        processed = await process_pdf(
            upload_file=file,
            doc_type=doc_type,
            company=company
        )
    except HTTPException:
        raise  # Pass through our own HTTP exceptions
    except Exception as e:
        logger.error(f"PDF processing failed: {e}")
        raise HTTPException(status_code=500, detail=f"PDF processing failed: {str(e)}")

    # ── Step 2: Embed and store in ChromaDB ───────────────────────────────────
    # (embed_and_store is built in Step 3 — import stays here)
    try:
        chunks_created = await embed_and_store(processed["pages"])
    except Exception as e:
        logger.error(f"Embedding failed: {e}")
        raise HTTPException(status_code=500, detail=f"Embedding and storage failed: {str(e)}")

    # ── Return success response ───────────────────────────────────────────────
    return UploadResponse(
        message=f"Successfully processed '{processed['filename']}'",
        filename=processed["filename"],
        chunks_created=chunks_created,
        doc_type=doc_type,
        company=company,
        pages_extracted=len(processed["pages"])
    )


# ── GET /documents ─────────────────────────────────────────────────────────────
@router.get("/documents", response_model=ListDocumentsResponse)
async def list_documents():
    """
    Returns all documents currently stored in ChromaDB.
    Used by the React frontend to show the sidebar document list.
    """
    try:
        collection = get_or_create_collection()

        # Get all items from ChromaDB (just metadata, not embeddings)
        results = collection.get(include=["metadatas"])

        if not results["metadatas"]:
            return ListDocumentsResponse(documents=[], total_chunks=0)

        # ── Group chunks by filename ─────────────────────────────────────────
        # Each document has many chunks — we want one entry per document
        doc_map = {}
        for meta in results["metadatas"]:
            filename = meta.get("filename", "unknown")
            if filename not in doc_map:
                doc_map[filename] = {
                    "filename": filename,
                    "doc_type": meta.get("doc_type", "unknown"),
                    "company": meta.get("company"),
                    "chunks": 0
                }
            doc_map[filename]["chunks"] += 1

        # Build response
        documents = [
            DocumentInfo(**doc_info)
            for doc_info in doc_map.values()
        ]

        return ListDocumentsResponse(
            documents=documents,
            total_chunks=len(results["metadatas"])
        )

    except Exception as e:
        logger.error(f"Failed to list documents: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ── DELETE /documents/{filename} ───────────────────────────────────────────────
@router.delete("/documents/{filename}")
async def delete_document(filename: str):
    """
    Deletes all chunks of a specific document from ChromaDB.

    Why delete by filename?
    ChromaDB stores chunks, not whole documents.
    We find all chunks with matching filename metadata and delete them.
    """
    try:
        collection = get_or_create_collection()

        # Delete all chunks where metadata["filename"] == filename
        collection.delete(
            where={"filename": filename}
        )

        logger.info(f"Deleted document: {filename}")
        return {"message": f"Document '{filename}' deleted successfully"}

    except Exception as e:
        logger.error(f"Failed to delete document: {e}")
        raise HTTPException(status_code=500, detail=str(e))