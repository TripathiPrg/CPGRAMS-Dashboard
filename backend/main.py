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

from backend.config import PROJECT_ROOT, HOST, PORT, ALLOWED_ORIGINS, LOCAL_BRIDGE_TOKEN
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
    settings,
    disposal
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

# Security Middleware: Localhost & GitHub Pages CORS and Security Headers
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    allow_private_network=True,
)

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "SAMEORIGIN"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "no-referrer"
        # Support Chrome/Edge Private Network Access (PNA) preflight from GitHub Pages
        if request.headers.get("access-control-request-private-network") == "true":
            response.headers["Access-Control-Allow-Private-Network"] = "true"
        return response

app.add_middleware(SecurityHeadersMiddleware)

# Bridge Authentication & Health Endpoints
@app.get("/api/bridge/status")
def bridge_status(request: Request):
    """
    Status endpoint queried by GitHub Pages frontend (tripathiprg.github.io)
    to verify local agent connectivity and handshake.
    """
    origin = request.headers.get("origin", "")
    return {
        "status": "online",
        "service": "CPGRAMS Personal Workbench Local Integration Agent",
        "division": "AI & Emerging Technologies Division, MeitY",
        "version": "1.0.0",
        "origin_detected": origin,
        "is_paired": True
    }

@app.get("/api/bridge/token")
def get_bridge_token(request: Request):
    """
    Returns the active local bridge pairing token when accessed from localhost.
    Used for pairing the GitHub Pages UI with the local machine.
    """
    client_host = request.client.host if request.client else ""
    if client_host not in ["127.0.0.1", "localhost", "::1", "testclient"]:
        return {"error": "Access denied. Token can only be viewed from localhost."}
    return {
        "token": LOCAL_BRIDGE_TOKEN,
        "instructions": "Copy this token to pair your hosted GitHub Pages dashboard with your local machine."
    }

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
app.include_router(disposal.router)

# Mount Static Assets
css_dir = PROJECT_ROOT / "css"
js_dir = PROJECT_ROOT / "js"
frontend_dir = PROJECT_ROOT / "frontend"

if css_dir.exists():
    app.mount("/css", StaticFiles(directory=str(css_dir)), name="css")
if js_dir.exists():
    app.mount("/js", StaticFiles(directory=str(js_dir)), name="js")
if frontend_dir.exists():
    app.mount("/static", StaticFiles(directory=str(frontend_dir)), name="static")

@app.get("/")
def serve_index():
    """Serves the primary Single Page Application interface."""
    root_index = PROJECT_ROOT / "index.html"
    if root_index.exists():
        return FileResponse(str(root_index))
    alt_index = frontend_dir / "index.html"
    if alt_index.exists():
        return FileResponse(str(alt_index))
    return {"message": "CPGRAMS Personal Workbench API is running. index.html not found."}

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
