# backend/tests/test_api.py
"""
Integration tests for PlacementGPT API endpoints.

Run with: pytest tests/ -v
Or single test: pytest tests/test_api.py::test_health -v

These tests hit the actual running FastAPI server.
Start the server before running: uvicorn main:app --reload
"""

import pytest
import httpx
import os
import io
from pathlib import Path

BASE_URL = "http://localhost:8000/api/v1"

# ── Fixtures ───────────────────────────────────────────────────────────────────

@pytest.fixture
def client():
    """Synchronous HTTP client for tests."""
    return httpx.Client(base_url=BASE_URL, timeout=60.0)


@pytest.fixture
def sample_pdf_bytes():
    """
    Creates a minimal valid PDF in memory.
    Uses a real PDF structure so PyPDF can parse it.
    """
    # Minimal PDF with one page of text
    pdf_content = b"""%PDF-1.4
1 0 obj
<< /Type /Catalog /Pages 2 0 R >>
endobj
2 0 obj
<< /Type /Pages /Kids [3 0 R] /Count 1 >>
endobj
3 0 obj
<< /Type /Page /Parent 2 0 R /Resources
   << /Font << /F1 << /Type /Font /Subtype /Type1 /BaseFont /Helvetica >> >> >>
   /MediaBox [0 0 612 792]
   /Contents 4 0 R
>>
endobj
4 0 obj
<< /Length 200 >>
stream
BT
/F1 12 Tf
50 700 Td
(DBMS Interview Notes) Tj
0 -20 Td
(A deadlock is a situation where two or more processes are waiting for each other) Tj
0 -20 Td
(to release resources. The four conditions are Mutual Exclusion, Hold and Wait,) Tj
0 -20 Td
(No Preemption, and Circular Wait. ACID properties: Atomicity Consistency) Tj
0 -20 Td
(Isolation Durability. Normalization removes redundancy from databases.) Tj
ET
endstream
endobj
xref
0 5
0000000000 65535 f
0000000009 00000 n
0000000058 00000 n
0000000115 00000 n
0000000274 00000 n
trailer
<< /Size 5 /Root 1 0 R >>
startxref
526
%%EOF"""
    return pdf_content


# ── Health Check ───────────────────────────────────────────────────────────────

def test_health(client):
    """Server should be running and return status."""
    response = client.get("http://localhost:8000/")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    print(f"\n  ✅ Health: {data['status']}")


# ── Upload Tests ───────────────────────────────────────────────────────────────

def test_upload_valid_pdf(client, sample_pdf_bytes):
    """Valid PDF upload should return chunk count."""
    response = client.post(
        "/upload",
        files={"file": ("test_dbms.pdf", io.BytesIO(sample_pdf_bytes), "application/pdf")},
        data={"doc_type": "dbms"}
    )
    assert response.status_code == 200, f"Upload failed: {response.text}"
    data = response.json()
    assert "chunks_created"   in data
    assert "filename"         in data
    assert "pages_extracted"  in data
    assert data["doc_type"]  == "dbms"
    print(f"\n  ✅ Upload: {data['chunks_created']} chunks, {data['pages_extracted']} pages")
    return data["filename"]


def test_upload_invalid_doc_type(client, sample_pdf_bytes):
    """Invalid doc_type should return 400."""
    response = client.post(
        "/upload",
        files={"file": ("test.pdf", io.BytesIO(sample_pdf_bytes), "application/pdf")},
        data={"doc_type": "invalid_type"}
    )
    assert response.status_code == 400
    assert "Invalid doc_type" in response.json()["detail"]
    print(f"\n  ✅ Invalid doc_type correctly rejected")


def test_upload_interview_experience_without_company(client, sample_pdf_bytes):
    """Interview experience without company should return 400."""
    response = client.post(
        "/upload",
        files={"file": ("interview.pdf", io.BytesIO(sample_pdf_bytes), "application/pdf")},
        data={"doc_type": "interview_experience"}
    )
    assert response.status_code == 400
    assert "Company name is required" in response.json()["detail"]
    print(f"\n  ✅ Missing company correctly rejected")


