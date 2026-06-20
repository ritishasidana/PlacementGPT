# backend/models/schemas.py

from pydantic import BaseModel, field_validator, Field
from typing import Optional, List

# ── Allowed Values (single source of truth) ───────────────────────────────────
ALLOWED_DOC_TYPES = ["dbms", "os", "cn", "oop", "interview_experience"]

ALLOWED_COMPANIES = [
    "amazon", "google", "microsoft", "flipkart",
    "infosys", "tcs", "wipro", "adobe", "samsung",
    "oracle", "uber", "swiggy", "zomato", "other"
]

# ── Upload Schemas ─────────────────────────────────────────────────────────────

class UploadResponse(BaseModel):
    """Returned after a PDF is successfully uploaded and processed."""
    message: str
    filename: str
    chunks_created: int
    doc_type: str
    company: Optional[str] = None
    pages_extracted: int


class DocumentInfo(BaseModel):
    """Info about a single uploaded document."""
    filename: str
    doc_type: str
    company: Optional[str] = None
    chunks: int


class ListDocumentsResponse(BaseModel):
    """List of all uploaded documents."""
    documents: List[DocumentInfo]
    total_chunks: int


# ── Query Schemas ──────────────────────────────────────────────────────────────

class QueryRequest(BaseModel):
    question: str
    doc_types: Optional[List[str]] = None
    company: Optional[str] = None
    top_k: int = Field(default=5, ge=1, le=20)

    @field_validator("question")
    @classmethod
    def validate_question(cls, value):
        if not value or not value.strip():
            raise ValueError("Question cannot be empty")
        return value.strip()

# ── Generate Schemas ──────────────────────────────────────────────────────────

class GenerateRequest(BaseModel):
    topic: str
    generate_type: str
    doc_type: Optional[str] = None
    company: Optional[str] = None
    num_questions: int = 5


class GenerateResponse(BaseModel):
    content: str
    topic: str
    generate_type: str

# ── Query Response Schemas ───────────────────────────────────────────────────
class Citation(BaseModel):
    source: str
    doc_type: str
    similarity: float
    chunk_text: str = ""

class QueryResponse(BaseModel):
    answer: str
    citations: List[Citation]
    chunks_retrieved: int