"""
CPGRAMS Personal Workbench - Configuration Module
AI & Emerging Technologies Division, MeitY, Government of India
"""

import os
from pathlib import Path

# Base Paths
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"
UPLOADS_DIR = DATA_DIR / "uploads"
EXPORTS_DIR = DATA_DIR / "exports"
BACKUPS_DIR = DATA_DIR / "backups"

for folder in [DATA_DIR, UPLOADS_DIR, EXPORTS_DIR, BACKUPS_DIR]:
    folder.mkdir(parents=True, exist_ok=True)

# Database
DATABASE_URL = f"sqlite:///{DATA_DIR / 'cpgrams_workbench.db'}"

# Network & Server Security
HOST = "127.0.0.1"  # Bound to localhost only
PORT = 8000
ALLOW_EXTERNAL_REQUESTS = False  # Local-only mode enforced

# Privacy & PII Handling
DEFAULT_MASK_PII = True
ALLOWED_FILE_EXTENSIONS = {".pdf", ".docx", ".txt", ".xlsx", ".xls", ".csv"}
MAX_UPLOAD_SIZE_MB = 25

# Browser Automation Settings
CPGRAMS_PORTAL_URL = "https://pgportal.gov.in/CPGOFFICE/"
CPGRAMS_OPERATIONAL_DESK_URL = "https://pgportal.gov.in/CPGOFFICE/OperationalDesk#"
CPGRAMS_SEARCH_URL = "https://pgportal.gov.in/CPGOFFICE/Search"
CPGRAMS_SEARCH_LIST_URL = "https://pgportal.gov.in/CPGOFFICE/Search/List"

# Common browser executable locations on Windows
CHROME_PATHS = [
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
    os.path.expanduser(r"~\AppData\Local\Google\Chrome\Application\chrome.exe"),
]
EDGE_PATHS = [
    r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
    r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
    os.path.expanduser(r"~\AppData\Local\Microsoft\Edge\Application\msedge.exe"),
]

def get_installed_browser():
    for path in CHROME_PATHS:
        if os.path.exists(path):
            return {"name": "chrome", "path": path}
    for path in EDGE_PATHS:
        if os.path.exists(path):
            return {"name": "msedge", "path": path}
    return None

# AI and Semantic Search Settings
AI_MODE = "local_heuristic"  # 'local_heuristic', 'local_ollama'
OLLAMA_BASE_URL = "http://127.0.0.1:11434"
OLLAMA_MODEL = "llama3:latest"
SIMILARITY_THRESHOLD = 0.25  # Minimum TF-IDF cosine score to consider a relevant precedent