def test_upload_interview_experience_with_company(client, sample_pdf_bytes):
    """Interview experience with company should succeed."""
    response = client.post(
        "/upload",
        files={"file": ("amazon_interview.pdf", io.BytesIO(sample_pdf_bytes), "application/pdf")},
        data={"doc_type": "interview_experience", "company": "amazon"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["company"] == "amazon"
    print(f"\n  ✅ Interview experience upload succeeded")


def test_upload_non_pdf(client):
    """Non-PDF file should return 400."""
    response = client.post(
        "/upload",
        files={"file": ("notes.txt", io.BytesIO(b"some text content"), "text/plain")},
        data={"doc_type": "dbms"}
    )
    assert response.status_code == 400
    assert "Only PDF files" in response.json()["detail"]
    print(f"\n  ✅ Non-PDF correctly rejected")


# ── Document List Tests ────────────────────────────────────────────────────────

def test_list_documents(client):
    """Should return list of uploaded documents."""
    response = client.get("/documents")
    assert response.status_code == 200
    data = response.json()
    assert "documents"    in data
    assert "total_chunks" in data
    assert isinstance(data["documents"],    list)
    assert isinstance(data["total_chunks"], int)
    print(f"\n  ✅ Listed {len(data['documents'])} documents, {data['total_chunks']} chunks")


# ── Filter Tests ───────────────────────────────────────────────────────────────

def test_get_filters(client):
    """Should return available filter options."""
    response = client.get("/filters")
    assert response.status_code == 200
    data = response.json()
    assert "companies" in data
    assert "doc_types" in data
    assert isinstance(data["companies"], list)
    assert isinstance(data["doc_types"], list)
    print(f"\n  ✅ Filters: doc_types={data['doc_types']}, companies={data['companies']}")


# ── Query Tests ────────────────────────────────────────────────────────────────

def test_query_basic(client):
    """Basic question should return answer + citations."""
    response = client.post("/query", json={
        "question": "What is a deadlock?",
        "top_k": 3
    })
    assert response.status_code == 200
    data = response.json()
    assert "answer"           in data
    assert "citations"        in data
    assert "chunks_retrieved" in data
    assert isinstance(data["answer"],    str)
    assert isinstance(data["citations"], list)
    assert len(data["answer"]) > 0
    print(f"\n  ✅ Query returned {data['chunks_retrieved']} chunks")
    print(f"     Answer preview: {data['answer'][:100]}...")


def test_query_with_doc_type_filter(client):
    """Query with doc_type filter should only return relevant chunks."""
    response = client.post("/query", json={
        "question": "Explain ACID properties",
        "doc_types": ["dbms"],
        "top_k": 3
    })
    assert response.status_code == 200
    data = response.json()
    # All citations should be from dbms doc_type
    for citation in data["citations"]:
        assert citation["doc_type"] == "dbms", \
            f"Expected dbms, got {citation['doc_type']}"
    print(f"\n  ✅ Doc type filter working: {len(data['citations'])} dbms citations")


def test_query_empty_question(client):
    """Empty question should return 422 validation error."""
    response = client.post("/query", json={"question": "   "})
    assert response.status_code == 422
    print(f"\n  ✅ Empty question correctly rejected")


def test_query_invalid_top_k(client):
    """top_k > 20 should return 422."""
    response = client.post("/query", json={
        "question": "test",
        "top_k": 100
    })
    assert response.status_code == 422
    print(f"\n  ✅ Invalid top_k correctly rejected")


# ── Generate Tests ─────────────────────────────────────────────────────────────

def test_generate_revision_notes(client):
    """Should generate structured revision notes."""
    response = client.post("/generate", json={
        "topic":         "Deadlock",
        "generate_type": "revision_notes",
        "doc_type":      "os"
    }, timeout=90.0)
    assert response.status_code == 200
    data = response.json()
    assert "content"       in data
    assert "topic"         in data
    assert "generate_type" in data
    assert len(data["content"]) > 100
    assert data["topic"]   == "Deadlock"
    print(f"\n  ✅ Revision notes: {len(data['content'])} chars")


def test_generate_interview_questions(client):
    """Should generate interview questions."""
    response = client.post("/generate", json={
        "topic":         "DBMS",
        "generate_type": "interview_questions",
        "num_questions": 5
    }, timeout=90.0)
    assert response.status_code == 200
    data = response.json()
    assert "content" in data
    assert len(data["content"]) > 100
    print(f"\n  ✅ Interview questions: {len(data['content'])} chars")


def test_generate_invalid_type(client):
    """Invalid generate_type should return 400."""
    response = client.post("/generate", json={
        "topic":         "DBMS",
        "generate_type": "magic_content"
    })
    assert response.status_code in [400, 422]
    print(f"\n  ✅ Invalid generate_type correctly rejected")


# ── Delete Test ────────────────────────────────────────────────────────────────

def test_delete_document(client, sample_pdf_bytes):
    """Upload then delete should work correctly."""
    # Upload first
    upload = client.post(
        "/upload",
        files={"file": ("to_delete.pdf", io.BytesIO(sample_pdf_bytes), "application/pdf")},
        data={"doc_type": "os"}
    )
    assert upload.status_code == 200
    filename = upload.json()["filename"]

    # Then delete
    delete = client.delete(f"/documents/{filename}")
    assert delete.status_code == 200
    assert "deleted successfully" in delete.json()["message"]
    print(f"\n  ✅ Delete working: {filename}")