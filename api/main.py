"""
FastAPI entry point — Module 26: Emergency Room Patient Alert System
Run: uvicorn api.main:app --reload
Docs: http://localhost:8000/docs
"""
import sys
from pathlib import Path

# Allow direct execution (python api/main.py) by adding project root.
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.module26.routes import router as module26_router

app = FastAPI(
    title="Module 26 — Emergency Room Patient Alert System",
    description=(
        "REST API for the ER Patient Alert module of the "
        "AI-Based Clinical Decision Support System.\n\n"
        "**DFD Processes:**\n"
        "- P26.1 Validate ER Visit Data\n"
        "- P26.2 Calculate Triage Score (ESI/CTAS/MTS)\n"
        "- P26.3 Generate Time-Sensitive Alerts\n"
        "- P26.4 Optimize Resource Allocation\n"
        "- P26.5 Generate Throughput Reports\n\n"
        "**Inter-module:** Receives from M25, sends to M27 & M29."
    ),
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(module26_router)


@app.get("/", tags=["Health"])
def health():
    return {"status": "ok", "module": 26, "name": "Emergency Room Patient Alert System"}