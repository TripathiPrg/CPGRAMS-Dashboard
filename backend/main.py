"""
CPGRAMS Personal Workbench - Application Entry Point
AI & Emerging Technologies Division, MeitY, Government of India
FastAPI Server bound strictly to 127.0.0.1
"""

import os
from pathlib import Path
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware

from backend.config import PROJECT_ROOT, HOST, PORT
from backend.database import init_db, SessionLocal
from backend.seed_data import seed_database
from backend.routers import (
    dashboard,
    portal,
    intake,
    grievances,
    precedents,
    drafting,
    correspondence,
    reports,
    settings
)

# Initialize Database and Seed realistic synthetic data
init_db()
with SessionLocal() as db:
    seed_database(db)

app = FastAPI(
    title="CPGRAMS Personal Workbench",
    description="Local Automation, Grievance Management & Precedent-Assisted Drafting for MeitY AI & Emerging Technologies Division",
    version="1.0.0"
)

# Security Middleware: Localhost CORS and Security Headers
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:8000",
        "http://localhost:8000",
        "http://127.0.0.1:8501"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "SAMEORIGIN"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "no-referrer"
        return response

app.add_middleware(SecurityHeadersMiddleware)

# Register Routers
app.include_router(dashboard.router)
app.include_router(portal.router)
app.include_router(intake.router)
app.include_router(grievances.router)
app.include_router(precedents.router)
app.include_router(drafting.router)
app.include_router(correspondence.router)
app.include_router(reports.router)
app.include_router(settings.router)

# Mount Frontend Static Assets
frontend_dir = PROJECT_ROOT / "frontend"
if frontend_dir.exists():
    app.mount("/static", StaticFiles(directory=str(frontend_dir)), name="static")

@app.get("/")
def serve_index():
    """Serves the primary Single Page Application interface."""
    index_file = frontend_dir / "index.html"
    if index_file.exists():
        return FileResponse(str(index_file))
    return {"message": "CPGRAMS Personal Workbench API is running. Frontend index.html not found."}

@app.get("/health")
def health_check():
    """Local liveness check."""
    return {
        "status": "healthy",
        "service": "CPGRAMS Personal Workbench",
        "division": "AI & Emerging Technologies Division, MeitY",
        "mode": "Local Offline / localhost bound"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host=HOST, port=PORT, reload=False)
