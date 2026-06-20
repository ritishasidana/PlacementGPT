# backend/main.py  (updated)

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from routers import upload, query, generate
import uvicorn
import os

# ── Load environment variables FIRST ──────────────────────────────────────────
# Must happen before any service that needs GOOGLE_API_KEY
from pathlib import Path

load_dotenv(Path(__file__).parent / ".env")

# ── Verify critical env vars ───────────────────────────────────────────────────
if not os.getenv("GOOGLE_API_KEY"):
    raise RuntimeError(
        "GOOGLE_API_KEY not found. "
        "Create a .env file in the backend/ directory with your Gemini API key."
    )

# ── App Initialization ─────────────────────────────────────────────────────────
app = FastAPI(
    title="PlacementGPT API",
    description="AI-Powered Placement Preparation Assistant",
    version="1.0.0",
    debug = True
)

# ── CORS Middleware ────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Register Routers ───────────────────────────────────────────────────────────
app.include_router(upload.router,   prefix="/api/v1", tags=["Upload"])
app.include_router(query.router,    prefix="/api/v1", tags=["Query"])
app.include_router(generate.router, prefix="/api/v1", tags=["Generate"])

# ── Health Check ───────────────────────────────────────────────────────────────
@app.get("/")
async def root():
    return {
        "status": "PlacementGPT is running ✅",
        "docs": "http://localhost:8000/docs"
    }

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)